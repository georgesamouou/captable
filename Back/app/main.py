from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.models import Base
from app.routers import auth, shareholders, issuances, dashboard, audit
from app.config import settings
from app.services import AuditService
from app.models import AuditAction
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Cap Table Management System",
    description="A comprehensive API for managing company capitalization tables and share issuances",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(shareholders.router)
app.include_router(issuances.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cap Table Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Cap Table Management System...")
    
    # Create default admin user if not exists
    db = next(get_db())
    try:
        from app.models import User, UserRole
        from app.auth import get_password_hash
        
        admin_user = db.query(User).filter(User.email == "admin@company.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@company.com",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            logger.info("Default admin user created: admin@company.com / admin123")
        
        # Create default shareholder for testing
        shareholder_user = db.query(User).filter(User.email == "shareholder@company.com").first()
        if not shareholder_user:
            shareholder_user = User(
                email="shareholder@company.com",
                hashed_password=get_password_hash("shareholder123"),
                role=UserRole.SHAREHOLDER
            )
            db.add(shareholder_user)
            db.flush()
            
            from app.models import ShareholderProfile
            shareholder_profile = ShareholderProfile(
                user_id=shareholder_user.id,
                first_name="John",
                last_name="Doe",
                phone="+1234567890",
                address="123 Main St, City, Country",
                tax_id="TAX123456"
            )
            db.add(shareholder_profile)
            db.commit()
            logger.info("Default shareholder user created: shareholder@company.com / shareholder123")
            
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Cap Table Management System...")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Not found", "message": "The requested resource was not found"}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "An unexpected error occurred"} 