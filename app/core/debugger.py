import os
import debugpy
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


def start_debugger():
    """Start the debugger if RUN_MAIN is set."""
    if settings.RUN_MAIN == True:
        debug_port = settings.DEBUG_PORT
        try:
            debugpy.listen(("0.0.0.0", debug_port))
            logger.info(f"🔍 Debugger is listening on port {debug_port}...")
        except Exception as e:
            logger.error(f"⚠️ Failed to start debugger: {e}")
