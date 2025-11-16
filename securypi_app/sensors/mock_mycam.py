import random
import threading
from time import sleep
from PIL import Image
from io import BytesIO


class MockStreamingOutput:
    def __init__(self, output=None):
        self.output = output

    def write(self, data):
        if self.output:
            self.output.write(data)


# Mocking Picamera2...

class MockEncoder:
    def __init__(self, *args, **kwargs):
        pass


class MockStreamConfig:
    """ Mocking object oriented camera configuration. """
    def __init__(self, size=None):
        self.size = size


class MockVideoConfiguration:
    """ Mocking object oriented camera configuration. """
    def __init__(self):
        self.main = MockStreamConfig()
        self.lores = None

    def enable_lores(self):
        if self.lores is None:
            self.lores = MockStreamConfig()


class MockPicamera2:
    """
    Mocking Picamera2 library for the purpouses of
    working with mycam module (MyPicamera2).
    """
    def __init__(self):
        self.sensor_resolution = (1920, 1080)
        self.started = False
        self.video_configuration = MockVideoConfiguration()

    def create_video_configuration(self, **kwargs):
        print("[MockPicamera2] Creating video config:", kwargs)
        return kwargs

    def create_still_configuration(self, **kwargs):
        print("[MockPicamera2] Creating still config:", kwargs)
        return kwargs

    def configure(self, config):
        print("[MockPicamera2] Configured with:", config)

    def start_recording(self, encoder, output, name="main"):
        """ Continuously generate fake frames """
        print(f"[MockPicamera2] Simulating video recording to {output} using {encoder} on stream '{name}'")

        def frame_generator():
            while True:
                img = self.create_random_color_image(640, 360, brightness=0.5)
                buffer = BytesIO()
                img.save(buffer, format="JPEG")
                jpeg_bytes = buffer.getvalue()

                output.write(jpeg_bytes)  # StreamOutput.write()
                sleep(2)  # 10 fps

        threading.Thread(target=frame_generator, daemon=True).start()

    def start(self):
        print("[MockPicamera2] Starting camera simulation...")

    def capture_file(self, stream, format='jpeg'):
        print("[MockPicamera2] Capturing fake image...")
        # Create a real JPEG image
        img = self.create_random_color_image(640, 360, brightness=0.5)
        img.save(stream, format=format)

    def stop(self):
        print("[MockPicamera2] Stopping mock camera.")

    @staticmethod
    def create_random_color_image(width, height, brightness=1.0):
        """Create an image with random colors."""
        max_value = round(255 * brightness)
        img = Image.new(
            'RGB',
            (width, height),
            color=(
                random.randint(0, max_value),
                random.randint(0, max_value),
                random.randint(0, max_value)
            )
        )
        return img
