# Product Requirements Document: Celebration & Event Planner

**Event:** PromptWars Virtual, Challenge 5 **Product name (working):** PlanIt AI — GenAI Celebration & Event Planner **Author:** Arpit **Version:** 1.0 **Status:** Revised to match the official rules and evaluation criteria

## 1. Challenge Brief (Source of Truth) 

**Challenge 5: Celebration & Event Planner.** Create a GenAI-powered planning assistant that helps users organize weddings, birthdays, and community events with budgets, timelines, vendor checklists, and personalized ideas.

**Event tagline:** Build, deploy & win from anywhere.

**What the brief explicitly requires:**

- A GenAI-powered planning assistant (conversational and generative, not a static form).
- Support for three event categories: weddings, birthdays, community events.
- Four core outputs: budgets, timelines, vendor checklists, personalized ideas.
- Runnable from a public GitHub repository with a documented local setup. A live URL is an optional bonus, not required by the submission rules.

**Assumptions (confirm in the portal):** the six evaluation areas are scored by an AI reviewer reading the repository; the High, Medium and Low impact tiers per area are not stated in the brief; an attempt means one submission of the repository link; a live URL is not required by the submission rules; no hardware dependencies are allowed.

## 1A. Official Submission Rules and Evaluation Criteria

The product is built to be scored by an AI code reviewer on six areas, inside hard submission rules; breaking a rule can mean the submission is not evaluated at all.

### Hard rules (pass or fail)

| Rule | Requirement | How we comply |
| --- | --- | --- |
| Attempts | Maximum 3 | Submit only when the pre-submission checklist in section 21 is fully green; keep attempts 2 and 3 as reserves for fixes; log each attempt |
| Repository size | Under 10 MB | Target under 3 MB: no node\_modules, no build output, no model files, no images over 100 KB; a CI step fails the build above 5 MB |
| Visibility | Public repository | Create it public on day one; verify in a logged-out browser window |
| Branches | Only one branch | Work only on main; no feature branches, no stale remote branches; verify with `git branch -a` before every submission |
| Contents | Complete code plus README | All source, tests, config and docs in the repo; README covers vertical, approach and logic, how it works, assumptions |
| Process | Clone inside the AI platform, build through prompting and coding, commit and push regularly | Small commits with clear messages, pushed after every working feature |
| Prerequisites | AI platform set up, Git configured, active GitHub account, able to create public repos | Done in phase 0 of the build plan before any code |

### Challenge expectations and our response

| Expectation | Product response |
| --- | --- |
| Smart, dynamic assistant | Conversational planner that regenerates only the sections affected when context changes |
| Logical decisions based on user context | Rule-based Decision Engine (section 7A) that reads the Event Profile and explains each decision to the user |
| Practical, real-world usability | Realistic budget splits, backward-planned timelines, actionable vendor questions, PDF and calendar export |
| Clean, maintainable code | Layered architecture, typed, linted and tested (section 9A) |
| One chosen vertical with persona and logic | **Vertical:** Celebration & Event Planner. **Persona:** the Organizer, a non-professional who is planning a wedding, birthday or community event for the first time, is short on time and money, and needs a clear next step at every point |

### Evaluation areas mapped to requirements

| Area | What the reviewer looks for | What we build | Proof in the repo |
| --- | --- | --- | --- |
| Code Quality | Structure, readability, maintainability | Layered folders (api, engine, agents, llm, schemas), type hints, files under 300 lines, one responsibility per module, no dead code | Linter and type-checker config, passing CI, architecture doc |
| Security | Safe and responsible implementation | No secrets in the repo, strict input validation, prompt-injection defence, rate limiting, safe headers, dependency audit | `.env.example`, security tests, security section in README |
| Efficiency | Optimal use of resources | Deterministic maths done in code not by the LLM, parallel agent calls, caching, token caps, lazy-loaded UI, small bundle | Performance budget in CI, token and latency logging |
| Testing | Validation of functionality | Unit tests for the engine, API integration tests, golden-scenario tests, mocked LLM, accessibility tests | Test folders, coverage report, test command in README |
| Accessibility | Inclusive, usable design | WCAG 2.1 AA, semantic HTML, keyboard and screen reader support, reduced motion, text alternatives for charts | Automated axe tests, accessibility statement in README |
| Problem Statement Alignment | Relevance to the stated problem | All three event types and all four outputs (budgets, timelines, vendor checklists, personalized ideas) | Feature-to-requirement table in README, demo scenarios |

