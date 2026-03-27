# Render Deployment Secrets Setup

## Required Secrets for Render Deployment

Add these to your GitHub repository to enable automatic Render deployment.

## Secrets to Add

### 1. RENDER_DEPLOY_HOOK (Required)
**Purpose**: Trigger deployments from GitHub Actions

**How to get:**
1. Go to https://dashboard.render.com/services
2. Select your EcoGuard service
3. Settings → Deploy Hook
4. Copy the full webhook URL

**Example:**
```
https://api.render.com/deploy/srv_xxx?key=rnd_xxx
```

**Add to GitHub:**
- Go to your repo → Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `RENDER_DEPLOY_HOOK`
- Paste the URL

### 2. RENDER_SERVICE_URL (Recommended)
**Purpose**: Health check verification after deployment

**How to get:**
- From Render dashboard: Service URL (e.g., https://ecoguard-api.onrender.com)
- Or from service settings

**Add to GitHub:**
- Name: `RENDER_SERVICE_URL`
- Value: `https://your-service-name.onrender.com`

### 3. RENDER_API_KEY (Optional)
**Purpose**: Advanced API operations (monitoring, notifications)

**How to get:**
1. https://dashboard.render.com → Account Settings
2. API Keys
3. Create new key
4. Copy the key

**Add to GitHub:**
- Name: `RENDER_API_KEY`
- Value: Your API key

### 4. RENDER_SERVICE_ID (Optional)
**Purpose**: Alternative to deploy hook

**How to get:**
- From service URL in dashboard: `srv_xxxxx`
- Or from Settings → Service ID

**Add to GitHub:**
- Name: `RENDER_SERVICE_ID`
- Value: `srv_xxxxx`

## Environment Variables for Render Service

These go in your Render service, NOT GitHub secrets.

### In Render Dashboard

1. Go to your service
2. Settings → Environment
3. Add each variable:

| Variable | Value | Example |
|----------|-------|---------|
| `ENVIRONMENT` | production | production |
| `LOG_LEVEL` | INFO | INFO |
| `SECRET_KEY` | Random string | (generate: `openssl rand -hex 32`) |
| `CORS_ORIGINS` | Your domain | https://yourdomain.com |
| `MLFLOW_TRACKING_URI` | MLflow server | https://mlflow.example.com:5000 |
| `DATABASE_URL` | DB connection | postgresql://user:pass@host/db |

### Generate SECRET_KEY

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows PowerShell
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).Guid))
```

## Step-by-Step Setup

### 1. Create Render Deploy Hook

```bash
1. Log in to Render dashboard
2. Click on your service (ecoguard-api)
3. Settings → Deploy Hook
4. "Enable deploy hook"
5. Copy the URL
```

### 2. Add GitHub Secret

```bash
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. New repository secret
4. Name: RENDER_DEPLOY_HOOK
5. Value: Paste the webhook URL
6. Click Add secret
```

### 3. Verify Secret Works

Push a test commit:
```bash
git commit --allow-empty -m "Test Render deployment"
git push origin main
```

Watch:
- GitHub Actions: https://github.com/user/ecoguard/actions
- Render Dashboard: https://dashboard.render.com

## GitHub Actions Workflow

The workflow in `.github/workflows/deploy-render.yml`:

1. **Trigger**: Push to main branch or create tag
2. **Test**: Run tests, lint, type check
3. **Deploy**: Call Render webhook
4. **Verify**: Check health endpoint for 30 seconds
5. **Notify**: Report success/failure

## Troubleshooting

### Secret Not Found Error

```
"Secret not found"
```

**Fix:**
- Check secret name is exactly: `RENDER_DEPLOY_HOOK`
- Secrets are case-sensitive
- Wait 1-2 minutes after adding secret
- Refresh the actions page

### Deployment Webhook Not Triggering

```
"curl: (7) Failed to connect"
```

**Fix:**
1. Verify webhook URL is correct
2. Check URL doesn't have extra spaces
3. Confirm service exists in Render
4. Try manual curl:
   ```bash
   curl -X POST "https://api.render.com/deploy/srv_xxx?key=xxx"
   ```

### Health Check Timing Out

```
"Service failed to become healthy"
```

**Fix:**
1. Check API is running locally: `python -m uvicorn app:app`
2. Verify health endpoint: `curl localhost:8000/health`
3. Check models are loading
4. Increase timeout in workflow (currently 30 seconds, max 10 attempts)

### Build Fails on Render

**Common causes:**
- Missing requirements in `requirements.txt`
- Model files too large (free tier has 1GB limit)
- Python version incompatibility

**Fix:**
1. Test locally: `docker build .`
2. Add any missing dependencies
3. Check file sizes
4. Verify Python 3.10 compatibility

## Monitoring Deployments

### GitHub Actions

```
https://github.com/your-username/ecoguard/actions
```

Click "Deploy to Render" workflow to see:
- Test results
- Deployment status
- Health check results
- Any errors

### Render Dashboard

```
https://dashboard.render.com/services
```

View:
- Deployment status
- Build logs
- Runtime logs
- Service metrics
- Environment variables

## Security Best Practices

✅ **Do:**
- Use strong SECRET_KEY (32+ characters)
- Restrict CORS_ORIGINS to your domain
- Rotate API keys regularly
- Use environment variables for sensitive data
- Enable GitHub branch protection

❌ **Don't:**
- Commit secrets to GitHub
- Share deploy hooks publicly
- Use weak SECRET_KEY
- Allow CORS from *
- Store API keys in code

## Automatic Deployments

### Workflow Triggers

Deployment automatically runs on:

1. **Push to main**: Every commit to main branch
2. **Tags**: Creating version tags (v1.0.0, etc.)
3. **Manual**: Workflow dispatch from Actions tab

### Disable Automatic Deploy

If you want to require approval:

In `.github/workflows/deploy-render.yml`:
```yaml
# Change this:
if: github.ref == 'refs/heads/main'

# To require manual trigger:
if: github.event_name == 'workflow_dispatch'
```

## Testing Without Deploying

To run tests without deploying:

```bash
# Local testing
pytest tests/ -v

# or with GitHub CLI
gh workflow run tests.yml
```

## Performance Monitoring

After deployment, monitor:

```bash
# Check API response time
time curl https://ecoguard-api.onrender.com/health

# Monitor model inference
curl https://ecoguard-api.onrender.com/docs

# Check logs
# Via Render dashboard or:
gh api repos/yourusername/ecoguard/actions/runs
```

## Rollback Deployment

If deployment fails:

1. **Automatic**: Render keeps previous version
2. **Manual**: 
   - Render Dashboard → Deployments
   - Click previous successful deployment
   - Click "Redeploy"

## Next Steps

1. ✅ Add `RENDER_DEPLOY_HOOK` secret to GitHub
2. ✅ Configure environment variables in Render
3. ✅ Push to main branch
4. ✅ Watch automatic deployment
5. ✅ Verify health endpoint
6. ✅ Check API docs

## Quick Reference

| Task | Where |
|------|-------|
| Add secrets | GitHub repo → Settings → Secrets |
| View deployments | Render dashboard → Deployments |
| Check logs | Render → Logs or GitHub Actions |
| Update env vars | Render service → Settings → Environment |
| Manual deploy | Push to main or GitHub Actions dispatch |
| Health check | `https://service.onrender.com/health` |

## Support

- **Render Help**: https://render.com/support
- **GitHub Secrets Docs**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Our Docs**: See `RENDER_DEPLOYMENT_GUIDE.md`

---

**Setup complete!** Your Render deployment is now connected to GitHub. 🚀
