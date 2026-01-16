#!/bin/bash
set -e

# Suppress PaddlePaddle's signal crash message
# PaddlePaddle has its own signal handler that crashes on SIGTERM
# Setting this env var tells glog (Google's logging library) to be less verbose
export GLOG_minloglevel=3
# Suppress C++ call stack prints
export FLAGS_call_stack_level=0

# PORT can be set via environment variable (defaults to 8080)
PORT="${PORT:-8080}"

echo "========================================="
echo "PaddleOCR FastAPI Service - Startup"
echo "========================================="
echo "Host: 0.0.0.0"
echo "Port: $PORT"
echo "Workers: 1"
echo "Device: ${DEVICE:-cpu}"
echo "Model Variant: ${MODEL_VARIANT:-server}"
echo "========================================="

# Start the FastAPI application with uvicorn
# Convert LOG_LEVEL to lowercase for uvicorn
LOG_LEVEL_LOWER=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 1 \
    --log-level "$LOG_LEVEL_LOWER"