**Weighting assumption:** the brief tags each parameter High, Medium or Low impact but does not say which is which here. Treat Problem Statement Alignment, Code Quality and Security as the likely high-impact areas, give Efficiency and Testing full effort, and still finish Accessibility and polish, because the brief says a perfect score needs the low-impact items too. Check the real tiers in the portal and adjust.

**Reviewer-friendly rule:** because an AI reads the code, intent must be obvious from the repo alone: descriptive names, short docstrings that say why, a README repo map, tests named as behaviours, and no clever tricks.

## 2. Product Vision and Goals

**Vision:** Anyone, from a first-time birthday host to a couple planning a wedding to a neighbourhood committee, should be able to describe an event in plain language and receive a complete, realistic, editable plan in under two minutes.

**Primary goals**

1. Turn a vague idea into a structured plan: budget, timeline, vendor checklist, and ideas.
2. Personalize output to guests, culture, location, budget, and tastes.
3. Keep the plan alive: users can chat to modify it and the whole plan updates consistently.
4. Ship a deployed, demo-ready product that maps directly to the challenge rubric.

**Non-goals (v1)**

- Real vendor booking, payments, or live marketplace integration.
- Native mobile apps (responsive web only).
- Multi-tenant enterprise features such as roles, billing, and SSO.
- Real-time vendor pricing from third-party APIs (v1 uses AI-estimated ranges clearly labelled as estimates).

## 3. Target Users and Personas

| Persona | Description | Key need |
| --- | --- | --- |
| Priya, the Wedding Planner-in-Chief | Couple or family member planning a multi-day wedding with a large guest list | Detailed budget split, ritual-aware timeline, vendor shortlist |
| Rahul, the Busy Birthday Host | Parent or friend planning a birthday for a child or adult | Fast theme ideas, simple budget, party-day schedule |
| Meera, the Community Organizer | Volunteer running a festival, fundraiser, or society event | Low-cost planning, volunteer tasks, permits and logistics checklist |
| Professional Planner (secondary) | Freelance planner managing several clients | Reusable templates, exportable plans |

## 4. Problem Statement

Event planning is stressful because information is scattered. People juggle spreadsheets for budgets, notes for timelines, WhatsApp threads for vendors, and endless searches for ideas. They also underestimate costs, miss deadlines (for example booking a venue too late), and forget items such as permits, backups, or thank-you notes. Existing tools are either generic checklists with no intelligence or expensive services with human planners.

## 5. Solution Overview

A web application with a conversational AI planner at its core. The user describes the event (or fills a guided intake). A multi-agent GenAI backend produces four linked artifacts: Budget, Timeline, Vendor Checklist, and Ideas. These live in a single dashboard and stay consistent: changing the guest count in chat re-flows the budget, timeline, and vendor needs.

**Core principle:** one shared Event Profile feeds every agent, so outputs never contradict each other.

## 6. User Journey

1. **Land:** the user sees a clear value proposition and picks an event type (Wedding, Birthday, Community, or Describe your own).
2. **Intake:** a short conversational or form-based flow collects date, location, guest count, total budget, style or theme, cultural preferences, and must-haves.
3. **Generate:** the planner produces the full plan with a visible progress state.
4. **Review:** the user explores tabs: Overview, Budget, Timeline, Vendors, Ideas.
5. **Refine:** the user chats ("cut budget by 20%", "make it outdoors", "add a mehendi night") and sees a diff of what changed.
6. **Track:** the user ticks off tasks, records actual spend, and marks vendors as contacted or booked.
7. **Export and share:** download PDF, copy a share link, or export the checklist to calendar.

## 7. Functional Requirements

Priority key: **P0** = must ship for the demo, **P1** = should ship, **P2** = nice to have.

### 7.1 Event Intake and Profile (P0)

- FR-1: Support event types Wedding, Birthday, Community, and Custom.
- FR-2: Collect fields: event name, type, date or date range, city and venue preference (indoor or outdoor), guest count, total budget and currency, theme or style, audience (kids, adults, mixed, elders), dietary or cultural needs, and special requests.
- FR-3: Accept free-text input and extract structured fields from it using the LLM (for example "Plan a 100-person birthday in Delhi under 50k on 15 Dec").
- FR-4: Ask follow-up questions only for missing critical fields (date, guests, budget). Never block generation if optional fields are empty; apply sensible defaults and state them.
- FR-5: Persist an Event Profile object that all agents read.

### 7.2 Budget Planner (P0)

