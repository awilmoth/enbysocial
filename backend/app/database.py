import os
from peewee import PostgresqlDatabase, Model
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database with all necessary parameters
db = PostgresqlDatabase(
    'enbysocial',
    user='postgres',
    password='postgres',
    host='db',
    port=5432,
    autocommit=True
)

class BaseModel(Model):
    """Base model class with common functionality."""
    
    class Meta:
        database = db
        legacy_table_names = False  # Use the exact table names we specify

    def to_dict(self):
        """Convert model instance to dictionary."""
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Model):
                value = value.id
            data[field] = value
        return data

def init_db():
    """Initialize database tables."""
    try:
        from app.models.user import User, PersonalAd, Message
        
        logger.info("Creating database tables...")
        # Close any existing connection
        if not db.is_closed():
            db.close()
        
        # Connect and create tables
        db.connect()
        with db.atomic():
            db.create_tables([User, PersonalAd, Message], safe=True)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()

# Initialize connection handler
@db.connection_context()
def get_db():
    """Get database connection context."""
    try:
        yield db
    finally:
        if not db.is_closed():
            db.close()
