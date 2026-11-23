"""
Main FastAPI Application Entrypoint for RetroMorph AI.
PS1 Character Generator Backend.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import generate, jobs, quality, health, samples

app = FastAPI(
    title="RetroMorph AI - PS1 Character Generator API",
    description="Single-photo to game-ready PlayStation 1 3D Character Generator API",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(generate.router)
app.include_router(jobs.router)
app.include_router(quality.router)
app.include_router(health.router)
app.include_router(samples.router)

# Ensure upload and generated storage directories exist
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.makedirs(os.path.join(PROJECT_ROOT, "backend", "uploads"), exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, "backend", "generated"), exist_ok=True)


@app.get("/")
async def root():
    return {
        "message": "RetroMorph AI Backend is running.",
        "documentation": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
