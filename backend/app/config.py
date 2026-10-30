"""Application configuration and decision rules."""
from typing import Dict, List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    google_api_key: str = ""
    port: int = 8000
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"
    rate_limit_per_minute: int = 20
    
    # LLM Settings
    model_name: str = "gemini-1.5-flash"
    model_name_pro: str = "gemini-1.5-pro"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout_seconds: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Budget allocation profiles (percentages that sum to 100)
BUDGET_PROFILES: Dict[str, Dict[str, float]] = {
    "wedding": {
        "venue": 20.0,
        "catering": 30.0,
        "decor": 12.0,
        "photography": 10.0,
        "attire_beauty": 8.0,
        "entertainment": 5.0,
        "invitations": 2.0,
        "transport_stay": 4.0,
        "favours_gifts": 2.0,
        "contingency": 7.0,
    },
    "birthday": {
        "venue": 15.0,
        "catering": 35.0,
        "decor": 15.0,
        "photography": 3.0,
        "entertainment": 15.0,
        "cake": 7.0,
        "invitations": 2.0,
        "favours_gifts": 3.0,
        "contingency": 5.0,
    },
    "community": {
        "venue_permits": 15.0,
        "catering": 25.0,
        "decor": 8.0,
        "sound_stage_lighting": 15.0,
        "invitations_promotion": 6.0,
        "safety_cleanup": 8.0,
        "volunteer_support": 3.0,
        "entertainment": 12.0,
        "contingency": 8.0,
    },
}


# Decision rules configuration
class DecisionRules:
    """Context-aware decision rules and thresholds."""
    
    # Feasibility thresholds (minimum per-guest cost in INR)
    MIN_PER_GUEST_COST = {
        "wedding": {"tier1": 2000, "tier2": 1500, "tier3": 1000},
        "birthday": {"tier1": 800, "tier2": 600, "tier3": 400},
        "community": {"tier1": 500, "tier2": 300, "tier3": 200},
    }
    
    # City tiers (for cost estimation)
    CITY_TIERS = {
        "tier1": ["mumbai", "delhi", "bangalore", "hyderabad", "pune", "chennai"],
        "tier2": ["jaipur", "ahmedabad", "kolkata", "surat", "lucknow", "kanpur"],
        "tier3": ["other"],  # Default tier
    }
    
    # Timeline adjustments
    STANDARD_PLANNING_WEEKS = 12
    SHORT_NOTICE_DAYS = 14
    PEAK_SEASON_LEAD_WEEKS = 4
    
    # Vendor lead times (in weeks)
    VENDOR_LEAD_TIMES = {
        "venue": 12,
        "caterer": 8,
        "photographer": 8,
        "decorator": 4,
        "entertainment": 6,
    }
    
    # Budget adjustments
    OUTDOOR_CONTINGENCY_BOOST = 2.0  # percentage points
    PEAK_SEASON_VENUE_BOOST = 2.0
    LARGE_EVENT_THRESHOLD = 200  # guests
    
    @staticmethod
    def get_city_tier(city: str) -> str:
        """Determine city tier for cost estimation."""
        city_lower = city.lower()
        for tier, cities in DecisionRules.CITY_TIERS.items():
            if any(c in city_lower for c in cities):
                return tier
        return "tier3"
    
    @staticmethod
    def is_peak_season(event_type: str, month: int) -> bool:
        """Check if event falls in peak season."""
        # Wedding peak: Oct-Mar in India
        if event_type == "wedding" and (month >= 10 or month <= 3):
            return True
        # Birthday peak: school holidays (May, Jun, Dec)
        if event_type == "birthday" and month in [5, 6, 12]:
            return True
        # Community peak: festival season (Sep-Nov)
        if event_type == "community" and month in [9, 10, 11]:
            return True
        return False


