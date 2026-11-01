"""Events API endpoints with improved security and error handling."""
import logging
import re
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..agents.ideas import generate_ideas
from ..agents.intake import extract_profile
from ..config import get_settings
from ..engine.budget import generate_budget
from ..engine.timeline import generate_timeline
from ..engine.vendors import generate_vendor_checklist
from ..llm.client import LLMClient
from ..schemas.plan import EventPlan
from ..schemas.profile import EventProfileInput

logger = logging.getLogger("planit_ai.api.events")

router = APIRouter()
settings = get_settings()

# In-memory storage (would be database in production)
events_store: Dict[str, EventPlan] = {}
chat_store: Dict[str, list] = {}

# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

_EVENT_ID_RE = re.compile(r"^evt_[a-f0-9]{12}$")
_SECTION_WHITELIST = frozenset({"budget", "timeline", "vendors", "ideas"})
_MAX_CHAT_MESSAGE_LENGTH = 5000


def _validate_event_id(event_id: str) -> str:
    """Validate event ID format to prevent injection attacks."""
    if not _EVENT_ID_RE.match(event_id):
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    return event_id


def _get_plan_or_404(event_id: str) -> EventPlan:
    """Retrieve event plan or raise 404."""
    event_id = _validate_event_id(event_id)
    plan = events_store.get(event_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return plan


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/", response_model=Dict)
async def create_event(input_data: EventProfileInput):
    """Create a new event from free text or structured input."""
    try:
        llm = LLMClient(settings.google_api_key)
        profile = await extract_profile(input_data, llm)

        plan = EventPlan(
            profile=profile,
            budget=None,
            timeline=None,
            vendors=None,
            ideas=None,
        )

        events_store[profile.id] = plan
        chat_store[profile.id] = []

        logger.info("Event created: %s (%s)", profile.id, profile.event_type.value)
        return {"event_id": profile.id, "message": "Event created"}

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create event")
        raise HTTPException(status_code=500, detail="Failed to create event") from exc


@router.get("/{event_id}", response_model=EventPlan)
async def get_event(event_id: str):
    """Get event plan by ID."""
    return _get_plan_or_404(event_id)


@router.post("/{event_id}/generate")
async def generate_plan(event_id: str):
    """Generate complete event plan (budget, timeline, vendors, ideas)."""
    plan = _get_plan_or_404(event_id)

    try:
        llm = LLMClient(settings.google_api_key)

        # Generate all sections
        budget = generate_budget(plan.profile)
        timeline = generate_timeline(plan.profile)
        vendors = generate_vendor_checklist(plan.profile)
        ideas = await generate_ideas(plan.profile, llm)

        plan.budget = budget
        plan.timeline = timeline
        plan.vendors = vendors
        plan.ideas = ideas

        events_store[event_id] = plan
        logger.info("Plan generated for event %s", event_id)

        return {
            "event_id": event_id,
            "status": "completed",
            "message": "Plan generated successfully",
            "completion": plan.completion_status,
        }

    except Exception as exc:
        logger.exception("Error generating plan for %s", event_id)
        raise HTTPException(
            status_code=500, detail="Failed to generate plan"
        ) from exc


@router.post("/{event_id}/generate/{section}")
async def regenerate_section(event_id: str, section: str):
    """Regenerate a specific plan section."""
    if section not in _SECTION_WHITELIST:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid section '{section}'. Must be one of: {', '.join(sorted(_SECTION_WHITELIST))}",
        )

    plan = _get_plan_or_404(event_id)
    llm = LLMClient(settings.google_api_key)

    try:
        if section == "budget":
            plan.budget = generate_budget(plan.profile)
        elif section == "timeline":
            plan.timeline = generate_timeline(plan.profile)
        elif section == "vendors":
            plan.vendors = generate_vendor_checklist(plan.profile)
        elif section == "ideas":
            plan.ideas = await generate_ideas(plan.profile, llm)

        events_store[event_id] = plan
        logger.info("Section '%s' regenerated for event %s", section, event_id)

        return {
            "event_id": event_id,
            "section": section,
            "status": "regenerated",
            "message": f"{section.title()} regenerated successfully",
        }

    except Exception as exc:
        logger.exception("Error regenerating %s for %s", section, event_id)
        raise HTTPException(
            status_code=500, detail=f"Failed to regenerate {section}"
        ) from exc


