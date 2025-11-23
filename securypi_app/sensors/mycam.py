import io
from threading import Condition, Timer
from datetime import datetime
from pathlib import Path

from securypi_app.services.string_parsing import timed_filename

# Conditional Import for RPi picamera2 library
try:
    from picamera2 import Picamera2    # pyright: ignore[reportMissingImports]
    from libcamera import controls    # pyright: ignore[reportMissingImports]
    from picamera2.encoders import JpegEncoder, H264Encoder, Quality    # pyright: ignore[reportMissingImports]
    from picamera2.outputs import FileOutput, PyavOutput    # pyright: ignore[reportMissingImports]
    
except ImportError as e:
    print("Failed to import picamera2 camera library, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")
    # Mock sensor classes for platform independent development
    from .mock_mycam import (
        MockPicamera2, MockEncoder, MockStreamingOutput, MockPyavOutput,
        MockQuality
    )
    Picamera2 = MockPicamera2
    JpegEncoder = MockEncoder
    H264Encoder = MockEncoder
    FileOutput = MockStreamingOutput
    PyavOutput = MockPyavOutput
    Quality = MockQuality


# @TODO move to global config
STREAM_TIMEOUT = 5 * 60 # 5 minutes
RECORDING_FRAMERATE = 25
SENSOR_RESOLUTION = (2304, 1296)
MAIN_RESOLUTION = (1920, 1080)
STREAM_RESOLUTION = (800, 450)


class StreamingOutput(io.BufferedIOBase):
    """
    Handles streaming of camera frames to a HTTP response.
    Uses a Condition to synchronize access to the latest frame.
    """

    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()


def generate_frames(output):
    """
    Generator function that yields camera frames in byte format.
    Wailts for a new frame from the camera and
    yields it as part of a multipart HTTP response.
    """
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n"
               b"Content-Length: " + f"{len(frame)}".encode() + b"\r\n\r\n" +
               frame + b"\r\n")


class MyPicamera2(Picamera2):
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
        self.configure_streams()
        self._streaming_output = StreamingOutput()
        self._stream_timer = None
        
        self._recording_encoder = None
        self._streaming_encoder = None

        self.configure_runtime_controls()
        self.start()

        self._initialized = True

    @classmethod
    def get_instance(cls):
        """ Singleton access method. """
        return cls()

    def configure_streams(self):
        """
        Configures camera streams:
        # main stream: high-res recording, snapshots
        # lores stream: for preview
        """
        config = self.video_configuration
        config.sensor = {'output_size': SENSOR_RESOLUTION, 'bit_depth': 10}
        config.main.size = MAIN_RESOLUTION

        stream_res = STREAM_RESOLUTION
        if STREAM_RESOLUTION > MAIN_RESOLUTION:
            stream_res = MAIN_RESOLUTION
        
        config.enable_lores()
        config.lores.size = stream_res
        # default stream for video encoding
        # config.encode = "main" (defaul value)

        self.configure(config)
        return self

    def configure_runtime_controls(self):
        self.set_noise_reduction() # turn off for now
        self.set_framerate(RECORDING_FRAMERATE)
        return self

    def set_noise_reduction(self):
        """
        0 -> Off
        1 -> Fast
        2 -> HighQuality
        """
        self.set_controls(
            {"NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Fast}
        )
        return self
    
    def set_framerate(self, framerate=None):
        if framerate is None:
            framerate = RECORDING_FRAMERATE
        if framerate < 1:
            framerate = 30
        
        duration_limit = int(round(1 / framerate * 1000000, 0))
        
        self.set_controls(
            {"FrameDurationLimits": (duration_limit, duration_limit)}
        )
        print(self.controls)
        return self

    def is_recording(self):
        return self._recording_encoder is not None

    def is_streaming(self):
        return self._streaming_encoder is not None

    def start_recording_to_file(self,
                                output_path: str,
                                stream: str = "main",
                                encode_quality=Quality.MEDIUM):
        """
        Start high-res video recording to file.
        -> output_path
        -> stream: which stream to record from ("main" or "lores")
        -> encode_quality: Quality.[LOW | MEDIUM | HIGH]
        """
        self._recording_encoder = H264Encoder()
        self.start_encoder(self._recording_encoder,
                           PyavOutput(output_path),
                           name=stream,
                           quality=encode_quality)
        return self
    
    def start_default_recording(self,
                                stream="main",
                                encode_quality=Quality.LOW):
        filename = timed_filename(".mp4")
        path_str = "captures/recordings/"
        
        path = Path(path_str)
        path.mkdir(parents=True, exist_ok=True)
        full_path = path / filename
        
        self.start_recording_to_file(full_path, stream, encode_quality)

    def stop_recording_to_file(self):
        if self._recording_encoder is not None:
            self.stop_encoder(self._recording_encoder)
            self._recording_encoder = None
        return self

    def start_capture_stream(
        self, stream: str = "lores"
    ) -> StreamingOutput:
        # cancel stream timeout, if set - avoid timing out prematurely
        if self._stream_timer is not None:
            self._stream_timer.cancel()
            self._stream_timer = None
        # won't be starting two encoders
        if self._streaming_encoder is None:
            self._streaming_encoder = JpegEncoder()
            self.start_encoder(self._streaming_encoder,
                               FileOutput(self._streaming_output),
                               name=stream)
            
        self._stream_timer = Timer(STREAM_TIMEOUT, self.stop_capture_stream)
        self._stream_timer.start()
        
        return self._streaming_output

    def stop_capture_stream(self):
        if self._streaming_encoder is not None:
            self.stop_encoder(self._streaming_encoder)
            self._streaming_encoder = None
            self._stream_timer = None
            print("Stopped video streaming (timer).")
        return self

    def capture_picture(self):
        # Capture an image to a BytesIO object
        buffer = io.BytesIO()
        self.capture_file(buffer, format="jpeg")

        # Return the byte data
        return buffer.getvalue()
