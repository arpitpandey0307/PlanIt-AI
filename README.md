# PlanIt AI 🎉

> **AI-powered event planning assistant** for weddings, birthdays, and community events — built with Google Gemini API, FastAPI, and React.

## 🔗 Live Demo

**https://planit-ai-frontend.onrender.com**

---

## ✨ Features

### Core Capabilities
- **Smart Budget Allocation** — Context-aware budget breakdown with decision traces explaining _why_ each allocation was made. Adapts for outdoor venues, peak season pricing, and city-tier rates.
- **Backward-Planned Timelines** — Automatically generates a week-by-week planning checklist working backward from your event date. Detects short-notice events and compresses the timeline accordingly.
- **Vendor Checklists** — Curated vendor categories with booking lead times, questions to ask, and due-diligence checklists. Adds weather contingency vendors for outdoor events and transport for large gatherings.
- **AI-Generated Theme Ideas** — Personalized theme concepts with color palettes, menu suggestions, activity ideas, and invitation wording — powered by Google Gemini.
- **Chat-Based Plan Refinement** — Modify budgets, guest counts, and venue types through natural language conversation.

### Technical Highlights
- **Deterministic + AI Hybrid** — Budget, timeline, and vendor engines run without LLM calls (fast, predictable, testable). Only creative tasks (themes, ideas) use the Gemini API.
- **Decision Transparency** — Every budget allocation includes a `decision_trace` explaining the reasoning (e.g., "Peak season: venues book early at premium rates").
- **Feasibility Warnings** — Flags when budget-per-guest falls below typical city-tier minimums and suggests concrete fixes.
- **Context-Aware Rules** — Adjusts for city tier (Tier 1/2/3), peak season, venue type, audience mix, and event scale.

---

## 🏗 Architecture

```
┌─────────────┐     REST API      ┌──────────────────────┐
│   React +   │ ──────────────▶   │    FastAPI Backend    │
│  TypeScript  │                   │                      │
│   (Vite)    │ ◀──────────────   │  ┌────────────────┐  │
└─────────────┘     JSON          │  │  Intake Agent   │  │
                                  │  │  (LLM + Rules)  │  │
                                  │  ├────────────────┤  │
                                  │  │  Budget Engine  │  │
                                  │  │  (Deterministic)│  │
                                  │  ├────────────────┤  │
                                  │  │ Timeline Engine │  │
                                  │  │ (Backward Plan) │  │
                                  │  ├────────────────┤  │
                                  │  │ Vendor Engine   │  │
                                  │  │ (Template-Based)│  │
                                  │  ├────────────────┤  │
                                  │  │  Ideas Agent    │  │
                                  │  │  (Gemini API)   │  │
                                  │  └────────────────┘  │
                                  └──────────────────────┘
```

## 🛡 Security

- **Rate limiting** (per-IP, sliding window)
- **Input sanitization** (XSS prevention, injection protection)
- **Security headers** (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- **CORS** with explicit origin whitelist (no wildcards)
- **Input validation** via Pydantic schemas with strict constraints
- **No API key exposure** — keys stay server-side only

## ♿ Accessibility

- **WCAG 2.1 AA** compliant structure
- Skip-to-content link
- Semantic HTML5 (`header`, `main`, `footer`, `section`, `article`)
- ARIA roles (`tablist`, `tab`, `tabpanel`, `progressbar`, `alert`, `group`)
- Keyboard navigation (arrow keys for tabs, Enter/Space for cards)
- Screen-reader support (`.sr-only` class, `aria-label`, `aria-live`)
- `prefers-reduced-motion` support
- `forced-colors` (Windows High Contrast) support
- Focus-visible outlines

## Tech Stack

| Layer       | Technology                     |
|-------------|--------------------------------|
| **Frontend** | React 18 + TypeScript + Vite  |
| **Backend**  | FastAPI + Python 3.10+        |
| **AI**       | Google Gemini API (Flash/Pro) |
| **Testing**  | pytest + Vitest               |
| **Deploy**   | Render (render.yaml)          |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Gemini API key ([Get one here](https://aistudio.google.com/))

### Installation

```bash
# Backend
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install

# Environment
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
```

### Run Locally

```bash
# Terminal 1 - Backend
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

Open http://localhost:5173

### Run Tests

```bash
# Backend tests (with coverage)
cd backend && python -m pytest

# Frontend tests
cd frontend && npx vitest run
```

---

## 📡 API Endpoints

| Method   | Endpoint                              | Description                |
|----------|---------------------------------------|----------------------------|
| `GET`    | `/healthz`                            | Health check               |
| `POST`   | `/api/events/`                        | Create event from text     |
| `GET`    | `/api/events/{id}`                    | Get event plan             |
| `POST`   | `/api/events/{id}/generate`           | Generate full plan         |
| `POST`   | `/api/events/{id}/generate/{section}` | Regenerate a section       |
| `POST`   | `/api/events/{id}/chat`               | Chat to refine plan        |
| `PATCH`  | `/api/events/{id}/tasks/{task_id}`    | Update task status         |
| `PATCH`  | `/api/events/{id}/budget`             | Update actual spend        |
| `GET`    | `/api/events/{id}/export?format=csv`  | Export budget as CSV       |
| `DELETE` | `/api/events/{id}`                    | Delete event               |

## Environment Variables

| Variable             | Required | Default                  | Description                        |
|----------------------|----------|--------------------------|------------------------------------|
| `GOOGLE_API_KEY`     | Yes      | —                        | Gemini API key                     |
| `PORT`               | No       | `8000`                   | Backend port                       |
| `ENVIRONMENT`        | No       | `development`            | `development` / `production`       |
| `FRONTEND_URL`       | No       | `http://localhost:5173`  | Allowed CORS origin                |
| `RATE_LIMIT_PER_MINUTE` | No   | `20`                     | Max requests per IP per minute     |

## Deploy

Uses `render.yaml` for one-click deployment to Render.

1. Fork this repo
2. Connect to Render
3. Add `GOOGLE_API_KEY` environment variable
4. Deploy

## License

MIT

---

**PlanIt AI** — Plan smarter, celebrate better ✨
