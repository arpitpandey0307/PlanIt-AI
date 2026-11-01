import { useState, useCallback } from 'react'
import './App.css'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/* =========================================================================
   Type Definitions
   ========================================================================= */

interface EventProfile {
  id: string
  name: string
  event_type: string
  event_date: string
  city: string
  guest_count: number
  budget_total: number
  currency: string
}

interface BudgetCategory {
  name: string
  percent: number
  estimated: number
  actual: number
  decision_trace?: string
}

interface Budget {
  total_budget: number
  categories: BudgetCategory[]
  remaining: number
  assumptions?: string[]
  saving_tips?: string[]
  feasibility_warning?: string | null
}

interface Task {
  id: string
  title: string
  description?: string
  due_date: string
  priority: string
  status: string
  phase: string
  owner?: string
}

interface VendorCategory {
  id: string
  name: string
  lead_time_weeks: number
  budget_share: number
  questions: string[]
  diligence: string[]
  status: string
}

interface IdeaCard {
  id: string
  kind: string
  title: string
  description: string
  palette?: string[]
  cost_level: string
  tags?: string[]
}

interface EventPlan {
  profile: EventProfile
  budget: Budget | null
  timeline: { tasks: Task[]; run_of_show?: unknown[] } | null
  vendors: { categories: VendorCategory[] } | null
  ideas: { themes: IdeaCard[]; menu?: IdeaCard[]; activities?: IdeaCard[]; invitations?: IdeaCard[] } | null
}

type Step = 'intro' | 'intake' | 'generating' | 'dashboard'
type TabName = 'overview' | 'budget' | 'timeline' | 'vendors' | 'ideas'

/* =========================================================================
   App Component
   ========================================================================= */

