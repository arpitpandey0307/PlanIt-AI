"""Tests for Pydantic schema validations."""
import pytest
from datetime import date, timedelta
from app.schemas.profile import EventProfile, EventProfileInput, EventType, VenueType, AudienceMix
from app.schemas.budget import Budget, BudgetCategory
from app.schemas.ideas import IdeaCard, IdeaKind, CostLevel, IdeasCollection
from app.schemas.timeline import Task, TaskPriority, TaskStatus, TaskOwner, Timeline, RunOfShowSlot
from app.schemas.vendors import VendorCategory, VendorChecklist, VendorStatus
from app.schemas.plan import EventPlan
from pydantic import ValidationError
from datetime import time


class TestEventProfile:
    """Tests for EventProfile schema."""

    def test_valid_profile(self):
        profile = EventProfile(
            id="evt_123456789012",
            name="Test Event",
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=30),
            city="Delhi",
            guest_count=100,
            budget_total=500000,
        )
        assert profile.id == "evt_123456789012"
        assert profile.currency == "INR"

    def test_invalid_guest_count_zero(self):
        with pytest.raises(ValidationError):
            EventProfile(
                id="evt_123456789012",
                name="Test",
                event_type=EventType.WEDDING,
                event_date=date.today(),
                city="Delhi",
                guest_count=0,
                budget_total=100000,
            )

    def test_invalid_guest_count_negative(self):
        with pytest.raises(ValidationError):
            EventProfile(
                id="evt_123456789012",
                name="Test",
                event_type=EventType.WEDDING,
                event_date=date.today(),
                city="Delhi",
                guest_count=-5,
                budget_total=100000,
            )

    def test_invalid_budget_zero(self):
        with pytest.raises(ValidationError):
            EventProfile(
                id="evt_123456789012",
                name="Test",
                event_type=EventType.WEDDING,
                event_date=date.today(),
                city="Delhi",
                guest_count=100,
                budget_total=0,
            )

    def test_end_date_before_start_raises(self):
        with pytest.raises(ValidationError):
            EventProfile(
                id="evt_123456789012",
                name="Test",
                event_type=EventType.WEDDING,
                event_date=date.today() + timedelta(days=30),
                event_end_date=date.today(),
                city="Delhi",
                guest_count=100,
                budget_total=100000,
            )

    def test_end_date_after_start_valid(self):
        profile = EventProfile(
            id="evt_123456789012",
            name="Test",
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=30),
            event_end_date=date.today() + timedelta(days=31),
            city="Delhi",
            guest_count=100,
            budget_total=100000,
        )
        assert profile.event_end_date == date.today() + timedelta(days=31)

    def test_default_values(self):
        profile = EventProfile(
            id="evt_123456789012",
            name="Test",
            event_type=EventType.BIRTHDAY,
            event_date=date.today(),
            city="Mumbai",
            guest_count=50,
            budget_total=50000,
        )
        assert profile.venue_type == VenueType.BOTH
        assert profile.audience == AudienceMix.MIXED
        assert profile.currency == "INR"


class TestEventProfileInput:
    """Tests for EventProfileInput schema."""

    def test_free_text_input(self):
        inp = EventProfileInput(free_text="Plan a wedding for 200 guests")
        assert inp.free_text == "Plan a wedding for 200 guests"

    def test_sanitization_removes_script(self):
        inp = EventProfileInput(free_text="<script>alert('xss')</script>hello")
        assert "<script>" not in inp.free_text
        assert "</script>" not in inp.free_text

    def test_sanitization_removes_javascript(self):
        inp = EventProfileInput(free_text="javascript:alert('xss')")
        assert "javascript:" not in inp.free_text

    def test_max_length_free_text(self):
        inp = EventProfileInput(free_text="a" * 2000)
        assert len(inp.free_text) == 2000

    def test_too_long_free_text(self):
        with pytest.raises(ValidationError):
            EventProfileInput(free_text="a" * 2001)


class TestBudgetSchema:
    """Tests for Budget schema."""

    def test_valid_budget(self):
        budget = Budget(
            event_id="evt_123456789012",
            total_budget=100000,
            categories=[
                BudgetCategory(name="Venue", percent=50.0, estimated=50000),
                BudgetCategory(name="Food", percent=50.0, estimated=50000),
            ],
        )
        assert budget.total_budget == 100000
        assert len(budget.categories) == 2

    def test_total_spent_property(self):
        budget = Budget(
            event_id="evt_123456789012",
            total_budget=100000,
            categories=[
                BudgetCategory(name="Venue", percent=50.0, estimated=50000, actual=20000),
                BudgetCategory(name="Food", percent=50.0, estimated=50000, actual=10000),
            ],
        )
        assert budget.total_spent == 30000

    def test_remaining_property(self):
        budget = Budget(
            event_id="evt_123456789012",
            total_budget=100000,
            categories=[
                BudgetCategory(name="Venue", percent=50.0, estimated=50000, actual=20000),
                BudgetCategory(name="Food", percent=50.0, estimated=50000, actual=10000),
            ],
        )
        assert budget.remaining == 70000


class TestTaskSchema:
    """Tests for Task schema."""

    def test_valid_task(self):
        task = Task(
            id="task_001",
            title="Book venue",
            due_date=date.today(),
            phase="12 weeks out",
        )
        assert task.status == TaskStatus.NOT_STARTED
        assert task.priority == TaskPriority.MEDIUM

    def test_task_with_all_fields(self):
        task = Task(
            id="task_001",
            title="Book venue",
            description="Find and book the perfect venue",
            due_date=date.today(),
            owner=TaskOwner.SELF,
            priority=TaskPriority.URGENT,
            status=TaskStatus.IN_PROGRESS,
            phase="12 weeks out",
            notes="Check availability",
        )
        assert task.priority == TaskPriority.URGENT
        assert task.status == TaskStatus.IN_PROGRESS


class TestIdeaCardSchema:
    """Tests for IdeaCard schema."""

    def test_valid_idea(self):
        idea = IdeaCard(
            id="idea_001",
            kind=IdeaKind.THEME,
            title="Royal Theme",
            description="A royal themed wedding",
        )
        assert idea.cost_level == CostLevel.MEDIUM
        assert idea.saved is False

    def test_idea_with_palette(self):
        idea = IdeaCard(
            id="idea_001",
            kind=IdeaKind.THEME,
            title="Test",
            description="Test desc",
            palette=["#FF0000", "#00FF00"],
        )
        assert len(idea.palette) == 2


class TestEventPlanSchema:
    """Tests for EventPlan schema."""

    def test_empty_plan(self, wedding_profile):
        plan = EventPlan(profile=wedding_profile)
        assert plan.is_complete is False
        assert plan.completion_status["profile"] is True
        assert plan.completion_status["budget"] is False

    def test_complete_check(self, wedding_profile):
        plan = EventPlan(profile=wedding_profile)
        assert plan.is_complete is False

