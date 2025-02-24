from typing import Dict
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents_router, category_router
from app.utils.debugger import start_debugger
from app.utils.config import settings
from app.api.error_handlers import (
    resource_not_found_exception_handler, duplicate_resource_exception_handler,invalid_input_exception_handler,
    permission_denied_exception_handler, database_exception_handler, generic_exception_handler
)
from app.core.exceptions import (
    ResourceNotFoundException, DuplicateResourceException,
    InvalidInputException,
    PermissionDeniedException, DatabaseException
)


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start debugger if enabled
start_debugger()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

# Enable CORS - restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Register Exception Handlers
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(DuplicateResourceException, duplicate_resource_exception_handler)
app.add_exception_handler(PermissionDeniedException, permission_denied_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(InvalidInputException, invalid_input_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)  # Catch-all handler

# ✅ Register Routers
app.include_router(agents_router.router)
app.include_router(category_router.router)


# ✅ Health Check Endpoint
@app.get("/", tags=["Health"])
def health_check() -> Dict[str, str]:
    logger.info("Health check endpoint accessed.")
    return {"status": "OK", "message": "Versa-Forge API is running"}
