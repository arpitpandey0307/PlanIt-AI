# 🎯 Render Deployment - Step by Step

## ✅ Issue Fixed!

The `render.yaml` configuration error has been fixed and pushed to GitHub.

---

## 📋 Complete Deployment Steps

### Step 1: Retry on Render ✅

On the Render Blueprint page, click the **"Retry"** button or refresh the page.

The Blueprint should now load successfully without errors.

---

### Step 2: Review Configuration ✅

You should see two services:

1. **planit-ai-backend** (Python Web Service)
   - Region: Oregon
   - Plan: Free
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **planit-ai-frontend** (Static Site)
   - Plan: Free
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `./frontend/dist`

---

### Step 3: Click "Apply" ✅

Click the **"Apply"** button to create both services.

Render will now:
- Create backend service
- Create frontend service
- Start building both

---

### Step 4: Add API Key to Backend 🔑

**IMPORTANT:** You need to add your Gemini API key!

1. Wait for services to be created (30 seconds)
2. Click on **"planit-ai-backend"** service
3. Go to **"Environment"** tab (left sidebar)
4. Click **"Add Environment Variable"**
5. Add:
   ```
   Key:   GOOGLE_API_KEY
   Value: AIzaSyAQAb8RN6I4ZTxk_pwIAB3wNfxNpO9XJERgmyXk2H0R0P2YpKAyvA
   ```
6. Click **"Save Changes"**

The backend will automatically redeploy with the API key.

---

### Step 5: Wait for Deployment ⏱️

**Deployment takes 3-5 minutes:**

- Backend build: ~2 minutes
- Frontend build: ~1 minute
- Both will show "Live" when ready

**You can watch the logs:**
- Click on each service
- View real-time build logs
- Look for "Deploy succeeded" message

---

### Step 6: Get Your URLs 🌐

Once deployed, you'll have two URLs:

**Frontend (your main app):**
```
https://planit-ai-frontend.onrender.com
```

**Backend API:**
```
https://planit-ai-backend.onrender.com
```

---

## ✅ Verification Checklist

After deployment, test these:

### Backend Health Check
Visit: `https://planit-ai-backend.onrender.com/healthz`

Should return:
```json
{
  "status": "healthy",
  "service": "planit-ai",
  "version": "1.0.0"
}
```

### Backend API Docs
Visit: `https://planit-ai-backend.onrender.com/docs`

Should show FastAPI Swagger documentation.

### Frontend App
Visit: `https://planit-ai-frontend.onrender.com`

Should show your event planner app.

### Test Creating an Event

1. Open frontend URL
2. Click "Wedding" or "Birthday"
3. Enter event details
4. Click "Create Plan"
5. Verify budget, timeline, vendors, and ideas load

---

## 🎉 Success!

If all checks pass, your app is live!

**Share your URLs:**
- **App:** https://planit-ai-frontend.onrender.com
- **API:** https://planit-ai-backend.onrender.com

---

## 🆘 Troubleshooting

### Issue: Backend build fails

**Check logs for:**
- Python version issues → Render uses Python 3.11 by default
- Missing dependencies → All in `requirements.txt`

**Fix:** 
- Check build logs in Backend service
- Look for specific error messages

### Issue: Frontend build fails

**Check logs for:**
- Node version issues → Render uses Node 18
- npm install errors

**Fix:**
- Check build logs in Frontend service
- Verify `package.json` is correct

### Issue: API key not working

**Symptoms:**
- Frontend loads but no data
- "API key not found" errors in logs

**Fix:**
1. Go to Backend service → Environment
2. Verify `GOOGLE_API_KEY` is set
3. Check value has no extra spaces
4. Click "Save Changes" to redeploy

### Issue: CORS errors

**Symptoms:**
- Frontend loads
- Network errors in browser console
- "CORS policy blocked" errors

**Fix:**
Update `FRONTEND_URL` environment variable in backend:
1. Backend service → Environment
2. Update `FRONTEND_URL` to your actual frontend URL
3. Save and redeploy

### Issue: 404 errors on frontend routes

**Symptoms:**
- Home page works
- Refreshing other pages shows 404

**This is normal for static sites.**
The `render.yaml` includes rewrite rules to handle this.

---

## 📊 Monitoring Your App

### View Logs
- Click on each service
- Go to "Logs" tab
- See real-time application logs

### Check Metrics
- Go to "Metrics" tab
- View requests, response times, memory usage

### Auto-Deploy
Render automatically deploys when you push to GitHub!
- Push code → Render detects → Auto-deploys

---

## 💰 Free Tier Limits

Render Free tier includes:
- ✅ 750 hours/month (enough for 1 service running 24/7)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Auto-deploy from GitHub
- ⚠️ Services spin down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes ~30 seconds

**Note:** If you deploy both backend and frontend, backend may spin down when not in use. First request will be slower.

---

## 🚀 Next Steps

1. ✅ Test your live app thoroughly
2. ✅ Update README.md with your live URL
3. ✅ Share your app for PromptWars submission
4. ✅ Optional: Set up custom domain

---

## 📝 Update Your README

Add this to your GitHub README:

```markdown
## 🌐 Live Demo

- **Application:** https://planit-ai-frontend.onrender.com
- **API Documentation:** https://planit-ai-backend.onrender.com/docs

*Note: Free tier may take 30 seconds to wake up on first request*
```

---

**You're all set! Click "Retry" on Render and follow the steps above.** 🎉
