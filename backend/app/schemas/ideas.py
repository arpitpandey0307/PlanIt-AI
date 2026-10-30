"""Ideas and suggestions schema."""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class IdeaKind(str, Enum):
    """Type of idea."""
    THEME = "theme"
    DECOR = "decor"
    MENU = "menu"
    ACTIVITY = "activity"
    INVITATION = "invitation"
    FAVOUR = "favour"
    ENTERTAINMENT = "entertainment"


class CostLevel(str, Enum):
    """Relative cost indication."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"


class IdeaCard(BaseModel):
    """Individual idea or suggestion."""
    
    id: str = Field(..., description="Idea ID")
    kind: IdeaKind = Field(..., description="Type of idea")
    title: str = Field(..., min_length=1, max_length=200, description="Idea title")
    description: str = Field(..., min_length=1, max_length=2000, description="Detailed description")
    palette: List[str] = Field(default_factory=list, description="Color palette (hex codes)")
    cost_level: CostLevel = Field(default=CostLevel.MEDIUM, description="Relative cost")
    saved: bool = Field(default=False, description="User saved this idea")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "idea_001",
                "kind": "theme",
                "title": "Royal Rajasthani",
                "description": "Embrace the grandeur of Rajasthan with gold and maroon decor, traditional folk music, puppet shows, and a regal entrance on elephant or horse. The mandap features Jaali work and marigold garlands.",
                "palette": ["#FFD700", "#8B0000", "#FFA500"],
                "cost_level": "high",
                "saved": False,
                "tags": ["traditional", "cultural", "luxurious", "rajasthani"]
            }
        }


class IdeasCollection(BaseModel):
    """Collection of ideas for an event."""
    
    event_id: str = Field(..., description="Associated event ID")
    themes: List[IdeaCard] = Field(default_factory=list, description="Theme concepts")
    decor: List[IdeaCard] = Field(default_factory=list, description="Decoration ideas")
    menu: List[IdeaCard] = Field(default_factory=list, description="Menu suggestions")
    activities: List[IdeaCard] = Field(default_factory=list, description="Activities and entertainment")
    invitations: List[IdeaCard] = Field(default_factory=list, description="Invitation wording")
    favours: List[IdeaCard] = Field(default_factory=list, description="Return gift ideas")
    
    @property
    def all_ideas(self) -> List[IdeaCard]:
        """Get all ideas as a flat list."""
        return (
            self.themes + self.decor + self.menu + 
            self.activities + self.invitations + self.favours
        )
    
    @property
    def saved_ideas(self) -> List[IdeaCard]:
        """Get only saved ideas."""
        return [idea for idea in self.all_ideas if idea.saved]
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_12345",
                "themes": [],
                "decor": [],
                "menu": [],
                "activities": [],
                "invitations": [],
                "favours": []
            }
        }
