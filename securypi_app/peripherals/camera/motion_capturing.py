import time
from datetime import datetime
from threading import Thread, Event
from pathlib import Path

import numpy as np   # pyright: ignore[reportMissingImports]
from scipy.ndimage import gaussian_filter   # pyright: ignore[reportMissingImports]

from securypi_app.services.string_parsing import timed_filename
from securypi_app.services.captures import motion_captures_path
from securypi_app.peripherals.camera.motion_capturing_interface import (
    MotionCapturingInterface
)
from securypi_app.peripherals.camera.mycam_interface import MyPicamera2Interface
from securypi_app.models.app_config import AppConfig


class MotionCapturing(MotionCapturingInterface):
    """
    Extension class of MyPicamera2.
    Background motion detection and capturing.
    """
    def __init__(self, mycam):
        """ Initialize with MyPicamera2 instance. """
        self._mycam: MyPicamera2Interface = mycam

        # background motion detector
        self._capture_motion_in_background = False
        self._capturing_thread = None
        self._capturing_stop_event = Event()
        self.apply_capturing_config()

    def apply_capturing_config(self):
        config = AppConfig.get()
        
        capture = config.camera.motion_capturing.capture_motion_in_background
        detection_rate = config.camera.motion_capturing.motion_detection_framerate
        threshold_ratio = config.camera.motion_capturing.frame_change_ratio_threshold
        min_length = config.camera.motion_capturing.min_motion_capture_length_sec
        max_length = config.camera.motion_capturing.max_motion_capture_length_sec

        self._capture_motion_in_background = capture
        self._detection_rate = detection_rate
        self._change_ratio_threshold = threshold_ratio
        self._min_recording_length = min_length
        self._max_recording_length = max_length

        if capture:
            self.start()

    def is_motion_capturing(self) -> bool:
        return self._capture_motion_in_background

    # setters / getters
    def set_motion_capturing(self, set: bool):
        if self.is_motion_capturing() != set:
            self._capture_motion_in_background = set
            if set:
                self.start()
            else:
                self.stop()
        
        # update config:
        config = AppConfig.get()
        if config.camera.motion_capturing.capture_motion_in_background != set:
            config.camera.motion_capturing.capture_motion_in_background = set
            config.save()

    def get_detection_rate(self) -> int:
        return self._detection_rate

    def set_detection_rate(self, framerate):
        self._detection_rate = framerate
        
        # update config:
        config = AppConfig.get()
        if config.camera.motion_capturing.motion_detection_framerate != framerate:
            config.camera.motion_capturing.motion_detection_framerate = framerate
            config.save()

        if self.is_motion_capturing():
            self.start()  # restarts the running logging

    def get_change_ratio_threshold(self) -> float:
        return self._change_ratio_threshold

    def set_change_ratio_threshold(self, threshold):
        self._change_ratio_threshold = threshold
        
        # update config:
        config = AppConfig.get()
        if config.camera.motion_capturing.frame_change_ratio_threshold != threshold:
            config.camera.motion_capturing.frame_change_ratio_threshold = threshold
            config.save()

    # recording length
    def get_min_recording_length(self) -> int:
        return self._min_recording_length

    def set_min_recording_length(self, seconds):
        self._min_recording_length = seconds
        
        # update config:
        config = AppConfig.get()
        if config.camera.motion_capturing.min_motion_capture_length_sec != seconds:
            config.camera.motion_capturing.min_motion_capture_length_sec = seconds
            config.save()

    def get_max_recording_length(self) -> int:
        return self._max_recording_length

    def set_max_recording_length(self, seconds):
        self._max_recording_length = seconds
        
        # update config:
        config = AppConfig.get()
        if config.camera.motion_capturing.max_motion_capture_length_sec != seconds:
            config.camera.motion_capturing.max_motion_capture_length_sec = seconds
            config.save()

    def start(self):
        """
        Start background motion capturing.
        If it was running, restart it.
        """
        if self._mycam.is_recording() and not self.is_motion_capturing():
            raise RuntimeError("Can not start MotionCapturing "
                               "while another recording is running.")
        if self._capturing_thread is not None:
            print("Background MotionCapturing was not stopped, "
                  "stopping now...")
            self.stop()

        self._capturing_thread = (
            Thread(target=self.loop_motion_capturing, daemon=True)
        )
        self._capturing_stop_event.clear()  # clear stop signal
        self._capturing_thread.start()
        print("Background MotionCapturing has started")

    def stop(self):
        if self._capturing_thread is not None:
            self._capturing_stop_event.set()  # signal stop
            if self._capturing_thread:
                self._capturing_thread.join(timeout=2.0)

            self._capturing_thread = None

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

        folderpath = motion_captures_path()
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

                        print(datetime.now().strftime("%Y-%m-%d_%H-%M"),
                              f"New motion: {round(ratio * 100, 2)}% "
                              f"frame change ratio")
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
