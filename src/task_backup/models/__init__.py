"""Common task data models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    """Task priority levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task completion status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Tag(BaseModel):
    """A tag or label for a task."""
    name: str
    color: Optional[str] = None


class Subtask(BaseModel):
    """A subtask or checklist item."""
    title: str
    completed: bool = False
    position: Optional[int] = None


class Recurrence(BaseModel):
    """Recurrence pattern for recurring tasks."""
    frequency: str  # daily, weekly, monthly, yearly
    interval: int = 1
    end_date: Optional[datetime] = None
    days_of_week: Optional[List[int]] = None  # 0-6 for Mon-Sun


class Task(BaseModel):
    """Common task data model.
    
    This model represents a task in a platform-agnostic way,
    compatible with Google Tasks, MS To Do, TickTick, Todoist, Notion, and Asana.
    """
    
    # Core fields
    id: Optional[str] = None
    title: str
    description: Optional[str] = None
    
    # Status and priority
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.NONE
    
    # Dates
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    start_date: Optional[datetime] = None
    
    # Organization
    project: Optional[str] = None
    parent_id: Optional[str] = None
    tags: List[Tag] = Field(default_factory=list)
    
    # Sub-items
    subtasks: List[Subtask] = Field(default_factory=list)
    
    # Recurrence
    recurrence: Optional[Recurrence] = None
    
    # Additional metadata
    notes: Optional[str] = None
    url: Optional[str] = None
    location: Optional[str] = None
    assignees: List[str] = Field(default_factory=list)
    
    # Platform-specific data (preserved during migration)
    platform_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Project(BaseModel):
    """A project or list containing tasks."""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    archived: bool = False
    platform_data: Dict[str, Any] = Field(default_factory=dict)


class Backup(BaseModel):
    """A complete backup of tasks and projects."""
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_platform: str
    projects: List[Project] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