- FR-6: Generate a category-wise budget allocation that sums exactly to the total budget (venue, catering, decor, entertainment, photography, attire, invitations, transport, gifts, contingency, and so on, depending on event type).
- FR-7: Show percentage and amount per category, with an editable value for each.
- FR-8: Include a contingency buffer (default 8 to 12 percent) and explain it.
- FR-9: Track estimated versus actual spend with a remaining balance, and visual warnings when a category exceeds its limit.
- FR-10: Provide cost-saving suggestions tailored to the plan.
- FR-11: Flag unrealistic budgets (for example a 500-guest wedding at a very low budget) with an honest explanation and alternatives.
- FR-12: Label all figures as AI estimates and show the assumptions used (city tier, season, per-plate cost).

### 7.3 Timeline and Task Scheduler (P0)

- FR-13: Generate a backwards-planned timeline from the event date: milestones such as 12 weeks, 8 weeks, 4 weeks, 1 week, day before, event day, and post-event.
- FR-14: Each task has title, description, due date, owner (self, family, vendor, volunteer), status, priority, and dependencies.
- FR-15: Provide an event-day run-of-show with time slots (setup, guest arrival, ceremony, meal, activities, closing, cleanup).
- FR-16: Adapt to short notice: if the event is under 2 weeks away, compress the schedule and highlight urgent tasks.
- FR-17: Offer calendar and list views, and drag or checkbox task completion (P1: Gantt-style view).
- FR-18: Export tasks to an .ics calendar file (P1).

### 7.4 Vendor Checklist (P0)

- FR-19: Generate the vendor categories needed for the specific event (for example venue, caterer, decorator, photographer, DJ, officiant or priest, makeup artist, baker, florist, tent and sound for community events).
- FR-20: Per category, show: purpose, recommended booking lead time, budget share, what to ask or check (questions list), contract and negotiation tips, and a status tracker (Not started, Shortlisting, Contacted, Quote received, Booked).
- FR-21: Let users add vendor notes: name, phone, quote, and advance paid.
- FR-22: Provide a due-diligence checklist per vendor (references, cancellation policy, inclusions, backup plan).
- FR-23: v1 does not fabricate named real businesses. Vendors are categories plus user-entered details. (P2: grounded local search via Google Maps or Places for real suggestions.)

### 7.5 Personalized Ideas Engine (P0)

- FR-24: Generate themes, decor ideas, menu suggestions, entertainment and activities, invitation wording, return gifts or favours, and games, tailored to the Event Profile.
- FR-25: Give 3 to 5 distinct theme concepts with a mood description, colour palette, decor, menu, and rough cost level.
- FR-26: Provide a "Regenerate" and "More like this" control per idea card, and let users save favourites.
- FR-27: Respect constraints (budget level, dietary needs, age group, culture, indoor or outdoor).
- FR-28: Generate invitation text and a short speech or toast draft (P1).
- FR-29: Generate a mood-board image or palette (P2, via an image generation model).

### 7.6 Conversational Planning Assistant (P0)

- FR-30: A persistent chat panel that can answer planning questions and modify the plan ("swap the DJ for a live band").
- FR-31: Tool-style actions: update profile, recompute budget, regenerate timeline, add or remove vendor category, add task.
- FR-32: After a change, show a summary of affected sections and a before/after diff, with undo.
- FR-33: Maintain conversation memory within the plan session.
- FR-34: Support multilingual input (English and Hindi at minimum) (P1).

### 7.7 Guests and Extras (P1/P2)

- FR-35: Guest list manager with RSVP status and dietary notes (P1).
- FR-36: Shareable read-only plan link for family or co-organizers (P1).
- FR-37: Collaborative editing with multiple organizers (P2).
- FR-38: Reminders via email or notification before due tasks (P2).

### 7.8 Export, Save, and Accounts (P0/P1)

- FR-39: Save plans (anonymous session in P0; no accounts in v1, which keeps the attack surface small; the plan is mirrored to browser storage).
- FR-40: Export the full plan as a PDF (P0) and the budget as CSV (P1).
- FR-41: Multiple events per user (P1).

## 7A. Context-Aware Decision Engine

Code decides numbers, dates and constraints; the LLM writes ideas, wording and explanations. This split gives the "logical decision making based on user context" the challenge asks for, makes every result testable, and saves tokens.

### Inputs the engine reads

Event type, date and days remaining, guest count, total budget, city tier, venue type (indoor or outdoor), audience mix (kids, adults, elders), dietary and cultural needs, season, and must-haves.

### Baseline budget profiles (percent of total, each sums to 100)

