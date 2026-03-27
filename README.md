# EcoGuard 🌍

AI-powered waste management and carbon tracking system with automatic model training and deployment.

## Quick Start

### 1. Local Development

```bash
# Install dependencies
make install

# Run API locally
make dev
# API available at http://localhost:8000

# Run full stack (API + MLflow + Database)
make compose
# API: http://localhost:8000
# MLflow: http://localhost:5000
# Docs: http://localhost:8000/docs
```

### 2. Deploy to Render (Production)

```bash
# 1. Sign up at https://render.com
# 2. Connect GitHub repo
# 3. Add GitHub secret: RENDER_DEPLOY_HOOK
# 4. Push code
git push origin main
# ✨ Auto-deploys in ~10 minutes!
```

## What is EcoGuard?

**Three ML Models in One API:**
- 🎯 **Vision Model** (YOLO v8) - Detects waste objects in images
- ⚖️ **Weight Estimator** (sklearn) - Estimates waste weight from bounding boxes
- 🌱 **Lifestyle Model** (sklearn) - Predicts carbon emissions from user habits

## Project Structure

```
latest_ecoguard/
├── app.py                          # FastAPI application
├── predictor.py                    # Model predictor class
├── Dockerfile                      # Container configuration
├── docker-compose.yml              # Local development stack
├── render.yaml                     # Render deployment config
│
├── .github/workflows/
│   └── deploy-render.yml           # Auto-deployment on push
│
├── mlops/                          # ML utilities
│   ├── model_registry.py          # MLflow integration
│   ├── monitoring.py              # Metrics & monitoring
│   ├── train_pipeline.py          # Model training
│   └── config.py                  # Configuration
│
├── tests/                          # Test suites
│   ├── test_api.py                # API tests
│   ├── test_load.py               # Load testing
│   └── test_mlflow.py             # MLflow tests
│
├── vision_model/                   # YOLO model
├── weight_model/                   # Weight estimator
├── lifestyle_model/                # Lifestyle model
│
└── Documentation:
    ├── RENDER_DEPLOYMENT_GUIDE.md  # Render setup guide
    ├── RENDER_SECRETS_SETUP.md     # GitHub secrets config
    └── RENDER_QUICK_REFERENCE.md   # Commands cheat sheet
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

### Core Endpoints
- `POST /api/vision/detect` - Detect waste objects
- `POST /api/weight/estimate` - Estimate weight from bbox
- `POST /api/carbon/calculate` - Calculate carbon emissions
- `POST /api/lifestyle/predict` - Predict lifestyle emissions
- `WS /api/sensor/stream` - Real-time sensor data
- `POST /api/user/log-action` - Log user actions

### Interactive Docs
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## Development Commands

```bash
make help                 # Show all commands

# Testing
make test               # Run all tests
make test-fast         # Run tests (fail fast)
make test-load         # Load testing

# Code Quality
make lint              # Linting & type checks
make format            # Auto-format code
make clean             # Clean artifacts

# Local Servers
make dev               # Run API with auto-reload
make compose           # Start full stack
make compose-down      # Stop stack
make mlflow            # Start MLflow UI
make logs              # View API logs

# Docker
make docker            # Build Docker image
make docker-run        # Run container
make docker-stop       # Stop container
```

## Deployment

### Automated Deployment to Render

```bash
# Just push code - everything else is automatic!
git push origin main

# Triggers:
# 1. GitHub Actions runs tests
# 2. If passing, triggers Render webhook
# 3. Render auto-builds & deploys
# 4. GitHub verifies health endpoint

# Monitor at: https://dashboard.render.com
```

### Setup Instructions

1. **Read**: [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
2. **Setup Secrets**: [RENDER_SECRETS_SETUP.md](RENDER_SECRETS_SETUP.md)
3. **Commands Ref**: [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md)

## Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Key variables:
```
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=<secure-random-string>
CORS_ORIGINS=https://yourdomain.com
MLFLOW_TRACKING_URI=http://mlflow:5000
```

## Features

✅ **Three ML Models** - Vision, weight, lifestyle predictions
✅ **Auto-Deployment** - Push → Auto-test → Auto-deploy to Render
✅ **Model Versioning** - MLflow registry with champion tracking
✅ **Monitoring** - Prometheus metrics + dashboards
✅ **Testing** - Unit, integration, and load tests
✅ **Health Checks** - Automatic health monitoring
✅ **API Documentation** - Interactive Swagger UI
✅ **Local Development** - Docker Compose full stack

## Performance

- Vision detection: ~200-400ms
- Weight estimation: ~50-100ms
- Lifestyle prediction: ~50-100ms
- **Total latency**: < 500ms per request

## Testing

```bash
# Unit & Integration Tests
pytest tests/ -v --cov=.

