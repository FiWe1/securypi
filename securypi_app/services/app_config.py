import json
import os
from typing import ClassVar, Tuple, Optional
from pydantic import BaseModel, Field
from pathlib import Path


# leaf schemas 
#
class MotionCaptureConfig(BaseModel):
    """ Appears in 'camera' and 'mock_camera'. """
    capture_motion_in_background: bool
    motion_detection_framerate: int = Field(gt=0) # > 0
    min_motion_capture_length_sec: int = Field(gt=0) # > 0
    max_motion_capture_length_sec: int
    frame_change_ratio_threshold: float = Field(ge=0.0, le=1.0) # 0.0 <= x= < 1.0
    description: Optional[str] = None

class StreamingConfig(BaseModel):
    resolution: Tuple[int, int]  # Enforces exactly two integers: [width, height]
    framerate: int = Field(gt=0) # > 0
    timeout_seconds: int
    description: Optional[str] = None

class RecordingConfig(BaseModel):
    resolution: Tuple[int, int]
    framerate: int
    description: Optional[str] = None

class WeatherStationConfig(BaseModel):
    logging_interval_sec: int = Field(gt=0) # > 0
    log_in_background: bool
    elevation_meters: int
    timezone: str
    description: Optional[str] = None

class MockSensorsConfig(BaseModel):
    mocked_temperature: float
    mocked_humidity: float
    mocked_pressure: float
    description: Optional[str] = None

class PasswordConfig(BaseModel):
    min_length: int = Field(ge=1) # >= 0
    max_length: int
    hash_method: str
    description: Optional[str] = None

class UsernameConfig(BaseModel):
    min_length: int
    max_length: int
    description: Optional[str] = None

class CapturesConfig(BaseModel):
    motion_captures_path: str
    recordings_path: str
    description: Optional[str] = None


# composite schemas
#
class CameraConfig(BaseModel):
    streaming: StreamingConfig
    recording: RecordingConfig
    motion_capturing: MotionCaptureConfig # <--- Reuse 1

class MeasurementsConfig(BaseModel):
    weather_station: WeatherStationConfig
    mock_sensors: MockSensorsConfig

class AuthenticationConfig(BaseModel):
    password: PasswordConfig
    username: UsernameConfig

class StorageConfig(BaseModel):
    captures: CapturesConfig

class MockCameraConfig(BaseModel):
    encoder_timeout_seconds: int
    motion_capturing: MotionCaptureConfig # <--- Reuse 2


# root schema
#
class AppConfig(BaseModel):
    camera: CameraConfig
    measurements: MeasurementsConfig
    authentication: AuthenticationConfig
    storage: StorageConfig
    mock_camera: MockCameraConfig
    description: Optional[str] = None

    # singleton & loading logic (ClassVar protects from pydantic)
    _instance: ClassVar[Optional['AppConfig']] = None

    @classmethod
    def get_file_path(cls) -> str:
        """ Assumes structure: root/config.json """
        return Path("app_config.json")

    @classmethod
    def load(cls):
        path = cls.get_file_path()
        with open(path, "r") as f:
            data = json.load(f)
            cls._instance = cls(**data)
            print(f"Configuration loaded from {path}")

    @classmethod
    def get(cls) -> 'AppConfig':
        if cls._instance is None:
            cls.load()
        return cls._instance