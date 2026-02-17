from securypi_app.peripherals.camera.motion_capturing import MotionCapturing


class MockMotionCapturing(MotionCapturing):
    """
    Mock class - a dummy in place of MotionCapturing
    for platform independent development and testing.
    """
    def start(self):
        print("Starting mocked motion capturing")
    
    def stop(self):
        print("Stopping mocked motion capturing")
