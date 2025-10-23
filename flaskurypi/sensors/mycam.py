import io
import time
import random
from threading import Condition

# Conditional Import
try:
    from picamera2 import Picamera2             # pyright: ignore[reportMissingImports]
    from picamera2.encoders import JpegEncoder  # pyright: ignore[reportMissingImports]
    from picamera2.outputs import FileOutput    # pyright: ignore[reportMissingImports]
    PICAMERA_AVAILABLE = True
    
except ImportError as e:
    print("\033[31m", "Failed to import picamera2, reverting to mock class:", e, "\033[0m")
    
    # Mock sensor classes for development outside RPi
    from .mycam_mock import MockPicamera2, MockEncoder, MockOutput

    Picamera2 = MockPicamera2
    JpegEncoder = MockEncoder
    FileOutput = MockOutput
    PICAMERA_AVAILABLE = False


class StreamingOutput(io.BufferedIOBase):
    """ Class to handle streaming of camera frames to a HTTP response.
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
    """Generator function that yields camera frames in byte format.
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
    """ My wrapper class for Picamera2 with methods for streaming and taking pictures
        for flask application purposes.
    """
    def configureAndStartStream(self, fileOutput):
        config = self.create_video_configuration(main={"size": (640, 360), "format": "XRGB8888"},
                                                 raw={"size": self.sensor_resolution})
        self.configure(config)
        self.start_recording(JpegEncoder(), FileOutput(fileOutput))
        
        return self
    
    def configureAndTakePicture(self):
        # Configure for still capture
        config = self.create_still_configuration(main={"size": (1920, 1080), "format": "XRGB8888"},
                                                 raw={"size": self.sensor_resolution})
        self.configure(config)
        self.start()
        
        # Capture an image to a BytesIO object
        stream = io.BytesIO()
        self.capture_file(stream, format='jpeg')
        self.stop()
        
        # Return the byte data
        return stream.getvalue()