| Category | Wedding | Birthday | Community |
| --- | --- | --- | --- |
| Venue (and permits for community) | 20 | 15 | 15 |
| Catering | 30 | 35 | 25 |
| Decor and theme | 12 | 15 | 8 |
| Photography and video | 10 | 3 | 0 |
| Attire and beauty | 8 | 0 | 0 |
| Entertainment and activities | 5 | 15 | 12 |
| Cake | 0 | 7 | 0 |
| Sound, stage and lighting | 0 | 0 | 15 |
| Invitations, printing and promotion | 2 | 2 | 6 |
| Transport and stay | 4 | 0 | 0 |
| Favours and gifts | 2 | 3 | 0 |
| Safety, first aid and cleanup | 0 | 0 | 8 |
| Volunteer support | 0 | 0 | 3 |
| Contingency | 7 | 5 | 8 |

### Decision rules (tunable defaults kept in one config file)

| Condition | Decision | Shown to the user as |
| --- | --- | --- |
| Outdoor venue | Add 2 points to contingency; add a tent or shade vendor category; add a backup-plan task | Outdoor events need a weather backup |
| Days remaining under 14 | Compress the timeline, mark long-lead vendors as book now, drop low-priority tasks | Short notice: here is the urgent path |
| Peak season for the event type | Add 4 weeks to venue and caterer lead time; raise venue share by 2 points | Peak dates fill early, so book first |
| Guests over 200 | Add a crowd-management task, a second serving point and a transport item | Large guest lists need flow planning |
| Kids in audience | Add child-safety tasks and a first-aid item; weight entertainment up; keep menu child-friendly | Kids attending: safety and activity added |
| Elders in audience | Add seating, accessibility and rest-area tasks | Comfort items added for elders |
| Dietary or cultural needs stated | Add caterer questions; filter menu ideas; add ritual or timing tasks | Menu and tasks adapted to your needs |
| Per-guest budget below the minimum for the city tier | Raise a feasibility warning with three options: fewer guests, a lower-cost venue, or a larger budget | Budget is tight for this guest count |
| Contradictory inputs (for example a 500-guest sit-down on a very low budget) | Resolve by priority: safety and legal, then budget cap, then date, then dietary and cultural needs, then theme | Here is what we changed and why |

Feasibility thresholds (per-guest minimums by event type and city tier) are placeholders stored in config, documented as assumptions in the README, and easy to change.

### Required behaviours

- **Decision trace:** every rule that fires is recorded and shown as a short "Why this?" note beside the affected budget line, task or vendor.
- **Exact totals:** the allocated budget always sums to the stated total, with rounding remainder assigned to contingency.
- **Date sanity:** no task is due after the event except post-event tasks; no task is due in the past; dependencies are respected.
- **Offline fallback:** if no API key is set or the LLM fails, the engine alone still produces a complete budget, timeline and vendor checklist, and the ideas section uses curated templates. This also makes tests deterministic.

## 8. AI and Agent Architecture

**Pattern:** supervisor plus specialist agents sharing a common Event Profile and plan state.

| Agent | Responsibility | Input | Output |
| --- | --- | --- | --- |
| Orchestrator | Routes user intent, merges results, ensures consistency | User message, plan state | Delegations and final response |
| Intake Agent | Parses free text into the Event Profile, asks follow-ups | Raw text | Structured profile JSON |
| Budget Agent | Allocates and validates the budget | Profile | Budget JSON (sums validated by code) |
| Timeline Agent | Backward-plans tasks and the run-of-show | Profile, vendors | Task list JSON |
| Vendor Agent | Builds vendor categories, checklists, and questions | Profile, budget | Vendor JSON |
| Ideas Agent | Themes, menus, decor, activities | Profile | Idea cards JSON |
| Reviewer Agent | Checks for contradictions, missed items, and realism | Whole plan | Issues list and fixes |

**Design rules**

- All LLM outputs use structured JSON with a schema (response schema or function calling) so the UI never parses prose.
- Deterministic code, not the LLM, verifies arithmetic (the budget must sum to the total) and date logic (no task due after the event, except post-event tasks).
- Prompts are versioned and stored separately from code.
- A single Event Profile is the source of truth. Any edit triggers selective regeneration of only the affected sections.
- Grounding: optional Google Search grounding for local costs and trends (P2). Otherwise label figures as estimates.
- Safety: filter unsafe content, avoid medical, legal, or religious claims presented as fact, and add a gentle disclaimer on cost estimates.

**Model choice:** Gemini via Vertex AI or the Gemini API (a fast Flash-class model for chat and intake, a stronger Pro-class model for full plan generation). Use streaming for responsiveness.

## 9. Recommended Technical Stack

Selected to fit a Google-aligned hackathon, fast delivery, and Cloud Run deployment.

