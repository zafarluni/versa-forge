import logging

import debugpy

from app.utils.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def start_debugger() -> None:
    """
    Starts debugpy remote debugger if settings.run_main is True.
    """
    if settings.run_main:
        try:
            debugpy.listen(("0.0.0.0", settings.debug_port))
            logger.info("Debugger is listening on port %s", settings.debug_port)
            # Optional: Uncomment next line to pause execution until debugger is attached
            # debugpy.wait_for_client()
        except Exception as e:
            logger.error("Failed to start debugger: %s", e)
