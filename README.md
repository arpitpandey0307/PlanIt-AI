# PlanIt AI

AI-powered event planning assistant for weddings, birthdays, and community events.

## Live Demo
🔗 **https://planit-ai-frontend.onrender.com**

## Features
- Smart budget allocation
- Backward-planned timelines
- Vendor checklists
- AI-generated theme ideas

## Tech Stack
- **Frontend:** React + TypeScript + Vite
- **Backend:** FastAPI + Python
- **AI:** Google Gemini API
- **Deploy:** Render

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key

### Installation
```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install

# Environment
cp .env.example .env
# Add your GOOGLE_API_KEY
```

### Run Locally
```bash
# Terminal 1 - Backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend  
cd frontend && npm run dev
```

Open http://localhost:5173

## Environment Variables
- `GOOGLE_API_KEY` - Required (get from [Google AI Studio](https://aistudio.google.com/))
- `PORT` - Optional (default: 8000)
- `FRONTEND_URL` - Optional (default: http://localhost:5173)

## Deploy

Uses `render.yaml` for one-click deployment to Render.

1. Fork this repo
2. Connect to Render
3. Add `GOOGLE_API_KEY` environment variable
4. Deploy

## License
MIT

---

**PlanIt AI** - Plan smarter, celebrate better ✨
