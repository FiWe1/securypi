"""
Helper functions for editing camera control configuration.
"""
from securypi_app.models.app_config import AppConfig
from securypi_app.peripherals.camera.mycam import MyPicamera2


def to_even(n: int) -> int:
    """ Convert uneven number to closest higher even nubmer. """
    return n + (n % 2)


def _parse_positive_int(raw, label) -> tuple[int, None] | tuple[None, str]:
    """
    Check if 'raw' input is positive int.
    On success return it's (int_value, None)
    Otherwise return (None, string_error_message)
    """
    try:
        v = int(raw)
    except (ValueError, TypeError):
        return None, f"{label} must be a positive integer, not '{raw}'"
    if v <= 0:
        return None, f"{label} must be a positive integer, not '{raw}'"
    return v, None


def _parse_positive_float(raw, label):
    """
    Check if 'raw' input is positive float.
    On success return it's (float_value, None)
    Otherwise return (None, string_error_message)
    """
    try:
        v = float(raw)
    except (ValueError, TypeError):
        return None, f"{label} must be a positive float, not '{raw}'"
    if v <= 0.0:
        return None, f"{label} must be a positive float, not '{raw}'"
    return v, None


def _parse_bounded_float(raw, label, lowest, highest):
    """
    Check if 'raw' input is 'lowest' <= float_value 'highest'.
    On success return it's (float_value, None)
    Otherwise return (None, string_error_message)
    """
    try:
        v = float(raw)
    except (ValueError, TypeError):
        return None, f"{label} must be a float between {lowest} and {highest}, not '{raw}'"
    if not (lowest <= v <= highest):
        return None, f"{label} must be a float between {lowest} and {highest}, not '{raw}'"
    return v, None


def get_recording_config() -> dict[str, int | tuple[int, int]]:
    """ Retrieve recording configuration from app_config.json """
    config = AppConfig.get()
    recording_config = {
        "resolution": config.camera.recording.resolution,
        "framerate": config.camera.recording.framerate
    }
    return recording_config


def get_streaming_config() -> dict[str, int | tuple[int, int]]:
    """ Retrieve recording configuration from app_config.json """
    config = AppConfig.get()
    streaming_config = {
        "resolution": config.camera.streaming.resolution,
        "framerate": config.camera.streaming.framerate,
        "timeout seconds": config.camera.streaming.timeout_seconds
    }
    return streaming_config


def get_motion_capturing_config() -> dict[str, int | float]:
    """ Retrieve motion capturing configuration from app_config.json """
    config = AppConfig.get()
    motion_capturing_config = {
        "motion detection framerate": config.camera.motion_capturing.motion_detection_framerate,
        "min capture length seconds": config.camera.motion_capturing.min_motion_capture_length_sec,
        "max capture length seconds": config.camera.motion_capturing.max_motion_capture_length_sec,
        "frame change ratio threshold": config.camera.motion_capturing.frame_change_ratio_threshold,
        "motion captures window size in GB": config.camera.motion_capturing.motion_captures_window_size_gb
    }
    return motion_capturing_config


def update_recording_config(current_config: dict[str, int | tuple[int, int]],
                            updated_config: dict[str, str]
                            ) -> str:
    """
    Update recording config according to user inputs.
    Returns result message.
    """
    # check inputs
    width_input = updated_config["resolution"]
    width, err = _parse_positive_int(width_input, "Resolution width")
    if err:
        return err
    width = to_even(width)
    aspect_ratio = 16 / 9
    height = to_even(int(width / aspect_ratio))
    updated_resolution = (width, height)

    framerate_input = updated_config["framerate"]
    updated_framerate, err = _parse_positive_int(framerate_input, "Framerate")
    if err:
        return err

    config = AppConfig.get()
    updated = False
    if updated_resolution != current_config["resolution"]:
        config.camera.recording.resolution = updated_resolution
        updated = True
    if updated_framerate != current_config["framerate"]:
        config.camera.recording.framerate = updated_framerate
        updated = True

    if updated:
        config.save()

        mycam = MyPicamera2.get_instance()
        mycam.refresh_configuration()

        return "Recording configuration updated."
    else:
        return "No changes."


