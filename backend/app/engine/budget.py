"""Budget allocation engine."""
from typing import List, Tuple
from ..schemas.profile import EventProfile
from ..schemas.budget import Budget, BudgetCategory
from ..config import BUDGET_PROFILES, DecisionRules


def generate_budget(profile: EventProfile) -> Budget:
    """
    Generate budget allocation based on event profile.
    Uses deterministic rules, no LLM calls.
    """
    # Get base profile for event type
    base_profile = BUDGET_PROFILES.get(profile.event_type.value, BUDGET_PROFILES["wedding"])
    
    # Apply context-aware adjustments
    adjusted_profile = apply_budget_adjustments(profile, base_profile.copy())
    
    # Calculate amounts
    categories = []
    total_allocated = 0.0
    
    for category_name, percent in adjusted_profile.items():
        estimated = (percent / 100.0) * profile.budget_total
        categories.append(
            BudgetCategory(
                name=category_name.replace("_", " & ").title(),
                percent=round(percent, 2),
                estimated=round(estimated, 2),
                actual=0.0,
                decision_trace=get_decision_trace(category_name, profile)
            )
        )
        total_allocated += estimated
    
    # Fix rounding errors by adjusting contingency
    if abs(total_allocated - profile.budget_total) > 0.01:
        diff = profile.budget_total - total_allocated
        contingency_cat = next((c for c in categories if "contingency" in c.name.lower()), None)
        if contingency_cat:
            contingency_cat.estimated += diff
    
    # Generate assumptions and tips
    assumptions = generate_assumptions(profile)
    saving_tips = generate_saving_tips(profile)
    feasibility_warning = check_feasibility(profile)
    
    return Budget(
        event_id=profile.id,
        total_budget=profile.budget_total,
        currency=profile.currency,
        categories=categories,
        assumptions=assumptions,
        saving_tips=saving_tips,
        feasibility_warning=feasibility_warning
    )


def apply_budget_adjustments(profile: EventProfile, base_profile: dict) -> dict:
    """Apply context-aware adjustments to base budget profile."""
    adjusted = base_profile.copy()
    
    # Outdoor venue adjustment
    if profile.venue_type.value == "outdoor":
        if "contingency" in adjusted:
            adjusted["contingency"] += DecisionRules.OUTDOOR_CONTINGENCY_BOOST
            # Normalize to 100%
            total = sum(adjusted.values())
            for key in adjusted:
                adjusted[key] = (adjusted[key] / total) * 100
    
    # Peak season adjustment
    if profile.event_date:
        month = profile.event_date.month
        is_peak = DecisionRules.is_peak_season(profile.event_type.value, month)
        if is_peak and "venue" in adjusted:
            # Shift budget toward venue
            adjusted["venue"] = min(adjusted["venue"] + DecisionRules.PEAK_SEASON_VENUE_BOOST, 30.0)
            # Normalize
            total = sum(adjusted.values())
            for key in adjusted:
                adjusted[key] = (adjusted[key] / total) * 100
    
    return adjusted


def get_decision_trace(category_name: str, profile: EventProfile) -> str:
    """Explain why this allocation was made."""
    traces = []
    
    if "contingency" in category_name:
        if profile.venue_type.value == "outdoor":
            traces.append("Outdoor venue: added weather buffer")
        traces.append("Reserve for unexpected costs")
    
    if "venue" in category_name:
        if profile.event_date:
            month = profile.event_date.month
            if DecisionRules.is_peak_season(profile.event_type.value, month):
                traces.append("Peak season: venues book early at premium rates")
    
    if profile.guest_count >= DecisionRules.LARGE_EVENT_THRESHOLD:
        if "catering" in category_name or "venue" in category_name:
            traces.append("Large guest count requires more resources")
    
    return "; ".join(traces) if traces else f"Standard allocation for {profile.event_type.value}"


def generate_assumptions(profile: EventProfile) -> List[str]:
    """Generate list of budget assumptions."""
    assumptions = [
        f"Currency: {profile.currency}",
        f"Based on {profile.city} pricing",
    ]
    
    city_tier = DecisionRules.get_city_tier(profile.city)
    assumptions.append(f"City tier: {city_tier.upper()} (affects vendor rates)")
    
    if profile.event_date:
        month = profile.event_date.month
        if DecisionRules.is_peak_season(profile.event_type.value, month):
            assumptions.append(f"Peak season (month {month}): 10-20% premium expected")
        else:
            assumptions.append(f"Off-peak season: better negotiation possible")
    
    if profile.event_type.value == "wedding":
        per_plate = profile.budget_total * 0.30 / profile.guest_count if profile.guest_count > 0 else 0
        assumptions.append(f"Estimated per-plate cost: ₹{per_plate:.0f}")
    
    assumptions.append("All amounts are AI estimates, not binding quotes")
    
    return assumptions


def generate_saving_tips(profile: EventProfile) -> List[str]:
    """Generate cost-saving suggestions."""
    tips = []
    
    if profile.event_type.value == "wedding":
        tips.append("Consider weekday booking for 15-20% venue discount")
        tips.append("Opt for buffet over plated service to reduce catering costs")
        tips.append("Book venue with in-house catering for package deals")
        if profile.guest_count > 200:
            tips.append("Negotiate bulk discounts with vendors for large guest count")
    
    elif profile.event_type.value == "birthday":
        tips.append("DIY decorations can save 30-40% on decor budget")
        tips.append("Book entertainers directly instead of through agencies")
        tips.append("Consider afternoon slots for better venue rates")
    
    elif profile.event_type.value == "community":
        tips.append("Partner with local businesses for sponsorships")
        tips.append("Use volunteer support to reduce staffing costs")
        tips.append("Bulk orders for food and supplies offer better rates")
    
    if profile.venue_type.value == "outdoor":
        tips.append("Have a free backup indoor option to avoid weather-related costs")
    
    return tips


def check_feasibility(profile: EventProfile) -> str | None:
    """Check if budget is realistic for the event."""
    if profile.guest_count == 0:
        return None
    
    per_guest = profile.budget_total / profile.guest_count
    city_tier = DecisionRules.get_city_tier(profile.city)
    
    min_costs = DecisionRules.MIN_PER_GUEST_COST.get(
        profile.event_type.value,
        {"tier1": 1000, "tier2": 750, "tier3": 500}
    )
    min_required = min_costs.get(city_tier, min_costs["tier3"])
    
    if per_guest < min_required:
        shortage = (min_required - per_guest) * profile.guest_count
        return (
            f"Budget may be tight: ₹{per_guest:.0f} per guest is below typical "
            f"₹{min_required} for {profile.event_type.value} in {profile.city}. "
            f"Consider increasing budget by ₹{shortage:.0f}, reducing guest count to "
            f"{int(profile.budget_total / min_required)}, or simplifying the event scope."
        )
    
    return None
