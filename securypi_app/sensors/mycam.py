import io
from threading import Condition

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
    _initialised = False

    def __new__(cls, *args, **kwargs):
        """ Guarantees only one instance - singleton. """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """ Initialise once. """
        if getattr(self, "_initialized", False):
            return
        super().__init__()
        self.configure_streams()
        self.recording_encoder = None
        self.streaming_encoder = None
        
        self.start()
        self.__configure_runtime_controls()

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
        config.main.size = (1920, 1080)

        config.enable_lores()
        config.lores.size = (640, 360)
        # default stream for video encoding
        # config.encode = "lores"

        self.configure(config)
        return self
    
    def __configure_runtime_controls(self):
        # self.set_noise_reduction() # turn off for now
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

    def is_recording(self):
        return self.recording_encoder is not None

    def is_streaming(self):
        return self.streaming_encoder is not None


    def start_recording_to_file(self,
                                output_path: str,
                                stream: str = "main",
                                encode_quality = Quality.MEDIUM):
        """
        Start high-res video recording to file.
        -> output_path
        -> stream: which stream to record from ("main" or "lores")
        -> encode_quality: Quality.[LOW | MEDIUM | HIGH]
        """
        self.recording_encoder = H264Encoder()
        self.start_encoder(self.recording_encoder,
                           PyavOutput(output_path),
                           name=stream,
                           quality=encode_quality)
        return self

    def start_capture_stream(self, streaming_output, stream: str = "lores"):
        self.streaming_encoder = JpegEncoder()
        self.start_encoder(self.streaming_encoder,
                           FileOutput(streaming_output),
                           name=stream)
        return self

    def stop_recording_to_file(self):
        if self.recording_encoder is not None:
            self.stop_encoder(self.recording_encoder)
            self.recording_encoder = None
        return self

    def stop_capture_stream(self):
        if self.streaming_encoder is not None:
            self.stop_encoder(self.streaming_encoder)
            self.streaming_encoder = None
        return self

    def capture_picture(self):
        # Capture an image to a BytesIO object
        buffer = io.BytesIO()
        self.capture_file(buffer, format="jpeg")

        # Return the byte data
        return buffer.getvalue()
