import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents_router, category_router
from app.core.debugger import start_debugger
from app.core.config import settings

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

# Include API routes
app.include_router(agents_router.router)
app.include_router(category_router.router)


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    logger.info("Health check endpoint accessed.")
    return {"status": "OK", "message": "Versa-Forge API is running"}
