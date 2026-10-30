"""Events API endpoints."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Optional
from ..schemas.profile import EventProfileInput
from ..schemas.plan import EventPlan, ChatMessage
from ..agents.intake import extract_profile
from ..agents.ideas import generate_ideas
from ..engine.budget import generate_budget
from ..engine.timeline import generate_timeline
from ..engine.vendors import generate_vendor_checklist
from ..llm.client import LLMClient
from ..config import get_settings
import json
from datetime import datetime

router = APIRouter()
settings = get_settings()

# In-memory storage (would be database in production)
events_store: Dict[str, EventPlan] = {}
chat_store: Dict[str, list] = {}


@router.post("/", response_model=Dict)
async def create_event(input_data: EventProfileInput):
    """
    Create a new event from profile or free text.
    Returns event ID immediately, generation happens via /generate endpoint.
    """
    try:
        # Initialize LLM client
        llm = LLMClient(settings.google_api_key)
        
        # Extract profile
        profile = await extract_profile(input_data, llm)
        
        # Create event plan with profile only
        plan = EventPlan(
            profile=profile,
            budget=None,
            timeline=None,
            vendors=None,
            ideas=None
        )
        
        # Store plan
        events_store[profile.id] = plan
        chat_store[profile.id] = []
        
        return {
            "event_id": profile.id,
            "message": "Event created successfully. Call /generate to create the full plan."
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error creating event: {e}")
        raise HTTPException(status_code=500, detail="Failed to create event")


@router.get("/{event_id}", response_model=EventPlan)
async def get_event(event_id: str):
    """Fetch the full event plan."""
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return events_store[event_id]


@router.post("/{event_id}/generate")
async def generate_plan(event_id: str, background_tasks: BackgroundTasks):
    """
    Generate complete event plan.
    Generates budget, timeline, vendors, and ideas.
    """
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    plan = events_store[event_id]
    
    try:
        # Initialize LLM client
        llm = LLMClient(settings.google_api_key)
        
        # Generate all sections (in parallel in production)
        budget = generate_budget(plan.profile)
        timeline = generate_timeline(plan.profile)
        vendors = generate_vendor_checklist(plan.profile)
        ideas = await generate_ideas(plan.profile, llm)
        
        # Update plan
        plan.budget = budget
        plan.timeline = timeline
        plan.vendors = vendors
        plan.ideas = ideas
        
        events_store[event_id] = plan
        
        return {
            "event_id": event_id,
            "status": "completed",
            "message": "Plan generated successfully",
            "completion": plan.completion_status
        }
    
    except Exception as e:
        print(f"Error generating plan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {str(e)}")


@router.post("/{event_id}/generate/{section}")
async def regenerate_section(event_id: str, section: str):
    """
    Regenerate a specific section: budget, timeline, vendors, or ideas.
    """
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    plan = events_store[event_id]
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
        else:
            raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
        
        events_store[event_id] = plan
        
        return {
            "event_id": event_id,
            "section": section,
            "status": "regenerated",
            "message": f"{section.title()} regenerated successfully"
        }
    
    except Exception as e:
        print(f"Error regenerating {section}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate {section}")


@router.post("/{event_id}/chat")
async def chat_with_assistant(event_id: str, message: Dict):
    """
    Chat with the assistant to refine the plan.
    """
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    plan = events_store[event_id]
    user_message = message.get("content", "")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    try:
        # Store user message
        chat_store[event_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Simple intent detection
        user_lower = user_message.lower()
        actions_taken = []
        response_text = "I understand your request. "
        
        # Budget modifications
        if "reduce" in user_lower and "budget" in user_lower:
            # Extract percentage if present
            import re
            percent_match = re.search(r'(\d+)\s*%', user_message)
            if percent_match:
                reduction = int(percent_match.group(1))
                old_budget = plan.profile.budget_total
                new_budget = old_budget * (1 - reduction / 100)
                plan.profile.budget_total = new_budget
                
                # Regenerate budget
                plan.budget = generate_budget(plan.profile)
                actions_taken.append(f"Reduced budget from ₹{old_budget:,.0f} to ₹{new_budget:,.0f}")
                response_text += f"I've reduced the budget by {reduction}% and updated all allocations. "
        
        # Guest count modifications
        if "guest" in user_lower and any(word in user_lower for word in ["reduce", "increase", "change"]):
            import re
            guest_match = re.search(r'(\d+)\s*guests?', user_message)
            if guest_match:
                old_guests = plan.profile.guest_count
                new_guests = int(guest_match.group(1))
                plan.profile.guest_count = new_guests
                
                # Regenerate affected sections
                plan.budget = generate_budget(plan.profile)
                plan.timeline = generate_timeline(plan.profile)
                plan.vendors = generate_vendor_checklist(plan.profile)
                
                actions_taken.append(f"Changed guest count from {old_guests} to {new_guests}")
                response_text += f"I've updated the guest count and regenerated the budget, timeline, and vendor checklist. "
        
        # Venue type change
        if "outdoor" in user_lower or "indoor" in user_lower:
            if "outdoor" in user_lower and plan.profile.venue_type.value != "outdoor":
                plan.profile.venue_type = "outdoor"
                plan.budget = generate_budget(plan.profile)
                plan.vendors = generate_vendor_checklist(plan.profile)
                actions_taken.append("Changed venue to outdoor")
                response_text += "I've switched to outdoor venue and added weather contingencies. "
        
        # If no specific actions, provide general response
        if not actions_taken:
            response_text = "I've noted your request. To make specific changes, you can ask me to modify the budget, guest count, venue type, or regenerate any section. What would you like to change?"
        
        # Store assistant response
        chat_store[event_id].append({
            "role": "assistant",
            "content": response_text,
            "actions_taken": actions_taken,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update plan
        events_store[event_id] = plan
        
        return {
            "role": "assistant",
            "content": response_text,
            "actions_taken": actions_taken,
            "updated_sections": ["budget", "timeline"] if actions_taken else []
        }
    
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


@router.patch("/{event_id}/tasks/{task_id}")
async def update_task(event_id: str, task_id: str, update_data: Dict):
    """Update a task's status or details."""
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    plan = events_store[event_id]
    if not plan.timeline:
        raise HTTPException(status_code=400, detail="Timeline not generated yet")
    
    # Find and update task
    task = next((t for t in plan.timeline.tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update allowed fields
    if "status" in update_data:
        task.status = update_data["status"]
    if "notes" in update_data:
        task.notes = update_data["notes"]
    
    events_store[event_id] = plan
    
    return {"message": "Task updated successfully", "task": task}


@router.patch("/{event_id}/budget")
async def update_budget(event_id: str, update_data: Dict):
    """Update budget category actual spend."""
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    plan = events_store[event_id]
    if not plan.budget:
        raise HTTPException(status_code=400, detail="Budget not generated yet")
    
    category_name = update_data.get("category")
    actual_spend = update_data.get("actual")
    
    if not category_name or actual_spend is None:
        raise HTTPException(status_code=400, detail="Category and actual spend required")
    
    # Find and update category
    category = next((c for c in plan.budget.categories if c.name == category_name), None)
    if not category:
        raise HTTPException(status_code=404, detail="Budget category not found")
    
    category.actual = float(actual_spend)
    events_store[event_id] = plan
    
    return {
        "message": "Budget updated successfully",
        "total_spent": plan.budget.total_spent,
        "remaining": plan.budget.remaining
    }


@router.get("/{event_id}/export")
async def export_plan(event_id: str, format: str = "pdf"):
    """
    Export the plan in various formats: pdf, csv, ics.
    """
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    plan = events_store[event_id]
    
    if format == "pdf":
        # Simple PDF export (would use reportlab in production)
        return {
            "message": "PDF export coming soon",
            "event_id": event_id,
            "format": "pdf"
        }
    elif format == "csv":
        # Export budget as CSV
        if not plan.budget:
            raise HTTPException(status_code=400, detail="Budget not generated")
        
        csv_lines = ["Category,Percent,Estimated,Actual,Remaining"]
        for cat in plan.budget.categories:
            remaining = cat.estimated - cat.actual
            csv_lines.append(f"{cat.name},{cat.percent},{cat.estimated},{cat.actual},{remaining}")
        
        csv_content = "\n".join(csv_lines)
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=budget_{event_id}.csv"}
        )
    elif format == "ics":
        # Export timeline as calendar
        return {
            "message": "ICS export coming soon",
            "event_id": event_id,
            "format": "ics"
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """Delete an event plan."""
    if event_id not in events_store:
        raise HTTPException(status_code=404, detail="Event not found")
    
    del events_store[event_id]
    if event_id in chat_store:
        del chat_store[event_id]
    
    return {"message": "Event deleted successfully"}
