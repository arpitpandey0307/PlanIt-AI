"""Budget schema."""
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class BudgetCategory(BaseModel):
    """Individual budget category."""
    
    name: str = Field(..., description="Category name")
    percent: float = Field(..., ge=0, le=100, description="Percentage of total budget")
    estimated: float = Field(..., ge=0, description="Estimated amount")
    actual: float = Field(default=0, ge=0, description="Actual spent amount")
    notes: Optional[str] = Field(None, max_length=500, description="Category notes")
    decision_trace: Optional[str] = Field(None, description="Why this allocation")


class Budget(BaseModel):
    """Complete budget breakdown."""
    
    event_id: str = Field(..., description="Associated event ID")
    total_budget: float = Field(..., gt=0, description="Total budget amount")
    currency: str = Field(default="INR", description="Currency code")
    categories: List[BudgetCategory] = Field(..., description="Budget categories")
    assumptions: List[str] = Field(default_factory=list, description="Budget assumptions")
    saving_tips: List[str] = Field(default_factory=list, description="Cost-saving suggestions")
    feasibility_warning: Optional[str] = Field(None, description="Warning if budget is tight")
    
    @validator('categories')
    def validate_budget_sum(cls, v, values):
        """Ensure categories sum to 100% and match total budget."""
        if not v:
            return v
        
        total_percent = sum(cat.percent for cat in v)
        if abs(total_percent - 100.0) > 0.1:  # Allow small floating point error
            raise ValueError(f"Budget percentages must sum to 100%, got {total_percent}%")
        
        if 'total_budget' in values:
            total_estimated = sum(cat.estimated for cat in v)
            expected = values['total_budget']
            if abs(total_estimated - expected) > 1.0:  # Allow ₹1 rounding error
                raise ValueError(
                    f"Category estimates must sum to total budget. "
                    f"Expected {expected}, got {total_estimated}"
                )
        
        return v
    
    @property
    def total_spent(self) -> float:
        """Calculate total actual spending."""
        return sum(cat.actual for cat in self.categories)
    
    @property
    def remaining(self) -> float:
        """Calculate remaining budget."""
        return self.total_budget - self.total_spent
    
    @property
    def spent_percentage(self) -> float:
        """Calculate percentage of budget spent."""
        if self.total_budget == 0:
            return 0.0
        return (self.total_spent / self.total_budget) * 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_12345",
                "total_budget": 1500000,
                "currency": "INR",
                "categories": [
                    {
                        "name": "Venue",
                        "percent": 20.0,
                        "estimated": 300000,
                        "actual": 0,
                        "decision_trace": "20% allocation for wedding venue"
                    },
                    {
                        "name": "Catering",
                        "percent": 30.0,
                        "estimated": 450000,
                        "actual": 50000,
                        "notes": "Advance paid to caterer"
                    }
                ],
                "assumptions": [
                    "Based on Jaipur Tier-2 city pricing",
                    "Per-plate cost estimated at ₹1,800",
                    "Peak season (Feb) pricing included"
                ],
                "saving_tips": [
                    "Consider weekday booking for 15-20% discount",
                    "Opt for buffet over plated service",
                    "Book venue with in-house catering for better rates"
                ]
            }
        }
