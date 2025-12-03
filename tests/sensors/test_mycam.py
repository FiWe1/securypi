import pytest
import os
from time import sleep

from securypi_app.sensors.camera.mycam import MyPicamera2, StreamingOutput


"""
Mycam package tests using pytest
"""


class TestMycamClass():

    @pytest.fixture
    def picam(self):
        """
        Every time yield the same MyPicamera2 instance,
        but with default configuration.
        """
        mypicam = MyPicamera2.get_instance()
        yield mypicam

        # try to get MyPicamera2 to default state
        mypicam._picam.stop()
        mypicam.configure_video_sensor()
        mypicam.configure_video_streams()
        mypicam.configure_runtime_controls()

        mypicam._streaming_output = StreamingOutput()
        mypicam._stream_timer = None

        mypicam._recording_encoder = None
        mypicam._streaming_encoder = None

        del mypicam  # delete object reference


    def test_singleton(self, picam):
        """ Try to break singleton """
        obj2 = MyPicamera2()
        assert picam is obj2
    
    @pytest.mark.parametrize(
        "target", ["main", "lores", "sensor"]
    )
    def test_current_resolution(self, picam, target):
        assert isinstance(picam.get_current_resolution(target),
                          tuple)

    def test_instance_type(self, picam):
        assert isinstance(picam, MyPicamera2)

    def test_capture_picture(self, picam):
        assert picam.capture_picture() is not None

    def test_stream(self, picam):
        output = picam._streaming_output
        assert isinstance(output, StreamingOutput)

        picam.start_capture_stream()
        sleep(1)
        assert picam.is_streaming()
        assert output.frame is not None

        picam.stop_capture_stream()
        assert picam._stream_timer is None
        assert picam._streaming_encoder is None

    def test_default_recording(self, picam):
        recording_path = picam.start_default_recording()
        sleep(1)
        assert picam.is_recording()

        assert recording_path.exists()
        assert recording_path.stat().st_size > 0  # verify not empty

        picam.stop_recording_to_file()
        assert picam._recording_encoder is None

        # Remove file afterwards
        os.remove(recording_path)
        assert not recording_path.exists()

    """
    Testing method Mypicamera2().get_best_sensor_mode(res, fps)

    ! parametrized for Raspberry Pi Camera Module 3 Wide !

    print(picamera2().sensor_modes)
    >>>
    [0]
    format: SRGGB10_CSI2P
    unpacked: SRGGB10
    bit_depth: 10
    size: (1536, 864)
    fps: 120.13
    crop_limits: (768, 432, 3072, 1728)
    exposure_limits: (9, 77208145, 20000)
    [1]
    format: SRGGB10_CSI2P
    unpacked: SRGGB10
    bit_depth: 10
    size: (2304, 1296)
    fps: 56.03
    crop_limits: (0, 0, 4608, 2592)
    exposure_limits: (13, 112015096, 20000)
    [2]
    format: SRGGB10_CSI2P
    unpacked: SRGGB10
    bit_depth: 10
    size: (4608, 2592)
    fps: 14.35
    crop_limits: (0, 0, 4608, 2592)
    exposure_limits: (26, 220416802, 20000)
    """

    modes = MyPicamera2.get_instance()._picam.sensor_modes

    @pytest.mark.parametrize(
        "resolution,fps,expected",
        [
            ((1920, 1080), 30, modes[1]),
            ((1920, 1080), 10, modes[2]),
            ((1280, 720), 120, modes[0]),
            ((1280, 720), 60, modes[0]),
            ((1280, 720), 55, modes[1]),
            ((1280, 720), 14, modes[2]),
            ((3840, 2160), 15, None),
            ((3840, 2160), 14, modes[2]),
            ((2000, 1500), 50, modes[1]),
        ],
    )
    def test_get_best_sensor_mode(self, picam, resolution, fps, expected):
        assert picam.get_best_sensor_mode(resolution, fps) == expected
