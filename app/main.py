from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents_router, category_router


# Initialize FastAPI app
app = FastAPI(
    title="Versa-Forge API",
    description="VersaForge – A modular platform for building custom GPT agents with multi-LLM support and RAG.",
    version="1.0.0",
)


# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(agents_router.router, prefix="/agents", tags=["Agents"])
app.include_router(category_router.router, prefix="/categories", tags=["Categories"])

"""
# app.include_router(files.router, prefix="/files", tags=["File Management"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
"""


# Health check route
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "OK", "message": "Versa-Forge API is running"}
