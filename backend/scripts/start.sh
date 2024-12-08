#!/bin/bash
set -e

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    while ! nc -z db 5432; do
        sleep 0.1
    done
    echo "PostgreSQL is ready!"
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    python migrations/manage.py run
}

# Main execution
wait_for_postgres

# Run migrations
run_migrations

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
