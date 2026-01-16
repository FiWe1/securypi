import json
import os
from typing import ClassVar, Tuple, Optional
from pydantic import BaseModel, Field
from pathlib import Path
from threading import Lock


# leaf schemas 
#
# - camera -
class StreamingConfig(BaseModel):
    resolution: Tuple[int, int]  # Enforces exactly two integers: [width, height]
    framerate: int = Field(gt=0) # > 0
    timeout_seconds: int
    description: Optional[str] = None

class RecordingConfig(BaseModel):
    resolution: Tuple[int, int]
    framerate: int
    description: Optional[str] = None

class MotionCaptureConfig(BaseModel):
    """ Appears in 'camera' and 'mock_camera'. """
    capture_motion_in_background: bool
    motion_detection_framerate: int = Field(gt=0) # > 0
    min_motion_capture_length_sec: int = Field(gt=0) # > 0
    max_motion_capture_length_sec: int
    frame_change_ratio_threshold: float = Field(ge=0.0, le=1.0) # 0.0 <= x= < 1.0
    description: Optional[str] = None

# - measurements -
class SensorsConfig(BaseModel):
    use_dht22: bool
    use_sht30: bool
    use_qmp6988: bool
    description: Optional[str] = None
    
class WeatherStationConfig(BaseModel):
    logging_interval_sec: int = Field(gt=0) # > 0
    log_in_background: bool
    description: Optional[str] = None

class GeolocationConfig(BaseModel):
    elevation_meters: int
    timezone: str
    description: Optional[str] = None

class MockSensorsConfig(BaseModel):
    mocked_temperature: float
    mocked_humidity: float
    mocked_pressure: float
    description: Optional[str] = None

# - authentication -
class PasswordConfig(BaseModel):
    min_length: int = Field(ge=1) # >= 0
    max_length: int
    hash_method: str
    description: Optional[str] = None

class UsernameConfig(BaseModel):
    min_length: int
    max_length: int
    description: Optional[str] = None

# - storage -
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
    sensors: SensorsConfig
    weather_station: WeatherStationConfig
    geolocation: GeolocationConfig
    mock_sensors: MockSensorsConfig

class AuthenticationConfig(BaseModel):
    password: PasswordConfig
    username: UsernameConfig

class StorageConfig(BaseModel):
    captures: CapturesConfig


# root schema
#
class AppConfig(BaseModel):
    camera: CameraConfig
    measurements: MeasurementsConfig
    authentication: AuthenticationConfig
    storage: StorageConfig
    description: Optional[str] = None

    _lock: ClassVar[Lock] = Lock() # (ClassVar protects from pydantic)
    # singleton & loading logic
    _instance: ClassVar[Optional['AppConfig']] = None

    @classmethod
    def get_file_path(cls) -> str:
        """ Assumes structure: root/config.json """
        return Path("app_config.json")

    @classmethod
    def fetch(cls):
        path = cls.get_file_path()
        with open(path, "r") as f:
            data = json.load(f)
            cls._instance = cls(**data)
            print(f"Configuration loaded from {path}")

    @classmethod
    def get(cls) -> 'AppConfig':
        if cls._instance is None:
            cls.fetch()
        return cls._instance
    
    def save(self):
        with self._lock:
            config_dict = self.model_dump()
            
            temp_path = f"{self.get_file_path()}.tmp"
            with open(temp_path, "w") as f:
                json.dump(config_dict, f, indent=2)
                
            # atomic rename - os-level operation
            # ('config.json' is never in a half-written state)
            os.replace(temp_path, self.get_file_path())
            print("Config saved safely to disk.")
