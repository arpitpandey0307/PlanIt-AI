"""Tests for budget engine."""
import pytest
from datetime import date
from app.schemas.profile import EventProfile, EventType, VenueType, AudienceMix
from app.engine.budget import generate_budget


def test_budget_sum_equals_total():
    """Budget categories should sum exactly to total budget."""
    profile = EventProfile(
        id="test_001",
        name="Test Wedding",
        event_type=EventType.WEDDING,
        event_date=date(2024, 6, 15),
        city="Delhi",
        venue_type=VenueType.INDOOR,
        guest_count=200,
        budget_total=1000000,
        currency="INR",
        audience=AudienceMix.MIXED
    )
    
    budget = generate_budget(profile)
    
    # Check that all categories sum to total budget
    total_estimated = sum(cat.estimated for cat in budget.categories)
    assert abs(total_estimated - budget.total_budget) < 1.0, "Budget categories must sum to total"


def test_budget_percentages_sum_to_100():
    """Budget percentages should sum to 100%."""
    profile = EventProfile(
        id="test_002",
        name="Test Birthday",
        event_type=EventType.BIRTHDAY,
        event_date=date(2024, 6, 15),
        city="Mumbai",
        venue_type=VenueType.INDOOR,
        guest_count=50,
        budget_total=50000,
        currency="INR",
        audience=AudienceMix.KIDS
    )
    
    budget = generate_budget(profile)
    
    # Check percentages sum to 100
    total_percent = sum(cat.percent for cat in budget.categories)
    assert abs(total_percent - 100.0) < 0.1, "Budget percentages must sum to 100%"


def test_outdoor_venue_adds_contingency():
    """Outdoor venue should increase contingency."""
    profile_indoor = EventProfile(
        id="test_003",
        name="Indoor Event",
        event_type=EventType.WEDDING,
        event_date=date(2024, 6, 15),
        city="Delhi",
        venue_type=VenueType.INDOOR,
        guest_count=200,
        budget_total=1000000,
        currency="INR",
        audience=AudienceMix.MIXED
    )
    
    profile_outdoor = EventProfile(
        id="test_004",
        name="Outdoor Event",
        event_type=EventType.WEDDING,
        event_date=date(2024, 6, 15),
        city="Delhi",
        venue_type=VenueType.OUTDOOR,
        guest_count=200,
        budget_total=1000000,
        currency="INR",
        audience=AudienceMix.MIXED
    )
    
    budget_indoor = generate_budget(profile_indoor)
    budget_outdoor = generate_budget(profile_outdoor)
    
    # Find contingency categories
    contingency_indoor = next((c for c in budget_indoor.categories if "contingency" in c.name.lower()), None)
    contingency_outdoor = next((c for c in budget_outdoor.categories if "contingency" in c.name.lower()), None)
    
    assert contingency_indoor and contingency_outdoor
    assert contingency_outdoor.percent > contingency_indoor.percent, "Outdoor should have higher contingency"


def test_feasibility_warning_for_low_budget():
    """Low per-guest budget should trigger feasibility warning."""
    profile = EventProfile(
        id="test_005",
        name="Low Budget Wedding",
        event_type=EventType.WEDDING,
        event_date=date(2024, 6, 15),
        city="Mumbai",  # Tier 1 city
        venue_type=VenueType.INDOOR,
        guest_count=500,  # Many guests
        budget_total=100000,  # Only 200 per guest
        currency="INR",
        audience=AudienceMix.MIXED
    )
    
    budget = generate_budget(profile)
    
    assert budget.feasibility_warning is not None, "Should warn about low budget"
    assert "tight" in budget.feasibility_warning.lower()


def test_assumptions_generated():
    """Budget should include assumptions."""
    profile = EventProfile(
        id="test_006",
        name="Test Event",
        event_type=EventType.WEDDING,
        event_date=date(2024, 6, 15),
        city="Jaipur",
        venue_type=VenueType.INDOOR,
        guest_count=200,
        budget_total=1000000,
        currency="INR",
        audience=AudienceMix.MIXED
    )
    
    budget = generate_budget(profile)
    
    assert len(budget.assumptions) > 0, "Budget should include assumptions"
    assert any("INR" in assumption for assumption in budget.assumptions)


def test_saving_tips_generated():
    """Budget should include saving tips."""
    profile = EventProfile(
        id="test_007",
        name="Test Event",
        event_type=EventType.WEDDING,
        event_date=date(2024, 6, 15),
        city="Delhi",
        venue_type=VenueType.INDOOR,
        guest_count=200,
        budget_total=1000000,
        currency="INR",
        audience=AudienceMix.MIXED
    )
    
    budget = generate_budget(profile)
    
    assert len(budget.saving_tips) > 0, "Budget should include saving tips"
