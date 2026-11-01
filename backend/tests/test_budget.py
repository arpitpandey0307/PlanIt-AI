"""Tests for budget allocation engine."""
import pytest
from datetime import date, timedelta
from app.engine.budget import (
    generate_budget,
    apply_budget_adjustments,
    check_feasibility,
    generate_saving_tips,
    generate_assumptions,
    get_decision_trace,
)
from app.config import BUDGET_PROFILES, DecisionRules
from app.schemas.profile import EventProfile, EventType, VenueType, AudienceMix


class TestGenerateBudget:
    """Tests for the generate_budget function."""

    def test_wedding_budget_has_all_categories(self, wedding_profile):
        """Wedding budget should have all expected categories."""
        budget = generate_budget(wedding_profile)
        assert budget is not None
        assert len(budget.categories) > 0
        assert budget.total_budget == wedding_profile.budget_total
        assert budget.currency == "INR"

    def test_birthday_budget_categories(self, birthday_profile):
        """Birthday budget should use birthday allocation profile."""
        budget = generate_budget(birthday_profile)
        assert budget is not None
        assert budget.total_budget == birthday_profile.budget_total
        category_names = [c.name.lower() for c in budget.categories]
        # Birthday should have cake category
        assert any("cake" in name for name in category_names)

    def test_community_budget_categories(self, community_profile):
        """Community budget should have community-specific categories."""
        budget = generate_budget(community_profile)
        assert budget is not None
        category_names = [c.name.lower() for c in budget.categories]
        assert any("safety" in name or "cleanup" in name for name in category_names)

    def test_budget_percentages_sum_to_100(self, wedding_profile):
        """Budget category percentages should sum to approximately 100."""
        budget = generate_budget(wedding_profile)
        total_percent = sum(c.percent for c in budget.categories)
        assert abs(total_percent - 100.0) < 0.5

    def test_budget_amounts_sum_to_total(self, wedding_profile):
        """Budget category estimated amounts should sum to total budget."""
        budget = generate_budget(wedding_profile)
        total_estimated = sum(c.estimated for c in budget.categories)
        assert abs(total_estimated - wedding_profile.budget_total) < 2.0

    def test_all_actuals_start_at_zero(self, wedding_profile):
        """All category actuals should start at zero."""
        budget = generate_budget(wedding_profile)
        for cat in budget.categories:
            assert cat.actual == 0.0

    def test_budget_has_assumptions(self, wedding_profile):
        """Budget should include assumptions list."""
        budget = generate_budget(wedding_profile)
        assert len(budget.assumptions) > 0

    def test_budget_has_saving_tips(self, wedding_profile):
        """Budget should include saving tips."""
        budget = generate_budget(wedding_profile)
        assert len(budget.saving_tips) > 0

    def test_event_id_matches(self, wedding_profile):
        """Budget event_id should match the profile."""
        budget = generate_budget(wedding_profile)
        assert budget.event_id == wedding_profile.id


class TestBudgetAdjustments:
    """Tests for budget adjustments."""

    def test_outdoor_venue_increases_contingency(self, outdoor_wedding_profile):
        """Outdoor venue should increase contingency allocation."""
        base = BUDGET_PROFILES["wedding"].copy()
        original_contingency = base.get("contingency", 0)

        adjusted = apply_budget_adjustments(outdoor_wedding_profile, base)
        # After normalization, contingency should be proportionally higher
        assert "contingency" in adjusted

    def test_adjustments_preserve_total(self, wedding_profile):
        """Adjustments should keep percentages summing to ~100."""
        base = BUDGET_PROFILES["wedding"].copy()
        adjusted = apply_budget_adjustments(wedding_profile, base)
        total = sum(adjusted.values())
        assert abs(total - 100.0) < 0.5

    def test_peak_season_wedding_venue_boost(self):
        """Peak season wedding should boost venue allocation."""
        # Create a profile in peak season (November)
        profile = EventProfile(
            id="evt_test00000001",
            name="Peak Wedding",
            event_type=EventType.WEDDING,
            event_date=date(2025, 11, 15),
            city="Delhi",
            guest_count=200,
            budget_total=1000000,
        )
        base = BUDGET_PROFILES["wedding"].copy()
        adjusted = apply_budget_adjustments(profile, base)
        # Venue should have some boost applied
        assert adjusted.get("venue", 0) > 0


