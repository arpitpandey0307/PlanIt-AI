"""Shared fixtures for backend tests."""
import os
import pytest
from datetime import date, timedelta

# Set test environment variables BEFORE importing app modules
os.environ["GOOGLE_API_KEY"] = "test-key-for-testing"
os.environ["ENVIRONMENT"] = "testing"
os.environ["FRONTEND_URL"] = "http://localhost:5173"

from app.schemas.profile import EventProfile, EventType, VenueType, AudienceMix


@pytest.fixture
def wedding_profile() -> EventProfile:
    """Create a sample wedding profile."""
    return EventProfile(
        id="evt_aabbccddee01",
        name="Priya & Rahul's Wedding",
        event_type=EventType.WEDDING,
        event_date=date.today() + timedelta(days=90),
        city="Jaipur",
        venue_type=VenueType.BOTH,
        guest_count=250,
        budget_total=1500000,
        currency="INR",
        theme="Royal Rajasthani",
        audience=AudienceMix.MIXED,
        dietary_needs="Vegetarian only",
        cultural_notes="Hindu ceremonies",
        must_haves="Mehendi, Sangeet",
    )


@pytest.fixture
def birthday_profile() -> EventProfile:
    """Create a sample birthday profile."""
    return EventProfile(
        id="evt_aabbccddee02",
        name="Arjun's 5th Birthday",
        event_type=EventType.BIRTHDAY,
        event_date=date.today() + timedelta(days=30),
        city="Mumbai",
        venue_type=VenueType.INDOOR,
        guest_count=50,
        budget_total=100000,
        currency="INR",
        audience=AudienceMix.KIDS,
    )


@pytest.fixture
def community_profile() -> EventProfile:
    """Create a sample community event profile."""
    return EventProfile(
        id="evt_aabbccddee03",
        name="Diwali Mela 2024",
        event_type=EventType.COMMUNITY,
        event_date=date.today() + timedelta(days=60),
        city="Delhi",
        venue_type=VenueType.OUTDOOR,
        guest_count=500,
        budget_total=500000,
        currency="INR",
        audience=AudienceMix.MIXED,
    )


@pytest.fixture
def short_notice_profile() -> EventProfile:
    """Create a profile with short notice (< 14 days)."""
    return EventProfile(
        id="evt_aabbccddee04",
        name="Last Minute Birthday",
        event_type=EventType.BIRTHDAY,
        event_date=date.today() + timedelta(days=7),
        city="Bangalore",
        venue_type=VenueType.INDOOR,
        guest_count=30,
        budget_total=50000,
        currency="INR",
    )


@pytest.fixture
def outdoor_wedding_profile() -> EventProfile:
    """Create an outdoor wedding profile."""
    return EventProfile(
        id="evt_aabbccddee05",
        name="Garden Wedding",
        event_type=EventType.WEDDING,
        event_date=date.today() + timedelta(days=120),
        city="Pune",
        venue_type=VenueType.OUTDOOR,
        guest_count=300,
        budget_total=2000000,
        currency="INR",
    )


@pytest.fixture
def large_community_profile() -> EventProfile:
    """Create a large community event (200+ guests)."""
    return EventProfile(
        id="evt_aabbccddee06",
        name="City Festival",
        event_type=EventType.COMMUNITY,
        event_date=date.today() + timedelta(days=90),
        city="Chennai",
        venue_type=VenueType.OUTDOOR,
        guest_count=1000,
        budget_total=1000000,
        currency="INR",
    )

