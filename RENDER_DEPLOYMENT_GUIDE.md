# Render Deployment Guide

## Overview

This guide shows how to deploy EcoGuard to Render.com - a simple, serverless platform perfect for ML APIs.

## Why Render?

✅ **Simple**: No Kubernetes complexity
✅ **Fast**: Deploy in minutes
✅ **Automatic**: Auto-scales on demand
✅ **Free tier**: Great for learning/testing
✅ **GitHub integration**: Auto-deploy on push
✅ **Built-in**: PostgreSQL, cron jobs, environment variables

## Prerequisites

1. **Render Account**: https://render.com (free tier available)
2. **GitHub Account**: Linked to your repository
3. **Environment Variables**: Ready to configure

## Step 1: Create Render Project

### Via Render Dashboard

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Select "Docker" or "Python"
4. Connect your GitHub repository
5. Choose the ecoguard repository

### Configuration

**Service Settings:**
- Name: `ecoguard-api`
- Runtime: Python
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Instance:**
- Plan: Free (suitable for testing)
  - Or Starter ($12/month) for production
- Region: Choose closest to users

**Environment Variables:**
Add these in Render dashboard:

```
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=<your-secret-key>
CORS_ORIGINS=https://yourdomain.com
MLFLOW_TRACKING_URI=<your-mlflow-url>
DATABASE_URL=postgresql://user:password@host/db
```

## Step 2: Set GitHub Secrets

Add these to your GitHub repository (Settings → Secrets):

```bash
# For Render deployment notification
RENDER_API_KEY          # From Render account settings
RENDER_SERVICE_ID       # Found in Render service URL
RENDER_DEPLOY_HOOK      # Deploy hook from Render dashboard
RENDER_SERVICE_URL      # e.g., https://ecoguard-api.onrender.com
```

### How to Get These Values

**RENDER_SERVICE_ID:**
- Service URL: `https://ecoguard-api.onrender.com`
- Or from dashboard URL: `https://dashboard.render.com/services/srv_xxxxx`

**RENDER_DEPLOY_HOOK:**
1. Go to Render Dashboard
2. Select your service
3. Settings → Deploy Hook
4. Copy the hook URL

**RENDER_API_KEY:**
1. Account Settings → API Keys
2. Create new key
3. Copy and add to GitHub secrets

## Step 3: Configure Auto-Deploy

### Option A: Dashboard (Recommended)

1. Render Dashboard → Your Service
2. Settings → Auto-Deploy: Toggle ON
3. Branch: `main`

Now every push to main automatically deploys!

### Option B: GitHub Actions (Advanced)

Uses `.github/workflows/deploy-render.yml`:

```yaml
# Triggered on push to main
# Runs tests → Notifies Render → Verifies deployment
```

## Step 4: Set Environment Variables

### In Render Dashboard

1. Service → Environment
2. Add each variable:
   - `ENVIRONMENT`: production
   - `LOG_LEVEL`: INFO
   - `SECRET_KEY`: (generate random string)
   - `CORS_ORIGINS`: your-domain.com
   - `MLFLOW_TRACKING_URI`: your-mlflow-url

### Important Variables

```env
# Required
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=<generate-random-string>

# Optional but recommended
CORS_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://...
MLFLOW_TRACKING_URI=http://mlflow-server.com:5000

# Feature flags
ENABLE_MODEL_EXPLANATIONS=false
ENABLE_BATCH_PREDICTIONS=true
```

## Step 5: Add Database (Optional)

### Using Render PostgreSQL

1. Render Dashboard → "New +" → "PostgreSQL"
2. Name: `ecoguard-postgres`
3. Note the connection string (DATABASE_URL)
4. Add DATABASE_URL to your service's environment

### Connection String

```
postgresql://user:password@host:5432/database
```

## Step 6: Deploy!

### First Deployment (Manual)

```bash
# Push to main branch
git push origin main

# Render automatically deploys the commit
# Watch deployment: https://dashboard.render.com/services
```

### Check Deployment

1. **Dashboard**: https://dashboard.render.com/services
2. **Logs**: Service → Logs
3. **Health**: https://your-service.onrender.com/health
4. **API Docs**: https://your-service.onrender.com/docs

## Monitoring Deployments

### Render Dashboard

- Service Status (Running, Building, etc.)
- Deployment History
- Logs (real-time)
- Metrics (CPU, RAM, bandwidth)
- Billing

### Health Check

```bash
curl https://ecoguard-api.onrender.com/health

# Should respond:
# {"status": "healthy", "version": "1.0.0"}
```

### API Endpoints

