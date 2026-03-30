import logging

from securypi_app.peripherals.camera.motion_capturing import MotionCapturing

logger = logging.getLogger(__name__)


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
        logger.debug("Starting mocked motion capturing.")
    
    def stop(self):
        """ Stop background motion capturing, if it was running. """
        logger.debug("Stopping mocked motion capturing.")