| Layer | Choice | Reason |
| --- | --- | --- |
| Frontend | React, Vite and TypeScript with CSS variables for theming | Fast, accessible, small bundle, easy to test |
| Backend | FastAPI and Pydantic v2 (Python) | Strict validation, async calls, clear structure |
| Decision logic | Pure Python rules engine with no LLM dependency | Deterministic, testable, free of token cost |
| LLM | Gemini through the google-genai SDK, behind an LLMClient interface | Structured output and streaming; swappable and fakeable in tests |
| Agents | Lightweight agent modules plus an async Orchestrator (Google ADK is an optional alternative) | Fewer dependencies and clearer code for review |
| Storage | In-memory repository behind an interface, mirrored to browser localStorage | No accounts or database to secure; refresh does not lose the plan |
| Quality tools | Ruff, mypy, ESLint, Prettier, pre-commit | Enforces readable, consistent code |
| Testing | pytest with pytest-cov, Vitest, Testing Library, jest-axe | Covers logic, API and accessibility |
| Security tooling | pip-audit, npm audit, gitleaks in CI | Catches vulnerable dependencies and leaked secrets |
| PDF export | Lightweight server or client library, with user text escaped | No heavy dependencies |
| Delivery | Dockerfile and GitHub Actions CI; Cloud Run deployment is optional | Runs anywhere; the submission only needs the public repo |

**Constraints to honour:** no hardware dependencies; Cloud Run compatible (stateless, listens on the PORT environment variable); repository kept small (target under 10 MB, no committed node\_modules or model files); no secrets in the repo; a single Dockerfile that builds and runs.

## 9A. Engineering Standards for the Six Evaluation Areas

### Repository layout

```text
event-planner/
├── README.md                  # vertical, approach and logic, how it works, assumptions
├── LICENSE
├── .gitignore  .env.example  .dockerignore  Dockerfile
├── .github/workflows/ci.yml   # lint, type-check, test, size and secret checks
├── backend/
│   ├── app/
│   │   ├── main.py            # app factory, middleware, security headers
│   │   ├── config.py          # settings and tunable rule defaults
│   │   ├── api/               # routers: events, chat, export, health
│   │   ├── schemas/           # pydantic models for profile, budget, tasks, vendors
│   │   ├── engine/            # decision engine: rules, budget, timeline, feasibility
│   │   ├── agents/            # orchestrator, intake, ideas, vendors, reviewer
│   │   ├── llm/               # client wrapper, prompts/, fake client for tests
│   │   ├── services/          # export (pdf, csv, ics), storage interface
│   │   └── security/          # sanitising, rate limit, prompt-injection guard
│   └── tests/                 # unit, integration, golden scenarios
├── frontend/
│   ├── src/                   # components, pages, hooks, api client, styles
│   └── tests/                 # component and accessibility tests
└── docs/                      # ARCHITECTURE.md, DECISIONS.md
```

### Code Quality

- Typed Python (type hints, mypy strict on `engine` and `schemas`) and TypeScript in strict mode.
- Ruff, ESLint and Prettier configured and passing; a pre-commit hook runs them.
- One responsibility per module, functions under 40 lines, files under 300 lines, no dead code, no commented-out code, no magic numbers (named constants or config).
- Dependency direction is one-way: api depends on agents and engine; engine depends on nothing but schemas. The LLM is behind an `LLMClient` interface.
- Docstrings state why, not what. `docs/ARCHITECTURE.md` and `docs/DECISIONS.md` (short decision records) explain the structure.
- Conventional commit messages (feat, fix, test, docs, refactor) on a single branch.

### Security

- No secrets in the repo or history; `.env.example` only; keys read from environment variables; secret scan in CI.
- Validate every request with Pydantic: length limits, allowed enums, numeric ranges, date ranges. Reject unknown fields.
- Prompt-injection defence: user text is wrapped and labelled as data, system instructions are separate, model output must pass a strict JSON schema, and the model has no tools that touch files, the network or the shell.
- Output safety: React escapes by default; any rendered rich text is sanitised; no `dangerouslySetInnerHTML`; PDF generation escapes user text.
- Rate limiting per client, request size limits, timeouts on LLM calls, and CORS restricted to the app origin.
- Security headers (CSP, X-Content-Type-Options, frame protection, referrer policy); generic error messages with no stack traces or key fragments; logs redact personal data.
- Dependency hygiene: pinned versions, `pip-audit` and `npm audit` in CI, minimal dependency list.
- Privacy: collect the minimum, say plainly that event details go to an AI model, and let users delete a plan.

### Efficiency

