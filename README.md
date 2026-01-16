# PaddleOCR FastAPI Docker Service

A production-ready OCR service using PaddleOCR PP-OCRv5 models with FastAPI and Docker. Features automatic multilingual detection for Simplified Chinese, Traditional Chinese, English, Japanese, and Pinyin.

## Features

- **PP-OCRv5 Model**: Latest PaddleOCR model with high accuracy
- **Automatic Language Detection**: Single multilingual model handles 5 text types automatically
- **Multiple Input Methods**:
  - Image file upload (multipart/form-data)
  - URL-based image processing
- **Dual Docker Support**:
  - CPU-optimized image (multi-stage build)
  - GPU-accelerated image (CUDA support)
- **Production Ready**:
  - Health checks and monitoring
  - Structured JSON responses
  - Request validation and error handling
  - SSRF protection
  - Non-root container user
- **Latest Dependencies**: All packages use latest stable versions (January 2026)

## Supported Languages

PP-OCRv5 automatically detects and processes:
- Simplified Chinese
- Traditional Chinese
- English
- Japanese
- Pinyin

**No explicit language specification needed!**

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- For GPU version: NVIDIA Docker runtime and compatible GPU

### CPU Version

```bash
# Clone the repository
git clone <your-repo-url>
cd paddle-ocr-docker

# Build and start the service
docker-compose up -d

# Check service status
curl http://localhost:8080/health
```

### GPU Version

```bash
# Build and start the GPU service
docker-compose -f docker-compose.gpu.yml up -d

# Check service status
curl http://localhost:8080/health/ready
```

### Model Variants

Choose between server (higher accuracy) or mobile (smaller/faster) models:

```bash
# Server models (default) - higher accuracy, ~2-3GB image
docker build -f Dockerfile.cpu -t paddleocr:server .

# Mobile models - smaller and faster, ~1.5GB image
docker build -f Dockerfile.cpu --build-arg MODEL_VARIANT=mobile -t paddleocr:mobile .
```

The service will be available at `http://localhost:8080`

## API Documentation

### Interactive API Docs

When running with `DEBUG=true`, access:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

### Endpoints

#### Health Checks

**GET /health** - Simple liveness check
```bash
curl http://localhost:8080/health
```

**GET /health/ready** - Readiness check with OCR status
```bash
curl http://localhost:8080/health/ready
```

#### OCR Processing

**POST /api/v1/ocr/upload** - Upload image file

```bash
curl -X POST "http://localhost:8080/api/v1/ocr/upload" \
  -F "file=@/path/to/image.jpg"
```

**POST /api/v1/ocr/url** - Process image from URL

```bash
curl -X POST "http://localhost:8080/api/v1/ocr/url" \
  -H "Content-Type: application/json" \
  -d '{"file_url": "https://example.com/image.jpg"}'
```

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file` | File | - | Image file (upload endpoint only) |
| `file_url` | URL | - | File URL (url endpoint only) |
| `output` | string | json | Output format: "json" or "text" (plain text only) |

### Response Format

```json
{
  "success": true,
  "message": "OCR processing completed successfully",
  "data": {
    "text": "all detected text joined by newlines",
    "text_boxes": [
      {
        "text": "detected text",
        "confidence": 0.95,
        "box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
      }
    ],
    "processing_time_ms": 1234.56,
    "num_detections": 5
  },
  "request_id": "uuid-string"
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error description",
  "error": {
    "code": "ERROR_CODE",
    "detail": "Detailed error message"
  },
  "request_id": "uuid-string"
}
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | PaddleOCR FastAPI Service | Application name |
| `DEBUG` | false | Enable debug mode |
| `DEVICE` | cpu | Device for OCR (cpu, gpu, or cuda:0) |
| `MODEL_VARIANT` | server | Model variant: "server" (accurate) or "mobile" (fast) |
| `ENABLE_DOC_ORIENTATION` | false | Enable document orientation detection |
| `ENABLE_DOC_UNWARPING` | false | Enable document unwarping |
| `ENABLE_TEXT_ORIENTATION` | true | Enable text orientation classification |
| `MAX_FILE_SIZE` | 10485760 | Max file size (10MB) |
| `IMAGE_DOWNLOAD_TIMEOUT` | 30 | URL download timeout (seconds) |
| `LOG_LEVEL` | INFO | Logging level |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8080 | Server port |
| `WORKERS` | 1 | Number of worker processes |

