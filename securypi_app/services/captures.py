"""
Helper functions for accessing captured videos in: captures/...
"""
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import zipstream


# "captures/motion_captures"
def list_motion_captures() -> list[str]:
    return sorted(os.listdir("captures/motion_captures"))


def motion_captures_full_path(current_app_root_path: str) -> str:
    project_root = Path(current_app_root_path).parent.resolve()
    return str(project_root / "captures" / "motion_captures")


def is_motion_capture_valid(filename: str) -> bool:
    return secure_filename(filename) in list_motion_captures()


def delete_motion_capture(filename: str) -> None:
    path = Path("captures") / "motion_captures" / filename
    if path.exists():
        path.unlink() # delete


def delete_motion_captures(motion_captures: list[str]) -> None:
    for motion in motion_captures:
        delete_motion_capture(motion)


# "captures/recordings"
def list_recordings() -> list[str]:
    return sorted(os.listdir("captures/recordings"))


def recordings_full_path(current_app_root_path: str) -> str:
    project_root = Path(current_app_root_path).parent.resolve()
    return str(project_root / "captures" / "recordings")


def is_recording_valid(filename: str) -> bool:
    return secure_filename(filename) in list_recordings()


def delete_recording(filename: str) -> None:
    path = Path("captures") / "recordings" / filename
    if path.exists():
        path.unlink() # delete


def delete_recordings(recordings: list[str]) -> None:
    for rec in recordings:
        delete_recording(rec)


# zip
def create_zip_stream(motion_captures: list[str],
                      recordings: list[str],
                      current_app_root_path: str) -> zipstream:
    """ Return zip stream with motion captures and recordings """
    zip = zipstream.ZipStream()

    mc_full_path = Path(motion_captures_full_path(current_app_root_path))
    downloads_fullpath_name = [
        (str(mc_full_path / motion), motion) for motion in motion_captures
    ]
    r_full_path = Path(recordings_full_path(current_app_root_path))
    downloads_fullpath_name.extend([
        (str(r_full_path / rec), rec) for rec in recordings
    ])
    
    for full_path, name in downloads_fullpath_name:
        zip.add(full_path, name)
    
    return zip
