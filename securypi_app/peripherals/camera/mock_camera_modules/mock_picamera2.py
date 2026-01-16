import random
from threading import Thread, Event
from io import BytesIO

from PIL import Image


class MockStreamingOutput:
    def __init__(self, output=None):
        self.output = output

    def write(self, data):
        if self.output:
            self.output.write(data)


class MockPyavOutput():
    def __init__(self, output=None):
        self.output = output

    def write(self, data):
        if self.output:
            with open(file=self.output, mode="w") as f:
                f.write("Mocking recording to a video output.")

# mocking controls.draft.NoiseReductionModeEnum


class NoiseReductionModeEnum:
    Off = 0
    Fast = 1
    HighQuality = 2
    Minimal = 3
    ZSL = 4

    __members__ = {'Off': 0, 'Fast': 1,
                   'HighQuality': 2, 'Minimal': 3, 'ZSL': 4}


class Draft:
    NoiseReductionModeEnum = NoiseReductionModeEnum


class Controls:
    draft = Draft


# mocking Picamera2...

class MockQuality:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MockEncoder:
    def __init__(self, *args, **kwargs):
        pass


class MockStreamConfig:
    """ Mocking object oriented camera configuration. """

    def __init__(self, size=None):
        self.size = size


class MockSensorConfig:
    """ Mocking object oriented camera configuration. """

    def __init__(self, size=None):
        self.output_size = size
        self.bit_depth = 10


class MockVideoConfiguration:
    """ Mocking object oriented camera configuration. """

    def __init__(self):
        self.main = MockStreamConfig((1920, 1080))
        self.lores = None
        self.sensor = MockSensorConfig((2304, 1296))

    def enable_lores(self):
        if self.lores is None:
            self.lores = MockStreamConfig()


class MockPicamera2:
    """
    Mocking Picamera2 library for the purpouses of
    working with mycam module (MyPicamera2).
    """
    _mock_encoder_thread = None
    _mock_encoder_stop_event = Event()

    # mocked sensor modes of RPI Camera Module 3 Wide
    sensor_modes = [
        {'format': "SRGGB10_CSI2P",
         'unpacked': "SRGGB10",
         'bit_depth': 10,
         'size': (1536, 864),
         'fps': 120.13,
         'crop_limits': (768, 432, 3072, 1728),
         'exposure_limits': (9, 77208145, 20000)},

        {'format': "SRGGB10_CSI2P",
         'unpacked': "SRGGB10",
         'bit_depth': 10,
         'size': (2304, 1296),
         'fps': 56.03,
         'crop_limits': (0, 0, 4608, 2592),
         'exposure_limits': (13, 112015096, 20000)},

        {'format': "SRGGB10_CSI2P",
         'unpacked': "SRGGB10",
         'bit_depth': 10,
         'size': (4608, 2592),
         'fps': 14.35,
         'crop_limits': (0, 0, 4608, 2592),
         'exposure_limits': (26, 220416802, 20000)}
    ]

    def __init__(self):
        self.sensor_resolution = (1920, 1080)
        self.started = False
        self.video_configuration = MockVideoConfiguration()
        self.new_frame_interval_seconds = 2  # new fake frame every n seconds

    def configure(self, config):
        print("[MockPicamera2] Configured with:", config)

    def start_encoder(self,
                      encoder,
                      output,
                      name="main",
                      quality=MockQuality.MEDIUM):
        """ Continuously generate fake frames """
        print(
            f"[MockPicamera2] Simulating video recording " +
            f"to {output} using {encoder} on stream '{name} "
            f"with quality '{quality}'")

        def frame_generator():
            while True:
                img = self.create_random_color_image(640, 360, brightness=0.5)
                buffer = BytesIO()
                img.save(buffer, format="JPEG")
                jpeg_bytes = buffer.getvalue()

                output.write(jpeg_bytes)
                if self._mock_encoder_stop_event.wait(
                    timeout=self.new_frame_interval_seconds
                ):
                    print("Mock encoder exited cleanly.")
                    break

        self._mock_encoder_stop_event.clear()  # clear stop signal

        self._mock_encoder_thread = Thread(target=frame_generator, daemon=True)
        self._mock_encoder_thread.start()

    def start_recording(self, encoder, output, name="main"):
        self.start_encoder(self, encoder, output, name)
        self.start()

    def stop_encoder(self, recording_encoder="<default mock encoder"):
        print(f"[MockPicamera2] Stopping encoder {recording_encoder}.")
        self._mock_encoder_stop_event.set()  # signal stop
        if self._mock_encoder_thread is not None:
            self._mock_encoder_thread.join(timeout=2.0)
        self._mock_encoder_stop_event.clear()  # clear stop signal

        self._mock_encoder_thread = None

    def stop_recording(self):
        self.stop()
        self.stop_encoder("[all encoders]")
        print("[MockPicamera2] Stopping recording.")

    def capture_file(self, stream, format="jpeg"):
        print("[MockPicamera2] Capturing fake image...")
        # Create a real JPEG image
        img = self.create_random_color_image(640, 360, brightness=0.5)
        img.save(stream, format=format)

    def start(self):
        print("[MockPicamera2] Starting mock camera.")

    def stop(self):
        print("[MockPicamera2] Stopping mock camera.")

    def set_controls(self, controls):
        print(f"Setting camera controls: {controls}")

    @staticmethod
    def create_random_color_image(width, height, brightness=1.0):
        """Create an image with random colors."""
        max_value = round(255 * brightness)
        img = Image.new(
            "RGB",
            (width, height),
            color=(
                random.randint(0, max_value),
                random.randint(0, max_value),
                random.randint(0, max_value)
            )
        )
        return img