@router.post("/{event_id}/chat")
async def chat_with_assistant(event_id: str, message: Dict):
    """Chat with the assistant to refine the plan."""
    plan = _get_plan_or_404(event_id)
    user_message = str(message.get("content", "")).strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message content is required")

    if len(user_message) > _MAX_CHAT_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Message too long (max {_MAX_CHAT_MESSAGE_LENGTH} characters)",
        )

    # Sanitize input
    user_message = _sanitize_chat_input(user_message)

    try:
        chat_store.setdefault(event_id, []).append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        user_lower = user_message.lower()
        actions_taken: list[str] = []
        response_text = "I understand your request. "

        # Budget modifications
        if "reduce" in user_lower and "budget" in user_lower:
            percent_match = re.search(r"(\d+)\s*%", user_message)
            if percent_match:
                reduction = min(int(percent_match.group(1)), 90)  # Cap at 90%
                old_budget = plan.profile.budget_total
                new_budget = old_budget * (1 - reduction / 100)
                plan.profile.budget_total = new_budget
                plan.budget = generate_budget(plan.profile)
                actions_taken.append(
                    f"Reduced budget from ₹{old_budget:,.0f} to ₹{new_budget:,.0f}"
                )
                response_text += (
                    f"I've reduced the budget by {reduction}% and updated all allocations. "
                )

        # Guest count modifications
        if "guest" in user_lower and any(
            word in user_lower for word in ["reduce", "increase", "change"]
        ):
            guest_match = re.search(r"(\d+)\s*guests?", user_message)
            if guest_match:
                new_guests = int(guest_match.group(1))
                if 1 <= new_guests <= 10000:
                    old_guests = plan.profile.guest_count
                    plan.profile.guest_count = new_guests
                    plan.budget = generate_budget(plan.profile)
                    plan.timeline = generate_timeline(plan.profile)
                    plan.vendors = generate_vendor_checklist(plan.profile)
                    actions_taken.append(
                        f"Changed guest count from {old_guests} to {new_guests}"
                    )
                    response_text += "I've updated the guest count and regenerated the budget, timeline, and vendor checklist. "

        # Venue type change
        if "outdoor" in user_lower or "indoor" in user_lower:
            if "outdoor" in user_lower and plan.profile.venue_type.value != "outdoor":
                plan.profile.venue_type = "outdoor"
                plan.budget = generate_budget(plan.profile)
                plan.vendors = generate_vendor_checklist(plan.profile)
                actions_taken.append("Changed venue to outdoor")
                response_text += "I've switched to outdoor venue and added weather contingencies. "

        if not actions_taken:
            response_text = (
                "I've noted your request. To make specific changes, you can ask me "
                "to modify the budget, guest count, venue type, or regenerate any section. "
                "What would you like to change?"
            )

        chat_store[event_id].append(
            {
                "role": "assistant",
                "content": response_text,
                "actions_taken": actions_taken,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        events_store[event_id] = plan

        return {
            "role": "assistant",
            "content": response_text,
            "actions_taken": actions_taken,
            "updated_sections": ["budget", "timeline"] if actions_taken else [],
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Chat error for event %s", event_id)
        raise HTTPException(
            status_code=500, detail="Failed to process chat message"
        ) from exc


@router.patch("/{event_id}/tasks/{task_id}")
async def update_task(event_id: str, task_id: str, update_data: Dict):
    """Update a task's status or details."""
    plan = _get_plan_or_404(event_id)

    if not plan.timeline:
        raise HTTPException(status_code=400, detail="Timeline not generated yet")

    task = next((t for t in plan.timeline.tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if "status" in update_data:
        allowed_statuses = {"not_started", "in_progress", "completed", "cancelled"}
        if update_data["status"] not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(sorted(allowed_statuses))}",
            )
        task.status = update_data["status"]

    if "notes" in update_data:
        notes = str(update_data["notes"])[:500]  # Truncate to max length
        task.notes = notes

    events_store[event_id] = plan
    return {"message": "Task updated successfully", "task": task}


@router.patch("/{event_id}/budget")
async def update_budget(event_id: str, update_data: Dict):
    """Update budget category actual spend."""
    plan = _get_plan_or_404(event_id)

    if not plan.budget:
        raise HTTPException(status_code=400, detail="Budget not generated yet")

    category_name = update_data.get("category")
    actual_spend = update_data.get("actual")

    if not category_name or actual_spend is None:
        raise HTTPException(
            status_code=400, detail="Category and actual spend required"
        )

    try:
        actual_spend = float(actual_spend)
        if actual_spend < 0:
            raise ValueError("Negative spend not allowed")
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=400, detail="Actual spend must be a non-negative number"
        ) from exc

    category = next(
        (c for c in plan.budget.categories if c.name == category_name), None
    )
    if not category:
        raise HTTPException(status_code=404, detail="Budget category not found")

    category.actual = actual_spend
    events_store[event_id] = plan

    return {
        "message": "Budget updated successfully",
        "total_spent": plan.budget.total_spent,
        "remaining": plan.budget.remaining,
    }


@router.get("/{event_id}/export")
async def export_plan(event_id: str, format: str = "csv"):
    """Export the plan in CSV format."""
    plan = _get_plan_or_404(event_id)

    allowed_formats = {"csv", "pdf", "ics"}
    if format not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{format}'. Must be one of: {', '.join(sorted(allowed_formats))}",
        )

    if format == "csv":
        if not plan.budget:
            raise HTTPException(status_code=400, detail="Budget not generated")

        csv_lines = ["Category,Percent,Estimated,Actual,Remaining"]
        for cat in plan.budget.categories:
            remaining = cat.estimated - cat.actual
            # Escape CSV values
            name = cat.name.replace('"', '""')
            csv_lines.append(
                f'"{name}",{cat.percent},{cat.estimated},{cat.actual},{remaining}'
            )

        csv_content = "\n".join(csv_lines)
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=budget_{event_id}.csv"
            },
        )
    elif format == "pdf":
        return {
            "message": "PDF export coming soon",
            "event_id": event_id,
            "format": "pdf",
        }
    elif format == "ics":
        return {
            "message": "ICS export coming soon",
            "event_id": event_id,
            "format": "ics",
        }


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """Delete an event plan."""
    _get_plan_or_404(event_id)  # Validates and checks existence

    del events_store[event_id]
    chat_store.pop(event_id, None)

    logger.info("Event deleted: %s", event_id)
    return {"message": "Event deleted successfully"}


# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------


def _sanitize_chat_input(text: str) -> str:
    """Sanitize user chat input to prevent injection attacks."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove potential script injection
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    # Remove null bytes
    text = text.replace("\x00", "")
    return text.strip()
