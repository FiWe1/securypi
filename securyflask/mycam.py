from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

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
        self.configure(self.create_video_configuration(main={"size": (640, 480)}))
        self.start_recording(JpegEncoder(), FileOutput(fileOutput))
        
        return self
    
    def configureAndTakePicture(self, fileOutput):
        self.configure(self.create_still_configuration(main={"size": (1920, 1080)}))
        
        self.start()
        array = self.capture_array()
        self.stop()
        
        jpeg = JpegEncoder.encode(array)
        
        fileOutput.write(jpeg)
        
        return self
