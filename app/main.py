from typing import Dict
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import user_router, agents_router, category_router
from app.utils.debugger import start_debugger
from app.utils.config import settings
from app.api.exception_handler import global_exception_handler

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
app.add_exception_handler(Exception, global_exception_handler)

# ✅ Register Routers
app.include_router(user_router.router)
app.include_router(agents_router.router)
app.include_router(category_router.router)


# ✅ Health Check Endpoint1
@app.get("/", tags=["Health"])
def health_check() -> Dict[str, str]:
    logger.info("Health check endpoint accessed.")
    return {"status": "OK", "message": "Versa-Forge API is running"}
