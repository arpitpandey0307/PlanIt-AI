"""Tests for LLM client."""
import pytest
from app.llm.client import LLMClient, FakeLLMClient
import json


class TestFakeLLMClient:
    """Tests for the FakeLLMClient."""

    @pytest.mark.asyncio
    async def test_fake_client_no_api_key(self):
        """FakeLLMClient should work without API key."""
        client = FakeLLMClient()
        assert client.model is None

    @pytest.mark.asyncio
    async def test_profile_extraction_fallback(self):
        """Should return profile JSON for extraction prompts."""
        client = FakeLLMClient()
        result = await client.generate("Extract profile from text")
        data = json.loads(result)
        assert "name" in data
        assert "event_type" in data

    @pytest.mark.asyncio
    async def test_ideas_fallback(self):
        """Should return ideas JSON for ideas prompts."""
        client = FakeLLMClient()
        result = await client.generate("Generate ideas for the event")
        data = json.loads(result)
        assert "themes" in data

    @pytest.mark.asyncio
    async def test_generic_fallback(self):
        """Should return unavailable message for other prompts."""
        client = FakeLLMClient()
        result = await client.generate("Something random")
        assert "unavailable" in result.lower() or "template" in result.lower()


class TestLLMClientInit:
    """Tests for LLMClient initialization."""

    def test_init_without_api_key(self):
        """LLMClient with empty key should have no model."""
        client = LLMClient("")
        assert client.model is None

    def test_init_with_test_key(self):
        """LLMClient with test key should attempt initialization."""
        # This may fail gracefully since 'test-key' is invalid
        client = LLMClient("test-key")
        # Model may be None if google-generativeai import fails
        # That's OK - the fallback should work

    def test_fallback_response_profile(self):
        """Fallback response for profile extraction."""
        client = LLMClient("")
        result = client._fallback_response("extract profile data")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_fallback_response_ideas(self):
        """Fallback response for ideas generation."""
        client = LLMClient("")
        result = client._fallback_response("generate ideas")
        data = json.loads(result)
        assert "themes" in data

