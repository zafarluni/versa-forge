import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.exception_handler import global_exception_handler
from app.api.routes import agents_router, category_router, user_router
from app.utils.config import get_settings
from app.utils.debugger import start_debugger

settings = get_settings()

# Logging setup - may be overridden by Uvicorn/Gunicorn
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Only start debugger in debug mode
if settings.debug_mode:
    start_debugger()

app = FastAPI(
    title=settings.project_name,
    description=settings.description,
    version=settings.version,
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(user_router.router)
app.include_router(agents_router.router)
app.include_router(category_router.router)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    logger.debug("Health check endpoint accessed.")
    return {"status": "OK", "message": "Versa-Forge API is running"}
