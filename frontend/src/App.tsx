import { useState } from 'react'
import './App.css'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

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
}

interface Budget {
  total_budget: number
  categories: BudgetCategory[]
  remaining: number
}

interface Task {
  id: string
  title: string
  due_date: string
  priority: string
  status: string
  phase: string
}

interface EventPlan {
  profile: EventProfile
  budget: Budget | null
  timeline: { tasks: Task[] } | null
  vendors: any
  ideas: any
}

function App() {
  const [step, setStep] = useState<'intro' | 'intake' | 'generating' | 'dashboard'>('intro')
  const [eventType, setEventType] = useState<string>('wedding')
  const [freeText, setFreeText] = useState<string>('')
  const [, setEventId] = useState<string>('')
  const [plan, setPlan] = useState<EventPlan | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'overview' | 'budget' | 'timeline' | 'vendors' | 'ideas'>('overview')

  const createEvent = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(`${API_BASE}/events/`, {
        free_text: freeText,
        event_type: eventType
      })
      
      setEventId(response.data.event_id)
      setStep('generating')
      
      // Generate the full plan
      await generatePlan(response.data.event_id)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create event')
      setLoading(false)
    }
  }

  const generatePlan = async (id: string) => {
    try {
      await axios.post(`${API_BASE}/events/${id}/generate`)
      
      // Fetch the generated plan
      const planResponse = await axios.get(`${API_BASE}/events/${id}`)
      setPlan(planResponse.data)
      setStep('dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate plan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <a href="#main-content" className="skip-link">Skip to main content</a>
      
      <header className="app-header">
        <div className="container">
          <h1>🎉 PlanIt AI</h1>
          <p>Your AI-powered celebration planner</p>
        </div>
      </header>

      <main id="main-content" className="app-main">
        <div className="container">
          {step === 'intro' && (
            <div className="intro-section">
              <h2>Plan your perfect celebration</h2>
              <p className="subtitle">Weddings • Birthdays • Community Events</p>
              
              <div className="event-types">
                <button
                  className={`event-type-card ${eventType === 'wedding' ? 'active' : ''}`}
                  onClick={() => { setEventType('wedding'); setStep('intake'); }}
                >
                  <span className="icon">💒</span>
                  <h3>Wedding</h3>
                  <p>Multi-day celebrations, rituals, large guest lists</p>
                </button>
                
                <button
                  className={`event-type-card ${eventType === 'birthday' ? 'active' : ''}`}
                  onClick={() => { setEventType('birthday'); setStep('intake'); }}
                >
                  <span className="icon">🎂</span>
                  <h3>Birthday</h3>
                  <p>Parties, themes, activities for all ages</p>
                </button>
                
                <button
                  className={`event-type-card ${eventType === 'community' ? 'active' : ''}`}
                  onClick={() => { setEventType('community'); setStep('intake'); }}
                >
                  <span className="icon">🎪</span>
                  <h3>Community Event</h3>
                  <p>Festivals, fundraisers, gatherings</p>
                </button>
              </div>
            </div>
          )}

          {step === 'intake' && (
            <div className="intake-section">
              <h2>Tell me about your {eventType}</h2>
              <p>Describe your event in plain language. Include date, location, guests, budget, and any special requirements.</p>
              
              <div className="intake-form">
                <textarea
                  placeholder="Example: Plan a 2-day wedding for 250 guests in Jaipur in February, budget 15 lakh, royal theme"
                  value={freeText}
                  onChange={(e) => setFreeText(e.target.value)}
                  rows={5}
                  aria-label="Event description"
                />
                
                {error && (
                  <div className="error-message" role="alert">
                    {error}
                  </div>
                )}
                
                <div className="button-group">
                  <button
                    className="btn-secondary"
                    onClick={() => setStep('intro')}
                    disabled={loading}
                  >
                    Back
                  </button>
                  <button
                    className="btn-primary"
                    onClick={createEvent}
                    disabled={loading || !freeText.trim()}
                  >
                    {loading ? <span className="loading"></span> : 'Create Plan'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {step === 'generating' && (
            <div className="generating-section">
              <div className="card text-center">
                <div className="loading-spinner"></div>
                <h2>Generating your plan...</h2>
                <p>Creating budget, timeline, vendor checklist, and personalized ideas.</p>
              </div>
            </div>
          )}

          {step === 'dashboard' && plan && (
            <div className="dashboard">
              <div className="dashboard-header">
                <h2>{plan.profile.name}</h2>
                <p>{plan.profile.event_type.toUpperCase()} • {plan.profile.guest_count} guests • ₹{plan.profile.budget_total.toLocaleString()}</p>
              </div>

              <div className="tabs">
                <button
                  className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  Overview
                </button>
                <button
                  className={`tab ${activeTab === 'budget' ? 'active' : ''}`}
                  onClick={() => setActiveTab('budget')}
                >
                  Budget
                </button>
                <button
                  className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
                  onClick={() => setActiveTab('timeline')}
                >
                  Timeline
                </button>
                <button
                  className={`tab ${activeTab === 'vendors' ? 'active' : ''}`}
                  onClick={() => setActiveTab('vendors')}
                >
                  Vendors
                </button>
                <button
                  className={`tab ${activeTab === 'ideas' ? 'active' : ''}`}
                  onClick={() => setActiveTab('ideas')}
                >
                  Ideas
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'overview' && (
                  <div className="overview">
                    <div className="stats-grid">
                      <div className="stat-card">
                        <h3>Budget Status</h3>
                        <p className="stat-value">₹{plan.budget?.remaining.toLocaleString() || 0}</p>
                        <p className="stat-label">Remaining</p>
                      </div>
                      
                      <div className="stat-card">
                        <h3>Tasks</h3>
                        <p className="stat-value">{plan.timeline?.tasks.length || 0}</p>
                        <p className="stat-label">Total tasks</p>
                      </div>
                      
                      <div className="stat-card">
                        <h3>Event Date</h3>
                        <p className="stat-value">{new Date(plan.profile.event_date).toLocaleDateString()}</p>
                        <p className="stat-label">Mark your calendar</p>
                      </div>
                    </div>

                    <div className="card">
                      <h3>Next Steps</h3>
                      {plan.timeline && plan.timeline.tasks.slice(0, 5).map(task => (
                        <div key={task.id} className="task-item">
                          <span className={`priority-badge ${task.priority}`}>{task.priority}</span>
                          <div>
                            <p><strong>{task.title}</strong></p>
                            <p className="task-meta">Due: {new Date(task.due_date).toLocaleDateString()} • {task.phase}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'budget' && plan.budget && (
                  <div className="budget">
                    <div className="card">
                      <h3>Budget Breakdown</h3>
                      <p>Total: ₹{plan.budget.total_budget.toLocaleString()}</p>
                      
                      <div className="budget-list">
                        {plan.budget.categories.map((cat, i) => (
                          <div key={i} className="budget-item">
                            <div className="budget-info">
                              <strong>{cat.name}</strong>
                              <span>{cat.percent}%</span>
                            </div>
                            <div className="budget-bar">
                              <div
                                className="budget-bar-fill"
                                style={{ width: `${cat.percent}%` }}
                              ></div>
                            </div>
                            <div className="budget-amounts">
                              <span>₹{cat.estimated.toLocaleString()}</span>
                              <span className="spent">Spent: ₹{cat.actual.toLocaleString()}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'timeline' && plan.timeline && (
                  <div className="timeline">
                    <div className="card">
                      <h3>Planning Timeline</h3>
                      
                      <div className="task-list">
                        {plan.timeline.tasks.map(task => (
                          <div key={task.id} className="task-card">
                            <div className="task-header">
                              <span className={`priority-badge ${task.priority}`}>{task.priority}</span>
                              <span className={`status-badge ${task.status}`}>{task.status}</span>
                            </div>
                            <h4>{task.title}</h4>
                            <p className="task-meta">
                              <span>📅 {new Date(task.due_date).toLocaleDateString()}</span>
                              <span>• {task.phase}</span>
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'vendors' && plan.vendors && (
                  <div className="vendors">
                    <div className="card">
                      <h3>Vendor Checklist</h3>
                      <p>{plan.vendors.categories.length} vendor categories to consider</p>
                      
                      <div className="vendor-list">
                        {plan.vendors.categories.map((vendor: any, i: number) => (
                          <div key={i} className="vendor-card">
                            <h4>{vendor.name}</h4>
                            <p className="vendor-meta">
                              Book {vendor.lead_time_weeks} weeks ahead • Budget share: {vendor.budget_share}%
                            </p>
                            <div className="vendor-questions">
                              <strong>Key questions:</strong>
                              <ul>
                                {vendor.questions.slice(0, 3).map((q: string, j: number) => (
                                  <li key={j}>{q}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'ideas' && plan.ideas && (
                  <div className="ideas">
                    {plan.ideas.themes.length > 0 && (
                      <div className="card">
                        <h3>Theme Ideas</h3>
                        <div className="idea-grid">
                          {plan.ideas.themes.map((idea: any) => (
                            <div key={idea.id} className="idea-card">
                              <h4>{idea.title}</h4>
                              <p>{idea.description}</p>
                              {idea.palette && idea.palette.length > 0 && (
                                <div className="palette">
                                  {idea.palette.map((color: string, i: number) => (
                                    <div
                                      key={i}
                                      className="color-swatch"
                                      style={{ backgroundColor: color }}
                                      title={color}
                                    ></div>
                                  ))}
                                </div>
                              )}
                              <span className={`cost-badge ${idea.cost_level}`}>{idea.cost_level} cost</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>Built for PromptWars Challenge 5 • PlanIt AI © 2024</p>
        </div>
      </footer>
    </div>
  )
}

export default App
