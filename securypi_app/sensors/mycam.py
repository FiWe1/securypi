import io
from threading import Condition

# Conditional Import
try:
    from picamera2 import Picamera2             # pyright: ignore[reportMissingImports]
    from picamera2.encoders import JpegEncoder  # pyright: ignore[reportMissingImports]
    from picamera2.outputs import FileOutput    # pyright: ignore[reportMissingImports]
    
except ImportError as e:
    print("Failed to import picamera2 camera library, "
          "reverting to mock class:\n", "\033[31m", e, "\033[0m")

    # Mock sensor classes for development outside RPi
    from .mock_mycam import MockPicamera2, MockEncoder, MockOutput

    Picamera2 = MockPicamera2
    JpegEncoder = MockEncoder
    FileOutput = MockOutput


class StreamingOutput(io.BufferedIOBase):
    """
    Handles streaming of camera frames to a HTTP response.
    Uses a Condition to synchronize access to the latest frame.
    """
    # @TODO ? singleton)

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
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n\r\n' +
               frame + b'\r\n')


class MyPicamera2(Picamera2):
    """
    My singleton wrapper class for Picamera2 with methods
    for streaming and taking pictures.
    """
    _instance = None
    _initialised = False

    def __new__(cls, *args, **kwargs):
        """ Guarantees only one instance - singleton. """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.configure_streams()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        """ Singleton access method. """
        return cls()
    
    
    def configure_streams(self):
        # main stream: high-res recording
        # lores stream: for preview
        config = self.video_configuration
        config.main.size = (1920, 1080)
        
        config.enable_lores()
        config.lores.size = (640, 360)
        # config.encode = "lores" # default stream for encoding
        
        self.configure(config)

    def start_capture_stream(self, streaming_output):
        self.start_recording(JpegEncoder(), FileOutput(streaming_output), name="lores")
        return self
    
    def stop_capture_stream(self):
        if self.is_recording():
            self.stop_recording()
        
        return self

    def capture_picture(self):
        self.start()

        # Capture an image to a BytesIO object
        buffer = io.BytesIO()
        self.capture_file(buffer, format='jpeg')
        self.stop()

        # Return the byte data
        return buffer.getvalue()
