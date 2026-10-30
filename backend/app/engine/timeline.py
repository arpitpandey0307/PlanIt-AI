"""Timeline generation engine."""
from datetime import date, time, timedelta
from typing import List
from ..schemas.profile import EventProfile
from ..schemas.timeline import (
    Timeline, Task, RunOfShowSlot, TaskPriority, TaskOwner, TaskStatus
)
from ..config import DecisionRules
import uuid


def generate_timeline(profile: EventProfile) -> Timeline:
    """
    Generate backward-planned timeline from event date.
    Uses deterministic rules, no LLM calls.
    """
    event_date = profile.event_date
    today = date.today()
    days_until_event = (event_date - today).days
    
    # Determine if short notice
    short_notice = days_until_event < DecisionRules.SHORT_NOTICE_DAYS
    
    # Calculate planning start date
    if short_notice:
        planning_weeks = min(days_until_event // 7, 4)  # Max 4 weeks if short notice
        planning_start = today
    else:
        planning_weeks = DecisionRules.STANDARD_PLANNING_WEEKS
        planning_start = event_date - timedelta(weeks=planning_weeks)
    
    # Generate tasks based on event type
    tasks = generate_tasks(profile, planning_start, event_date, short_notice)
    
    # Generate event day schedule
    run_of_show = generate_run_of_show(profile)
    
    return Timeline(
        event_id=profile.id,
        tasks=tasks,
        run_of_show=run_of_show,
        planning_start_date=planning_start,
        event_date=event_date,
        short_notice=short_notice
    )


def generate_tasks(
    profile: EventProfile,
    start_date: date,
    event_date: date,
    short_notice: bool
) -> List[Task]:
    """Generate planning tasks based on event type."""
    tasks = []
    
    # Define phases and their timing
    days_until = (event_date - start_date).days
    weeks_until = days_until // 7
    
    if short_notice:
        phases = [
            ("Immediate", start_date),
            ("This week", start_date + timedelta(days=3)),
            ("Next week", start_date + timedelta(weeks=1)),
            ("Final week", event_date - timedelta(days=7)),
            ("Day before", event_date - timedelta(days=1)),
            ("Event day", event_date),
        ]
    else:
        phases = [
            ("12 weeks out", event_date - timedelta(weeks=12)),
            ("8 weeks out", event_date - timedelta(weeks=8)),
            ("6 weeks out", event_date - timedelta(weeks=6)),
            ("4 weeks out", event_date - timedelta(weeks=4)),
            ("2 weeks out", event_date - timedelta(weeks=2)),
            ("1 week out", event_date - timedelta(weeks=1)),
            ("Day before", event_date - timedelta(days=1)),
            ("Event day", event_date),
            ("Post-event", event_date + timedelta(days=1)),
        ]
    
    # Filter phases that are in the future
    today = date.today()
    phases = [(name, d) for name, d in phases if d >= today]
    
    # Generate tasks by event type
    if profile.event_type.value == "wedding":
        tasks.extend(generate_wedding_tasks(profile, phases, short_notice))
    elif profile.event_type.value == "birthday":
        tasks.extend(generate_birthday_tasks(profile, phases, short_notice))
    elif profile.event_type.value == "community":
        tasks.extend(generate_community_tasks(profile, phases, short_notice))
    
    return tasks


def generate_wedding_tasks(
    profile: EventProfile,
    phases: List[tuple],
    short_notice: bool
) -> List[Task]:
    """Generate wedding-specific tasks."""
    tasks = []
    phase_map = {name: due for name, due in phases}
    
    # Early tasks
    if "12 weeks out" in phase_map:
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Book venue",
                description=f"Reserve venue for {profile.guest_count} guests, confirm backup date availability",
                due_date=phase_map["12 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.URGENT,
                status=TaskStatus.NOT_STARTED,
                phase="12 weeks out"
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Book caterer",
                description="Arrange tasting, finalize menu, confirm dietary accommodations",
                due_date=phase_map["12 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.URGENT,
                status=TaskStatus.NOT_STARTED,
                phase="12 weeks out"
            ),
        ])
    
    if "8 weeks out" in phase_map:
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Book photographer/videographer",
                description="Review portfolios, confirm package, sign contract",
                due_date=phase_map["8 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase="8 weeks out"
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Book priest/officiant",
                description="Confirm ceremony details, muhurat, ritual requirements",
                due_date=phase_map["8 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase="8 weeks out"
            ),
        ])
    
    if "6 weeks out" in phase_map:
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Send invitations",
                description="Finalize guest list, print and mail invitations",
                due_date=phase_map["6 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase="6 weeks out"
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Book makeup artist",
                description="Schedule trial, confirm event day timing",
                due_date=phase_map["6 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase="6 weeks out"
            ),
        ])
    
    if "4 weeks out" in phase_map:
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Finalize decoration plan",
                description="Meet decorator, confirm theme, mandap design, lighting",
                due_date=phase_map["4 weeks out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase="4 weeks out"
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Arrange accommodation for guests",
                description="Block hotel rooms, arrange transport if needed",
                due_date=phase_map["4 weeks out"],
                owner=TaskOwner.FAMILY,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase="4 weeks out"
            ),
        ])
    
    if "1 week out" in phase_map:
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Confirm all vendor timings",
                description="Call each vendor, reconfirm arrival times and setup",
                due_date=phase_map["1 week out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase="1 week out"
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Finalize seating arrangement",
                description="Create seating chart, print place cards",
                due_date=phase_map["1 week out"],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase="1 week out"
            ),
        ])
    
    # Add outdoor-specific tasks
    if profile.venue_type.value == "outdoor":
        if "4 weeks out" in phase_map:
            tasks.append(
                Task(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    title="Arrange tent and weather backup",
                    description="Book tent/canopy, confirm backup indoor arrangement",
                    due_date=phase_map["4 weeks out"],
                    owner=TaskOwner.SELF,
                    priority=TaskPriority.HIGH,
                    status=TaskStatus.NOT_STARTED,
                    phase="4 weeks out",
                    notes="Outdoor venue requires weather contingency"
                )
            )
    
    return tasks


