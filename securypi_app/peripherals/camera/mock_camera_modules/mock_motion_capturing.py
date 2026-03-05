from securypi_app.peripherals.camera.motion_capturing import MotionCapturing


class MockMotionCapturing(MotionCapturing):
    """
    Mock class - a dummy in place of MotionCapturing
    for platform independent development and testing.
    """
    def start(self):
        """ 
        Start background motion capturing.
        If it was running, restart it.
        """
        print("Starting mocked motion capturing")
    
    def stop(self):
        """ Stop background motion capturing, if it was running. """
        print("Stopping mocked motion capturing")
