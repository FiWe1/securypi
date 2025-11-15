class MockDHT22:
    def __init__(self, pin):
        pass

    @property
    def temperature(self):
        return 999  # Mock temperature

    @property
    def humidity(self):
        return 999  # Mock humidity

    def exit(self):
        pass


class MockBoard:
    D4 = None  # Mock pin