def update_streaming_config(current_config: dict[str, int | tuple[int, int]],
                            updated_config: dict[str, str]
                            ) -> str:
    """
    Update streaming config according to user inputs.
    Returns result message.
    """
    # check inputs
    width_input = updated_config["resolution"]
    width, err = _parse_positive_int(width_input, "Resolution width")
    if err:
        return err
    width = to_even(width)
    aspect_ratio = 16 / 9
    height = to_even(int(width / aspect_ratio))
    updated_resolution = (width, height)

    framerate_input = updated_config["framerate"]
    updated_framerate, err = _parse_positive_int(framerate_input, "Framerate")
    if err:
        return err

    timeout_input = updated_config["timeout seconds"]
    updated_timeout, err = _parse_positive_int(timeout_input, "Timeout")
    if err:
        return err

    config = AppConfig.get()
    updated = False
    if updated_resolution != current_config["resolution"]:
        config.camera.streaming.resolution = updated_resolution
        updated = True
    if updated_framerate != current_config["framerate"]:
        config.camera.streaming.framerate = updated_framerate
        updated = True
    if updated_timeout != current_config["timeout seconds"]:
        config.camera.streaming.timeout_seconds = updated_timeout
        updated = True

    if updated:
        config.save()

        mycam = MyPicamera2.get_instance()
        mycam.refresh_configuration()

        return "Streaming configuration updated."
    else:
        return "No changes."


def update_motion_capturing_config(current_config: dict[str, int | float],
                                   updated_config: dict[str, str]
                            ) -> str:
    """
    Update motion_capturing config according to user inputs.
    Returns result message.
    """
    # check inputs
    framerate_input = updated_config["motion detection framerate"]
    framerate, err = _parse_positive_int(framerate_input, "'motion detection framerate'")
    if err:
        return err

    min_length_input = updated_config["min capture length seconds"]
    min_length, err = _parse_positive_int(min_length_input, "'min capture length seconds'")
    if err:
        return err

    max_length_input = updated_config["max capture length seconds"]
    max_length, err = _parse_positive_int(max_length_input, "'max capture length seconds'")
    if err:
        return err

    if min_length > max_length:
        return f"'min capture length seconds' ({min_length}) must not exceed 'max capture length seconds' ({max_length})"

    ratio_threshold_input = updated_config["frame change ratio threshold"]
    ratio_threshold, err = _parse_bounded_float(ratio_threshold_input, "'frame change ratio threshold'", 0.0, 1.0)
    if err:
        return err

    window_size_input = updated_config["motion captures window size in GB"]
    window_size, err = _parse_positive_float(window_size_input, "'motion captures window size in GB'")
    if err:
        return err

    config = AppConfig.get()
    updated = False
    if framerate != current_config["motion detection framerate"]:
        config.camera.motion_capturing.motion_detection_framerate = framerate
        updated = True
    if min_length != current_config["min capture length seconds"]:
        config.camera.motion_capturing.min_motion_capture_length_sec = min_length
        updated = True
    if max_length != current_config["max capture length seconds"]:
        config.camera.motion_capturing.max_motion_capture_length_sec = max_length
        updated = True
    if ratio_threshold != current_config["frame change ratio threshold"]:
        config.camera.motion_capturing.frame_change_ratio_threshold = ratio_threshold
        updated = True
    if window_size != current_config["motion captures window size in GB"]:
        config.camera.motion_capturing.motion_captures_window_size_gb = window_size
        updated = True

    if updated:
        config.save()

        mycam = MyPicamera2.get_instance()
        mycam.motion_capturing.apply_capturing_config()

        return "Motion capturing configuration updated."
    else:
        return "No changes."
