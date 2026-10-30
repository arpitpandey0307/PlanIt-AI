"""Vendor checklist generation engine."""
from typing import List
from ..schemas.profile import EventProfile
from ..schemas.vendors import VendorChecklist, VendorCategory, VendorStatus
from ..config import VENDOR_CATEGORIES
import uuid


def generate_vendor_checklist(profile: EventProfile) -> VendorChecklist:
    """
    Generate vendor checklist based on event type.
    Uses templates from config, no LLM calls needed for structure.
    """
    # Get vendor templates for this event type
    vendor_templates = VENDOR_CATEGORIES.get(
        profile.event_type.value,
        VENDOR_CATEGORIES["wedding"]
    )
    
    categories = []
    for template in vendor_templates:
        category = VendorCategory(
            id=f"vendor_{uuid.uuid4().hex[:8]}",
            name=template["name"],
            lead_time_weeks=template["lead_time_weeks"],
            budget_share=0.0,  # Will be set by budget allocation
            questions=template["questions"],
            diligence=template["diligence"],
            status=VendorStatus.NOT_STARTED
        )
        categories.append(category)
    
    # Add context-specific vendors
    if profile.venue_type.value == "outdoor":
        # Add tent/weather vendor if not already present
        if not any("tent" in cat.name.lower() for cat in categories):
            categories.append(
                VendorCategory(
                    id=f"vendor_{uuid.uuid4().hex[:8]}",
                    name="Tent/Canopy Rental",
                    lead_time_weeks=6,
                    budget_share=0.0,
                    questions=[
                        "Size options for guest count?",
                        "Weather-resistant materials?",
                        "Setup and teardown timing?",
                        "Side panels for wind/rain?",
                    ],
                    diligence=[
                        "Check structural safety",
                        "Confirm setup requirements",
                        "Ask about weather limits",
                        "Verify insurance coverage",
                    ],
                    status=VendorStatus.NOT_STARTED
                )
            )
    
    if profile.guest_count >= 200 and profile.event_type.value != "birthday":
        # Add transport/logistics
        if not any("transport" in cat.name.lower() for cat in categories):
            categories.append(
                VendorCategory(
                    id=f"vendor_{uuid.uuid4().hex[:8]}",
                    name="Guest Transport",
                    lead_time_weeks=4,
                    budget_share=0.0,
                    questions=[
                        "Vehicle capacity and types?",
                        "Pickup/drop points?",
                        "Driver reliability?",
                        "Fuel and toll inclusions?",
                    ],
                    diligence=[
                        "Check vehicle condition",
                        "Verify driver licenses",
                        "Confirm timing coordination",
                        "Ask about backup vehicles",
                    ],
                    status=VendorStatus.NOT_STARTED
                )
            )
    
    return VendorChecklist(
        event_id=profile.id,
        categories=categories
    )