- **Base**: https://ecoguard-api.onrender.com
- **Docs**: https://ecoguard-api.onrender.com/docs
- **Health**: https://ecoguard-api.onrender.com/health
- **Metrics**: https://ecoguard-api.onrender.com/metrics

## Continuous Deployment

### GitHub Actions Workflow

Automatic on every push to main:

```
1. Run Tests
2. Train Models (optional)
3. Trigger Render Deployment
4. Verify Health
5. Notify Success
```

Check workflow status: https://github.com/youruser/ecoguard/actions

## Updating Models

### Method 1: Automatic Training

Models train weekly automatically (scheduled GitHub Actions):
- Trains all 3 models
- Compares with champion
- Auto-deploys if improvement found

### Method 2: Manual Update

```bash
# Just push code changes
git commit -m "Update model weights"
git push origin main

# Render auto-deploys the new version
```

## Scaling

### Auto-Scaling (Free)

Render automatically scales based on:
- CPU usage
- Memory usage
- Request load

No configuration needed!

### Manual Scaling

1. Render Dashboard → Service
2. Settings → Instance Type
3. Choose larger plan for guaranteed resources

## Cost Estimation

| Plan | Price | Best For |
|------|-------|----------|
| **Free** | $0 | Development, testing |
| **Starter** | $12/month | Small production |
| **Standard** | $29/month | Medium traffic |
| **Pro** | $49/month | High traffic |

Each additional resource (DB, Redis, etc.) adds cost.

## Troubleshooting

### Build Failed

```bash
# Check logs in Render dashboard
# Common issues:
# - Missing requirement in requirements.txt
# - Python version mismatch
# - Memory limit exceeded during build

# Fix: 
# 1. Check requirements.txt
# 2. Test locally: docker build .
# 3. Retry deploy
```

### Service Not Starting

```bash
# Check service logs
# Common issues:
# - Port binding (use $PORT variable)
# - Missing environment variables
# - Model loading timeout

# Fix:
# 1. Verify ENVIRONMENT variables
# 2. Check app.py startup code
# 3. Increase build timeout
```

### Health Check Failing

```bash
curl https://your-service.onrender.com/health

# Should respond with 200 status
# If failing:
# 1. Check app logs
# 2. Verify health endpoint exists
# 3. Check environment variables
```

### Slow Deployment

```bash
# First deploy: 5-10 minutes (builds image)
# Subsequent: 1-2 minutes (redeploy only)

# Speed up subsequent deploys:
# - Smaller requirements.txt
# - Smaller models (quantize if possible)
# - Cache Docker layers
```

## Production Checklist

- [ ] Environment variables set correctly
- [ ] Database connection configured (if using)
- [ ] Health checks passing
- [ ] API documentation accessible
- [ ] Models loading successfully
- [ ] CORS configured properly
- [ ] Monitoring alerts set up
- [ ] Backup/restore plan
- [ ] Domain configured (custom domain)
- [ ] SSL/TLS enabled (automatic)

## Custom Domain

### Setup Custom Domain

1. Render Dashboard → Service → Settings
2. Custom Domain
3. Add your domain (e.g., api.yourdomain.com)
4. Update DNS records

```
CNAME yourdomain.com → yourdomain.onrender.com
```

## Cron Jobs (Optional)

### Schedule Model Retraining

```bash
# In Render dashboard: Cron Job
# Schedule: Weekly (0 2 * * 0)
# Command: python mlops/train_pipeline.py
```

## Environment File Example

Create `.env.render`:

```env
# Production on Render
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# API
CORS_ORIGINS=https://yourdomain.com
API_PORT=8000

# MLflow
MLFLOW_TRACKING_URI=https://mlflow.onrender.com:5000

# Database
DATABASE_URL=postgresql://user:pass@host/db

# Models
MODEL_CONFIDENCE_THRESHOLD=0.5
ENABLE_ADVANCED_METRICS=true

# Security
SECRET_KEY=<very-long-random-string>
```

## Quick Reference

| Task | Command |
|------|---------|
| View logs | `Dashboard → Logs` |
| Restart service | `Dashboard → More → Restart service` |
| Check status | `curl api-url/health` |
| Manual deploy | `Push to main branch` |
| Access API | `https://service-name.onrender.com` |
| View docs | `https://service-name.onrender.com/docs` |

## Links

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Pricing**: https://render.com/pricing
- **Service Status**: https://status.render.com

## Support

- **Render Docs**: https://render.com/docs
- **Render Support**: https://render.com/support
- **Community Chat**: https://render.com/community
- **GitHub Issues**: Report issues in your repo

---

**You're ready to deploy! 🚀**

For immediate deployment:
1. Push to main branch
2. Watch Render dashboard
3. Check health endpoint
4. Monitor logs for issues