### Build Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `MODEL_VARIANT` | server | Bake server or mobile models into image |

## Development

### Local Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run locally
python app/main.py
```

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff app/ tests/

# Type checking
mypy app/
```

## Project Structure

```
paddle-ocr-docker/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration settings
│   ├── models/                  # Pydantic models
│   │   ├── request.py
│   │   └── response.py
│   ├── services/                # Business logic
│   │   ├── ocr_service.py
│   │   └── image_service.py
│   ├── api/                     # API endpoints
│   │   ├── health.py
│   │   └── ocr.py
│   └── utils/                   # Utilities
│       ├── exceptions.py
│       └── validators.py
├── scripts/
│   ├── download_models.py       # Model pre-download
│   └── startup.sh               # Container startup
├── tests/                       # Test files
├── Dockerfile.cpu               # CPU Docker image
├── Dockerfile.gpu               # GPU Docker image
├── docker-compose.yml           # CPU compose
├── docker-compose.gpu.yml       # GPU compose
├── requirements.txt             # Python dependencies
└── README.md
```

## Docker Images

### CPU Image
- Base: Python 3.13-slim
- Multi-stage build for smaller size
- ~1.5GB final image size

### GPU Image
- Base: NVIDIA CUDA 12.6 + cuDNN
- Supports CUDA-capable GPUs
- ~4GB final image size

## Performance

### Expected Performance
- **CPU**: ~2-5 seconds per image
- **GPU**: ~0.5-1 second per image (4-10x faster)
- **Memory**: ~1.5-2GB per OCR instance
- **Cold Start**: ~10-30 seconds (models baked into image)

### Optimization Tips

1. **Use Mobile Models**: Build with `--build-arg MODEL_VARIANT=mobile` for smaller images and faster inference
2. **Resource Limits**: Adjust Docker resource limits based on workload
3. **Horizontal Scaling**: Run multiple containers behind a load balancer
4. **GPU Acceleration**: Use GPU version for high-throughput scenarios

## Production Deployment

### Recommended Configuration

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      memory: 2G
```

### Security Best Practices

1. **HTTPS/TLS**: Use reverse proxy (nginx, traefik) with TLS termination
2. **Rate Limiting**: Implement rate limiting at proxy or application level
3. **Authentication**: Add API key authentication if needed
4. **Network**: Run in private network, expose via reverse proxy only
5. **Updates**: Keep dependencies updated regularly

### Monitoring

1. **Health Checks**: Use `/health` and `/health/ready` endpoints
2. **Metrics**: Integrate with Prometheus for metrics collection
3. **Logging**: Aggregate logs with ELK stack or similar
4. **Alerts**: Set up alerts for high memory usage or slow responses

### Scaling Strategy

**Horizontal Scaling:**
```bash
# Scale to 3 replicas
docker-compose up -d --scale paddleocr-api=3

# Use load balancer (nginx, HAProxy, Kubernetes Service)
```

**Kubernetes Deployment:**
- Use Deployment with multiple replicas
- Configure HorizontalPodAutoscaler
- Use PersistentVolume for model cache

## Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs -f

# Verify model download
docker exec -it paddleocr-api-cpu ls -la /home/appuser/.paddleocr
```

### High Memory Usage
- Reduce `MAX_FILE_SIZE` to limit input image sizes
- Ensure only one worker process (default)
- Monitor with `docker stats`

### Slow Processing
- Use GPU version for better performance
- Preprocess large images (automatic resizing enabled)
- Check CPU/memory allocation

### GPU Not Detected
```bash
# Verify NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi

# Check GPU availability in container
docker exec -it paddleocr-api-gpu nvidia-smi
```

## Dependencies

Built with latest stable versions (January 2026):
- FastAPI 0.128.0
- PaddleOCR 3.3.2
- PaddlePaddle 3.3.0
- Python 3.13

See `requirements.txt` for complete list.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Support

For issues and questions:
- Open an issue on GitHub
- Check PaddleOCR documentation: https://github.com/PaddlePaddle/PaddleOCR

## Acknowledgments

- PaddlePaddle team for PaddleOCR
- FastAPI for the excellent web framework
