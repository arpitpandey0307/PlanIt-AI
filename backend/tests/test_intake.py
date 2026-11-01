"""Tests for intake agent profile extraction."""
import pytest
from datetime import date, timedelta
from app.agents.intake import extract_profile, extract_from_text
from app.schemas.profile import EventProfileInput, EventType, VenueType, AudienceMix
from app.llm.client import FakeLLMClient


@pytest.fixture
def fake_llm():
    """Create a fake LLM client for testing."""
    return FakeLLMClient()


class TestExtractProfile:
    """Tests for the extract_profile function."""

    @pytest.mark.asyncio
    async def test_structured_input_all_fields(self, fake_llm):
        """Fully structured input should create profile directly."""
        input_data = EventProfileInput(
            name="Test Wedding",
            event_type=EventType.WEDDING,
            event_date=date.today() + timedelta(days=90),
            guest_count=200,
            budget_total=1000000,
            city="Mumbai",
            venue_type=VenueType.INDOOR,
        )
        profile = await extract_profile(input_data, fake_llm)
        assert profile.name == "Test Wedding"
        assert profile.event_type == EventType.WEDDING
        assert profile.guest_count == 200
        assert profile.budget_total == 1000000
        assert profile.city == "Mumbai"

    @pytest.mark.asyncio
    async def test_free_text_wedding_extraction(self, fake_llm):
        """Free text mentioning wedding should extract wedding type."""
        input_data = EventProfileInput(
            free_text="Plan a wedding for 250 guests in Jaipur, budget 15 lakh"
        )
        profile = await extract_profile(input_data, fake_llm)
        assert profile is not None
        assert profile.event_type == EventType.WEDDING
        assert profile.id.startswith("evt_")

    @pytest.mark.asyncio
    async def test_free_text_birthday_extraction(self, fake_llm):
        """Free text mentioning birthday should extract birthday type."""
        input_data = EventProfileInput(
            free_text="Plan a birthday party for 50 guests in Mumbai"
        )
        profile = await extract_profile(input_data, fake_llm)
        assert profile.event_type == EventType.BIRTHDAY

    @pytest.mark.asyncio
    async def test_free_text_community_extraction(self, fake_llm):
        """Free text mentioning community should extract community type."""
        input_data = EventProfileInput(
            free_text="Plan a community festival for 500 people in Delhi"
        )
        profile = await extract_profile(input_data, fake_llm)
        assert profile.event_type == EventType.COMMUNITY

    @pytest.mark.asyncio
    async def test_insufficient_input_raises(self, fake_llm):
        """Empty input should raise ValueError."""
        input_data = EventProfileInput()
        with pytest.raises(ValueError):
            await extract_profile(input_data, fake_llm)


class TestExtractFromText:
    """Tests for text extraction rules."""

    @pytest.mark.asyncio
    async def test_guest_count_extraction(self, fake_llm):
        """Should extract guest count from text."""
        result = await extract_from_text("party for 150 guests", fake_llm)
        assert result["guest_count"] == 150

    @pytest.mark.asyncio
    async def test_guest_count_people(self, fake_llm):
        """Should extract guest count using 'people' keyword."""
        result = await extract_from_text("event for 300 people", fake_llm)
        assert result["guest_count"] == 300

    @pytest.mark.asyncio
    async def test_budget_lakh_extraction(self, fake_llm):
        """Should extract budget in lakhs."""
        result = await extract_from_text("budget 15 lakh", fake_llm)
        assert result["budget_total"] == 1500000

    @pytest.mark.asyncio
    async def test_budget_k_extraction(self, fake_llm):
        """Should extract budget with 'k' suffix."""
        result = await extract_from_text("budget 500k", fake_llm)
        assert result["budget_total"] == 500000

    @pytest.mark.asyncio
    async def test_city_mumbai_extraction(self, fake_llm):
        """Should extract Mumbai as city."""
        result = await extract_from_text("wedding in Mumbai", fake_llm)
        assert result["city"] == "Mumbai"

    @pytest.mark.asyncio
    async def test_city_delhi_extraction(self, fake_llm):
        """Should extract Delhi as city."""
        result = await extract_from_text("party in delhi", fake_llm)
        assert result["city"] == "Delhi"

    @pytest.mark.asyncio
    async def test_city_bangalore_extraction(self, fake_llm):
        """Should extract Bangalore as city."""
        result = await extract_from_text("event in bangalore", fake_llm)
        assert result["city"] == "Bangalore"

    @pytest.mark.asyncio
    async def test_outdoor_venue_extraction(self, fake_llm):
        """Should extract outdoor venue type."""
        result = await extract_from_text("outdoor wedding", fake_llm)
        assert result["venue_type"] == "outdoor"

    @pytest.mark.asyncio
    async def test_indoor_venue_extraction(self, fake_llm):
        """Should extract indoor venue type."""
        result = await extract_from_text("indoor birthday party", fake_llm)
        assert result["venue_type"] == "indoor"

    @pytest.mark.asyncio
    async def test_default_event_date(self, fake_llm):
        """Should set default event date ~90 days out."""
        result = await extract_from_text("plan a wedding", fake_llm)
        assert "event_date" in result
        expected = date.today() + timedelta(days=90)
        assert abs((result["event_date"] - expected).days) <= 1

    @pytest.mark.asyncio
    async def test_wedding_type_detection(self, fake_llm):
        """Should detect wedding event type."""
        result = await extract_from_text("wedding ceremony", fake_llm)
        assert result["event_type"] == "wedding"

    @pytest.mark.asyncio
    async def test_festival_maps_to_community(self, fake_llm):
        """Festival keyword should map to community type."""
        result = await extract_from_text("plan a festival", fake_llm)
        assert result["event_type"] == "community"

    @pytest.mark.asyncio
    async def test_mela_maps_to_community(self, fake_llm):
        """Mela keyword should map to community type."""
        result = await extract_from_text("organize a mela", fake_llm)
        assert result["event_type"] == "community"

