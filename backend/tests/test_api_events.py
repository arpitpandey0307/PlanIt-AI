"""Tests for API event endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.events import events_store, chat_store


@pytest.fixture(autouse=True)
def clear_stores():
    """Clear in-memory stores before each test."""
    events_store.clear()
    chat_store.clear()
    yield
    events_store.clear()
    chat_store.clear()


async def _create_event(client: AsyncClient) -> str:
    """Helper to create an event and return its ID."""
    response = await client.post(
        "/api/events/",
        json={
            "free_text": "Plan a wedding for 200 guests in Delhi, budget 10 lakh",
            "event_type": "wedding",
        },
    )
    assert response.status_code == 200
    return response.json()["event_id"]


class TestCreateEvent:
    """Tests for POST /api/events/"""

    @pytest.mark.asyncio
    async def test_create_event_success(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/events/",
                json={
                    "free_text": "Plan a wedding for 200 guests in Delhi, budget 10 lakh",
                    "event_type": "wedding",
                },
            )
        assert response.status_code == 200
        data = response.json()
        assert "event_id" in data
        assert data["message"] == "Event created"

    @pytest.mark.asyncio
    async def test_create_event_birthday(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/events/",
                json={
                    "free_text": "Plan a birthday party for 50 guests in Mumbai",
                    "event_type": "birthday",
                },
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_event_community(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/events/",
                json={
                    "free_text": "Plan a community festival for 500 people in Chennai",
                    "event_type": "community",
                },
            )
        assert response.status_code == 200


class TestGetEvent:
    """Tests for GET /api/events/{event_id}"""

    @pytest.mark.asyncio
    async def test_get_event_success(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.get(f"/api/events/{event_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["profile"]["id"] == event_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_event(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/events/evt_000000000000")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_invalid_event_id_format(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/events/invalid-id")
        assert response.status_code == 400


class TestGeneratePlan:
    """Tests for POST /api/events/{event_id}/generate"""

    @pytest.mark.asyncio
    async def test_generate_plan_success(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.post(f"/api/events/{event_id}/generate")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    @pytest.mark.asyncio
    async def test_generate_plan_nonexistent(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/events/evt_000000000000/generate")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generated_plan_has_all_sections(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            await client.post(f"/api/events/{event_id}/generate")
            response = await client.get(f"/api/events/{event_id}")
        data = response.json()
        assert data["budget"] is not None
        assert data["timeline"] is not None
        assert data["vendors"] is not None
        assert data["ideas"] is not None


class TestRegenerateSection:
    """Tests for POST /api/events/{event_id}/generate/{section}"""

    @pytest.mark.asyncio
    async def test_regenerate_budget(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            await client.post(f"/api/events/{event_id}/generate")
            response = await client.post(f"/api/events/{event_id}/generate/budget")
        assert response.status_code == 200
        assert response.json()["section"] == "budget"

    @pytest.mark.asyncio
    async def test_regenerate_timeline(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.post(f"/api/events/{event_id}/generate/timeline")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_regenerate_invalid_section(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.post(f"/api/events/{event_id}/generate/invalid")
        assert response.status_code == 400


class TestChat:
    """Tests for POST /api/events/{event_id}/chat"""

    @pytest.mark.asyncio
    async def test_chat_message(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            await client.post(f"/api/events/{event_id}/generate")
            response = await client.post(
                f"/api/events/{event_id}/chat",
                json={"content": "What about the venue?"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "assistant"
        assert len(data["content"]) > 0

    @pytest.mark.asyncio
    async def test_chat_empty_message(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.post(
                f"/api/events/{event_id}/chat",
                json={"content": ""},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_chat_budget_reduction(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            await client.post(f"/api/events/{event_id}/generate")
            response = await client.post(
                f"/api/events/{event_id}/chat",
                json={"content": "Reduce the budget by 20%"},
            )
        assert response.status_code == 200
        data = response.json()
        assert len(data["actions_taken"]) > 0


class TestExport:
    """Tests for GET /api/events/{event_id}/export"""

    @pytest.mark.asyncio
    async def test_export_csv(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            await client.post(f"/api/events/{event_id}/generate")
            response = await client.get(f"/api/events/{event_id}/export?format=csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_invalid_format(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.get(f"/api/events/{event_id}/export?format=xml")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_export_csv_no_budget(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.get(f"/api/events/{event_id}/export?format=csv")
        assert response.status_code == 400


class TestDeleteEvent:
    """Tests for DELETE /api/events/{event_id}"""

    @pytest.mark.asyncio
    async def test_delete_event(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            response = await client.delete(f"/api/events/{event_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/events/evt_000000000000")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_after_delete(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            event_id = await _create_event(client)
            await client.delete(f"/api/events/{event_id}")
            response = await client.get(f"/api/events/{event_id}")
        assert response.status_code == 404

