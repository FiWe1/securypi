"""
Helper functions for accessing captured videos in: captures/...
"""
import logging
import os
import shutil
from pathlib import Path
from werkzeug.utils import secure_filename
from zipstream import ZipStream
from securypi_app.models.app_config import AppConfig

logger = logging.getLogger(__name__)

MIN_FREE_STORAGE_BYTES = 1 * 1024 ** 3  # 1 GB


def has_enough_free_storage(path: Path) -> bool:
    """
    Return True if the filesystem hosting 'path' has at least 1 GB free.
    """
    path.mkdir(parents=True, exist_ok=True)
    return shutil.disk_usage(path).free >= MIN_FREE_STORAGE_BYTES


def motion_captures_path() -> Path:
    """
    Return Path to motion_captures (relative) in project directory,
    ensuring it exists.
    """
    config = AppConfig.get()
    path_str = config.storage.captures.motion_captures_path

    path = Path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return path


def recordings_path() -> Path:
    """
    Return Path to recordings (relative) in project directory,
    ensuring it exists.
    """
    config = AppConfig.get()
    path_str = config.storage.captures.recordings_path

    path = Path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return path


def enforce_motion_captures_window(path: Path, window_size_gb: float) -> None:
    """
    Delete oldest motion captures until the total folder size fits within
    window_size_gb
    """
    window_size_bytes = window_size_gb * 1024 ** 3
    # files sorted by modification time, from oldest to newer
    files = sorted(
        (f for f in path.iterdir() if f.is_file()),
        key=lambda f: f.stat().st_mtime
    )
    total = sum(f.stat().st_size for f in files)
    for f in files:
        if total <= window_size_bytes:
            break
        size = f.stat().st_size
        f.unlink()
        total -= size
        logger.info("Window size enforcement: deleted %s", f.name)


# "captures/motion_captures"
def list_motion_captures(reverse: bool = False) -> list[str]:
    return sorted(os.listdir(motion_captures_path()), reverse=reverse)


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
def list_recordings(reverse: bool = False) -> list[str]:
    return sorted(os.listdir(recordings_path()), reverse=reverse)


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
