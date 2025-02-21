import logging
import debugpy
from app.utils.config import settings

logger = logging.getLogger(__name__)

def start_debugger() -> None:
    if settings.RUN_MAIN:
        try:
            debugpy.listen(("0.0.0.0", settings.DEBUG_PORT))
            logger.info("Debugger is listening on port %s", settings.DEBUG_PORT)
        except Exception as e: # pylint: disable=PylintW0718:broad-exception-caught
            logger.error("Failed to start debugger: %s", e)
