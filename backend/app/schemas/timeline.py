"""Timeline and task schemas."""
from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Task completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskOwner(str, Enum):
    """Who is responsible for the task."""
    SELF = "self"
    FAMILY = "family"
    VENDOR = "vendor"
    VOLUNTEER = "volunteer"


class Task(BaseModel):
    """Individual task in the timeline."""
    
    id: str = Field(..., description="Task ID")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task details")
    due_date: date = Field(..., description="Task due date")
    owner: TaskOwner = Field(default=TaskOwner.SELF, description="Task owner")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priority")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="Status")
    phase: str = Field(..., description="Planning phase (e.g., '12 weeks out', 'Event day')")
    depends_on: List[str] = Field(default_factory=list, description="Task IDs this depends on")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "task_001",
                "title": "Book venue",
                "description": "Reserve wedding venue for 250 guests, check availability for backup date",
                "due_date": "2023-11-15",
                "owner": "self",
                "priority": "urgent",
                "status": "not_started",
                "phase": "12 weeks out",
                "depends_on": []
            }
        }


class RunOfShowSlot(BaseModel):
    """Time slot in the event day schedule."""
    
    start_time: time = Field(..., description="Slot start time")
    end_time: time = Field(..., description="Slot end time")
    activity: str = Field(..., min_length=1, max_length=200, description="Activity name")
    description: Optional[str] = Field(None, max_length=500, description="Activity details")
    owner: TaskOwner = Field(default=TaskOwner.SELF, description="Who manages this")
    location: Optional[str] = Field(None, max_length=100, description="Location within venue")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_time": "10:00:00",
                "end_time": "11:00:00",
                "activity": "Guest arrival & welcome drinks",
                "description": "Guests arrive, registration, welcome drinks and snacks",
                "owner": "vendor",
                "location": "Main entrance & lobby"
            }
        }


class Timeline(BaseModel):
    """Complete event timeline."""
    
    event_id: str = Field(..., description="Associated event ID")
    tasks: List[Task] = Field(..., description="All planning tasks")
    run_of_show: List[RunOfShowSlot] = Field(default_factory=list, description="Event day schedule")
    planning_start_date: date = Field(..., description="When planning begins")
    event_date: date = Field(..., description="Event date")
    short_notice: bool = Field(default=False, description="Whether timeline is compressed")
    
    @property
    def tasks_by_phase(self) -> dict:
        """Group tasks by phase."""
        phases = {}
        for task in self.tasks:
            if task.phase not in phases:
                phases[task.phase] = []
            phases[task.phase].append(task)
        return phases
    
    @property
    def completed_tasks_count(self) -> int:
        """Count completed tasks."""
        return sum(1 for task in self.tasks if task.status == TaskStatus.COMPLETED)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if not self.tasks:
            return 0.0
        return (self.completed_tasks_count / len(self.tasks)) * 100
    
    @property
    def urgent_tasks(self) -> List[Task]:
        """Get urgent incomplete tasks."""
        return [
            task for task in self.tasks
            if task.priority == TaskPriority.URGENT
            and task.status != TaskStatus.COMPLETED
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_12345",
                "planning_start_date": "2023-11-15",
                "event_date": "2024-02-15",
                "short_notice": False,
                "tasks": []
            }
        }
