"""Vendor checklist schema."""
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class VendorStatus(str, Enum):
    """Vendor booking status."""
    NOT_STARTED = "not_started"
    SHORTLISTING = "shortlisting"
    CONTACTED = "contacted"
    QUOTE_RECEIVED = "quote_received"
    BOOKED = "booked"
    CANCELLED = "cancelled"


class VendorCategory(BaseModel):
    """Vendor category with checklist."""
    
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Vendor category name")
    lead_time_weeks: int = Field(..., ge=0, description="Recommended booking lead time")
    budget_share: float = Field(..., ge=0, le=100, description="Percentage of budget")
    questions: List[str] = Field(..., description="Questions to ask vendor")
    diligence: List[str] = Field(..., description="Due diligence checklist")
    status: VendorStatus = Field(default=VendorStatus.NOT_STARTED, description="Booking status")
    
    # User-entered details
    vendor_name: Optional[str] = Field(None, max_length=200, description="Vendor business name")
    contact: Optional[str] = Field(None, max_length=200, description="Contact info")
    quote: Optional[float] = Field(None, ge=0, description="Quoted amount")
    advance_paid: float = Field(default=0, ge=0, description="Advance paid")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "vendor_001",
                "name": "Photographer/Videographer",
                "lead_time_weeks": 8,
                "budget_share": 10.0,
                "status": "contacted",
                "vendor_name": "Perfect Moments Photography",
                "contact": "+91-98765-43210",
                "quote": 150000,
                "advance_paid": 50000,
                "notes": "Booked for both days, includes drone shots",
                "questions": ["Full day coverage or hours-based?"],
                "diligence": ["Review complete portfolios"]
            }
        }


class VendorChecklist(BaseModel):
    """Complete vendor checklist for an event."""
    
    event_id: str = Field(..., description="Associated event ID")
    categories: List[VendorCategory] = Field(..., description="Vendor categories")
    
    @property
    def booked_count(self) -> int:
        """Count of booked vendors."""
        return sum(1 for cat in self.categories if cat.status == VendorStatus.BOOKED)
    
    @property
    def total_quoted(self) -> float:
        """Sum of all quotes."""
        return sum(cat.quote for cat in self.categories if cat.quote)
    
    @property
    def total_advanced(self) -> float:
        """Sum of all advances paid."""
        return sum(cat.advance_paid for cat in self.categories)
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_12345",
                "categories": []
            }
        }
