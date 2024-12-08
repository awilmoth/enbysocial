FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts

# Set execute permissions for the start script
RUN chmod +x scripts/start.sh && \
    # Ensure line endings are correct
    sed -i 's/\r$//' scripts/start.sh

EXPOSE 8000

# Use the startup script as the entry point
ENTRYPOINT ["/bin/bash", "./scripts/start.sh"]
