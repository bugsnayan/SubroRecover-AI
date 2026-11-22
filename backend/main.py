"""
SubroRecover AI - FastAPI Enterprise REST Application Entrypoint
"""

import os
import sys
import time
import logging
from fastapi import FastAPI, Request, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

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

# Frontend dist path
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

# SPA HTML Navigation Middleware (serves index.html when a browser requests any page)
@app.middleware("http")
async def spa_html_navigation_middleware(request: Request, call_next):
    accept = request.headers.get("accept", "")
    path = request.url.path
    if (
        "text/html" in accept
        and not path.startswith("/api")
        and not path.startswith("/docs")
        and not path.startswith("/redoc")
        and not path.startswith("/openapi.json")
        and not path.startswith("/assets")
        and not any(path.endswith(ext) for ext in [".svg", ".png", ".ico", ".js", ".css", ".json", ".map", ".pdf"])
    ):
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
    return await call_next(request)

# Request Timing & Correlation Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} responded {response.status_code} in {process_time}ms")
    return response

# Startup Event: Ensure Database Schema is Ready & Seeded
@app.on_event("startup")
def on_startup():
    logger.info("Initializing SubroRecover AI database schema...")
    init_db()
    
    # Auto-seed if database is empty (e.g., fresh container or Render cloud deployment)
    try:
        from database.connection import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            claim_count = conn.execute(text("SELECT COUNT(*) FROM insurance_claims")).scalar()
            if not claim_count:
                logger.info("Empty database detected. Running automated ETL pipeline and deterministic seed...")
                from data_engineering.pipeline import run_etl_pipeline
                from scripts.seed_assessments import seed_all_assessments
                run_etl_pipeline()
                seed_all_assessments()
                logger.info("Database auto-seeded successfully with 180 claims.")
    except Exception as e:
        logger.warning(f"Database auto-seed check skipped: {e}")

    logger.info("SubroRecover AI Backend service started successfully.")

# Mount API Routers (under /api for frontend client and proxy)
api_router = APIRouter(prefix="/api")
api_router.include_router(claims_router)
api_router.include_router(documents_router)
api_router.include_router(investigation_router)
api_router.include_router(reports_router)
api_router.include_router(analytics_router)
api_router.include_router(system_router)

@api_router.get("/")
def api_root():
    return {
        "service": "SubroRecover AI Enterprise API",
        "docs": "/docs",
        "health": "/api/health",
        "version": "1.0.0"
    }

app.include_router(api_router)

# Mount direct routers for backwards compatibility with test suite and direct callers
app.include_router(claims_router)
app.include_router(documents_router)
app.include_router(investigation_router)
app.include_router(reports_router)
app.include_router(analytics_router)
app.include_router(system_router)

# Mount Frontend Single Page Application (SPA) if dist bundle exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist) and os.path.isdir(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/shield.svg")
    def shield_icon():
        return FileResponse(os.path.join(frontend_dist, "shield.svg"))

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Exclude reserved API, docs, and health prefixes
        if full_path.startswith("api") or full_path.startswith("health") or full_path in ["docs", "redoc", "openapi.json"]:
            raise HTTPException(status_code=404, detail="Resource not found")
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "SubroRecover AI API is running."}
else:
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
