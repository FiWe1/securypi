"""
Helper functions for accessing captured videos in: captures/...
"""
import os
from werkzeug.utils import secure_filename


# "captures/motion_captures"
def list_motion_captures() -> list[str]:
    return sorted(os.listdir("captures/motion_captures"))


def motion_captures_full_path(current_app_root_path: str) -> str:
    project_root = os.path.abspath(os.path.join(current_app_root_path, ".."))
    return os.path.join(project_root, "captures", "motion_captures")


def is_motion_capture_valid(filename: str) -> bool:
    return secure_filename(filename) in list_motion_captures()


# "captures/recordings"
def list_recordings() -> list[str]:
    return sorted(os.listdir("captures/recordings"))


def recordings_full_path(current_app_root_path: str) -> str:
    project_root = os.path.abspath(os.path.join(current_app_root_path, ".."))
    return os.path.join(project_root, "captures", "recordings")


def is_recording_valid(filename: str) -> bool:
    return secure_filename(filename) in list_recordings()
