"""Intake agent for profile extraction."""
from datetime import date, datetime
from ..schemas.profile import EventProfile, EventProfileInput, EventType, VenueType, AudienceMix
from ..llm.client import LLMClient
import uuid
import json
import re


async def extract_profile(input_data: EventProfileInput, llm: LLMClient) -> EventProfile:
    """
    Extract structured event profile from free text or structured input.
    """
    # If fully structured, just validate and return
    if not input_data.free_text and all([
        input_data.name,
        input_data.event_type,
        input_data.event_date,
        input_data.guest_count,
        input_data.budget_total,
        input_data.city
    ]):
        return EventProfile(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            name=input_data.name,
            event_type=input_data.event_type,
            event_date=input_data.event_date,
            event_end_date=input_data.event_end_date,
            city=input_data.city,
            venue_type=input_data.venue_type or VenueType.BOTH,
            guest_count=input_data.guest_count,
            budget_total=input_data.budget_total,
            currency=input_data.currency,
            theme=input_data.theme,
            audience=input_data.audience or AudienceMix.MIXED,
            dietary_needs=input_data.dietary_needs,
            cultural_notes=input_data.cultural_notes,
            must_haves=input_data.must_haves
        )
    
    # Extract from free text using LLM or rules
    if input_data.free_text:
        extracted = await extract_from_text(input_data.free_text, llm)
        # Merge with any provided structured fields
        return EventProfile(
            id=f"evt_{uuid.uuid4().hex[:12]}",
            name=input_data.name or extracted.get("name", "My Event"),
            event_type=input_data.event_type or EventType(extracted.get("event_type", "wedding")),
            event_date=input_data.event_date or extracted.get("event_date", date.today()),
            event_end_date=input_data.event_end_date or extracted.get("event_end_date"),
            city=input_data.city or extracted.get("city", "Delhi"),
            venue_type=input_data.venue_type or VenueType(extracted.get("venue_type", "both")),
            guest_count=input_data.guest_count or extracted.get("guest_count", 100),
            budget_total=input_data.budget_total or extracted.get("budget_total", 100000),
            currency=input_data.currency,
            theme=input_data.theme or extracted.get("theme"),
            audience=input_data.audience or AudienceMix(extracted.get("audience", "mixed")),
            dietary_needs=input_data.dietary_needs or extracted.get("dietary_needs"),
            cultural_notes=input_data.cultural_notes or extracted.get("cultural_notes"),
            must_haves=input_data.must_haves or extracted.get("must_haves")
        )
    
    # Default fallback
    raise ValueError("Insufficient information to create event profile")


async def extract_from_text(text: str, llm: LLMClient) -> dict:
    """Extract structured fields from free text."""
    # Simple rule-based extraction as fallback
    result = {
        "name": "My Event",
        "event_type": "wedding",
        "guest_count": 100,
        "budget_total": 100000,
        "city": "Delhi",
        "venue_type": "both",
        "audience": "mixed"
    }
    
    # Try to extract numbers
    text_lower = text.lower()
    
    # Event type
    if "wedding" in text_lower:
        result["event_type"] = "wedding"
    elif "birthday" in text_lower:
        result["event_type"] = "birthday"
    elif "community" in text_lower or "festival" in text_lower or "mela" in text_lower:
        result["event_type"] = "community"
    
    # Guest count
    guest_match = re.search(r'(\d+)\s*(?:guests?|people|persons?)', text_lower)
    if guest_match:
        result["guest_count"] = int(guest_match.group(1))
    
    # Budget (look for lakh, thousand, k)
    budget_match = re.search(r'(?:budget|cost)?\s*(?:of)?\s*(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)\s*(lakh|thousand|k)?', text_lower)
    if budget_match:
        amount = float(budget_match.group(1))
        unit = budget_match.group(2) or ""
        if "lakh" in unit:
            result["budget_total"] = amount * 100000
        elif "k" in unit or "thousand" in unit:
            result["budget_total"] = amount * 1000
        else:
            result["budget_total"] = amount
    
    # City
    cities = ["mumbai", "delhi", "bangalore", "hyderabad", "pune", "chennai", 
              "jaipur", "ahmedabad", "kolkata", "surat", "lucknow"]
    for city in cities:
        if city in text_lower:
            result["city"] = city.title()
            break
    
    # Venue type
    if "outdoor" in text_lower and "indoor" not in text_lower:
        result["venue_type"] = "outdoor"
    elif "indoor" in text_lower and "outdoor" not in text_lower:
        result["venue_type"] = "indoor"
    
    # Theme
    theme_match = re.search(r'(?:theme|style)[:\s]+([^,.]+)', text_lower)
    if theme_match:
        result["theme"] = theme_match.group(1).strip()
    
    # Try to extract date (simple patterns)
    date_patterns = [
        r'(?:on|date:?)\s*(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',
        r'(?:in|on)\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                if len(match.groups()) == 3:  # DD/MM/YYYY format
                    day, month, year = match.groups()
                    year = int(year)
                    if year < 100:
                        year += 2000
                    result["event_date"] = date(year, int(month), int(day))
                else:  # Month Day format
                    month_name, day = match.groups()
                    month_map = {
                        "january": 1, "february": 2, "march": 3, "april": 4,
                        "may": 5, "june": 6, "july": 7, "august": 8,
                        "september": 9, "october": 10, "november": 11, "december": 12
                    }
                    month = month_map.get(month_name, 1)
                    year = date.today().year
                    if month < date.today().month:
                        year += 1
                    result["event_date"] = date(year, month, int(day))
                break
            except:
                pass
    
    if "event_date" not in result:
        # Default to 3 months from now
        from datetime import timedelta
        result["event_date"] = date.today() + timedelta(days=90)
    
    return result
