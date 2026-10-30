"""Complete event plan schema."""
from typing import Optional
from pydantic import BaseModel, Field
from .profile import EventProfile
from .budget import Budget
from .timeline import Timeline
from .vendors import VendorChecklist
from .ideas import IdeasCollection


class EventPlan(BaseModel):
    """Complete event plan with all components."""
    
    profile: EventProfile = Field(..., description="Event profile")
    budget: Optional[Budget] = Field(None, description="Budget breakdown")
    timeline: Optional[Timeline] = Field(None, description="Task timeline")
    vendors: Optional[VendorChecklist] = Field(None, description="Vendor checklist")
    ideas: Optional[IdeasCollection] = Field(None, description="Ideas and suggestions")
    
    @property
    def is_complete(self) -> bool:
        """Check if all sections are generated."""
        return all([
            self.budget is not None,
            self.timeline is not None,
            self.vendors is not None,
            self.ideas is not None
        ])
    
    @property
    def completion_status(self) -> dict:
        """Get completion status of each section."""
        return {
            "profile": True,
            "budget": self.budget is not None,
            "timeline": self.timeline is not None,
            "vendors": self.vendors is not None,
            "ideas": self.ideas is not None,
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "profile": {"id": "evt_12345", "name": "Test Event"},
                "budget": None,
                "timeline": None,
                "vendors": None,
                "ideas": None
            }
        }


class ChatMessage(BaseModel):
    """Chat message for plan refinement."""
    
    id: str = Field(..., description="Message ID")
    event_id: str = Field(..., description="Associated event ID")
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    actions_taken: list = Field(default_factory=list, description="Actions performed")
    timestamp: str = Field(..., description="ISO timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "msg_001",
                "event_id": "evt_12345",
                "role": "user",
                "content": "Reduce the budget by 20%",
                "actions_taken": [],
                "timestamp": "2024-02-15T10:30:00Z"
            }
        }
