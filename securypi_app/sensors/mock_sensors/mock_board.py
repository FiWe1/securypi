"""
Mockinig RPI's board used by sensors
for platform independent development and testing.
"""
from typing import NamedTuple

class I2C:
    def __init__(self):
        pass
    
class MockBoard(NamedTuple):
    """ Mock RPI's board """
    D4 = None # MockDHT22
    I2C = I2C # MockSHT31D
