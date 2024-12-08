FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libmtdev-dev \
    libmtdev1 \
    xvfb \
    xserver-xorg-input-evdev \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p static assets screens

# Copy the web application
COPY web/app.py .
COPY web/templates ./templates

# Copy frontend screens and assets
COPY frontend/screens ./screens
COPY frontend/assets ./assets

# Set permissions
RUN chmod -R 755 .

EXPOSE 5000

# Start the Flask application with eventlet
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV DISPLAY=:99

# Start Xvfb and Flask
CMD Xvfb :99 -screen 0 900x600x24 -ac +extension GLX +render -noreset & \
    python -m flask run --host=0.0.0.0 --port=5000