def generate_birthday_tasks(
    profile: EventProfile,
    phases: List[tuple],
    short_notice: bool
) -> List[Task]:
    """Generate birthday-specific tasks."""
    tasks = []
    phase_map = {name: due for name, due in phases}
    
    if len(phase_map) >= 3:
        first_phase = list(phase_map.keys())[0]
        mid_phase = list(phase_map.keys())[len(phase_map) // 2]
        late_phase = list(phase_map.keys())[-3] if len(phase_map) > 2 else first_phase
        
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Book venue",
                description="Reserve party venue, confirm duration and facilities",
                due_date=phase_map[first_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase=first_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Send invitations",
                description="Finalize guest list, send invitations (digital or printed)",
                due_date=phase_map[first_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase=first_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Order cake",
                description="Choose flavor and design, confirm delivery timing",
                due_date=phase_map[mid_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase=mid_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Arrange entertainment",
                description="Book entertainer (magician/games/activities)",
                due_date=phase_map[mid_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase=mid_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Buy decorations and supplies",
                description="Purchase or arrange balloons, banners, party supplies",
                due_date=phase_map[late_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                phase=late_phase
            ),
        ])
    
    return tasks


def generate_community_tasks(
    profile: EventProfile,
    phases: List[tuple],
    short_notice: bool
) -> List[Task]:
    """Generate community event tasks."""
    tasks = []
    phase_map = {name: due for name, due in phases}
    
    if len(phase_map) >= 3:
        first_phase = list(phase_map.keys())[0]
        mid_phase = list(phase_map.keys())[len(phase_map) // 2]
        
        tasks.extend([
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Apply for permits",
                description="Submit applications for public space permits, noise permits",
                due_date=phase_map[first_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.URGENT,
                status=TaskStatus.NOT_STARTED,
                phase=first_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Secure venue/space",
                description="Book or reserve community space, confirm capacity",
                due_date=phase_map[first_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.URGENT,
                status=TaskStatus.NOT_STARTED,
                phase=first_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Recruit volunteers",
                description="Form volunteer team, assign responsibilities",
                due_date=phase_map[mid_phase],
                owner=TaskOwner.SELF,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase=mid_phase
            ),
            Task(
                id=f"task_{uuid.uuid4().hex[:8]}",
                title="Arrange safety and first aid",
                description="Hire security, arrange first aid station, emergency plan",
                due_date=phase_map[mid_phase],
                owner=TaskOwner.VOLUNTEER,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                phase=mid_phase
            ),
        ])
    
    # Large event specific
    if profile.guest_count >= DecisionRules.LARGE_EVENT_THRESHOLD:
        if len(phase_map) > 0:
            phase_name = list(phase_map.keys())[0]
            tasks.append(
                Task(
                    id=f"task_{uuid.uuid4().hex[:8]}",
                    title="Plan crowd management",
                    description="Design entry/exit flow, queue management, signage",
                    due_date=phase_map[phase_name],
                    owner=TaskOwner.VOLUNTEER,
                    priority=TaskPriority.HIGH,
                    status=TaskStatus.NOT_STARTED,
                    phase=phase_name,
                    notes=f"Large event ({profile.guest_count} people) requires crowd control"
                )
            )
    
    return tasks


def generate_run_of_show(profile: EventProfile) -> List[RunOfShowSlot]:
    """Generate event day schedule."""
    slots = []
    
    if profile.event_type.value == "wedding":
        slots = [
            RunOfShowSlot(
                start_time=time(9, 0),
                end_time=time(10, 30),
                activity="Setup and decoration completion",
                owner=TaskOwner.VENDOR,
                location="Venue"
            ),
            RunOfShowSlot(
                start_time=time(10, 30),
                end_time=time(11, 30),
                activity="Guest arrival and welcome",
                description="Reception, welcome drinks, registration",
                owner=TaskOwner.FAMILY,
                location="Entrance"
            ),
            RunOfShowSlot(
                start_time=time(11, 30),
                end_time=time(13, 0),
                activity="Ceremony",
                description="Wedding rituals and ceremony",
                owner=TaskOwner.VENDOR,
                location="Mandap"
            ),
            RunOfShowSlot(
                start_time=time(13, 0),
                end_time=time(14, 30),
                activity="Photography session",
                description="Family and couple photos",
                owner=TaskOwner.VENDOR,
                location="Photo booth area"
            ),
            RunOfShowSlot(
                start_time=time(14, 30),
                end_time=time(16, 0),
                activity="Lunch service",
                description="Buffet or plated meal",
                owner=TaskOwner.VENDOR,
                location="Dining area"
            ),
            RunOfShowSlot(
                start_time=time(16, 0),
                end_time=time(17, 0),
                activity="Closing and guest departure",
                owner=TaskOwner.FAMILY,
                location="Venue"
            ),
        ]
    
    elif profile.event_type.value == "birthday":
        slots = [
            RunOfShowSlot(
                start_time=time(15, 0),
                end_time=time(15, 30),
                activity="Setup and decorations",
                owner=TaskOwner.SELF,
                location="Venue"
            ),
            RunOfShowSlot(
                start_time=time(15, 30),
                end_time=time(16, 0),
                activity="Guest arrival",
                description="Welcome guests, mingling",
                owner=TaskOwner.SELF,
                location="Entrance"
            ),
            RunOfShowSlot(
                start_time=time(16, 0),
                end_time=time(17, 0),
                activity="Games and activities",
                description="Organized entertainment",
                owner=TaskOwner.SELF,
                location="Activity area"
            ),
            RunOfShowSlot(
                start_time=time(17, 0),
                end_time=time(17, 30),
                activity="Cake cutting and singing",
                description="Birthday song, cake cutting, photos",
                owner=TaskOwner.SELF,
                location="Main area"
            ),
            RunOfShowSlot(
                start_time=time(17, 30),
                end_time=time(18, 30),
                activity="Food service",
                description="Snacks and meal",
                owner=TaskOwner.VENDOR,
                location="Dining area"
            ),
            RunOfShowSlot(
                start_time=time(18, 30),
                end_time=time(19, 0),
                activity="Return gifts and departure",
                owner=TaskOwner.SELF,
                location="Exit"
            ),
        ]
    
    elif profile.event_type.value == "community":
        slots = [
            RunOfShowSlot(
                start_time=time(8, 0),
                end_time=time(10, 0),
                activity="Setup: stage, tents, stalls",
                owner=TaskOwner.VOLUNTEER,
                location="Venue"
            ),
            RunOfShowSlot(
                start_time=time(10, 0),
                end_time=time(10, 30),
                activity="Opening ceremony",
                description="Welcome speech, lamp lighting",
                owner=TaskOwner.SELF,
                location="Main stage"
            ),
            RunOfShowSlot(
                start_time=time(10, 30),
                end_time=time(13, 0),
                activity="Main activities and performances",
                description="Cultural programs, stalls open",
                owner=TaskOwner.VOLUNTEER,
                location="Throughout venue"
            ),
            RunOfShowSlot(
                start_time=time(13, 0),
                end_time=time(14, 30),
                activity="Lunch service",
                description="Community meal",
                owner=TaskOwner.VENDOR,
                location="Food area"
            ),
            RunOfShowSlot(
                start_time=time(14, 30),
                end_time=time(17, 0),
                activity="Continued activities",
                description="Games, competitions, entertainment",
                owner=TaskOwner.VOLUNTEER,
                location="Throughout venue"
            ),
            RunOfShowSlot(
                start_time=time(17, 0),
                end_time=time(17, 30),
                activity="Closing ceremony",
                description="Thank you speech, prize distribution",
                owner=TaskOwner.SELF,
                location="Main stage"
            ),
            RunOfShowSlot(
                start_time=time(17, 30),
                end_time=time(19, 0),
                activity="Cleanup and teardown",
                owner=TaskOwner.VOLUNTEER,
                location="Venue"
            ),
        ]
    
    return slots
