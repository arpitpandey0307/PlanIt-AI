"""Ideas generation agent."""
from typing import List
from ..schemas.profile import EventProfile
from ..schemas.ideas import IdeasCollection, IdeaCard, IdeaKind, CostLevel
from ..llm.client import LLMClient
import uuid


async def generate_ideas(profile: EventProfile, llm: LLMClient) -> IdeasCollection:
    """
    Generate personalized ideas for the event.
    Uses LLM for creative suggestions.
    """
    # Generate theme ideas
    themes = await generate_theme_ideas(profile, llm)
    
    # Generate menu ideas
    menu = await generate_menu_ideas(profile, llm)
    
    # Generate activity ideas
    activities = await generate_activity_ideas(profile, llm)
    
    # Generate invitation ideas
    invitations = await generate_invitation_ideas(profile, llm)
    
    return IdeasCollection(
        event_id=profile.id,
        themes=themes,
        menu=menu,
        activities=activities,
        invitations=invitations
    )


async def generate_theme_ideas(profile: EventProfile, llm: LLMClient) -> List[IdeaCard]:
    """Generate theme concepts."""
    # Template-based themes for fallback
    themes = []
    
    if profile.event_type.value == "wedding":
        themes = [
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Royal Rajasthani",
                description="Embrace the grandeur of Rajasthan with gold and maroon decor, traditional folk music, puppet shows, and a regal entrance. The mandap features intricate Jaali work and marigold garlands.",
                palette=["#FFD700", "#8B0000", "#FFA500"],
                cost_level=CostLevel.HIGH,
                tags=["traditional", "cultural", "luxurious"]
            ),
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Modern Minimalist",
                description="Clean lines, neutral colors (white, grey, sage green), simple elegant decor with greenery and fairy lights. Perfect for intimate weddings with a contemporary feel.",
                palette=["#FFFFFF", "#808080", "#8FBC8F"],
                cost_level=CostLevel.MEDIUM,
                tags=["modern", "simple", "elegant"]
            ),
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Rustic Garden",
                description="Outdoor celebration with wooden elements, wildflowers, burlap accents, and string lights. Natural, relaxed atmosphere with vintage charm.",
                palette=["#8B4513", "#F5DEB3", "#9ACD32"],
                cost_level=CostLevel.MEDIUM,
                tags=["outdoor", "natural", "rustic"]
            ),
        ]
    elif profile.event_type.value == "birthday":
        themes = [
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Superhero Adventure",
                description="Bold primary colors, superhero cutouts and balloons, cape station for kids, obstacle course activities. Action-packed celebration for young heroes.",
                palette=["#FF0000", "#0000FF", "#FFFF00"],
                cost_level=CostLevel.MEDIUM,
                tags=["kids", "active", "fun"]
            ),
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Enchanted Garden",
                description="Pastel colors, floral decorations, butterfly and fairy elements, tea party setup. Magical garden atmosphere perfect for all ages.",
                palette=["#FFB6C1", "#E6E6FA", "#90EE90"],
                cost_level=CostLevel.LOW,
                tags=["elegant", "nature", "whimsical"]
            ),
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Movie Night",
                description="Cinema-themed decor, popcorn bar, red carpet entrance, photo booth with props. Turn the celebration into a blockbuster event.",
                palette=["#FF0000", "#000000", "#FFD700"],
                cost_level=CostLevel.MEDIUM,
                tags=["entertainment", "unique", "fun"]
            ),
        ]
    elif profile.event_type.value == "community":
        themes = [
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Cultural Festival",
                description="Celebrate local heritage with traditional performances, craft stalls, regional food, folk music and dance. Colorful ethnic decor and inclusive activities.",
                palette=["#FF6347", "#FFD700", "#9370DB"],
                cost_level=CostLevel.MEDIUM,
                tags=["traditional", "inclusive", "cultural"]
            ),
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.THEME,
                title="Eco-Friendly Fair",
                description="Green theme with sustainable practices, tree planting, recycling stations, organic food stalls, environmental awareness activities.",
                palette=["#228B22", "#8FBC8F", "#F5DEB3"],
                cost_level=CostLevel.LOW,
                tags=["eco-friendly", "awareness", "nature"]
            ),
        ]
    
    return themes


async def generate_menu_ideas(profile: EventProfile, llm: LLMClient) -> List[IdeaCard]:
    """Generate menu suggestions."""
    menu = []
    
    if profile.event_type.value == "wedding":
        menu.append(
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.MENU,
                title="Traditional North Indian Feast",
                description="Starters: Paneer tikka, vegetable samosas. Main: Dal makhani, vegetable biryani, naan, raita. Desserts: Gulab jamun, kulfi. Live chaat counter.",
                cost_level=CostLevel.MEDIUM,
                tags=["vegetarian", "traditional", "north-indian"]
            )
        )
    elif profile.event_type.value == "birthday":
        menu.append(
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.MENU,
                title="Kid-Friendly Party Menu",
                description="Mini pizzas, pasta, french fries, nuggets, fruit platter, juice bar, ice cream station. Options for dietary restrictions available.",
                cost_level=CostLevel.LOW,
                tags=["kids", "fun", "casual"]
            )
        )
    
    return menu


async def generate_activity_ideas(profile: EventProfile, llm: LLMClient) -> List[IdeaCard]:
    """Generate activity and entertainment ideas."""
    activities = []
    
    if profile.event_type.value == "wedding":
        activities.append(
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.ACTIVITY,
                title="Mehendi & Sangeet Night",
                description="Pre-wedding celebration with mehendi artists, music, dance performances by family and friends, DJ or live band.",
                cost_level=CostLevel.MEDIUM,
                tags=["traditional", "music", "dance"]
            )
        )
    elif profile.event_type.value == "birthday":
        activities.append(
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.ACTIVITY,
                title="Interactive Games Station",
                description="Bouncy castle, face painting, magic show, treasure hunt, musical chairs. Keeps kids engaged throughout the party.",
                cost_level=CostLevel.MEDIUM,
                tags=["kids", "interactive", "fun"]
            )
        )
    
    return activities


async def generate_invitation_ideas(profile: EventProfile, llm: LLMClient) -> List[IdeaCard]:
    """Generate invitation wording ideas."""
    invitations = []
    
    if profile.event_type.value == "wedding":
        invitations.append(
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.INVITATION,
                title="Traditional Wedding Invitation",
                description="With great joy, we invite you to celebrate the union of [Names]. Join us for the wedding ceremonies on [Date] at [Venue]. Your presence will make our day special. Seeking your blessings.",
                cost_level=CostLevel.LOW,
                tags=["formal", "traditional"]
            )
        )
    elif profile.event_type.value == "birthday":
        invitations.append(
            IdeaCard(
                id=f"idea_{uuid.uuid4().hex[:8]}",
                kind=IdeaKind.INVITATION,
                title="Fun Birthday Invitation",
                description="Join us for a birthday bash! [Name] is turning [Age]! Date: [Date], Time: [Time], Venue: [Venue]. Games, cake, and fun guaranteed. RSVP by [Date].",
                cost_level=CostLevel.LOW,
                tags=["casual", "fun"]
            )
        )
    
    return invitations
