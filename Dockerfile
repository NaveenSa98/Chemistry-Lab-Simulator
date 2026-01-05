# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Expose port (Fly.io uses PORT env variable)
EXPOSE 8080

# Start command using gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 backend.app:app
