import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import App from './App'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    isAxiosError: vi.fn(() => false),
  },
}))

const mockAxios = axios as unknown as {
  post: ReturnType<typeof vi.fn>
  get: ReturnType<typeof vi.fn>
  isAxiosError: ReturnType<typeof vi.fn>
}

// Sample plan data for dashboard tests
const samplePlan = {
  profile: {
    id: 'evt_test12345678',
    name: "Test Wedding",
    event_type: 'wedding',
    event_date: '2025-06-15',
    city: 'Delhi',
    guest_count: 200,
    budget_total: 1000000,
    currency: 'INR',
  },
  budget: {
    total_budget: 1000000,
    categories: [
      { name: 'Venue', percent: 20, estimated: 200000, actual: 0 },
      { name: 'Catering', percent: 30, estimated: 300000, actual: 50000 },
    ],
    remaining: 950000,
    assumptions: ['Based on Delhi pricing'],
    saving_tips: ['Book on weekdays for discounts'],
    feasibility_warning: null,
  },
  timeline: {
    tasks: [
      {
        id: 'task_001',
        title: 'Book venue',
        description: 'Reserve the wedding venue',
        due_date: '2025-03-15',
        priority: 'urgent',
        status: 'not_started',
        phase: '12 weeks out',
        owner: 'self',
      },
      {
        id: 'task_002',
        title: 'Book caterer',
        due_date: '2025-03-20',
        priority: 'high',
        status: 'in_progress',
        phase: '12 weeks out',
        owner: 'self',
      },
    ],
  },
  vendors: {
    categories: [
      {
        id: 'vendor_001',
        name: 'Venue',
        lead_time_weeks: 12,
        budget_share: 20,
        questions: ['Capacity?', 'Indoor/outdoor?', 'Catering included?'],
        diligence: ['Visit in person', 'Check reviews'],
        status: 'not_started',
      },
    ],
  },
  ideas: {
    themes: [
      {
        id: 'idea_001',
        kind: 'theme',
        title: 'Royal Rajasthani',
        description: 'Grand Rajasthani theme with gold and maroon.',
        palette: ['#FFD700', '#8B0000'],
        cost_level: 'high',
        tags: ['traditional', 'luxurious'],
      },
    ],
    menu: [
      {
        id: 'idea_menu_001',
        kind: 'menu',
        title: 'North Indian Feast',
        description: 'Traditional north Indian menu.',
        cost_level: 'medium',
      },
    ],
    activities: [
      {
        id: 'idea_act_001',
        kind: 'activity',
        title: 'Sangeet Night',
        description: 'Music and dance performances.',
        cost_level: 'medium',
      },
    ],
  },
}

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ---- INTRO STEP ----

  describe('Intro Step', () => {
    it('renders the app title', () => {
      render(<App />)
      expect(screen.getByText('🎉 PlanIt AI')).toBeInTheDocument()
    })

    it('renders subtitle text', () => {
      render(<App />)
      expect(screen.getByText(/Plan your perfect celebration/i)).toBeInTheDocument()
    })

    it('renders all three event type cards', () => {
      render(<App />)
      expect(screen.getByText('Wedding')).toBeInTheDocument()
      expect(screen.getByText('Birthday')).toBeInTheDocument()
      expect(screen.getByText('Community Event')).toBeInTheDocument()
    })

    it('event type cards have aria-labels', () => {
      render(<App />)
      expect(screen.getByLabelText(/Plan a Wedding/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Plan a Birthday/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Plan a Community Event/i)).toBeInTheDocument()
    })

    it('clicking Wedding card navigates to intake', () => {
      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Wedding/i))
      expect(screen.getByText(/Tell me about your wedding/i)).toBeInTheDocument()
    })

    it('clicking Birthday card navigates to intake', () => {
      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Birthday/i))
      expect(screen.getByText(/Tell me about your birthday/i)).toBeInTheDocument()
    })

    it('clicking Community card navigates to intake', () => {
      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Community Event/i))
      expect(screen.getByText(/Tell me about your community/i)).toBeInTheDocument()
    })
  })

  // ---- ACCESSIBILITY ----

  describe('Accessibility', () => {
    it('has a skip-to-content link', () => {
      render(<App />)
      const skipLink = screen.getByText('Skip to main content')
      expect(skipLink).toBeInTheDocument()
      expect(skipLink).toHaveAttribute('href', '#main-content')
    })

    it('main content has correct id', () => {
      render(<App />)
      expect(document.getElementById('main-content')).toBeInTheDocument()
    })

    it('header has banner role', () => {
      render(<App />)
      expect(screen.getByRole('banner')).toBeInTheDocument()
    })

    it('main has main role', () => {
      render(<App />)
      expect(screen.getByRole('main')).toBeInTheDocument()
    })

    it('footer has contentinfo role', () => {
      render(<App />)
      expect(screen.getByRole('contentinfo')).toBeInTheDocument()
    })

    it('event type group has group role', () => {
      render(<App />)
      expect(screen.getByRole('group')).toBeInTheDocument()
    })
  })

  // ---- INTAKE STEP ----

  describe('Intake Step', () => {
    beforeEach(() => {
      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Wedding/i))
    })

    it('shows textarea for event description', () => {
      expect(screen.getByLabelText(/Event description/i)).toBeInTheDocument()
    })

    it('shows Back button', () => {
      expect(screen.getByLabelText(/Go back/i)).toBeInTheDocument()
    })

    it('shows Create Plan button', () => {
      expect(screen.getByLabelText(/Create event plan/i)).toBeInTheDocument()
    })

    it('Create Plan button is disabled when textarea is empty', () => {
      const btn = screen.getByLabelText(/Create event plan/i)
      expect(btn).toBeDisabled()
    })

    it('Create Plan button becomes enabled when text is entered', async () => {
      const textarea = screen.getByLabelText(/Event description/i)
      await userEvent.type(textarea, 'Plan a wedding for 200 guests')
      const btn = screen.getByLabelText(/Create event plan/i)
      expect(btn).not.toBeDisabled()
    })

    it('Back button returns to intro', () => {
      fireEvent.click(screen.getByLabelText(/Go back/i))
      expect(screen.getByText(/Plan your perfect celebration/i)).toBeInTheDocument()
    })

    it('textarea has aria-required', () => {
      const textarea = screen.getByLabelText(/Event description/i)
      expect(textarea).toHaveAttribute('aria-required', 'true')
    })

    it('textarea has maxLength', () => {
      const textarea = screen.getByLabelText(/Event description/i)
      expect(textarea).toHaveAttribute('maxLength', '2000')
    })
  })

  // ---- API INTERACTION ----

  describe('Event Creation', () => {
    it('shows error on API failure', async () => {
      mockAxios.post.mockRejectedValueOnce({
        response: { data: { detail: 'Server error' } },
      })
      mockAxios.isAxiosError.mockReturnValue(true)

      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Wedding/i))
      const textarea = screen.getByLabelText(/Event description/i)
      await userEvent.type(textarea, 'Plan a wedding')
      fireEvent.click(screen.getByLabelText(/Create event plan/i))

      await waitFor(() => {
        const alert = document.querySelector('[role="alert"]')
        expect(alert).toBeInTheDocument()
      })
    })

    it('shows generating state on success', async () => {
      mockAxios.post.mockResolvedValueOnce({
        data: { event_id: 'evt_test12345678' },
      })
      // The generate call - make it pending
      mockAxios.post.mockReturnValueOnce(new Promise(() => {}))

      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Wedding/i))
      const textarea = screen.getByLabelText(/Event description/i)
      await userEvent.type(textarea, 'Plan a wedding')
      fireEvent.click(screen.getByLabelText(/Create event plan/i))

      await waitFor(() => {
        expect(screen.getByText(/Generating your plan/i)).toBeInTheDocument()
      })
    })
  })

  // ---- DASHBOARD ----

  describe('Dashboard', () => {
    beforeEach(async () => {
      // Mock successful creation and generation
      mockAxios.post
        .mockResolvedValueOnce({ data: { event_id: 'evt_test12345678' } })
        .mockResolvedValueOnce({ data: { status: 'completed' } })
      mockAxios.get.mockResolvedValueOnce({ data: samplePlan })

      render(<App />)
      fireEvent.click(screen.getByLabelText(/Plan a Wedding/i))
      const textarea = screen.getByLabelText(/Event description/i)
      await userEvent.type(textarea, 'Plan a wedding')
      fireEvent.click(screen.getByLabelText(/Create event plan/i))

      await waitFor(() => {
        expect(screen.getByText('Test Wedding')).toBeInTheDocument()
      })
    })

    it('shows the event name', () => {
      expect(screen.getByText('Test Wedding')).toBeInTheDocument()
    })

    it('shows event details', () => {
      expect(screen.getByText(/200 guests/)).toBeInTheDocument()
    })

    it('has tab navigation with tablist role', () => {
      expect(screen.getByRole('tablist')).toBeInTheDocument()
    })

    it('shows all five tabs', () => {
      expect(screen.getByRole('tab', { name: 'Overview' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Budget' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Timeline' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Vendors' })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: 'Ideas' })).toBeInTheDocument()
    })

    it('Overview tab is active by default', () => {
      const tab = screen.getByRole('tab', { name: 'Overview' })
      expect(tab).toHaveAttribute('aria-selected', 'true')
    })

    it('shows budget remaining in overview', () => {
      expect(screen.getByText(/Remaining/i)).toBeInTheDocument()
    })

    it('shows task count in overview', () => {
      expect(screen.getByText('2')).toBeInTheDocument() // 2 tasks
    })

    it('shows next steps tasks', () => {
      expect(screen.getByText('Book venue')).toBeInTheDocument()
      expect(screen.getByText('Book caterer')).toBeInTheDocument()
    })

    it('clicking Budget tab shows budget breakdown', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Budget' }))
      await waitFor(() => {
        expect(screen.getByText('Budget Breakdown')).toBeInTheDocument()
        expect(screen.getByText('Venue')).toBeInTheDocument()
        expect(screen.getByText('Catering')).toBeInTheDocument()
      })
    })

    it('budget items have progressbar role', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Budget' }))
      await waitFor(() => {
        const progressBars = screen.getAllByRole('progressbar')
        expect(progressBars.length).toBeGreaterThan(0)
      })
    })

    it('clicking Timeline tab shows tasks', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Timeline' }))
      await waitFor(() => {
        expect(screen.getByText('Planning Timeline')).toBeInTheDocument()
      })
    })

    it('clicking Vendors tab shows vendor list', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Vendors' }))
      await waitFor(() => {
        expect(screen.getByText('Vendor Checklist')).toBeInTheDocument()
        expect(screen.getByText('1 vendor categories to manage')).toBeInTheDocument()
      })
    })

    it('clicking Ideas tab shows theme ideas', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Ideas' }))
      await waitFor(() => {
        expect(screen.getByText('Royal Rajasthani')).toBeInTheDocument()
      })
    })

    it('ideas show color swatches', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Ideas' }))
      await waitFor(() => {
        const swatches = screen.getAllByRole('img')
        expect(swatches.length).toBeGreaterThan(0)
      })
    })

    it('ideas show tags', async () => {
      fireEvent.click(screen.getByRole('tab', { name: 'Ideas' }))
      await waitFor(() => {
        expect(screen.getByText('#traditional')).toBeInTheDocument()
        expect(screen.getByText('#luxurious')).toBeInTheDocument()
      })
    })
  })

  // ---- FOOTER ----

  describe('Footer', () => {
    it('shows footer with copyright', () => {
      render(<App />)
      expect(screen.getByText(/PlanIt AI ©/)).toBeInTheDocument()
    })

    it('shows current year in footer', () => {
      render(<App />)
      const year = new Date().getFullYear().toString()
      expect(screen.getByText(new RegExp(year))).toBeInTheDocument()
    })
  })
})

