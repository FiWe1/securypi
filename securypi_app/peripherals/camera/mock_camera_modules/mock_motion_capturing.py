from securypi_app.peripherals.camera.motion_capturing_interface import MotionCapturingInterface


CAPTURE_MOTION_IN_BACKGROUND = False
MOTION_DETECTION_FRAMERATE = 10
MIN_MOTION_CAPTURE_LENGTH_SEC = 2
MAX_MOTION_CAPTURE_LENGTH_SEC = 60
FRAME_CHANGE_RATIO_THRESHOLD = 0.001


class MockMotionCapturing(MotionCapturingInterface):
    """
    Mock class - a dummy in place of MotionCapturing
    for platform independent development and testing.
    """

    def __init__(self, mycam):
        super().__init__()
        self._mycam = mycam
        self._is_motion_capturing = False

    def apply_capturing_config(self):
        # @TODO: from json
        capture = CAPTURE_MOTION_IN_BACKGROUND
        detection_rate = MOTION_DETECTION_FRAMERATE
        threshold_ratio = FRAME_CHANGE_RATIO_THRESHOLD
        min_length = MIN_MOTION_CAPTURE_LENGTH_SEC
        max_length = MAX_MOTION_CAPTURE_LENGTH_SEC

        self._detection_rate = detection_rate
        self._change_ratio_threshold = threshold_ratio
        self._min_recording_length = min_length
        self._max_recording_length = max_length

        self.set_motion_capturing(capture)

    def is_motion_capturing(self) -> bool:
        return self._is_motion_capturing

    def set_motion_capturing(self, set: bool):
        self._is_motion_capturing = set
        # @TODO: update json

    def get_detection_rate(self) -> int:
        return self._detection_rate

    def set_detection_rate(self, framerate: int):
        self._detection_rate = framerate
        # @TODO: update json

    def get_change_ratio_threshold(self) -> float:
        return self._change_ratio_threshold

    def set_change_ratio_threshold(self, threshold: float):
        self._change_ratio_threshold = threshold
        # @TODO: update json

    def get_min_recording_length(self) -> int:
        return self._min_recording_length

    def set_min_recording_length(self, seconds: int):
        self._min_recording_length = seconds
        # @TODO: update json

    def get_max_recording_length(self) -> int:
        return self._max_recording_length

    def set_max_recording_length(self, seconds: int):
        self._max_recording_length = seconds
        # @TODO: update json
