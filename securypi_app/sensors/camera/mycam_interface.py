from abc import ABC, abstractmethod
from pathlib import Path

class MyPicamera2Interface(ABC):
    """
    Interface for MyPicamera2's public methods.
    Must Not be instanciated.
    """
    @classmethod
    @abstractmethod
    def get_instance(cls):
        """ Singleton access method. """
        pass
    
    @abstractmethod
    def get_current_resolution(self, target) -> tuple[int, int]:
        """
        Get current configured resolution for:
        'target' = "sensor" -> sensor resolution
        'target' = "main" -> main encoder resolution
        'target' = "lores" -> lores encoder resolution
        """

    @abstractmethod
    def set_noise_reduction(self, noise_reduction_mode):
        """
        Noise Reduction Modes:
        {
            'Off': <NoiseReductionModeEnum.Off: 0>,
            'Fast': <NoiseReductionModeEnum.Fast: 1>,
            'HighQuality': <NoiseReductionModeEnum.HighQuality: 2>,
            'Minimal': <NoiseReductionModeEnum.Minimal: 3>,
            'ZSL': <NoiseReductionModeEnum.ZSL: 4>
        }
        """
        pass
    
    @abstractmethod
    def set_framerate(self, framerate):
        pass

    @abstractmethod
    def is_recording(self) -> bool:
        pass

    @abstractmethod
    def is_streaming(self) -> bool:
        pass

    @abstractmethod
    def start_recording_to_file(self,
                                output_path: str,
                                stream: str,
                                encode_quality):
        """
        Start high-res video recording to file.
        - 'output_path': full path to output file as string
        - 'stream': which stream to record from ("main" or "lores")
        - 'encode_quality': Quality.[LOW | MEDIUM | HIGH]
        """
        pass
    @abstractmethod
    def start_default_recording(self,
                                stream,
                                encode_quality) -> Path:
        """
        Start recording to /captures/recordings
        with returned default filename (current datetime).
        - 'stream': which stream to record from ("main" or "lores")
        - 'encode_quality': Quality.[LOW | MEDIUM | HIGH]
        """
        pass

    @abstractmethod
    def stop_recording_to_file(self):
        """ If recording, stop recording to file. """
        pass

    @abstractmethod
    def start_capture_stream(self, stream: str = "lores"):
        """ Start live streaming mjpeg to the returned StreamingOutput. """
        pass

    @abstractmethod
    def stop_capture_stream(self):
        """ If running, stop live streaming mjpeg. Cancel timer if running. """
        pass

    @abstractmethod
    def capture_picture(self):
        """ Capture an image, return image data. """
        pass
