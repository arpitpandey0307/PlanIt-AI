# 🚀 Quick Start Guide

Get PlanIt AI running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:

- [ ] **Python 3.10+** installed
  ```bash
  python --version
  ```
  
- [ ] **Node.js 18+** installed
  ```bash
  node --version
  ```

- [ ] **Google Gemini API Key**
  - Get it FREE at: https://aistudio.google.com/
  - Click "Get API Key" → "Create API Key"

## Installation (3 Steps)

### Step 1: Install Dependencies

**Windows:**
```bash
# Double-click or run:
install.bat
```

**Mac/Linux:**
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node dependencies
cd frontend && npm install && cd ..
```

### Step 2: Add Your API Key

1. Open the `.env` file (created by install script)
2. Replace `your_api_key_here` with your actual Gemini API key:
   ```
   GOOGLE_API_KEY=AIzaSyC...your_actual_key_here
   ```
3. Save the file

### Step 3: Run the Application

**Windows:**

Open TWO terminal windows:

**Terminal 1 (Backend):**
```bash
start.bat
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

**Terminal 2 (Frontend):**
```bash
start-frontend.bat
```
Wait for: `Local: http://localhost:5173/`

**Mac/Linux:**

Open TWO terminal windows:

**Terminal 1 (Backend):**
```bash
python backend/app/main.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend && npm run dev
```

## Open the App

**Browser:** http://localhost:5173

You should see:
```
🎉 PlanIt AI
Your AI-powered celebration planner
```

## Try It Out!

### Example 1: Plan a Wedding

1. Click **"Wedding"**
2. Enter: `Plan a 2-day wedding for 250 guests in Jaipur in February, budget 15 lakh, royal theme`
3. Click **"Create Plan"**
4. Wait 10-20 seconds
5. Explore the generated plan!

### Example 2: Plan a Birthday

1. Click **"Birthday"**
2. Enter: `100-person birthday party in Delhi under 50k on December 15`
3. Click **"Create Plan"**
4. See budget, timeline, vendor checklist, and theme ideas!

### Example 3: Plan a Community Event

1. Click **"Community Event"**
2. Enter: `Community Diwali mela for 500 people, outdoor, budget 2 lakh`
3. Click **"Create Plan"**
4. Review safety tasks, permits, and crowd management!

## What You'll See

✅ **Budget** - Category-wise allocation with percentages
✅ **Timeline** - Backward-planned tasks from event date  
✅ **Vendors** - Checklist with questions and due diligence  
✅ **Ideas** - AI-generated themes, menus, activities  
✅ **Overview** - Dashboard with key metrics

## Troubleshooting

### "Module not found" error

```bash
# Reinstall Python dependencies
pip install -r backend/requirements.txt
```

### "Port already in use"

```bash
# Windows: Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux: Kill process
lsof -ti:8000 | xargs kill -9
```

### API key errors

1. Check your `.env` file
2. Verify API key at https://aistudio.google.com/
3. Restart backend after changing `.env`

### Frontend won't load

1. Check backend is running: http://localhost:8000/healthz
2. Check frontend terminal for errors
3. Try: `cd frontend && rm -rf node_modules && npm install`

## Testing Without API Key

The app works WITHOUT an API key using template-based planning:

1. Leave `GOOGLE_API_KEY` empty in `.env`
2. Run the app normally
3. Plans will be generated using rule-based logic + templates
4. Budget and timeline work fully, ideas use preset themes

## Next Steps

📖 **Read the docs:**
- [README.md](README.md) - Full documentation
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [SETUP.md](SETUP.md) - Detailed setup guide

🧪 **Run tests:**
```bash
cd backend && pytest --cov=app tests/
```

🔧 **Explore the code:**
- `backend/app/engine/` - Decision logic
- `backend/app/agents/` - AI agents
- `frontend/src/App.tsx` - React UI

🚀 **Deploy:**
```bash
docker build -t planit-ai .
docker run -p 8000:8000 -e GOOGLE_API_KEY=xxx planit-ai
```

## Features to Try

- ✨ Create events for all 3 types: Wedding, Birthday, Community
- 💰 Check budget breakdown with contingency
- 📅 Review backward-planned timeline
- 🏪 Explore vendor checklists with questions
- 💡 Browse AI-generated theme ideas
- 📊 View event countdown and task progress

## Support

- **Issues?** Check SETUP.md Troubleshooting section
- **Questions?** See README.md or ARCHITECTURE.md
- **API Docs:** http://localhost:8000/docs (when running)

---

## One-Line Install & Run

If you're comfortable with command line:

```bash
# Install everything
pip install -r backend/requirements.txt && cd frontend && npm install && cd ..

# Add your API key to .env (edit manually)

# Run backend (Terminal 1)
python backend/app/main.py

# Run frontend (Terminal 2)
cd frontend && npm run dev
```

**Then open:** http://localhost:5173

---

**PlanIt AI** - Plan smarter, celebrate better! 🎉