function App() {
  const [step, setStep] = useState<Step>('intro')
  const [eventType, setEventType] = useState<string>('wedding')
  const [freeText, setFreeText] = useState<string>('')
  const [eventId, setEventId] = useState<string>('')
  const [plan, setPlan] = useState<EventPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [activeTab, setActiveTab] = useState<TabName>('overview')

  /* ---- API Interactions ---- */

  const generatePlan = useCallback(async (id: string) => {
    try {
      await axios.post(`${API_BASE}/api/events/${id}/generate`)
      const planResponse = await axios.get(`${API_BASE}/api/events/${id}`)
      setPlan(planResponse.data)
      setStep('dashboard')
    } catch (err: unknown) {
      const message =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Failed to generate plan'
      setError(message)
      setStep('intake')
    } finally {
      setLoading(false)
    }
  }, [])

  const createEvent = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await axios.post(`${API_BASE}/api/events/`, {
        free_text: freeText,
        event_type: eventType,
      })

      setEventId(response.data.event_id)
      setStep('generating')
      await generatePlan(response.data.event_id)
    } catch (err: unknown) {
      const message =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Failed to create event'
      setError(message)
      setLoading(false)
    }
  }, [freeText, eventType, generatePlan])

  const handleEventTypeSelect = useCallback((type: string) => {
    setEventType(type)
    setStep('intake')
  }, [])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent, type: string) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        handleEventTypeSelect(type)
      }
    },
    [handleEventTypeSelect],
  )

  /* ---- Render Helpers ---- */

  const formatCurrency = (amount: number): string =>
    `₹${amount.toLocaleString('en-IN')}`

  const formatDate = (dateStr: string): string =>
    new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })

  /* ---- Tab data for keyboard navigation ---- */
  const tabs: { key: TabName; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'budget', label: 'Budget' },
    { key: 'timeline', label: 'Timeline' },
    { key: 'vendors', label: 'Vendors' },
    { key: 'ideas', label: 'Ideas' },
  ]

  const handleTabKeyDown = (e: React.KeyboardEvent, idx: number) => {
    let newIdx = idx
    if (e.key === 'ArrowRight') newIdx = (idx + 1) % tabs.length
    else if (e.key === 'ArrowLeft') newIdx = (idx - 1 + tabs.length) % tabs.length
    else return

    e.preventDefault()
    setActiveTab(tabs[newIdx].key)
    // Focus the new tab button
    const tabEl = document.getElementById(`tab-${tabs[newIdx].key}`)
    tabEl?.focus()
  }

  /* =========================================================================
     JSX
     ========================================================================= */

  return (
    <div className="app">
      {/* Accessibility: Skip-to-content link */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* ---- Header ---- */}
      <header className="app-header" role="banner">
        <div className="container">
          <h1>🎉 PlanIt AI</h1>
          <p>Your AI-powered event planning assistant</p>
        </div>
      </header>

      {/* ---- Main Content ---- */}
      <main id="main-content" className="app-main" role="main">
        <div className="container">
          {/* ======== INTRO STEP ======== */}
          {step === 'intro' && (
            <section className="intro-section" aria-label="Choose event type">
              <h2>Plan your perfect celebration</h2>
              <p className="subtitle">Weddings • Birthdays • Community Events</p>

              <div className="event-types" role="group" aria-label="Event type options">
                {[
                  { type: 'wedding', icon: '💒', title: 'Wedding', desc: 'Multi-day celebrations, rituals, large guest lists' },
                  { type: 'birthday', icon: '🎂', title: 'Birthday', desc: 'Parties, themes, activities for all ages' },
                  { type: 'community', icon: '🎪', title: 'Community Event', desc: 'Festivals, fundraisers, gatherings' },
                ].map(({ type, icon, title, desc }) => (
                  <button
                    key={type}
                    className={`event-type-card ${eventType === type ? 'active' : ''}`}
                    onClick={() => handleEventTypeSelect(type)}
                    onKeyDown={(e) => handleKeyDown(e, type)}
                    aria-label={`Plan a ${title}`}
                    aria-pressed={eventType === type}
                  >
                    <span className="icon" aria-hidden="true">{icon}</span>
                    <h3>{title}</h3>
                    <p>{desc}</p>
                  </button>
                ))}
              </div>
            </section>
          )}

          {/* ======== INTAKE STEP ======== */}
          {step === 'intake' && (
            <section className="intake-section" aria-label="Event details form">
              <h2>Tell me about your {eventType}</h2>
              <p>
                Describe your event in plain language. Include date, location,
                guests, budget, and any special requirements.
              </p>

              <form
                className="intake-form"
                onSubmit={(e) => {
                  e.preventDefault()
                  if (freeText.trim()) createEvent()
                }}
                aria-label="Event intake form"
              >
                <label htmlFor="event-description" className="sr-only">
                  Event description
                </label>
                <textarea
                  id="event-description"
                  placeholder="Example: Plan a 2-day wedding for 250 guests in Jaipur in February, budget 15 lakh, royal theme"
                  value={freeText}
                  onChange={(e) => setFreeText(e.target.value)}
                  rows={5}
                  aria-label="Event description"
                  aria-required="true"
                  aria-invalid={!!error}
                  aria-describedby={error ? 'error-msg' : undefined}
                  maxLength={2000}
                />

                {error && (
                  <div
                    id="error-msg"
                    className="error-message"
                    role="alert"
                    aria-live="assertive"
                  >
                    {error}
                  </div>
                )}

                <div className="button-group">
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={() => setStep('intro')}
                    disabled={loading}
                    aria-label="Go back to event type selection"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    className="btn-primary"
                    disabled={loading || !freeText.trim()}
                    aria-label="Create event plan"
                    aria-busy={loading}
                  >
                    {loading ? (
                      <span className="loading" role="status" aria-label="Loading">
                        <span className="sr-only">Creating plan…</span>
                      </span>
                    ) : (
                      'Create Plan'
                    )}
                  </button>
                </div>
              </form>
            </section>
          )}

          {/* ======== GENERATING STEP ======== */}
          {step === 'generating' && (
            <section className="generating-section" aria-label="Generating plan" aria-live="polite">
              <div className="card text-center">
                <div className="loading-spinner" role="status" aria-label="Loading">
                  <span className="sr-only">Generating your plan…</span>
                </div>
                <h2>Generating your plan…</h2>
                <p>
                  Creating budget, timeline, vendor checklist, and personalized
                  ideas.
                </p>
              </div>
            </section>
          )}

          {/* ======== DASHBOARD STEP ======== */}
          {step === 'dashboard' && plan && (
            <section className="dashboard" aria-label="Event plan dashboard">
              {/* Header */}
              <div className="dashboard-header">
                <h2>{plan.profile.name}</h2>
                <p>
                  {plan.profile.event_type.toUpperCase()} •{' '}
                  {plan.profile.guest_count} guests •{' '}
                  {formatCurrency(plan.profile.budget_total || 0)}
                </p>
              </div>

              {/* Tab Navigation (WAI-ARIA tabs pattern) */}
              <div className="tabs" role="tablist" aria-label="Plan sections">
                {tabs.map((tab, idx) => (
                  <button
                    key={tab.key}
                    id={`tab-${tab.key}`}
                    className={`tab ${activeTab === tab.key ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.key)}
                    onKeyDown={(e) => handleTabKeyDown(e, idx)}
                    role="tab"
                    aria-selected={activeTab === tab.key}
                    aria-controls={`tabpanel-${tab.key}`}
                    tabIndex={activeTab === tab.key ? 0 : -1}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Panels */}
              <div className="tab-content">
                {/* ---- Overview Panel ---- */}
                {activeTab === 'overview' && (
                  <div
                    id="tabpanel-overview"
                    role="tabpanel"
                    aria-labelledby="tab-overview"
                    className="overview"
                  >
                    <div className="stats-grid" role="list" aria-label="Event statistics">
                      <div className="stat-card" role="listitem">
                        <h3>Budget Status</h3>
                        <p className="stat-value">
                          {formatCurrency(plan.budget?.remaining || 0)}
                        </p>
                        <p className="stat-label">Remaining</p>
                      </div>
                      <div className="stat-card" role="listitem">
                        <h3>Tasks</h3>
                        <p className="stat-value">
                          {plan.timeline?.tasks.length || 0}
                        </p>
                        <p className="stat-label">Total tasks</p>
                      </div>
                      <div className="stat-card" role="listitem">
                        <h3>Event Date</h3>
                        <p className="stat-value">
                          {formatDate(plan.profile.event_date)}
                        </p>
                        <p className="stat-label">Mark your calendar</p>
                      </div>
                    </div>

                    <div className="card">
                      <h3>Next Steps</h3>
                      {plan.timeline &&
                        plan.timeline.tasks.slice(0, 5).map((task) => (
                          <div key={task.id} className="task-item" role="listitem">
                            <span
                              className={`priority-badge ${task.priority}`}
                              aria-label={`Priority: ${task.priority}`}
                            >
                              {task.priority}
                            </span>
                            <div>
                              <p>
                                <strong>{task.title}</strong>
                              </p>
                              <p className="task-meta">
                                Due: {formatDate(task.due_date)} • {task.phase}
                              </p>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* ---- Budget Panel ---- */}
                {activeTab === 'budget' && plan.budget && (
                  <div
                    id="tabpanel-budget"
                    role="tabpanel"
                    aria-labelledby="tab-budget"
                    className="budget"
                  >
                    <div className="card">
                      <h3>Budget Breakdown</h3>
                      <p>Total: {formatCurrency(plan.budget.total_budget || 0)}</p>

                      {plan.budget.feasibility_warning && (
                        <div className="error-message" role="alert">
                          ⚠️ {plan.budget.feasibility_warning}
                        </div>
                      )}

                      <div className="budget-list" role="list" aria-label="Budget categories">
                        {plan.budget.categories.map((cat, i) => (
                          <div key={i} className="budget-item" role="listitem">
                            <div className="budget-info">
                              <strong>{cat.name}</strong>
                              <span aria-label={`${cat.percent} percent`}>
                                {cat.percent}%
                              </span>
                            </div>
                            <div
                              className="budget-bar"
                              role="progressbar"
                              aria-valuenow={cat.percent}
                              aria-valuemin={0}
                              aria-valuemax={100}
                              aria-label={`${cat.name} allocation`}
                            >
                              <div
                                className="budget-bar-fill"
                                style={{ width: `${cat.percent}%` }}
                              />
                            </div>
                            <div className="budget-amounts">
                              <span>{formatCurrency(cat.estimated || 0)}</span>
                              <span className="spent">
                                Spent: {formatCurrency(cat.actual || 0)}
                              </span>
                            </div>
                            {cat.decision_trace && (
                              <p className="task-meta" aria-label="Decision explanation">
                                💡 {cat.decision_trace}
                              </p>
                            )}
                          </div>
                        ))}
                      </div>

                      {plan.budget.saving_tips && plan.budget.saving_tips.length > 0 && (
                        <div className="saving-tips" style={{ marginTop: '24px' }}>
                          <h4>💰 Saving Tips</h4>
                          <ul aria-label="Budget saving tips">
                            {plan.budget.saving_tips.map((tip, i) => (
                              <li key={i} style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>{tip}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {plan.budget.assumptions && plan.budget.assumptions.length > 0 && (
                        <div className="assumptions" style={{ marginTop: '16px' }}>
                          <h4>📋 Assumptions</h4>
                          <ul aria-label="Budget assumptions">
                            {plan.budget.assumptions.map((a, i) => (
                              <li key={i} style={{ marginBottom: '4px', color: 'var(--text-light)', fontSize: '14px' }}>{a}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* ---- Timeline Panel ---- */}
                {activeTab === 'timeline' && plan.timeline && (
                  <div
                    id="tabpanel-timeline"
                    role="tabpanel"
                    aria-labelledby="tab-timeline"
                    className="timeline"
                  >
                    <div className="card">
                      <h3>Planning Timeline</h3>
                      <div className="task-list" role="list" aria-label="Planning tasks">
                        {plan.timeline.tasks.map((task) => (
                          <article key={task.id} className="task-card" role="listitem">
                            <div className="task-header">
                              <span
                                className={`priority-badge ${task.priority}`}
                                aria-label={`Priority: ${task.priority}`}
                              >
                                {task.priority}
                              </span>
                              <span
                                className={`status-badge ${task.status}`}
                                aria-label={`Status: ${task.status.replace('_', ' ')}`}
                              >
                                {task.status.replace('_', ' ')}
                              </span>
                            </div>
                            <h4>{task.title}</h4>
                            {task.description && <p>{task.description}</p>}
                            <p className="task-meta">
                              <span>📅 {formatDate(task.due_date)}</span>
                              <span> • {task.phase}</span>
                              {task.owner && <span> • 👤 {task.owner}</span>}
                            </p>
                          </article>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* ---- Vendors Panel ---- */}
                {activeTab === 'vendors' && plan.vendors && (
                  <div
                    id="tabpanel-vendors"
                    role="tabpanel"
                    aria-labelledby="tab-vendors"
                    className="vendors"
                  >
                    <div className="card">
                      <h3>Vendor Checklist</h3>
                      <p>
                        {plan.vendors.categories.length} vendor categories to
                        manage
                      </p>

                      <div className="vendor-list" role="list" aria-label="Vendor categories">
                        {plan.vendors.categories.map(
                          (vendor, i) => (
                            <article key={vendor.id || i} className="vendor-card" role="listitem">
                              <h4>{vendor.name}</h4>
                              <p className="vendor-meta">
                                📅 Book {vendor.lead_time_weeks} weeks ahead
                                {vendor.budget_share > 0 &&
                                  ` • 💰 Budget share: ${vendor.budget_share}%`}
                              </p>
                              <div className="vendor-questions">
                                <strong>Key questions to ask:</strong>
                                <ul aria-label={`Questions for ${vendor.name}`}>
                                  {vendor.questions
                                    .slice(0, 3)
                                    .map((q, j) => (
                                      <li key={j}>{q}</li>
                                    ))}
                                </ul>
                              </div>
                              {vendor.diligence && vendor.diligence.length > 0 && (
                                <div className="vendor-questions" style={{ marginTop: '12px' }}>
                                  <strong>Due diligence checklist:</strong>
                                  <ul aria-label={`Due diligence for ${vendor.name}`}>
                                    {vendor.diligence.slice(0, 3).map((d, j) => (
                                      <li key={j}>{d}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </article>
                          ),
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* ---- Ideas Panel ---- */}
                {activeTab === 'ideas' && plan.ideas && (
                  <div
                    id="tabpanel-ideas"
                    role="tabpanel"
                    aria-labelledby="tab-ideas"
                    className="ideas"
                  >
                    {plan.ideas.themes.length > 0 && (
                      <div className="card">
                        <h3>🎨 Theme Ideas</h3>
                        <div className="idea-grid" role="list" aria-label="Theme ideas">
                          {plan.ideas.themes.map((idea) => (
                            <article key={idea.id} className="idea-card" role="listitem">
                              <h4>{idea.title}</h4>
                              <p>{idea.description}</p>
                              {idea.palette && idea.palette.length > 0 && (
                                <div className="palette" aria-label="Color palette">
                                  {idea.palette.map((color, i) => (
                                    <div
                                      key={i}
                                      className="color-swatch"
                                      style={{ backgroundColor: color }}
                                      title={`Color: ${color}`}
                                      aria-label={`Color swatch: ${color}`}
                                      role="img"
                                    />
                                  ))}
                                </div>
                              )}
                              <span
                                className={`cost-badge ${idea.cost_level}`}
                                aria-label={`Cost level: ${idea.cost_level}`}
                              >
                                {idea.cost_level} cost
                              </span>
                              {idea.tags && idea.tags.length > 0 && (
                                <div className="idea-tags" style={{ marginTop: '8px' }}>
                                  {idea.tags.map((tag, i) => (
                                    <span key={i} className="tag" style={{
                                      display: 'inline-block',
                                      padding: '2px 8px',
                                      margin: '2px',
                                      borderRadius: '12px',
                                      fontSize: '12px',
                                      background: 'var(--bg-secondary)',
                                      color: 'var(--text-secondary)',
                                    }}>
                                      #{tag}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </article>
                          ))}
                        </div>
                      </div>
                    )}

                    {plan.ideas.menu && plan.ideas.menu.length > 0 && (
                      <div className="card">
                        <h3>🍽️ Menu Ideas</h3>
                        <div className="idea-grid" role="list" aria-label="Menu ideas">
                          {plan.ideas.menu.map((idea) => (
                            <article key={idea.id} className="idea-card" role="listitem">
                              <h4>{idea.title}</h4>
                              <p>{idea.description}</p>
                              <span className={`cost-badge ${idea.cost_level}`}>
                                {idea.cost_level} cost
                              </span>
                            </article>
                          ))}
                        </div>
                      </div>
                    )}

                    {plan.ideas.activities && plan.ideas.activities.length > 0 && (
                      <div className="card">
                        <h3>🎭 Activity Ideas</h3>
                        <div className="idea-grid" role="list" aria-label="Activity ideas">
                          {plan.ideas.activities.map((idea) => (
                            <article key={idea.id} className="idea-card" role="listitem">
                              <h4>{idea.title}</h4>
                              <p>{idea.description}</p>
                              <span className={`cost-badge ${idea.cost_level}`}>
                                {idea.cost_level} cost
                              </span>
                            </article>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </main>

      {/* ---- Footer ---- */}
      <footer className="app-footer" role="contentinfo">
        <div className="container">
          <p>PlanIt AI © {new Date().getFullYear()} • Your AI-Powered Celebration Planner</p>
        </div>
      </footer>
    </div>
  )
}

export default App
