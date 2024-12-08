from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.database import db, init_db
from app.routers import user, personal_ads, messages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enby Social API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Manage database connections for each request."""
    try:
        # Close any existing connection
        if not db.is_closed():
            db.close()
        
        # Connect for this request
        db.connect()
        
        # Process request
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return Response("Database connection error", status_code=500)
    finally:
        if not db.is_closed():
            db.close()

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up database connections on shutdown."""
    logger.info("Shutting down application...")
    if not db.is_closed():
        db.close()

# Include routers
app.include_router(user.router)
app.include_router(personal_ads.router)
app.include_router(messages.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Enby Social API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        if not db.is_closed():
            db.close()
        db.connect()
        db.execute_sql('SELECT 1')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health check error: {e}")
        db_status = "error"
    finally:
        if not db.is_closed():
            db.close()
    
    return {
        "status": "healthy",
        "database": db_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
