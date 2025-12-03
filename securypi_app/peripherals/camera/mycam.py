import io
from pathlib import Path

from securypi_app.services.string_parsing import timed_filename
from securypi_app.peripherals.camera.mycam_interface import MyPicamera2Interface
from securypi_app.peripherals.camera.streaming import Streaming

# Conditional Import for RPi picamera2 library
try:
    from picamera2 import Picamera2    # pyright: ignore[reportMissingImports]
    from libcamera import controls # pyright: ignore[reportMissingImports]
    from picamera2.encoders import H264Encoder, Quality # pyright: ignore[reportMissingImports]
    from picamera2.outputs import PyavOutput # pyright: ignore[reportMissingImports]
    from securypi_app.peripherals.camera.motion_capturing import MotionCapturing # motion capturing is dependent on picamera2

except ImportError as e:
    print("Failed to import picamera2 camera library, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    from securypi_app.peripherals.camera.mock_camera_modules.mock_picamera2 import (
        MockPicamera2, MockEncoder, MockPyavOutput,
        MockQuality, Controls
    )
    from securypi_app.peripherals.camera.mock_camera_modules.mock_motion_capturing import (
        MockMotionCapturing
    )
    Picamera2 = MockPicamera2
    H264Encoder = MockEncoder
    PyavOutput = MockPyavOutput
    Quality = MockQuality
    controls = Controls
    MotionCapturing = MockMotionCapturing


# @TODO move to global config
STREAM_TIMEOUT = 5 * 60  # 5 minutes
RECORDING_FRAMERATE = 25
MAIN_RESOLUTION = (1920, 1080)
STREAM_RESOLUTION = (800, 450)


class MyPicamera2(MyPicamera2Interface):
    """
    My singleton wrapper class for Picamera2 with methods
    for streaming and taking pictures.
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """ Guarantees only one instance - singleton. """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """ Initialise once. """
        if self._initialized:
            return
        super().__init__()

        # wrapping PiCamera2 instance
        self._picam = Picamera2()

        self.configure_video_sensor()
        self.configure_video_streams()
        self.configure_runtime_controls()

        # encoders
        self._recording_encoder = None

        # extensions
        self.streaming = Streaming(self)
        self.motion_capturing = MotionCapturing(self)

        # Really only once.
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    def get_best_sensor_mode(self, resolution, fps):
        """
        Find highest resolution sensor mode
        with ability to provide requested framerate.
        """
        all_modes = self._picam.sensor_modes

        fps_eligible = []
        for mode in all_modes:
            if mode["fps"] >= fps:
                fps_eligible.append(mode)

        if fps_eligible[-1]["size"] >= resolution:
            # Last mode provides the highes sensor resolution
            best_mode = fps_eligible[-1]
        else:
            best_mode = None

        return best_mode

    def configure_video_sensor(self):
        """
        Set sensor configuration to the best mode
        inside the passed config.
        """
        # @TODO retrieve from config.json
        resolution = MAIN_RESOLUTION
        fps = RECORDING_FRAMERATE

        config = self._picam.video_configuration

        self._picam.stop()  # must be stopped before configuring
        best_config = self.get_best_sensor_mode(resolution, fps)
        if best_config is not None:
            size = best_config["size"]
            bit_depth = best_config["bit_depth"]

            config.sensor.output_size = size
            config.sensor.bit_depth = bit_depth

            self._picam.configure(config)
            print(f"Configured video sensor resolution to "
                  f"{size} with bit depth {bit_depth} at {fps} fps.")
        else:
            print(f"WARNING: Cannot configure sensor to "
                  f"resolution {resolution} at {fps} fps.\n"
                  f"Using default sensor mode (might be cropped - "
                  f"check camera.sensor_modes).")
        return self

    def configure_video_streams(self):
        """
        Configures camera streams:
        - main stream: high-res recording, snapshots
        - lores stream: for preview
        """
        # @TODO retrieve from config.json
        main_resolution = MAIN_RESOLUTION
        stream_resolution = STREAM_RESOLUTION

        self._picam.stop()  # must be stopped before configuring

        config = self._picam.video_configuration
        config.main.size = main_resolution

        stream_res = stream_resolution
        if (stream_resolution[0] > main_resolution[0] or
                stream_resolution[1] > main_resolution[1]):
            stream_res = MAIN_RESOLUTION

        config.enable_lores()
        config.lores.size = stream_res
        # default stream for video encoding
        # config.encode = "main" (defaul value)

        self._picam.configure(config)
        return self

    def get_current_resolution(self, target="sensor") -> tuple[int, int]:
        if target == "main":
            return self._picam.video_configuration.main.size
        elif target == "lores":
            return self._picam.video_configuration.lores.size

        return self._picam.video_configuration.sensor.output_size

    def configure_runtime_controls(self):
        self.set_noise_reduction()
        self.set_framerate(RECORDING_FRAMERATE)
        return self

    def set_noise_reduction(self, noise_reduction_mode="Fast"):
        nr_modes = controls.draft.NoiseReductionModeEnum.__members__
        if noise_reduction_mode not in nr_modes.keys():
            raise ValueError(f"Unknown NR mode value {noise_reduction_mode}. "
                             f"Expected one of: {[key for key in nr_modes.keys()]}")
        self._picam.set_controls(
            {"NoiseReductionMode": nr_modes[noise_reduction_mode]}
        )
        return self

    def set_framerate(self, framerate=None):
        if framerate is None:
            framerate = RECORDING_FRAMERATE
        if framerate < 1:
            framerate = 30

        duration_limit = int(round(1 / framerate * 1000000, 0))

        self._picam.set_controls(
            {"FrameDurationLimits": (duration_limit, duration_limit)}
        )

        return self

    def is_recording(self) -> bool:
        return self._recording_encoder is not None

    def start_recording_to_file(self,
                                output_path: str,
                                stream: str = "main",
                                encode_quality=Quality.MEDIUM):
        if self._recording_encoder is not None:
            raise RuntimeError("Recording already in progress.")

        self._recording_encoder = H264Encoder()
        self._picam.start_encoder(self._recording_encoder,
                                  PyavOutput(output_path),
                                  name=stream,
                                  quality=encode_quality)
        self._picam.start()
        return self

    def start_default_recording(self,
                                stream="main",
                                encode_quality=Quality.LOW) -> Path:
        filename = timed_filename(".mp4")
        path_str = "captures/recordings/"

        path = Path(path_str)
        path.mkdir(parents=True, exist_ok=True)
        full_path = path / filename

        self.start_recording_to_file(str(full_path), stream, encode_quality)

        return full_path

    def stop_recording_to_file(self):
        if self._recording_encoder is not None:
            self._picam.stop_encoder(self._recording_encoder)
            self._recording_encoder = None
        return self

    def capture_picture(self):
        """ Capture still picture and return it's raw value. """
        buffer = io.BytesIO()
        self._picam.start()
        self._picam.capture_file(buffer, format="jpeg")

        # Return the byte data
        return buffer.getvalue()