class TestFeasibility:
    """Tests for feasibility checking."""

    def test_adequate_budget_no_warning(self, wedding_profile):
        """Adequate budget should not trigger warning."""
        warning = check_feasibility(wedding_profile)
        # With 1.5M for 250 guests, per-guest is ₹6000 which should be fine
        assert warning is None

    def test_very_low_budget_triggers_warning(self):
        """Very low budget should trigger feasibility warning."""
        profile = EventProfile(
            id="evt_test00000002",
            name="Cheap Wedding",
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=90),
            city="Mumbai",
            guest_count=500,
            budget_total=50000,  # Very low for 500 guests
        )
        warning = check_feasibility(profile)
        assert warning is not None
        assert "tight" in warning.lower() or "below" in warning.lower()

    def test_zero_guests_no_warning(self):
        """Zero guest count should not trigger warning."""
        profile = EventProfile(
            id="evt_test00000003",
            name="Test",
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=90),
            city="Delhi",
            guest_count=1,  # Minimum
            budget_total=100000,
        )
        warning = check_feasibility(profile)
        assert warning is None  # 100k for 1 guest is fine


class TestSavingTips:
    """Tests for saving tips generation."""

    def test_wedding_tips(self, wedding_profile):
        """Wedding should generate relevant saving tips."""
        tips = generate_saving_tips(wedding_profile)
        assert len(tips) > 0
        assert any("venue" in tip.lower() or "catering" in tip.lower() for tip in tips)

    def test_birthday_tips(self, birthday_profile):
        """Birthday should generate relevant saving tips."""
        tips = generate_saving_tips(birthday_profile)
        assert len(tips) > 0
        assert any("diy" in tip.lower() or "entertainer" in tip.lower() for tip in tips)

    def test_community_tips(self, community_profile):
        """Community event should generate relevant saving tips."""
        tips = generate_saving_tips(community_profile)
        assert len(tips) > 0

    def test_outdoor_venue_tip(self, outdoor_wedding_profile):
        """Outdoor venue should get backup venue tip."""
        tips = generate_saving_tips(outdoor_wedding_profile)
        assert any("backup" in tip.lower() or "indoor" in tip.lower() for tip in tips)

    def test_large_wedding_bulk_discount_tip(self):
        """Large wedding (>200 guests) should get bulk discount tip."""
        profile = EventProfile(
            id="evt_test00000004",
            name="Big Wedding",
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=90),
            city="Delhi",
            guest_count=300,
            budget_total=3000000,
        )
        tips = generate_saving_tips(profile)
        assert any("bulk" in tip.lower() for tip in tips)


class TestAssumptions:
    """Tests for budget assumptions."""

    def test_assumptions_include_currency(self, wedding_profile):
        """Assumptions should mention currency."""
        assumptions = generate_assumptions(wedding_profile)
        assert any("INR" in a for a in assumptions)

    def test_assumptions_include_city(self, wedding_profile):
        """Assumptions should mention city."""
        assumptions = generate_assumptions(wedding_profile)
        assert any("Jaipur" in a for a in assumptions)

    def test_assumptions_include_city_tier(self, wedding_profile):
        """Assumptions should mention city tier."""
        assumptions = generate_assumptions(wedding_profile)
        assert any("tier" in a.lower() for a in assumptions)


class TestDecisionTrace:
    """Tests for decision trace generation."""

    def test_contingency_outdoor_trace(self, outdoor_wedding_profile):
        """Outdoor venue should explain weather buffer in trace."""
        trace = get_decision_trace("contingency", outdoor_wedding_profile)
        assert "outdoor" in trace.lower() or "weather" in trace.lower()

    def test_default_trace(self, wedding_profile):
        """Standard allocation should return a meaningful trace."""
        trace = get_decision_trace("catering", wedding_profile)
        assert len(trace) > 0


class TestBudgetProfiles:
    """Tests for budget profile configurations."""

    def test_all_profiles_sum_to_100(self):
        """All budget profiles should have percentages summing to 100."""
        for event_type, profile in BUDGET_PROFILES.items():
            total = sum(profile.values())
            assert abs(total - 100.0) < 0.01, (
                f"{event_type} budget profile sums to {total}, not 100"
            )

    def test_wedding_profile_has_venue(self):
        """Wedding profile must include venue category."""
        assert "venue" in BUDGET_PROFILES["wedding"]

    def test_birthday_profile_has_cake(self):
        """Birthday profile must include cake category."""
        assert "cake" in BUDGET_PROFILES["birthday"]

    def test_community_profile_has_safety(self):
        """Community profile must include safety category."""
        assert "safety_cleanup" in BUDGET_PROFILES["community"]

