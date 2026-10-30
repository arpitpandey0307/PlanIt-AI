"""Event profile schema."""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class EventType(str, Enum):
    """Supported event types."""
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    COMMUNITY = "community"
    CUSTOM = "custom"


class VenueType(str, Enum):
    """Venue type preference."""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    BOTH = "both"


class AudienceMix(str, Enum):
    """Audience composition."""
    KIDS = "kids"
    ADULTS = "adults"
    MIXED = "mixed"
    ELDERS = "elders"


class EventProfile(BaseModel):
    """Structured event profile that all agents read."""
    
    # Core identifiers
    id: str = Field(..., description="Unique event identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Event name")
    event_type: EventType = Field(..., description="Type of event")
    
    # Date and location
    event_date: date = Field(..., description="Event date")
    event_end_date: Optional[date] = Field(None, description="End date for multi-day events")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    venue_type: VenueType = Field(default=VenueType.BOTH, description="Venue preference")
    
    # Scale and budget
    guest_count: int = Field(..., gt=0, le=10000, description="Number of guests")
    budget_total: float = Field(..., gt=0, le=100_000_000, description="Total budget")
    currency: str = Field(default="INR", description="Currency code")
    
    # Preferences
    theme: Optional[str] = Field(None, max_length=500, description="Theme or style")
    audience: AudienceMix = Field(default=AudienceMix.MIXED, description="Audience type")
    dietary_needs: Optional[str] = Field(None, max_length=500, description="Dietary requirements")
    cultural_notes: Optional[str] = Field(None, max_length=500, description="Cultural or religious needs")
    must_haves: Optional[str] = Field(None, max_length=1000, description="Must-have elements")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('event_date')
    def validate_event_date(cls, v):
        """Ensure event date is not too far in the past."""
        if v < date.today():
            # Allow past dates but flag for warning
            pass
        return v
    
    @validator('event_end_date')
    def validate_end_date(cls, v, values):
        """Ensure end date is after start date."""
        if v and 'event_date' in values:
            if v < values['event_date']:
                raise ValueError("End date must be after start date")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "evt_12345",
                "name": "Priya & Rahul's Wedding",
                "event_type": "wedding",
                "event_date": "2024-02-15",
                "event_end_date": "2024-02-16",
                "city": "Jaipur",
                "venue_type": "both",
                "guest_count": 250,
                "budget_total": 1500000,
                "currency": "INR",
                "theme": "Royal Rajasthani",
                "audience": "mixed",
                "dietary_needs": "Vegetarian only",
                "cultural_notes": "Hindu ceremonies, 2-day wedding",
                "must_haves": "Mehendi, Sangeet, Traditional ceremonies",
            }
        }


class EventProfileInput(BaseModel):
    """Input for creating an event profile."""
    
    # Can be structured or free text
    free_text: Optional[str] = Field(None, max_length=2000, description="Free-form event description")
    
    # Structured fields (optional if free_text provided)
    name: Optional[str] = Field(None, max_length=200)
    event_type: Optional[EventType] = None
    event_date: Optional[date] = None
    event_end_date: Optional[date] = None
    city: Optional[str] = Field(None, max_length=100)
    venue_type: Optional[VenueType] = None
    guest_count: Optional[int] = Field(None, gt=0, le=10000)
    budget_total: Optional[float] = Field(None, gt=0)
    currency: str = Field(default="INR")
    theme: Optional[str] = Field(None, max_length=500)
    audience: Optional[AudienceMix] = None
    dietary_needs: Optional[str] = Field(None, max_length=500)
    cultural_notes: Optional[str] = Field(None, max_length=500)
    must_haves: Optional[str] = Field(None, max_length=1000)
    
    @validator('free_text', 'name', 'theme', 'dietary_needs', 'cultural_notes', 'must_haves')
    def sanitize_text(cls, v):
        """Basic sanitization of text fields."""
        if v:
            # Remove potential injection patterns
            v = v.replace("<script>", "").replace("</script>", "")
            v = v.replace("javascript:", "")
            v = v.strip()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "free_text": "Plan a 2-day wedding for 250 guests in Jaipur in February, budget 15 lakh, royal theme"
            }
        }
