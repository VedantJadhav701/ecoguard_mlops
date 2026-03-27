# Render Deployment Quick Reference

## Essential Commands

### Push Code & Auto-Deploy
```bash
git add .
git commit -m "Update model"
git push origin main
# ✨ Automatically deploys to Render in ~10 minutes
```

### Check API Status
```bash
# Health check
curl https://ecoguard-api.onrender.com/health

# Interactive docs
open https://ecoguard-api.onrender.com/docs

# API endpoint example
curl -X POST https://ecoguard-api.onrender.com/api/vision/detect \
  -F "file=@image.jpg"
```

### View Logs
```bash
# In browser
https://dashboard.render.com/services

# Watch real-time
# Dashboard → Your Service → Logs (auto-refreshing)
```

### Manual Redeploy
```bash
# Via Render Dashboard
1. Service page
2. More → Redeploy

# Or via curl (if you have deploy hook)
curl -X POST https://api.render.com/deploy/srv_xxx?key=yyy
```

### Environment Variables
```bash
# Add/update in Render Dashboard
Settings → Environment → Add Variable

# Variables for EcoGuard
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=<your-key>
CORS_ORIGINS=https://yourdomain.com
MLFLOW_TRACKING_URI=<your-mlflow-url>
```

## GitHub Actions Workflows

### View Deployment Status
```bash
# In browser
https://github.com/yourusername/ecoguard/actions

# Or via GitHub CLI
gh run list --branch main
```

### Watch Live Deployment
```bash
# GitHub Actions → Deploy to Render workflow
# See:
# ✅ Tests passing
# ✅ Render webhook triggered
# ✅ Health check verifying
```

## Troubleshooting

### Service Won't Build
```bash
# Check what failed
1. Render Dashboard → Logs
2. Look for error messages
3. Common issues:
   - Missing requirement in requirements.txt
   - Model files too large
   - Python version mismatch

# Fix: Update code locally, push again
git push origin main
```

### Service Not Responding
```bash
# Check if running
curl https://ecoguard-api.onrender.com/health

# Check Render dashboard
1. Service page
2. Status should be "Running"
3. Check Logs for errors

# Restart if needed
1. Dashboard → More → Restart Service
```

### Models Not Loading
```bash
# Check logs
1. Render Dashboard → Logs
2. Look for import errors
3. Check if model files exist

# Verify locally first
python predictor.py  # Test model loading
```

### Slow Startup
```bash
# First deploy: 5-10 minutes (downloads dependencies, models)
# Subsequent: 1-3 minutes (just code update)

# Speed tip: Cache Docker layers
# Smaller requirements.txt → faster builds
```

## Performance Monitoring

### Response Time
```bash
# Time a request
time curl https://ecoguard-api.onrender.com/health

# Should be < 100ms for health check
```

### Model Inference Speed
```bash
# Via API docs at:
https://ecoguard-api.onrender.com/docs

# Click "Try it out" on endpoints
# Watch execution time
```

### View Metrics
```bash
1. Render Dashboard
2. Your Service
3. Metrics tab
4. See CPU, RAM, Requests
```

## Deployment Process

### What Happens When You Push

```
1. You: git push origin main (2 sec)
   ↓
2. GitHub: Receives push (1 sec)
   ↓
3. Actions: Clones repo, runs tests (2-5 min)
   ↓
4. Actions: Success → Triggers Render webhook (1 sec)
   ↓
5. Render: Receives webhook, starts build (1 sec)
   ↓
6. Render: pip install requirements (1-3 min)
   ↓
7. Render: Start uvicorn server (5-10 sec)
   ↓
8. Render: Load YOLO, weight, lifestyle models (10-30 sec)
   ↓
9. Actions: Verify health endpoint (1 min)
   ↓
10. ✅ Live! (Total: ~7-13 minutes)
```

## GitHub Secrets Check

```bash
# List your secrets (names only, not values)
gh secret list

# Should include:
RENDER_DEPLOY_HOOK
RENDER_SERVICE_URL

# If missing, add via:
# GitHub → Repo Settings → Secrets → New secret
```

## Common Tasks

| Task | How |
|------|-----|
| Check logs | Dashboard → Logs |
| Restart service | Dashboard → More → Restart |
| Update env var | Dashboard → Settings → Environment |
| View metrics | Dashboard → Metrics |
| Redeploy | Dashboard → More → Redeploy |
| Test API | https://service/docs |
| Check health | https://service/health |
| View deployment status | GitHub Actions tab |

## If Something Breaks

```bash
# Option 1: Rollback to previous version
Render Dashboard → Deployments → Click previous → Redeploy

# Option 2: Fix code and push
git add .
git commit -m "Fix issue"
git push origin main
# Auto-redeploys

# Option 3: Manual redeploy
curl -X POST $RENDER_DEPLOY_HOOK
```

## Performance Checklist

- ✅ Health check < 100ms
- ✅ Vision detection < 500ms  
- ✅ Weight estimation < 200ms
- ✅ API docs loading
- ✅ All models loaded
- ✅ No error logs
- ✅ CPU < 80%
- ✅ Memory < 80%

## Cost Estimation

```
Free Tier:
- $0/month
- Perfect for testing
- May sleep if inactive

Starter ($12/month):
- Guaranteed uptime
- Better for production
- Consistent performance
```

## Key Differences from Kubernetes

```
❌ Kubernetes approach:
- Complex setup (2+ hours)
- Requires cluster access
- Manual scaling config
- More infrastructure knowledge

✅ Render approach:
- Simple setup (10 minutes)
- GitHub connected
- Auto-scaling built-in
- Minimal ops knowledge
```

## Next Steps

1. **First Time**: Follow [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
2. **GitHub Secrets**: Follow [RENDER_SECRETS_SETUP.md](RENDER_SECRETS_SETUP.md)
3. **Push Code**: `git push origin main`
4. **Watch Deploy**: GitHub Actions → deploy-render workflow
5. **Verify**: https://ecoguard-api.onrender.com/health
6. **Test API**: https://ecoguard-api.onrender.com/docs

## Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **API Docs**: https://service-name.onrender.com/docs
- **GitHub Actions**: https://github.com/yourusername/ecoguard/actions
- **Render Docs**: https://render.com/docs
- **Our guides**: RENDER_*.md files

## Pro Tips

💡 **Tip 1**: Keep requirements.txt minimal for faster builds
💡 **Tip 2**: Use caching in GitHub Actions
💡 **Tip 3**: Check logs immediately if deployment fails
💡 **Tip 4**: Test locally with same Python version
💡 **Tip 5**: Use Render's free tier for development, Starter for production

---

**Keep this file handy for quick reference!** 🚀
