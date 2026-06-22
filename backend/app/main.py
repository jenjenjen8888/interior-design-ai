from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import suggestions

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered interior design suggestion API",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_provider": settings.model_provider}


app.include_router(suggestions.router, prefix="/api/v1")
