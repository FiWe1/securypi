"""
Mock piqmp6988 package of sensor_qmp6988
for platform independent development and testing.

- QMP6988 connected to I2C
"""
from enum import IntEnum
from typing import NamedTuple


MOCKED_TEMPERATURE = 21.5
MOCKED_PRESSURE = 1013.25


class MockOversampling(IntEnum):
    X1 = 1
    X2 = 2
    X4 = 4
    X8 = 8
    X16 = 16
    X32 = 32


class MockFilter(IntEnum):
    COEFFECT_0 = 0
    COEFFECT_2 = 2
    COEFFECT_4 = 4
    COEFFECT_8 = 8
    COEFFECT_16 = 16
    COEFFECT_32 = 32


class MockPowermode(IntEnum):
    SLEEP = 0
    NORMAL = 1


class MockPiQmp6988:
    """ Mock pressure (and temperature) sensor. """
    def __init__(self, config: dict | None = None):
        self.config = config or {}
    
    def read(self) -> dict[str, float]:
        return {
            "temperature": MOCKED_TEMPERATURE,
            "pressure": MOCKED_PRESSURE
        }


class MockQMP(NamedTuple):
    Oversampling = MockOversampling
    Filter = MockFilter
    Powermode = MockPowermode
    PiQmp6988 = MockPiQmp6988