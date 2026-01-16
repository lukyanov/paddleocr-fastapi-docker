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
# WORKERS controls uvicorn worker processes (defaults to 1)
# With thread pool OCR, 1 worker is usually sufficient
WORKERS="${WORKERS:-1}"

echo "========================================="
echo "PaddleOCR FastAPI Service - Startup"
echo "========================================="
echo "Server:"
echo "  Host: 0.0.0.0"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Log Level: $LOG_LEVEL"
echo "OCR:"
echo "  Device: $DEVICE"
echo "  Model Variant: $MODEL_VARIANT"
echo "  Doc Orientation: $ENABLE_DOC_ORIENTATION"
echo "  Doc Unwarping: $ENABLE_DOC_UNWARPING"
echo "  Text Orientation: $ENABLE_TEXT_ORIENTATION"
echo "========================================="

# Start the FastAPI application with uvicorn
# Convert LOG_LEVEL to lowercase for uvicorn
LOG_LEVEL_LOWER=$(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --log-level "$LOG_LEVEL_LOWER"
