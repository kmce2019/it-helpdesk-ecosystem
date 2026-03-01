from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
from .config import settings
from .database import engine
from .models.models import Base
from .routers import auth, users, tickets, slas, assets, agent, reporting, settings as settings_router
from .services.cve_service import run_full_cve_scan

# Create tables
Base.metadata.create_all(bind=engine)

from .database import SessionLocal
from .models.models import User, UserRole
from .utils.auth import get_password_hash

def bootstrap_admin():
    db = SessionLocal()
    try:
        user_count = db.query(User).count()
        if user_count == 0:
            admin = User(
                username=settings.BOOTSTRAP_ADMIN_USERNAME,
                email="admin@local.invalid",
                full_name="System Administrator",
                hashed_password=get_password_hash(settings.BOOTSTRAP_ADMIN_PASSWORD),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ Bootstrapped initial admin user")
    finally:
        db.close()

bootstrap_admin()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Complete IT Help Desk Ecosystem for School Districts"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(slas.router)
app.include_router(assets.router)
app.include_router(agent.router)
app.include_router(reporting.router)
app.include_router(settings_router.router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# Background scheduler for CVE scanning
scheduler = BackgroundScheduler()


async def scheduled_cve_scan():
    """Run CVE scan on a schedule."""
    from .database import SessionLocal
    db = SessionLocal()
    try:
        logger.info("Starting scheduled CVE scan...")
        result = await run_full_cve_scan(db)
        logger.info(f"CVE scan completed: {result}")
    except Exception as e:
        logger.error(f"CVE scan failed: {e}")
    finally:
        db.close()


@app.on_event("startup")
def startup_event():
    """Initialize background tasks on startup."""
    logger.info(f"{settings.APP_NAME} started")

    # Schedule CVE scan (weekly)
    scheduler.add_job(
        scheduled_cve_scan,
        "interval",
        hours=settings.CVE_CHECK_INTERVAL_HOURS,
        id="cve_scan_job",
        name="CVE Vulnerability Scan",
        replace_existing=True
    )
    scheduler.start()
    logger.info("CVE scan scheduler started")


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown."""
    scheduler.shutdown()
    logger.info(f"{settings.APP_NAME} stopped")

# Auth / Registration
OPEN_REGISTRATION: bool = False
BOOTSTRAP_ADMIN_USERNAME: str = "admin"
BOOTSTRAP_ADMIN_PASSWORD: str = "password"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