- Budget, dates and rules are computed in code, not by the LLM, so most of the plan costs no tokens.
- A full plan uses at most 3 LLM calls (ideas, vendor enrichment, review), run in parallel; intake adds one only for free-text input.
- Cache results by a hash of the Event Profile; regenerate only the affected section after a chat edit.
- Token caps per call, model tiering (fast model for intake and chat, stronger model for ideas), streaming responses.
- Frontend: route-level code splitting, initial JavaScript under 200 KB gzipped, no heavy UI libraries, no images over 100 KB.
- Docker image is multi-stage and small; the app starts in under 3 seconds.

### Testing

- Backend: pytest with coverage targets of 85 percent for `engine` and 75 percent overall.
- Unit tests for every decision rule, the budget sum, date logic and schema validation.
- Integration tests for each endpoint using a fake LLM client, including failure and timeout paths and the offline fallback.
- Golden-scenario tests: one wedding, one birthday and one community event with expected outputs, plus edge cases (tiny budget, very large guest list, event in under 7 days, past date, non-English text, injection attempts).
- Security tests: oversized input, malformed JSON, injection strings, rate-limit behaviour.
- Frontend: Vitest and Testing Library for components; `jest-axe` automated accessibility checks on every page.
- One command runs everything (`make test`); CI runs it on every push.

### Accessibility

- Target WCAG 2.1 AA: semantic landmarks and headings, labelled form controls, visible focus, a skip link, and a correct page language.
- Everything works by keyboard alone; focus moves sensibly after generation and after chat edits.
- Streaming and status changes announced with `aria-live`; errors tied to fields with `aria-describedby`.
- Colour contrast of at least 4.5 to 1; information never conveyed by colour alone; a high-contrast and dark theme; respects reduced-motion settings.
- Charts always have a data-table alternative and a text summary.
- Works at 200 percent zoom and on small screens; touch targets at least 44 px; plain-language microcopy.
- Lighthouse accessibility score of 95 or more, checked in CI where practical, and an accessibility statement in the README.

### Git workflow and size control

- Create the public repository first, clone it inside the AI platform, and keep everything on `main`.
- Commit and push after each working feature; never create other branches; run `git branch -a` before submitting.
- `.gitignore` covers `node_modules`, build output, caches, virtual environments, `.env` and editor files.
- Check size with `git count-objects -vH` and a folder size check before each submission; keep it under 3 MB.

### README outline (required content first)

1. **Chosen vertical:** Celebration & Event Planner and the Organizer persona.
2. **Approach and logic:** the engine-plus-LLM split and the decision rules table.
3. **How the solution works:** architecture diagram, request flow, feature walkthrough.
4. **Assumptions:** every default, placeholder threshold and limitation.
5. Setup in three commands, environment variables, how to run tests, project structure.
6. Evaluation mapping: one short section per area (quality, security, efficiency, testing, accessibility, alignment).
7. Demo scenarios and known limitations.

## 10. System Architecture

1. **Client (React SPA)** calls the backend over HTTPS REST plus Server-Sent Events for streaming.
2. **API layer (FastAPI)** exposes endpoints, validates input with schemas, and handles sessions.
3. **Agent layer (ADK)** hosts the orchestrator and specialist agents, calling Gemini.
4. **Validation layer** performs deterministic checks on budget sums, date logic, and schema conformity.
5. **Data layer (Firestore)** stores events, plans, tasks, and chat history.
6. **Export service** renders PDF, CSV, and .ics.

**Request flow (generate plan):** Client posts the profile, the API validates it, the orchestrator runs the Budget, Vendor, Ideas, and Timeline agents (in parallel where possible), the Reviewer checks the result, the validators correct it, the plan is saved and streamed back section by section.

## 11. Data Model (Core Entities)

**EventProfile:** id, type, name, date, location, venueType, guestCount, budgetTotal, currency, theme, audience, culturalNotes, dietary, mustHaves, createdAt.

**Budget:** eventId, categories\[ {name, percent, estimated, actual, notes} \], contingency, assumptions\[\], savingTips\[\].

**Task:** id, eventId, title, description, dueDate, owner, priority, status, dependsOn\[\], phase.

**RunOfShow:** eventId, slots\[ {startTime, endTime, activity, owner} \].

**VendorCategory:** id, eventId, name, leadTimeWeeks, budgetShare, askList\[\], diligenceList\[\], status, vendorName, contact, quote, advancePaid, notes.

**IdeaCard:** id, eventId, kind (theme, decor, menu, activity, invitation, favour), title, description, palette\[\], costLevel, saved.

**ChatMessage:** id, eventId, role, content, actionsTaken\[\], timestamp.