# Vendor categories by event type
VENDOR_CATEGORIES: Dict[str, List[Dict[str, any]]] = {
    "wedding": [
        {
            "name": "Venue",
            "lead_time_weeks": 12,
            "questions": [
                "Capacity for guests?",
                "Indoor/outdoor options?",
                "Catering included or external allowed?",
                "Backup date availability?",
                "Decoration restrictions?",
            ],
            "diligence": [
                "Check availability for backup date",
                "Review cancellation policy",
                "Ask for references from recent weddings",
                "Visit venue in person",
                "Clarify inclusions (furniture, power, parking)",
            ],
        },
        {
            "name": "Caterer",
            "lead_time_weeks": 8,
            "questions": [
                "Sample menu tasting available?",
                "Dietary restrictions accommodation?",
                "Service staff included?",
                "Tableware and setup provided?",
                "Minimum and maximum guest count?",
            ],
            "diligence": [
                "Taste test before booking",
                "Check FSSAI license",
                "Ask about ingredient sourcing",
                "Confirm service staff count",
                "Review food safety practices",
            ],
        },
        {
            "name": "Photographer/Videographer",
            "lead_time_weeks": 8,
            "questions": [
                "Full day coverage or hours-based?",
                "How many photographers/videographers?",
                "Deliverables timeline?",
                "Drone shots included?",
                "Raw photos provided?",
            ],
            "diligence": [
                "Review complete wedding portfolios",
                "Check equipment backup plans",
                "Clarify editing style and timeline",
                "Confirm rights to photos",
                "Ask about backup photographer",
            ],
        },
        {
            "name": "Decorator",
            "lead_time_weeks": 4,
            "questions": [
                "Setup and teardown timing?",
                "Fresh or artificial flowers?",
                "Stage and mandap design options?",
                "Lighting included?",
                "Weather-backup decor plan?",
            ],
            "diligence": [
                "See photos of similar setups",
                "Visit a live event if possible",
                "Confirm setup completion time",
                "Check material quality",
                "Discuss theme alignment",
            ],
        },
        {
            "name": "Makeup Artist & Hair",
            "lead_time_weeks": 6,
            "questions": [
                "Trial session included?",
                "Products used (bridal or regular)?",
                "Travel to venue included?",
                "Touchup services during event?",
                "Package for family members?",
            ],
            "diligence": [
                "Book trial at least 2 weeks before",
                "Check product brands (for allergies)",
                "Review photos of past work",
                "Confirm arrival time on event day",
                "Discuss look preferences in detail",
            ],
        },
        {
            "name": "Entertainment/DJ/Band",
            "lead_time_weeks": 6,
            "questions": [
                "Music genre specialization?",
                "Custom playlist acceptance?",
                "Sound system and setup included?",
                "Duration of performance?",
                "Backup equipment available?",
            ],
            "diligence": [
                "Listen to live performance or recordings",
                "Check references from recent events",
                "Confirm equipment list",
                "Discuss song list and restrictions",
                "Ask about contingency for artist unavailability",
            ],
        },
        {
            "name": "Priest/Officiant",
            "lead_time_weeks": 8,
            "questions": [
                "Rituals included?",
                "Ceremony duration estimate?",
                "Puja materials provided?",
                "Flexibility with timing?",
                "Language preference?",
            ],
            "diligence": [
                "Meet in person to discuss rituals",
                "Confirm muhurat alignment",
                "Ask about travel arrangements",
                "Clarify material responsibilities",
                "Discuss custom or modern rituals",
            ],
        },
    ],
    "birthday": [
        {
            "name": "Venue",
            "lead_time_weeks": 6,
            "questions": [
                "Party duration allowed?",
                "Decoration permissions?",
                "Cake cutting arrangement?",
                "Music/entertainment restrictions?",
                "Kid-friendly safety features?",
            ],
            "diligence": [
                "Check safety for age group",
                "Confirm parking availability",
                "Ask about noise restrictions",
                "Verify capacity",
                "Discuss cleanup responsibilities",
            ],
        },
        {
            "name": "Caterer",
            "lead_time_weeks": 4,
            "questions": [
                "Age-appropriate menu?",
                "Allergy accommodation?",
                "Beverage options?",
                "Service style (buffet/plated)?",
                "Tableware included?",
            ],
            "diligence": [
                "Taste test if possible",
                "Check food safety practices",
                "Confirm serving time",
                "Ask about kid-friendly options",
                "Review cancellation terms",
            ],
        },
        {
            "name": "Baker (Cake)",
            "lead_time_weeks": 3,
            "questions": [
                "Custom design options?",
                "Flavor choices?",
                "Dietary restrictions (eggless/vegan)?",
                "Size for guest count?",
                "Delivery and setup included?",
            ],
            "diligence": [
                "See portfolio of designs",
                "Taste test flavors",
                "Confirm allergen information",
                "Check delivery timing",
                "Discuss storage requirements",
            ],
        },
        {
            "name": "Entertainment (Magician/Games/Activities)",
            "lead_time_weeks": 4,
            "questions": [
                "Age-appropriate shows?",
                "Performance duration?",
                "Space requirements?",
                "Interactive activities included?",
                "Backup performer available?",
            ],
            "diligence": [
                "Watch performance videos",
                "Check references from parents",
                "Confirm engagement style",
                "Discuss equipment needs",
                "Ask about child safety measures",
            ],
        },
        {
            "name": "Photographer",
            "lead_time_weeks": 4,
            "questions": [
                "Hours of coverage?",
                "Digital photos delivery timeline?",
                "Candid or posed style?",
                "Props included?",
                "Group shots guaranteed?",
            ],
            "diligence": [
                "Review birthday portfolio",
                "Check turnaround time",
                "Confirm number of edited photos",
                "Discuss backup equipment",
                "Clarify usage rights",
            ],
        },
    ],
    "community": [
        {
            "name": "Venue & Permits",
            "lead_time_weeks": 12,
            "questions": [
                "Public space permits required?",
                "Capacity and open space size?",
                "Power supply availability?",
                "Parking and access?",
                "Weather contingency options?",
            ],
            "diligence": [
                "Apply for permits 8+ weeks early",
                "Check local authority requirements",
                "Visit site at event time of day",
                "Confirm utilities availability",
                "Plan for crowd control",
            ],
        },
        {
            "name": "Tent/Canopy & Seating",
            "lead_time_weeks": 6,
            "questions": [
                "Size options for guest count?",
                "Setup and takedown timing?",
                "Weather-resistant materials?",
                "Flooring included?",
                "Side panels for wind/rain?",
            ],
            "diligence": [
                "Check structural safety certifications",
                "Confirm ground condition requirements",
                "Ask about wind/weather limits",
                "Verify setup crew experience",
                "Discuss backup plan",
            ],
        },
        {
            "name": "Sound System & Stage",
            "lead_time_weeks": 8,
            "questions": [
                "Coverage area for audience size?",
                "Microphones and mixers included?",
                "Stage size and height?",
                "Power backup available?",
                "Technician support during event?",
            ],
            "diligence": [
                "Test equipment quality beforehand",
                "Check power requirements",
                "Confirm setup and soundcheck time",
                "Ask about backup equipment",
                "Discuss volume restrictions",
            ],
        },
        {
            "name": "Catering & Food Stalls",
            "lead_time_weeks": 6,
            "questions": [
                "Menu variety for large crowds?",
                "Hygiene and safety compliance?",
                "Serving infrastructure (counters/stalls)?",
                "Waste management plan?",
                "Dietary variety (veg/non-veg/vegan)?",
            ],
            "diligence": [
                "Verify food safety licenses",
                "Check serving capacity per hour",
                "Confirm waste disposal plan",
                "Ask about allergen labeling",
                "Review crowd management experience",
            ],
        },
        {
            "name": "Security & First Aid",
            "lead_time_weeks": 8,
            "questions": [
                "Number of security personnel?",
                "Trained first aid staff?",
                "Emergency response plan?",
                "Communication equipment?",
                "Crowd control barriers?",
            ],
            "diligence": [
                "Verify security training certifications",
                "Check first aid kit contents",
                "Confirm emergency evacuation plan",
                "Discuss coordination with local police",
                "Ask about insurance coverage",
            ],
        },
        {
            "name": "Cleanup & Waste Management",
            "lead_time_weeks": 4,
            "questions": [
                "Post-event cleanup included?",
                "Waste segregation provided?",
                "Bins and trash bags supplied?",
                "Timeline for complete cleanup?",
                "Disposal certifications?",
            ],
            "diligence": [
                "Confirm environmental compliance",
                "Check disposal location legality",
                "Ask about recycling options",
                "Verify crew size",
                "Discuss site restoration",
            ],
        },
    ],
}
