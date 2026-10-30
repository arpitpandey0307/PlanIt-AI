# Architecture Documentation

## System Overview

PlanIt AI is a full-stack web application that uses a **hybrid decision-making architecture**: deterministic code handles calculations and constraints, while GenAI provides creative content and natural language understanding.

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│           React Frontend (Vite + TS)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Intake  │  │Dashboard │  │   Chat   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────┬────────────────────────────┘
                     │ REST + JSON
┌────────────────────▼────────────────────────────┐
│           FastAPI Backend (Python)               │
│  ┌──────────────────────────────────────────┐  │
│  │         API Layer (Routes)                │  │
│  └──────────────────┬────────────────────────┘  │
│  ┌──────────────────▼────────────────────────┐  │
│  │      Decision Engine (Deterministic)      │  │
│  │  • Budget allocation rules                │  │
│  │  • Timeline backward planning             │  │
│  │  • Feasibility validation                 │  │
│  └──────────────────┬────────────────────────┘  │
│  ┌──────────────────▼────────────────────────┐  │
│  │         AI Agents (LLM-powered)           │  │
│  │  • Intake: Profile extraction             │  │
│  │  • Ideas: Theme & menu suggestions        │  │
│  │  • Chat: Conversational refinement        │  │
│  └──────────────────┬────────────────────────┘  │
│  ┌──────────────────▼────────────────────────┐  │
│  │         LLM Client (Gemini API)           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Component Responsibilities

### Frontend (React + TypeScript)

- **Intake Flow**: Multi-step wizard for event creation
- **Dashboard**: Tabbed interface showing budget, timeline, vendors, ideas
- **Chat Panel**: Conversational interface for plan refinement
- **Accessibility**: WCAG 2.1 AA compliant, keyboard navigation, screen reader support

### Backend (FastAPI + Python)

#### API Layer (`app/api/`)
- **events.py**: CRUD operations, plan generation, chat endpoint
- **health.py**: Health check for monitoring
- Security headers, CORS, rate limiting

#### Decision Engine (`app/engine/`)
- **budget.py**: Budget allocation by event type, context-aware adjustments
- **timeline.py**: Backward planning from event date, task generation
- **vendors.py**: Vendor category selection based on event profile
- **All deterministic**: No LLM calls, fully testable, token-free

#### AI Agents (`app/agents/`)
- **intake.py**: Extract structured profile from free text
- **ideas.py**: Generate themes, menu, activities, invitations
- Uses LLM for creativity, falls back to templates if unavailable

#### LLM Client (`app/llm/`)
- **client.py**: Wrapper for Google Gemini API
- **FakeLLMClient**: Mock for testing without API key
- Handles timeouts, errors, fallback responses

#### Schemas (`app/schemas/`)
- **Pydantic models**: EventProfile, Budget, Timeline, Vendors, Ideas
- **Validation**: Length limits, enum constraints, arithmetic checks
- **Type safety**: Full type hints throughout

## Data Flow

### Plan Generation Flow

1. **User submits event description** (free text or structured)
2. **Intake agent extracts** EventProfile (LLM or rule-based parsing)
3. **Profile stored** in events_store (in-memory, would be DB in production)
4. **Parallel generation**:
   - Budget: `generate_budget(profile)` → applies rules, calculates amounts
   - Timeline: `generate_timeline(profile)` → backward plans from event date
   - Vendors: `generate_vendor_checklist(profile)` → selects categories
   - Ideas: `generate_ideas(profile, llm)` → LLM generates themes/suggestions
5. **Validation**: Budget must sum to total, tasks must have valid dates
6. **Response streamed** to frontend section by section

### Chat Refinement Flow

1. **User sends chat message**: "Reduce budget by 20%"
2. **Intent detection**: Simple pattern matching in message
3. **Profile update**: Modify budget_total, guest_count, venue_type, etc.
4. **Selective regeneration**: Only affected sections regenerated
5. **Diff calculation**: Before/after comparison sent to user
6. **Updated plan saved** and returned

## Security Architecture

### Input Validation
- **Pydantic schemas**: All inputs validated at API boundary
- **Length limits**: 200 chars for names, 2000 for free text, 5000 for chat
- **Sanitization**: Remove `<script>`, `javascript:` from text fields
- **Enum constraints**: Only allowed event types, venue types, etc.

### Prompt Injection Defense
- **User text wrapped**: System instructions separate from user content
- **Strict output schemas**: LLM must return valid JSON or plain text
- **No code execution**: No tools that touch filesystem, network, shell
- **Content filtering**: Reject harmful/off-topic requests