## 12. API Specification (Core Endpoints)

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | /api/events | Create an event from a profile or free text |
| GET | /api/events/{id} | Fetch the full plan |
| POST | /api/events/{id}/generate | Generate or regenerate all sections (streamed) |
| POST | /api/events/{id}/generate/{section} | Regenerate one section (budget, timeline, vendors, ideas) |
| POST | /api/events/{id}/chat | Chat with the assistant; may modify the plan |
| PATCH | /api/events/{id}/tasks/{taskId} | Update task status or details |
| PATCH | /api/events/{id}/budget | Edit amounts or record actual spend |
| PATCH | /api/events/{id}/vendors/{vendorId} | Update vendor status and notes |
| GET | /api/events/{id}/export?format=pdf\|csv\|ics | Export |
| GET | /healthz | Health check for Cloud Run |

## 13. UX and UI Requirements

- **Look and feel:** clean, celebratory but professional; a dark mode option; consistent colour palette that adapts to event type (for example warm golds for weddings, bright colours for birthdays).
- **Layout:** a left or top navigation with tabs (Overview, Budget, Timeline, Vendors, Ideas) and a persistent chat panel (collapsible on mobile).
- **Overview dashboard:** event countdown, budget used versus remaining, tasks done percentage, upcoming tasks, vendors booked.
- **Key states:** empty, loading (skeletons and streaming progress), error with retry, partial success.
- **Responsive:** fully usable on mobile (majority of event planners use phones).
- **Accessibility:** WCAG 2.1 AA targets: contrast, keyboard navigation, ARIA labels, focus states, and screen reader friendly charts (with text alternatives).
- **Microcopy:** friendly, concise, and honest about estimates.
- **Visuals:** budget donut chart, timeline progress bar, and colour-coded task priorities.

## 14. Non-Functional Requirements

- **Performance:** first plan generated and visible (streamed) within 20 seconds; chat reply starts within 3 seconds; UI interactions under 200 ms.
- **Reliability:** graceful fallbacks if the LLM fails (retry with backoff, then a cached template plan); schema validation with automatic repair.
- **Scalability:** stateless containers on Cloud Run with autoscaling; rate limiting per session.
- **Security:** no secrets in client code; input sanitisation; protection against prompt injection (treat user text as data, strict output schemas); CORS locked to the app origin; HTTPS only.
- **Privacy:** collect minimum personal data; clear note that event details are sent to an AI model; ability to delete a plan; no selling of data.
- **Compliance and safety:** content moderation for harmful requests; avoid stereotyping when suggesting cultural or religious elements; cost estimates marked as non-binding.
- **Observability:** structured logging, request IDs, latency and token usage metrics, and error tracking.
- **Portability:** one Dockerfile, an .env.example file, and a documented local run in three commands.

## 15. Success Metrics

**Product metrics**

- Time to first full plan under 2 minutes from landing.
- Plan completeness: all four sections present in 100 percent of generations.
- Budget arithmetic correctness: 100 percent (validated by code).
- Chat edit success rate above 90 percent (the change is applied correctly).
- Demo-user satisfaction of at least 4 out of 5 in quick feedback.

**Official evaluation alignment**

| Official evaluation area | Target | How it is measured |
| --- | --- | --- |
| Code Quality | Linters and type checks clean; files under 300 lines; clear layers | CI results and a reviewer-readable repo map |
| Security | No secrets, validated inputs, injection defence, audited dependencies | Security tests, gitleaks and audit runs in CI |
| Efficiency | At most 3 LLM calls per plan; initial JavaScript under 200 KB gzipped; cached results | Logged token counts, latency and bundle-size check |
| Testing | 85 percent coverage on the engine, 75 percent overall, golden scenarios pass | Coverage report and one-command test run |
| Accessibility | WCAG 2.1 AA; Lighthouse accessibility of 95 or more; axe tests pass | Automated axe and Lighthouse checks plus keyboard walkthrough |
| Problem Statement Alignment | All three event types and all four outputs, with context-based decisions | Feature-to-requirement table in the README and three demo scenarios |

## 16. Scope and Release Plan

**MVP (build first, P0):** intake, budget, timeline, vendor checklist, ideas, chat refinement, PDF export, Cloud Run deployment.

**v1.1 (P1):** saved multiple events (browser storage), shareable link, guest list, .ics and CSV export, Hindi support, invitation and toast generation.

**v2 (P2):** grounded local vendor suggestions, mood-board images, collaboration, reminders, and RSVP pages.

## 17. Suggested Build Plan (Hackathon Timeline)

