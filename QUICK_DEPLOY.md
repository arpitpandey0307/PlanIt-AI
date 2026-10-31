# ⚡ Quick Deploy Guide

Choose your deployment method:

---

## 🚀 Option 1: Vercel (Recommended - 5 minutes)

### Method A: Automated Script (Windows)

```bash
# Just run this!
deploy-vercel.bat
```

### Method B: Manual Steps

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
vercel

# 4. Add API key
vercel env add GOOGLE_API_KEY production
# (paste your API key when prompted)

# 5. Deploy to production
vercel --prod
```

**Done!** Your app will be live at `https://planit-ai-xxxxx.vercel.app`

---

## 🎨 Option 2: Render (No CLI needed - 5 minutes)

### Using Dashboard (Easiest!)

1. Go to **https://render.com** and sign up with GitHub
2. Click **"New +"** → **"Blueprint"**
3. Select your **PlanIt-AI** repository
4. Render will detect `render.yaml` and set up everything
5. Go to **Backend service** → **Environment**
6. Add variable:
   - Key: `GOOGLE_API_KEY`
   - Value: `[Your API key]`
7. Click **"Manual Deploy"** → **"Deploy latest commit"**

**Done!** Your app will be live at:
- Frontend: `https://planit-ai.onrender.com`
- Backend: `https://planit-ai-backend.onrender.com`

---

## 🚂 Option 3: Railway (Fastest - 2 minutes)

1. Go to **https://railway.app** and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select **PlanIt-AI** repository
4. Railway auto-detects and deploys
5. Click on your service → **"Variables"** tab
6. Add: `GOOGLE_API_KEY` = `[Your API key]`

**Done!** Your app will be live at `https://planit-ai.up.railway.app`

---

## 🎯 Recommended: Use Render

**Why?** 
- ✅ Free tier (no credit card needed)
- ✅ Automatic HTTPS
- ✅ Easy environment variables
- ✅ Pre-configured with `render.yaml`
- ✅ Great for demos

---

## 📝 After Deployment

1. **Test your live app:**
   - Try creating a wedding event
   - Check budget generation
   - Test timeline display
   - Verify ideas load

2. **Update GitHub with deployment URL:**
   ```bash
   # Edit README.md and add:
   ## 🌐 Live Demo
   [https://your-app-url.com](https://your-app-url.com)
   ```

3. **Share your app:**
   - Get the live URL
   - Share with your community
   - Test on mobile devices

---

## ⚠️ Important: Environment Variables

**All platforms need this:**
```
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Where to add:**
- **Vercel:** `vercel env add GOOGLE_API_KEY production`
- **Render:** Dashboard → Service → Environment → Add Variable
- **Railway:** Project → Variables → New Variable

---

## 🆘 Need Help?

**Common Issues:**

1. **Build fails?**
   - Check Node version (need 18+)
   - Check Python version (need 3.10+)
   - Clear cache: `rm -rf node_modules && npm install`

2. **App loads but no data?**
   - Verify API key is set
   - Check backend URL in frontend
   - Look at browser console for errors

3. **CORS errors?**
   - Update `FRONTEND_URL` in backend settings
   - Check `allow_origins` in `main.py`

---

## ✅ Deployment Checklist

Before sharing your app:

- [ ] App loads without errors
- [ ] Can create events (all 3 types)
- [ ] Budget displays correctly
- [ ] Timeline shows tasks
- [ ] Vendors list appears
- [ ] Ideas generate successfully
- [ ] Mobile responsive works
- [ ] HTTPS enabled (automatic)

---

**Choose a platform above and get your app live in 5 minutes!** 🚀
