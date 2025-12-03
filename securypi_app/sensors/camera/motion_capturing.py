import time
from threading import Thread, Event
from pathlib import Path
from abc import ABC, abstractmethod

import numpy as np
from scipy.ndimage import gaussian_filter

from securypi_app.services.string_parsing import timed_filename


CAPTURE_MOTION_IN_BACKGROUND = False
MOTION_DETECTION_FRAMERATE = 10
MIN_MOTION_CAPTURE_LENGTH_SEC = 2
MAX_MOTION_CAPTURE_LENGTH_SEC = 60
FRAME_CHANGE_RATIO_THRESHOLD = 0.001


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


class MotionCapturing(MotionCapturingInterface):
    """
    Background motion detection and capturing using MyPicamera2 instance.
    """
    def __init__(self, mycam):
        super().__init__()
        self._mycam = mycam

        # background motion detector
        self._capture_motion_in_background = False
        self._capturing_thread = None
        self._capturing_stop_event = Event()
        self.apply_capturing_config()

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
        return self._capturing_thread is not None

    # setters / getters
    def set_motion_capturing(self, set: bool):
        self._capture_motion_in_background = set
        if set:
            self.start()
        else:
            self.stop()

    def get_detection_rate(self) -> int:
        return self._detection_rate

    def set_detection_rate(self, framerate):
        self._detection_rate = framerate
        # @TODO: update json

        if self.is_motion_capturing():
            self.start()  # restarts the running logging

    def get_change_ratio_threshold(self) -> float:
        return self._change_ratio_threshold

    def set_change_ratio_threshold(self, threshold):
        self._change_ratio_threshold = threshold
        # @TODO: update json

    # recording length
    def get_min_recording_length(self) -> int:
        return self._min_recording_length

    def set_min_recording_length(self, seconds):
        self._min_recording_length = seconds
        # @TODO: update json

    def get_max_recording_length(self) -> int:
        return self._max_recording_length

    def set_max_recording_length(self, seconds):
        self._max_recording_length = seconds
        # @TODO: update json

    def start(self):
        """
        Start background motion capturing.
        If it was running, restart it.
        """
        if self._mycam.is_recording() and not self.is_motion_capturing():
            raise RuntimeError("Can not start MotionCapturing "
                               "while another recording is running.")
        if self.is_motion_capturing():
            print("Background MotionCapturing was not stopped, "
                  "stopping now...")
            self.stop()

        self._capturing_thread = (
            Thread(target=self.loop_motion_capturing)
        )
        self._capturing_stop_event.clear()  # clear stop signal
        self._capturing_thread.start()
        print("Background MotionCapturing has started")

    def stop(self):
        if self.is_motion_capturing():
            self._capturing_stop_event.set()  # signal stop
            if self._capturing_thread:
                self._capturing_thread.join()

            self._capturing_thread = None
        else:
            print("Can't stop background MotionCapturing, "
                  "it is not running.")

    def loop_motion_capturing(self, debug=False):
        """
        Detect motion in background and save output to:
        'captures/motion_captures/'.
        Start/stop recording according to:
        - self._detection_rate
        - self._change_ratio_threshold
        - self._min_recording_length
        - self._max_recording_length
        """
        w, h = self._mycam.get_current_resolution(target="lores")

        folderpath = Path("captures/motion_captures")
        folderpath.mkdir(parents=True, exist_ok=True)
        detection_timeout = 1 / self._detection_rate

        last_detected: time = 0
        recording_start_time: time = 0
        prev = None
        while True:
            cur = self._mycam._picam.capture_buffer("lores")
            cur = cur[:w * h].reshape(h, w)
            cur = gaussian_filter(cur.astype(np.float32), sigma=1)  # smooth

            if prev is not None:
                # Measure pixels differences between current and
                # previous frame
                ratio = self.image_change_ratio(prev, cur)

                # debug - empiric search for change ratio
                if debug:
                    print(round(ratio * 100, 2))

                # detect motion
                if ratio >= self.get_change_ratio_threshold():
                    if not self._mycam.is_recording():
                        filename = folderpath / timed_filename(".mp4")

                        self._mycam.start_recording_to_file(filename)
                        recording_start_time = time.time()

                        print("New Motion", round(ratio * 100, 2))
                    last_detected = time.time()
                else:
                    # Stop recording if no motion detected for
                    # minimal recording length
                    if self._mycam.is_recording() and (
                        time.time() - last_detected > self.get_min_recording_length()
                    ):
                        self._mycam.stop_recording_to_file()

                # restart recording if it exceeds max length
                if self._mycam.is_recording() and (
                    time.time() - recording_start_time >
                    self._max_recording_length
                ):
                    self._mycam.stop_recording_to_file()
                    self._mycam.start_recording_to_file(folderpath /
                                                        timed_filename(".mp4"))
                    recording_start_time = time.time()
            prev = cur

            if self._capturing_stop_event.wait(timeout=detection_timeout):
                if self._mycam.is_recording():
                    self._mycam.stop_recording_to_file()
                print("Background MotionCapturing exited cleanly.")
                break

    @staticmethod
    def image_change_ratio(prev: np.ndarray,
                           cur: np.ndarray,
                           pixel_threshold: float = 12.0):
        """ Calculate ratio of pixels changed more than 'pixel_threshold'. """
        absdiff = np.abs(cur.astype(np.int16) - prev.astype(np.int16))
        changed = (absdiff >= pixel_threshold)  # per-pixel threshold

        return changed.mean()
