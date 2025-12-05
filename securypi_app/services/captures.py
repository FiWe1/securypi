"""
Helper functions for accessing captured videos in: captures/...
"""
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from zipstream import ZipStream


# @TODO move to global json config
MOTION_CAPTURES_PROJECT_PATH = "captures/motion_captures"
RECORDINGS_PROJECT_PATH = "captures/recordings"


def motion_captures_path() -> Path:
    """
    Return Path to motion_captures (relative) in project directory,
    ensuring it exists.
    """
    # @TODO: load from json config
    path_str = MOTION_CAPTURES_PROJECT_PATH

    path = Path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return path


def recordings_path() -> Path:
    """
    Return Path to recordings (relative) in project directory,
    ensuring it exists.
    """
    # @TODO: load from json config
    path_str = RECORDINGS_PROJECT_PATH

    path = Path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return path


# "captures/motion_captures"
def list_motion_captures() -> list[str]:
    return sorted(os.listdir(motion_captures_path()))


def motion_captures_absolute_path(current_app_root_path: str) -> str:
    """
    Absolute path to */*/{project_dir}/{motion_captures_path}
    Needed for direct downloads.
    """
    project_root = Path(current_app_root_path).parent.resolve()
    return str(project_root / motion_captures_path())


def is_motion_capture_valid(filename: str) -> bool:
    return secure_filename(filename) in list_motion_captures()


def delete_motion_capture(filename: str) -> None:
    path = motion_captures_path() / filename
    if path.exists():
        path.unlink()  # delete


def delete_motion_captures(motion_captures: list[str]) -> None:
    for motion in motion_captures:
        delete_motion_capture(motion)


# "captures/recordings"
def list_recordings() -> list[str]:
    return sorted(os.listdir(recordings_path()))


def recordings_absolute_path(current_app_root_path: str) -> str:
    """
    Absolute path to */*/{project_dir}/{recordings_path}
    Needed for direct downloads.
    """
    project_root = Path(current_app_root_path).parent.resolve()
    return str(project_root / recordings_path())


def is_recording_valid(filename: str) -> bool:
    return secure_filename(filename) in list_recordings()


def delete_recording(filename: str) -> None:
    path = recordings_path() / filename
    if path.exists():
        path.unlink()  # delete


def delete_recordings(recordings: list[str]) -> None:
    for rec in recordings:
        delete_recording(rec)


# zip
def create_zip_stream(motion_captures: list[str],
                      recordings: list[str]) -> ZipStream:
    """ Return zip stream with motion captures and recordings """
    zip_stream = ZipStream()

    downloads_fullpath_name = [
        (str(motion_captures_path() / motion), motion) for motion in motion_captures
    ]
    downloads_fullpath_name.extend([
        (str(recordings_path() / rec), rec) for rec in recordings
    ])

    for full_path, name in downloads_fullpath_name:
        zip_stream.add_path(full_path, name)

    return zip_stream
