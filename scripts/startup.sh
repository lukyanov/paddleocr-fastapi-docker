#!/bin/bash
set -e

echo "========================================="
echo "PaddleOCR FastAPI Service - Startup"
echo "========================================="

# Check if models are already cached
if [ ! -d "$PADDLEOCR_HOME/whl" ]; then
    echo "Models not found in cache. Pre-downloading models..."
    python3 /app/scripts/download_models.py

    if [ $? -ne 0 ]; then
        echo "ERROR: Model download failed"
        exit 1
    fi
else
    echo "Models found in cache, skipping download"
fi

echo "========================================="
echo "Starting FastAPI application..."
echo "Host: 0.0.0.0"
echo "Port: 8000"
echo "Workers: 1"
echo "Device: ${DEVICE:-cpu}"
echo "========================================="

# Start the FastAPI application with uvicorn
# Convert LOG_LEVEL to lowercase for uvicorn
LOG_LEVEL_LOWER=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level "$LOG_LEVEL_LOWER"
