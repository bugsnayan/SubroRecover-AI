"""
SubroRecover AI - FastAPI Enterprise REST Application Entrypoint
"""

import os
import sys
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.api.claims import router as claims_router
from backend.api.documents import router as documents_router
from backend.api.investigation import router as investigation_router
from backend.api.reports import router as reports_router
from backend.api.analytics import router as analytics_router
from backend.api.system import router as system_router
from database.connection import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("subrorecover.backend")

app = FastAPI(
    title="SubroRecover AI — Enterprise API",
    description="REST API service for the AI-Powered Multi-Agent Insurance Subrogation & Recovery Intelligence Platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing & Correlation Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} responded {response.status_code} in {process_time}ms")
    return response

# Startup Event: Ensure Database Schema is Ready
@app.on_event("startup")
def on_startup():
    logger.info("Initializing SubroRecover AI database schema...")
    init_db()
    logger.info("SubroRecover AI Backend service started successfully.")

# Mount Routers
app.include_router(claims_router)
app.include_router(documents_router)
app.include_router(investigation_router)
app.include_router(reports_router)
app.include_router(analytics_router)
app.include_router(system_router)

@app.get("/")
def root():
    return {
        "message": "SubroRecover AI Enterprise API is running.",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