### Secrets Management
- **Environment variables**: API keys never in code or repo
- **.env.example**: Template with dummy values
- **gitleaks**: CI check for leaked secrets
- **Docker secrets**: Use secrets mount in production

### API Security
- **Rate limiting**: 20 requests/minute per client (configurable)
- **CORS**: Locked to frontend origin only
- **Security headers**: CSP, X-Content-Type-Options, X-Frame-Options
- **HTTPS only**: Redirect HTTP in production
- **Generic errors**: No stack traces or key fragments in responses

## Performance Optimizations

### Backend
- **Code over LLM**: Budget/timeline use zero tokens
- **Parallel agents**: Ideas, vendors can run concurrently
- **Caching**: Results cached by profile hash (not implemented in v1)
- **Async I/O**: FastAPI async endpoints, non-blocking LLM calls
- **Timeouts**: 30s timeout on LLM calls, graceful fallback

### Frontend
- **Code splitting**: Route-level lazy loading
- **Bundle size**: Target < 200KB gzipped JavaScript
- **No heavy libraries**: React, axios only (no Material-UI, Ant Design)
- **Lazy rendering**: Only visible tabs load data
- **Debounced inputs**: Chat input debounced by 300ms

## Testing Strategy

### Unit Tests
- **Budget engine**: Sum validation, percentage checks, feasibility warnings
- **Timeline engine**: Date logic, dependency validation, phase grouping
- **Schemas**: Pydantic validation, edge cases, malformed inputs

### Integration Tests
- **API endpoints**: Create, generate, chat, update, export
- **LLM fallback**: Tests run with FakeLLMClient (no API key)
- **Golden scenarios**: One wedding, one birthday, one community event

### Accessibility Tests
- **jest-axe**: Automated WCAG checks on every page
- **Manual**: Keyboard-only walkthrough, screen reader testing

### CI Pipeline
- **Lint**: Ruff, mypy (Python), ESLint (TypeScript)
- **Test**: pytest, Vitest
- **Coverage**: 75% overall, 85% on engine
- **Size check**: Fail if repo > 10MB
- **Security audit**: pip-audit, npm audit, gitleaks

## Deployment

### Local Development
```bash
# Backend
python backend/app/main.py

# Frontend (separate terminal)
cd frontend && npm run dev
```

### Docker
```bash
docker build -t planit-ai .
docker run -p 8000:8000 -e GOOGLE_API_KEY=xxx planit-ai
```

### Cloud Run (Production)
- **Stateless**: No local storage, session data in DB
- **PORT env var**: Read from environment
- **Health check**: `/healthz` endpoint
- **Autoscaling**: 0-10 instances based on load
- **Secrets**: Stored in Secret Manager, mounted as env vars

## Future Enhancements

### v1.1
- **Browser storage**: Save multiple events locally
- **Shareable links**: Read-only plan sharing
- **Export formats**: ICS calendar, CSV budget, PDF plan
- **Hindi support**: Multilingual intake and UI

### v2
- **Database**: PostgreSQL for persistence
- **Authentication**: User accounts, saved plans
- **Real vendors**: Google Maps integration for local suggestions
- **Collaboration**: Multi-user plan editing
- **Reminders**: Email/SMS for upcoming tasks
- **Image generation**: Mood boards via Imagen

## Compliance

### WCAG 2.1 AA
- **Contrast**: 4.5:1 minimum, tested with Lighthouse
- **Keyboard**: All actions accessible without mouse
- **Screen reader**: Semantic HTML, ARIA labels, live regions
- **Motion**: Respects `prefers-reduced-motion`

### Data Privacy
- **Minimal collection**: Only event details, no PII stored
- **AI disclosure**: Clear notice that details sent to Gemini
- **Delete capability**: Full plan deletion via API
- **No selling**: User data never sold or shared

### Content Safety
- **Filtering**: Reject harmful, illegal, or discriminatory requests
- **Disclaimers**: Cost estimates marked as non-binding
- **Cultural respect**: Avoid stereotypes in suggestions

## Monitoring (Production)

- **Structured logging**: JSON logs with request IDs
- **Metrics**: Latency, token usage, error rate
- **Error tracking**: Sentry or Cloud Error Reporting
- **Health checks**: `/healthz` polled every 30s
- **Alerts**: Slack/email on high error rate or downtime
