from picamera2 import Picamera2 # pyright: ignore[reportMissingImports]
from picamera2.encoders import JpegEncoder # pyright: ignore[reportMissingImports]
from picamera2.outputs import FileOutput # pyright: ignore[reportMissingImports]

from threading import Condition
import io


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

def generate_frames(output):
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n\r\n' +
               frame + b'\r\n')


class MyPicamera2(Picamera2):
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