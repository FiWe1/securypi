import random 
from PIL import Image


class MockEncoder:
    def __init__(self, *args, **kwargs):
        pass

class MockOutput:
    def __init__(self, output=None):
        self.output = output
    
    def write(self, data):
        if self.output:
            self.output.write(data)

class MockPicamera2:
    started = True
    def __init__(self):
        self.sensor_resolution = (1920, 1080)

    def create_video_configuration(self, **kwargs):
        print("[MockPicamera2] Creating video config:", kwargs)
        return kwargs

    def create_still_configuration(self, **kwargs):
        print("[MockPicamera2] Creating still config:", kwargs)
        return kwargs

    def configure(self, config):
        print("[MockPicamera2] Configured with:", config)

    def start_recording(self, encoder, output):
        print("[MockPicamera2] Simulating video recording start...")

        # Continuously generate fake frames
        import threading

        def frame_generator():
            from io import BytesIO
            from time import sleep

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
