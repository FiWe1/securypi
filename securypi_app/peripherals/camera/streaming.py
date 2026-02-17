import io
from threading import Condition, Timer
from time import sleep

from securypi_app.peripherals.camera.streaming_interface import StreamingInterface
from securypi_app.models.app_config import AppConfig

# Conditional Import for RPi picamera2 library
try:
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    
except ImportError as e:
    # Mock sensor classes for platform independent development
    from securypi_app.peripherals.camera.mock_camera_modules.mock_picamera2 import (
        MockEncoder, MockStreamingOutput
    )
    JpegEncoder = MockEncoder
    FileOutput = MockStreamingOutput


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

    def generate_frames(self):
        """
        Generator function that yields camera frames in byte format.
        Wailts for a new frame from the camera and
        yields it as part of a multipart HTTP response.
        """
        config = AppConfig.get()
        framerate = config.camera.streaming.framerate
        sleep_time = 1 / framerate
        
        while True:
            with self.condition:
                self.condition.wait()
                frame = self.frame
            yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + f"{len(frame)}".encode() + b"\r\n\r\n" +
                frame + b"\r\n")
            sleep(sleep_time)


class Streaming(StreamingInterface):
    """
    Extension class of MyPicamera2.
    Handles live MJPEG streaming functionality.
    """
    
    def __init__(self, mycam):
        """ Initialize with MyPicamera2 instance. """
        self._mycam = mycam
        
        self._streaming_output = StreamingOutput()
        
        self._streaming_encoder = None
        self._stream_timer = None

    def is_streaming(self) -> bool:
        return self._streaming_encoder is not None

    def start_capture_stream(self, stream: str = "lores") -> StreamingOutput:
        config = AppConfig.get()
        stream_timeout = config.camera.streaming.timeout_seconds
        
        # cancel stream timeout if set - avoid timing out prematurely
        if self._stream_timer is not None:
            self._stream_timer.cancel()
        # won't be starting two encoders
        if self._streaming_encoder is None:
            self._streaming_encoder = JpegEncoder()
            self._mycam._picam.start_encoder(self._streaming_encoder,
                                      FileOutput(self._streaming_output),
                                      name=stream)
            self._mycam._picam.start()

        self._stream_timer = Timer(stream_timeout, self.stop_capture_stream)
        self._stream_timer.start()

        return self._streaming_output

        return self._streaming_output

    def stop_capture_stream(self):
        """ Stop capturing stream. Resets the timeout timer. """
        if self._stream_timer is not None:
            self._stream_timer.cancel()
            self._stream_timer = None
            
        if self._streaming_encoder is not None:
            self._mycam._picam.stop_encoder(self._streaming_encoder)
            self._streaming_encoder = None
            print("Stopped video streaming (timer).")
        return self
