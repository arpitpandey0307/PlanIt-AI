"""Tests for vendor checklist engine."""
import pytest
from app.engine.vendors import generate_vendor_checklist
from app.schemas.profile import EventProfile, EventType, VenueType


class TestGenerateVendorChecklist:
    """Tests for vendor checklist generation."""

    def test_wedding_vendors_created(self, wedding_profile):
        """Wedding should generate vendor categories."""
        checklist = generate_vendor_checklist(wedding_profile)
        assert checklist is not None
        assert len(checklist.categories) > 0
        assert checklist.event_id == wedding_profile.id

    def test_birthday_vendors_created(self, birthday_profile):
        """Birthday should generate vendor categories."""
        checklist = generate_vendor_checklist(birthday_profile)
        assert checklist is not None
        assert len(checklist.categories) > 0

    def test_community_vendors_created(self, community_profile):
        """Community event should generate vendor categories."""
        checklist = generate_vendor_checklist(community_profile)
        assert checklist is not None
        assert len(checklist.categories) > 0

    def test_vendors_have_questions(self, wedding_profile):
        """All vendor categories should have questions."""
        checklist = generate_vendor_checklist(wedding_profile)
        for cat in checklist.categories:
            assert len(cat.questions) > 0

    def test_vendors_have_diligence(self, wedding_profile):
        """All vendor categories should have diligence items."""
        checklist = generate_vendor_checklist(wedding_profile)
        for cat in checklist.categories:
            assert len(cat.diligence) > 0

    def test_vendors_have_lead_times(self, wedding_profile):
        """All vendor categories should have lead times."""
        checklist = generate_vendor_checklist(wedding_profile)
        for cat in checklist.categories:
            assert cat.lead_time_weeks >= 0

    def test_vendors_have_unique_ids(self, wedding_profile):
        """All vendor categories should have unique IDs."""
        checklist = generate_vendor_checklist(wedding_profile)
        ids = [cat.id for cat in checklist.categories]
        assert len(ids) == len(set(ids))

    def test_vendors_initial_status(self, wedding_profile):
        """All vendor categories should start as not_started."""
        checklist = generate_vendor_checklist(wedding_profile)
        for cat in checklist.categories:
            assert cat.status.value == "not_started"


class TestOutdoorVendors:
    """Tests for outdoor venue specific vendors."""

    def test_outdoor_adds_tent_vendor(self, outdoor_wedding_profile):
        """Outdoor wedding should add tent/canopy vendor."""
        checklist = generate_vendor_checklist(outdoor_wedding_profile)
        names = [c.name.lower() for c in checklist.categories]
        assert any("tent" in name or "canopy" in name for name in names)


class TestLargeEventVendors:
    """Tests for large event specific vendors."""

    def test_large_event_adds_transport(self, large_community_profile):
        """Large events should add transport vendor."""
        checklist = generate_vendor_checklist(large_community_profile)
        names = [c.name.lower() for c in checklist.categories]
        assert any("transport" in name for name in names)

    def test_small_event_no_transport(self, birthday_profile):
        """Small events should not add transport vendor."""
        checklist = generate_vendor_checklist(birthday_profile)
        names = [c.name.lower() for c in checklist.categories]
        assert not any("transport" in name for name in names)

