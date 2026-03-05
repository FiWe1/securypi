"""
Helper functions for editing camera control configuration.
"""
from securypi_app.models.app_config import AppConfig
from securypi_app.peripherals.camera.mycam import MyPicamera2


def to_even(n: int) -> int:
    """ Convert uneven number to closest higher even nubmer. """
    return n + (n % 2)


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
        "frame change ratio threshold": config.camera.motion_capturing.frame_change_ratio_threshold
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
    try:
        width = to_even(int(width_input))
    except Exception as e:
        return f"Resolution width must be an integer, no: {width_input}"
    aspect_ratio = 16 / 9
    height = to_even(int(width / aspect_ratio))
    updated_resolution = (width, height)
    
    framerate_input = updated_config["framerate"]
    try:
        updated_framerate = int(framerate_input)
    except Exception as e:
        return f"Framerate must be an integer, no: {framerate_input}"
    
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
    try:
        width = int(width_input)
    except Exception as e:
        return f"Resolution width must be an integer, no: {width_input}"
    aspect_ratio = 16 / 9
    height = int(width / aspect_ratio)
    updated_resolution = (width, height)
    
    framerate_input = updated_config["framerate"]
    try:
        updated_framerate = int(framerate_input)
    except Exception as e:
        return f"Framerate must be an integer, no: {framerate_input}"
    
    timeout_input = updated_config["timeout seconds"]
    try:
        updated_timeout = int(timeout_input)
    except Exception as e:
        return f"Timeout input must be an integer, no: {timeout_input}"
    
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
        
        return "Streamig configuration updated."
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
    try:
        framerate = int(framerate_input)
    except Exception as e:
        return f"motion_detection_framerate must be an integer, no: {framerate_input}"
    
    min_length_input = updated_config["min capture length seconds"]
    try:
        min_length = int(min_length_input)
    except Exception as e:
        return f"min_motion_capture_length_sec must be an integer, no: {min_length_input}"
    
    max_length_input = updated_config["max capture length seconds"]
    try:
        max_length = int(max_length_input)
    except Exception as e:
        return f"min_motion_capture_length_sec must be an integer, no: {max_length_input}"
    
    ratio_threshold_input = updated_config["frame change ratio threshold"]
    try:
        ratio_threshold = float(ratio_threshold_input)
        assert ratio_threshold <= 1
    except Exception as e:
        return f"frame_change_ratio_threshold must be a float <= 1.0, no: {ratio_threshold_input}"
    
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
        
    if updated:
        config.save()
        
        mycam = MyPicamera2.get_instance()
        mycam.motion_capturing.apply_capturing_config()
        
        return "Motion capturing configuration updated."
    else:
        return "No changes."
