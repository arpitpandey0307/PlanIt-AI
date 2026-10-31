# 🚀 Deployment Guide - PlanIt AI

Complete guide to deploy your event planner application to production.

---

## 📋 Table of Contents

1. [Quick Deployment Options](#quick-deployment-options)
2. [Option 1: Vercel (Recommended - Free)](#option-1-vercel-recommended)
3. [Option 2: Google Cloud Run](#option-2-google-cloud-run)
4. [Option 3: Render (Free Tier)](#option-3-render)
5. [Option 4: Railway](#option-4-railway)
6. [Environment Variables Setup](#environment-variables-setup)
7. [Post-Deployment Checklist](#post-deployment-checklist)

---

## 🎯 Quick Deployment Options

| Platform | Cost | Difficulty | Build Time | Best For |
|----------|------|------------|------------|----------|
| **Vercel** | Free | ⭐ Easy | ~3 min | Frontend + Serverless Backend |
| **Render** | Free | ⭐⭐ Medium | ~5 min | Full-stack with free tier |
| **Railway** | $5/month | ⭐ Easy | ~3 min | Quick deployment |
| **Google Cloud Run** | Pay-as-you-go | ⭐⭐⭐ Advanced | ~10 min | Scalable production |

---

## Option 1: Vercel (Recommended) ⭐

**Best for:** Quick deployment, free hosting, automatic HTTPS

### Step 1: Prepare Backend for Serverless

Create a serverless API directory:

```bash
# In your project root
mkdir api
```

Create `api/index.py`:

```python
from backend.app.main import app

# Vercel serverless handler
def handler(request):
    return app(request)
```

### Step 2: Create `vercel.json`

Create in project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    },
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/app/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/dist/$1"
    }
  ],
  "env": {
    "GOOGLE_API_KEY": "@google_api_key"
  }
}
```

### Step 3: Deploy to Vercel

**Option A: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: planit-ai
# - Which directory? ./
# - Override settings? No

# Add environment variable
vercel env add GOOGLE_API_KEY production
# Paste your API key when prompted

# Deploy to production
vercel --prod
```

**Option B: Using Vercel Web Interface**

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Import Project"
4. Select your `PlanIt-AI` repository
5. Configure:
   - Framework Preset: Vite
   - Root Directory: `./`
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`
6. Add Environment Variable:
   - Key: `GOOGLE_API_KEY`
   - Value: Your Gemini API key
7. Click "Deploy"

**Your app will be live at:** `https://planit-ai.vercel.app`

---

## Option 2: Google Cloud Run

**Best for:** Scalable production deployment, containerized apps

### Prerequisites

- Google Cloud account ([Free $300 credit](https://cloud.google.com/free))
- Google Cloud SDK installed

### Step 1: Install Google Cloud SDK

**Windows:**
Download and install from: https://cloud.google.com/sdk/docs/install

**Verify installation:**
```bash
gcloud --version
```

### Step 2: Setup Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create planit-ai-prod --name="PlanIt AI Production"

# Set as current project
gcloud config set project planit-ai-prod

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Step 3: Build and Deploy

```bash
# Navigate to your project
cd "c:\Users\ARPIT PANDEY\Pictures\Event"

# Build and deploy in one command
gcloud run deploy planit-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_API_KEY_HERE

# Or deploy using our Dockerfile
gcloud builds submit --tag gcr.io/planit-ai-prod/planit-ai
gcloud run deploy planit-ai \
  --image gcr.io/planit-ai-prod/planit-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=YOUR_API_KEY_HERE
```

**Your app will be live at:** `https://planit-ai-xxxxx.run.app`

### Step 4: Set up Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service planit-ai \
  --domain planit.yourdomain.com \
  --region us-central1
```

---

## Option 3: Render

**Best for:** Free tier, easy setup, PostgreSQL included

### Step 1: Prepare for Render

Create `render.yaml` in project root:

```yaml
services:
  # Backend Service
  - type: web
    name: planit-ai-backend
    env: python
    region: oregon
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: FRONTEND_URL
        value: https://planit-ai-frontend.onrender.com
    healthCheckPath: /healthz

  # Frontend Service
  - type: web
    name: planit-ai-frontend
    env: static
    region: oregon
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: ./frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_URL
        value: https://planit-ai-backend.onrender.com
```

### Step 2: Deploy to Render

**Using Render Dashboard:**

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Blueprint"
4. Connect your `PlanIt-AI` repository
5. Render will detect `render.yaml` and create services
6. Add environment variable:
   - Go to Backend service → Environment
   - Add: `GOOGLE_API_KEY` = Your API key
7. Click "Apply" and wait for deployment

**Your app will be live at:**
- Backend: `https://planit-ai-backend.onrender.com`
- Frontend: `https://planit-ai-frontend.onrender.com`

---

## Option 4: Railway

**Best for:** Fastest deployment, developer-friendly

### Step 1: Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `PlanIt-AI` repository
5. Railway will auto-detect and deploy

### Step 2: Configure Environment

1. Click on your project
2. Go to "Variables" tab
3. Add:
   ```
   GOOGLE_API_KEY=your_api_key_here
   PORT=8000
   ```
4. Redeploy if needed

### Step 3: Configure Domains

Railway provides automatic domains:
- Backend: `https://planit-ai-backend-production.up.railway.app`
- Frontend: Configure in settings

**Your app will be live at:** `https://your-app.up.railway.app`

---

## 🔐 Environment Variables Setup

### Required Variables for All Platforms

```bash
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  # Your Gemini API key
PORT=8000                                              # Backend port
FRONTEND_URL=https://your-frontend-url.com             # For CORS
ENVIRONMENT=production                                 # Environment
```

### How to Add Environment Variables

**Vercel:**
```bash
vercel env add GOOGLE_API_KEY production
```

**Google Cloud Run:**
```bash
gcloud run services update planit-ai \
  --set-env-vars GOOGLE_API_KEY=your_key
```

**Render:**
- Dashboard → Service → Environment → Add Variable

**Railway:**
- Project → Variables → New Variable

---

## 🎨 Frontend Configuration

Update API URL for production:

### Create `frontend/.env.production`

```bash
VITE_API_URL=https://your-backend-url.com
```

### Update `frontend/src/App.tsx`

Replace:
```typescript
const API_BASE = 'http://localhost:8000/api'
```

With:
```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
```

---

## 📝 Post-Deployment Checklist

### ✅ Security

- [ ] API key added to environment variables (not in code)
- [ ] HTTPS enabled (automatic on most platforms)
- [ ] CORS configured for production domain
- [ ] Rate limiting active
- [ ] Security headers configured

### ✅ Functionality

- [ ] Backend health check works: `/healthz`
- [ ] API documentation accessible: `/docs`
- [ ] Can create event from UI
- [ ] Budget generation works
- [ ] Timeline displays correctly
- [ ] Vendor checklist loads
- [ ] Ideas generation works
- [ ] Chat functionality works

### ✅ Performance

- [ ] Page loads under 3 seconds
- [ ] API responses under 2 seconds
- [ ] Frontend bundle optimized
- [ ] Images compressed
- [ ] Caching configured

### ✅ Monitoring

- [ ] Error tracking setup (optional)
- [ ] Analytics added (optional)
- [ ] Uptime monitoring (optional)

---

## 🔧 Troubleshooting

### Issue: API Key Not Working

**Solution:**
```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Test locally first
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"
```

### Issue: CORS Errors

**Solution:** Update `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.com", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Build Fails

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Check Node version
node --version    # Should be 18+

# Clear caches
rm -rf node_modules package-lock.json
npm install
```

### Issue: App Crashes on Start

**Solution:**
```bash
# Check logs
# Vercel: vercel logs
# Render: Dashboard → Logs
# Railway: Dashboard → Deployments → Logs

# Common fixes:
# 1. Ensure all dependencies in requirements.txt
# 2. Check PORT environment variable
# 3. Verify API key is set
```

---

## 💰 Cost Estimates

### Vercel
- **Free tier:** 100GB bandwidth, 100 builds/month
- **Pro:** $20/month (unlimited builds)

### Google Cloud Run
- **Free tier:** 2 million requests/month
- **Typical cost:** $5-20/month for small apps

### Render
- **Free tier:** 750 hours/month (enough for 1 app)
- **Starter:** $7/month per service

### Railway
- **Free:** $5 credit/month
- **Pro:** $20/month (usage-based)

---

## 🎯 Recommended Deployment Strategy

### For Demo/Testing:
✅ **Use Vercel** - Free, fast, reliable

### For Production:
✅ **Use Google Cloud Run** - Scalable, pay-as-you-go

### For Learning:
✅ **Try all platforms** - Each has unique features

---

## 📱 Mobile PWA (Optional)

Make your app installable on mobile:

### Create `frontend/public/manifest.json`

```json
{
  "name": "PlanIt AI - Event Planner",
  "short_name": "PlanIt AI",
  "description": "AI-powered celebration and event planner",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#8b5cf6",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Link in `frontend/index.html`:
```html
<link rel="manifest" href="/manifest.json">
```

---

## 🎉 Quick Start Commands

### Deploy to Vercel (Fastest)
```bash
npm install -g vercel
vercel login
vercel
vercel env add GOOGLE_API_KEY production
vercel --prod
```

### Deploy to Railway (Easiest)
```bash
# Just push to GitHub, connect on railway.app
git push origin main
# Then connect repo on Railway dashboard
```

### Deploy to Google Cloud Run (Most Powerful)
```bash
gcloud run deploy planit-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 📞 Support

If you encounter issues:

1. Check platform-specific logs
2. Verify environment variables
3. Test locally first
4. Check GitHub Issues: https://github.com/arpitpandey0307/PlanIt-AI/issues

---

## 🎊 Next Steps After Deployment

1. ✅ Test all features on production URL
2. ✅ Share your demo link with users
3. ✅ Add deployment URL to README
4. ✅ Monitor logs and performance
5. ✅ Celebrate! 🎉

---

**Choose your deployment platform and follow the guide above. Good luck!** 🚀
