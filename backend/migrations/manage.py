#!/usr/bin/env python3
import os
import sys
from peewee_migrate import Router
from peewee import PostgresqlDatabase
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
    autocommit=True,  # Enable autocommit for migrations
    autorollback=True
)

def run_migrations():
    """Run all pending migrations."""
    try:
        # Ensure we're connected
        if db.is_closed():
            db.connect()

        # Create router with our database
        router = Router(db)
        
        # Run migrations
        router.run()
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()

def rollback(steps=1):
    """Rollback the specified number of migrations."""
    try:
        # Ensure we're connected
        if db.is_closed():
            db.connect()

        # Create router with our database
        router = Router(db)
        
        # Rollback migrations
        router.rollback(steps)
        logger.info(f"Rolled back {steps} migration(s)")
    except Exception as e:
        logger.error(f"Failed to rollback migrations: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python manage.py [run|rollback <steps>]")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "run":
            run_migrations()
        elif command == "rollback" and len(sys.argv) == 3:
            try:
                steps = int(sys.argv[2])
                rollback(steps)
            except ValueError:
                print("Steps must be a number")
                sys.exit(1)
        else:
            print("Invalid command")
            print("Usage: python manage.py [run|rollback <steps>]")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)
