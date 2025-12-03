from abc import ABC, abstractmethod


class MotionCapturingInterface(ABC):
    """
    Interface for MotionCapturing's public methods.
    Must Not be instanciated.
    """
    
    @abstractmethod
    def is_motion_capturing(self) -> bool:
        """ Is motion capturing running in background?. """
        pass

    @abstractmethod
    def set_motion_capturing(self, set: bool):
        """ Set and start/stop background motion capturing. """
        pass

    @abstractmethod
    def get_detection_rate(self) -> int:
        """ Get motion detection rate per second. """
        pass

    @abstractmethod
    def set_detection_rate(self, framerate: int):
        """
        Update motion detection rate per second.
        If running, restart and detect motion at this rate.
        """
        pass

    @abstractmethod
    def get_change_ratio_threshold(self) -> float:
        """ Frame change ratio threshold - beyond it motion is captured. """
        pass

    @abstractmethod
    def set_change_ratio_threshold(self, threshold: float):
        """
        Update frame change ratio threshold - beyond it motion is captured.
        """
        pass

    @abstractmethod
    def get_min_recording_length(self) -> int:
        """ Get minimal length of motion capture in seconds. """
        pass

    @abstractmethod
    def set_min_recording_length(self, seconds: int):
        """ Update minimal length of motion capture. """
        pass

    @abstractmethod
    def get_max_recording_length(self) -> int:
        """ Get maximal length of motion capture in seconds. """
        pass

    @abstractmethod
    def set_max_recording_length(self, seconds: int):
        """ Update maximal length of motion capture. """
        pass
