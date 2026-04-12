""" Shared pytest fixtures. """

import pytest

from securypi_app.peripherals.camera.mycam import MyPicamera2


@pytest.fixture(scope="session", autouse=True)
def close_picamera():
    """
    Explicitly close the Picamera2 after the full test session.
    ensuring the Picamera2 cleanup (and its log
    messages) happen while the logging streams are still open.
    """
    yield
    instance = MyPicamera2._instance
    if instance is not None:
        instance._picam.close()