# Load Testing (concurrent requests)
pytest tests/test_load.py -v

# View coverage report
open htmlcov/index.html
```

## Monitoring

### Local (Docker Compose)
```bash
make compose
# MLflow: http://localhost:5000
# API: http://localhost:8000/docs
```

### Production (Render)
```
https://dashboard.render.com/services
```

View:
- Deployment status
- Real-time logs
- CPU/Memory metrics
- Request counts

## Model Training

### Weekly Auto-Training
Models can be retrained automatically each week. See [mlops/train_pipeline.py](mlops/train_pipeline.py)

### Manual Training
```bash
python mlops/train_pipeline.py
```

## Troubleshooting

### API Won't Start
```bash
# Check locally
make dev

# Check logs
make logs

# Verify requirements.txt has all dependencies
pip install -r requirements.txt
```

### Models Not Loading
```bash
# Test model imports
python -c "from predictor import ModelPredictor; p = ModelPredictor()"

# Check model files exist
ls models/
ls vision_model/
ls weight_model/
ls lifestyle_model/
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/ -vv

# Check for missing dependencies
pip install -r requirements-dev.txt
```

### Render Deployment Issues
See [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md#troubleshooting)

## Cost

**Development**: Free (local or Render free tier)
**Production**: $12/month (Render Starter plan)

Free tier may sleep if inactive. Starter plan guarantees uptime.

## Architecture

```
Git Repo
   ↓
GitHub Actions (Tests)
   ↓
Render Webhook Trigger
   ↓
Render Auto-Build
   ↓
Load Models
   ↓
✨ Live API
```

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | FastAPI server |
| `predictor.py` | Model predictor class |
| `Dockerfile` | Container image |
| `render.yaml` | Render config |
| `.github/workflows/deploy-render.yml` | Auto-deploy workflow |
| `mlops/model_registry.py` | MLflow integration |
| `mlops/monitoring.py` | Metrics & monitoring |
| `tests/test_api.py` | API tests |

## Documentation

- **Setup**: [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
- **GitHub Secrets**: [RENDER_SECRETS_SETUP.md](RENDER_SECRETS_SETUP.md)
- **Quick Commands**: [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md)
- **API Docs**: http://localhost:8000/docs (when running)

## Technologies Used

### ML & Data
- PyTorch (YOLO v8)
- Scikit-learn
- MLflow

### Backend
- FastAPI
- Uvicorn
- Pydantic

### Infrastructure
- Docker
- Render
- GitHub Actions

### Testing
- Pytest
- Coverage

### Monitoring
- Prometheus
- MLflow UI

## Quick Links

| Link | Purpose |
|------|---------|
| `make help` | Show all commands |
| `/docs` | Interactive API docs |
| `https://dashboard.render.com` | Deployment dashboard |
| `.github/workflows/deploy-render.yml` | Auto-deploy config |
| `render.yaml` | Service config |

## Getting Help

1. Check [RENDER_QUICK_REFERENCE.md](RENDER_QUICK_REFERENCE.md)
2. Review logs:
   - Local: `make logs`
   - Render: Dashboard → Logs
3. Test locally first:
   - `make dev`
   - `curl http://localhost:8000/health`
4. Check GitHub Actions:
   - https://github.com/yourusername/ecoguard/actions

## Contributing

1. Create feature branch
2. Make changes
3. Run tests: `make test`
4. Format code: `make format`
5. Push to branch
6. Create Pull Request

Tests + linting must pass before deployment.

## License

MIT License - see LICENSE file

## Project Status

✅ **Production Ready**
- Auto-deployment working
- All tests passing
- Models loading correctly
- Monitoring in place

---

**Ready to deploy?** → Push to main and watch it go live! 🚀

```bash
git push origin main
# ✨ Auto-deploys in ~10 minutes
# Monitor at https://dashboard.render.com
```
