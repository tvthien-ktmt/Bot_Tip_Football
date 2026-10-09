import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.data.seed_data import seed_database
from backend.app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("keolab")


from backend.app.data.sync_database import sync_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed database
    logger.info("Initializing KèoLab Database & Quantitative Models...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from backend.app.models.entities import Match
        if db.query(Match).filter_by(status="SCHEDULED").count() == 0:
            logger.info("No SCHEDULED matches found, running sync_database...")
            sync_database(db, force_reseed_scheduled=True)
    finally:
        db.close()
    yield
    # Shutdown
    logger.info("Shutting down KèoLab...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="KèoLab – Quantitative Football Tip Analyzer. For entertainment & academic analysis only.",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Welcome to KèoLab – Football Tip Analyzer API",
        "docs_url": "/docs",
        "disclaimer": "Chỉ mang tính giải trí & tham khảo học thuật. Không đảm bảo lợi nhuận. Không nhận cược."
    }
