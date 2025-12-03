from abc import ABC, abstractmethod

class StreamingInterface(ABC):
    """
    Interface for Streaming's public methods.
    Must Not be instanciated.
    """

    @abstractmethod
    def is_streaming(self) -> bool:
        pass

    @abstractmethod
    def start_capture_stream(self, stream: str = "lores"):
        """ Start live streaming mjpeg to the returned StreamingOutput. """
        pass

    @abstractmethod
    def stop_capture_stream(self):
        """ If running, stop live streaming mjpeg. Cancel timer if running. """
        pass
