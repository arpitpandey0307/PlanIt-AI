# Setup Instructions

## Quick Start (3 Commands)

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install Node dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your Google Gemini API key
# Get your API key from: https://aistudio.google.com/
```

Edit `.env` file:
```
GOOGLE_API_KEY=your_actual_api_key_here
PORT=8000
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
python backend/app/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open your browser to **http://localhost:5173**

## Detailed Setup

### Prerequisites

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **Node.js 18 or higher** ([Download](https://nodejs.org/))
- **Google Gemini API Key** ([Get API Key](https://aistudio.google.com/))

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Event
```

#### 2. Backend Setup

```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Verify installation
python -c "import fastapi; import google.generativeai; print('✓ Dependencies installed')"
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list react
```

#### 4. Environment Configuration

```bash
# Copy template
copy .env.example .env

# Edit .env with your favorite text editor
notepad .env
```

Required variables:
- `GOOGLE_API_KEY`: Your Gemini API key (required)
- `PORT`: Backend port (default: 8000)
- `FRONTEND_URL`: Frontend URL for CORS (default: http://localhost:5173)

#### 5. Run the Application

**Option A: Manual (Two Terminals)**

Terminal 1 (Backend):
```bash
python backend/app/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.0.8  ready in xxx ms
➜  Local:   http://localhost:5173/
```

**Option B: Using Make (if you have make installed)**

```bash
make install    # Install all dependencies
make dev        # Run backend (frontend separate)
```

### Verifying the Setup

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/healthz
   ```
   Expected response: `{"status":"healthy","service":"planit-ai","version":"1.0.0"}`

2. **Frontend Access**
   - Open http://localhost:5173 in your browser
   - You should see the "PlanIt AI" landing page
   - Try creating a test event

3. **API Documentation**
   - Open http://localhost:8000/docs
   - Interactive API documentation (Swagger UI)

## Running Tests

### Backend Tests

```bash
cd backend
pytest --cov=app tests/
```

Expected output:
```
==================== test session starts ====================
collected X items

tests/test_budget.py ........                         [100%]

---------- coverage: platform windows ----------
Name                     Stmts   Miss  Cover
--------------------------------------------
app/engine/budget.py       120     12    90%
...
TOTAL                      450     45    90%
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Linting

```bash
# Backend
cd backend
ruff check app/
mypy app/ --ignore-missing-imports

# Frontend
cd frontend
npm run lint
```

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Build image
docker build -t planit-ai .

# Run container
docker run -p 8000:8000 -e GOOGLE_API_KEY=your_key_here planit-ai
```

Access at http://localhost:8000

## Troubleshooting

### "Module not found" errors

**Problem:** Import errors when running backend

**Solution:**
```bash
# Make sure you're in the right directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+
```

### "Port already in use"

**Problem:** `Address already in use` error

**Solution:**
```bash
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or change port in .env
PORT=8001
```

### "API key invalid" errors

**Problem:** 401 Unauthorized from Gemini API

**Solution:**
1. Verify your API key at https://aistudio.google.com/
2. Check `.env` file has correct key (no quotes, no spaces)
3. Restart backend after changing `.env`

### Frontend not connecting to backend

**Problem:** Network errors in browser console

**Solution:**
1. Check backend is running: http://localhost:8000/healthz
2. Check CORS settings in `.env`: `FRONTEND_URL=http://localhost:5173`
3. Clear browser cache
4. Check browser console for specific error messages

### "Cannot find module 'react'" in frontend

**Problem:** npm dependencies not installed

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Development Tips

### Hot Reload

- **Backend**: Automatic reload on file changes (uvicorn --reload)
- **Frontend**: Instant HMR with Vite

### API Testing

Use the interactive docs at http://localhost:8000/docs to:
- Test endpoints without writing code
- See request/response schemas
- Try different payloads

### Debugging

**Backend:**
```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use print debugging
print(f"Profile: {profile}")
```

**Frontend:**
```typescript
// Browser DevTools
console.log('Event data:', plan)
debugger;  // Pauses execution
```

### Environment-Specific Settings

Create multiple `.env` files:
- `.env.development` (local development)
- `.env.production` (production deployment)
- `.env.test` (testing)

## Next Steps

1. **Try the demo scenarios** from README.md
2. **Read ARCHITECTURE.md** to understand the system
3. **Run the test suite** to verify everything works
4. **Make your first change** and see hot reload in action
5. **Check out the API docs** at http://localhost:8000/docs

## Getting Help

- **Documentation**: See README.md and ARCHITECTURE.md
- **Issues**: Check existing issues on GitHub
- **API Reference**: http://localhost:8000/docs when server is running

## Production Deployment

For deploying to production (Cloud Run, Heroku, etc.), see:
- Dockerfile for containerization
- .github/workflows/ci.yml for CI/CD pipeline
- README.md for deployment instructions
