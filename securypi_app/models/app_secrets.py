import json
import os
from typing import ClassVar, Optional
from pydantic import BaseModel
from threading import Lock


class AppSecrets(BaseModel):
    smtp_password: str = ""

    _lock: ClassVar[Lock] = Lock()
    _instance: ClassVar[Optional['AppSecrets']] = None

    @classmethod
    def get_file_path(cls) -> str:
        """
        Get relative path to .json configuration file.
        Assumes structure: {project_root}/instance/secrets.json
        """
        return os.path.join("instance", "app_secrets.json")

    @classmethod
    def fetch(cls):
        """ Fetch data into instance from .json configuration file. """
        path = cls.get_file_path()
        if not os.path.exists(path):
            os.makedirs("instance", exist_ok=True)
            instance = cls()
            instance._write(path)
            cls._instance = instance
        else:
            with open(path, "r") as f:
                cls._instance = cls(**json.load(f))

    @classmethod
    def get(cls) -> 'AppSecrets':
        """ Get the singleton instance of AppSecrets. """
        with cls._lock:
            if cls._instance is None:
                cls.fetch()
        return cls._instance

    def save(self):
        """ Save the current instance to the .json configuration file. """
        with self._lock:
            self._write(self.get_file_path())

    def _write(self, path: str):
        """ Atomic write to the .json configuration file. """
        temp_path = f"{path}.tmp"
        with open(temp_path, "w") as f:
            json.dump(self.model_dump(), f, indent=2)
        os.replace(temp_path, path)
