import pytest

from securypi_app.sensors.mycam import MyPicamera2



my_picam = MyPicamera2.get_instance()



"""
Testing method MyPicamera2().get_best_sensor_mode(res, fps)

! parametrized for Raspberry Pi Camera Module 3 Wide !

print(Picamera2().sensor_modes)
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

modes = my_picam.sensor_modes

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
def test_get_best_sensor_mode(resolution, fps, expected):
    assert my_picam.get_best_sensor_mode(resolution, fps) == expected