| Phase | Work | Output |
| --- | --- | --- |
| 0. Prerequisites | Set up the AI platform, Git and GitHub; create the public repo; clone it in the platform; add .gitignore, README stub, CI | Empty but compliant single-branch repo |
| 1. Foundations | Schemas, config, Event Profile, LLM interface with a fake client, health endpoint | Typed skeleton with first tests |
| 2. Decision engine | Budget profiles, rules, feasibility, timeline and run-of-show, decision trace, with unit tests | Offline plan generation that passes tests |
| 3. AI layer | Intake, ideas, vendor enrichment, reviewer, orchestrator, injection guard | Full plan with LLM enrichment and fallback |
| 4. UI | Intake flow, dashboard tabs, charts with table alternatives, chat panel, streaming | Accessible end-to-end app |
| 5. Refinement | Chat-driven edits, diff and undo, selective regeneration, caching | Consistent edits |
| 6. Hardening | Security headers, rate limits, audits, accessibility pass, performance budget, coverage targets | Green CI on every check |
| 7. Submission | README, architecture doc, size and branch checks, fresh-clone run test, then submit as attempt 1 | Submission package; attempts 2 and 3 kept in reserve |

## 18. Testing and Quality Plan

- **Unit tests:** budget sum validator, date and dependency validator, schema parsing.
- **Prompt and golden tests:** a fixed set of sample events (one wedding, one birthday, one community event, plus edge cases) checked for completeness and sanity.
- **Integration tests:** API endpoints for create, generate, chat edit, and export.
- **Edge cases:** zero or tiny budget, very large guest count, date in the past or less than 7 days away, conflicting requests, non-English input, empty optional fields, and malicious or off-topic prompts.
- **Manual QA:** mobile and desktop browsers, keyboard-only use, slow network.

## 19. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| LLM returns invalid or inconsistent JSON | UI breaks | Response schemas, validators, auto-repair retry, fallback template |
| Hallucinated vendors or prices | Loss of trust | No fabricated business names; label estimates; optional grounding |
| Slow generation | Poor demo | Parallel agents, streaming, faster model for non-critical parts |
| Budget and timeline drift after edits | Inconsistent plan | Single source of truth profile, selective regeneration, Reviewer agent |
| Quota or rate limits during judging | Demo failure | Caching sample plans, retry and backoff, a pre-generated demo mode |
| Repo too large or deploy failures | Disqualification | Small repo, .dockerignore, test the deploy early and often |
| Prompt injection | Misbehaviour | Strict schemas, treat user text as data, output filtering |

## 20. Demo Script (Judging)

1. Open the live URL and choose Wedding.
2. Type: "Plan a 2-day wedding for 250 guests in Jaipur in February, budget 15 lakh, royal theme."
3. Watch the plan stream in: budget donut, timeline, vendor checklist, ideas.
4. Say in chat: "Reduce the budget by 20 percent and make it more intimate (150 guests)." Show the diff and the updated budget, tasks, and vendors.
5. Switch to Birthday and Community to show breadth.
6. Tick a task, record spend, and export the PDF.
7. Close with the architecture slide and the Cloud Run URL.

## 21. Deliverables Checklist

- [ ] Repository is public (checked while logged out)
- [ ] Only one branch exists (`git branch -a` shows main only)
- [ ] Repository size is under 10 MB (target under 3 MB)
- [ ] No secrets, keys or `.env` in the files or history
- [ ] Complete code, tests and config are committed and pushed
- [ ] README covers chosen vertical, approach and logic, how it works, and assumptions
- [ ] README setup works from a fresh clone in three commands
- [ ] Lint, type checks, tests, coverage targets and accessibility checks pass in CI
- [ ] Dependency audit and secret scan are clean
- [ ] All three event types and all four outputs demonstrated
- [ ] Attempt log updated (maximum 3 attempts; submit only when everything above is ticked)
- [ ] Optional: live demo URL and short demo video

## 22. Open Questions

- Which of the six areas are High, Medium and Low impact in the portal?
- What exactly counts as an attempt: a submission, or each push?
- Does the detailed submission guide (the document link in the brief) require extra files or a specific README format?
- Is a live URL scored at all? Assumed no.
- Which AI platform is allowed or expected for the build, and must prompts be kept?
- Default currency and region (INR and India assumed).

## 23. Glossary

- **Event Profile:** the structured description of the event that every agent reads.
- **Run-of-show:** a minute-by-minute schedule for the event day.
- **Contingency:** a reserved budget buffer for unexpected costs.
- **Grounding:** anchoring model answers in real, retrievable sources.
- **ADK:** Google's Agent Development Kit for building multi-agent systems.
