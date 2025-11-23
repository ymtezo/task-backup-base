# Data Schema Documentation

This document describes the common data schema used by Task Backup Base for representing tasks and projects across different platforms.

## Common Data Model

The common data model is designed to be platform-agnostic while preserving the essential features of task management systems.

### Task Schema

```python
class Task:
    # Core Identification
    id: Optional[str]                    # Unique identifier
    title: str                           # Task title (required)
    description: Optional[str]            # Detailed description
    
    # Status and Priority
    status: TaskStatus                   # todo, in_progress, completed, cancelled
    priority: TaskPriority               # none, low, medium, high, urgent
    
    # Timestamps
    created_at: Optional[datetime]       # Creation timestamp
    updated_at: Optional[datetime]       # Last update timestamp
    due_date: Optional[datetime]         # Due date and time
    completed_at: Optional[datetime]     # Completion timestamp
    start_date: Optional[datetime]       # Start date
    
    # Organization
    project: Optional[str]               # Project/list ID
    parent_id: Optional[str]             # Parent task ID (for subtasks)
    tags: List[Tag]                      # Tags/labels
    
    # Sub-items
    subtasks: List[Subtask]              # Checklist items
    
    # Recurrence
    recurrence: Optional[Recurrence]     # Recurring task pattern
    
    # Additional Metadata
    notes: Optional[str]                 # Additional notes
    url: Optional[str]                   # Associated URL
    location: Optional[str]              # Location information
    assignees: List[str]                 # Assigned user IDs
    
    # Platform Preservation
    platform_data: Dict[str, Any]        # Platform-specific data
```

### Project Schema

```python
class Project:
    # Core Identification
    id: Optional[str]                    # Unique identifier
    name: str                            # Project name (required)
    description: Optional[str]           # Project description
    
    # Visual
    color: Optional[str]                 # Color code or name
    
    # Timestamps
    created_at: Optional[datetime]       # Creation timestamp
    updated_at: Optional[datetime]       # Last update timestamp
    
    # Status
    archived: bool                       # Archive status (default: False)
    
    # Platform Preservation
    platform_data: Dict[str, Any]        # Platform-specific data
```

### Supporting Types

#### TaskStatus
```python
class TaskStatus(Enum):
    TODO = "todo"                        # Not started
    IN_PROGRESS = "in_progress"          # Currently working on
    COMPLETED = "completed"              # Finished
    CANCELLED = "cancelled"              # Cancelled/dismissed
```

#### TaskPriority
```python
class TaskPriority(Enum):
    NONE = "none"                        # No priority
    LOW = "low"                          # Low priority
    MEDIUM = "medium"                    # Medium priority
    HIGH = "high"                        # High priority
    URGENT = "urgent"                    # Urgent/critical
```

#### Tag
```python
class Tag:
    name: str                            # Tag name
    color: Optional[str]                 # Tag color
```

#### Subtask
```python
class Subtask:
    title: str                           # Subtask title
    completed: bool                      # Completion status
    position: Optional[int]              # Order position
```

#### Recurrence
```python
class Recurrence:
    frequency: str                       # daily, weekly, monthly, yearly
    interval: int                        # Repeat every N periods (default: 1)
    end_date: Optional[datetime]         # When recurrence ends
    days_of_week: Optional[List[int]]    # For weekly: 0-6 (Mon-Sun)
```

### Backup Container

```python
class Backup:
    version: str                         # Schema version
    created_at: datetime                 # Backup creation time
    source_platform: str                 # Original platform
    projects: List[Project]              # All projects
    tasks: List[Task]                    # All tasks
    metadata: Dict[str, Any]             # Additional metadata
```

## Platform Mappings

### Google Tasks

| Google Tasks Field | Common Model Field | Notes |
|-------------------|-------------------|-------|
| id | id | Direct mapping |
| title | title | Direct mapping |
| notes | description | Direct mapping |
| status | status | "completed" → COMPLETED, else TODO |
| due | due_date | ISO 8601 datetime |
| completed | completed_at | ISO 8601 datetime |
| parent | parent_id | For hierarchical tasks |

### Microsoft To Do

| MS To Do Field | Common Model Field | Notes |
|----------------|-------------------|-------|
| id | id | Direct mapping |
| title | title | Direct mapping |
| body.content | description | May contain HTML |
| status | status | "completed" → COMPLETED, else TODO |
| importance | priority | low/normal/high mapping |
| dueDateTime.dateTime | due_date | ISO 8601 datetime |
| checklistItems | subtasks | Array of items |

### Todoist

| Todoist Field | Common Model Field | Notes |
|---------------|-------------------|-------|
| id | id | Direct mapping |
| content | title | Direct mapping |
| description | description | Direct mapping |
| checked | status | 1 → COMPLETED, 0 → TODO |
| priority | priority | 1-4 scale (4 = highest) |
| due.date | due_date | ISO 8601 datetime |
| labels | tags | Array of label IDs |

### TickTick

| TickTick Field | Common Model Field | Notes |
|----------------|-------------------|-------|
| id | id | Direct mapping |
| title | title | Direct mapping |
| content | description | Direct mapping |
| status | status | 2 → COMPLETED, else TODO |
| priority | priority | 0-5 scale (5 = highest) |
| dueDate | due_date | ISO 8601 or timestamp |
| tags | tags | Array of tag names |
| items | subtasks | Checklist items |

### Notion

| Notion Field | Common Model Field | Notes |
|-------------|-------------------|-------|
| id | id | Page ID |
| properties.Name.title | title | Rich text array |
| properties.Status.status.name | status | String status |
| properties.Priority.select.name | priority | Select value |
| properties.Tags.multi_select | tags | Array of tags |
| properties.Due.date.start | due_date | ISO 8601 date |

### Asana

| Asana Field | Common Model Field | Notes |
|------------|-------------------|-------|
| gid | id | Global ID |
| name | title | Direct mapping |
| notes | description | Direct mapping |
| completed | status | Boolean → COMPLETED/TODO |
| due_on | due_date | Date only |
| tags | tags | Array of tag objects |
| subtasks | subtasks | Array of subtask objects |

## Platform-Specific Data Preservation

Each platform may have unique fields that don't map to the common model. These are preserved in the `platform_data` dictionary:

```python
task.platform_data = {
    "google": { /* original Google Tasks data */ },
    "todoist": { /* original Todoist data */ },
    # etc.
}
```

This allows for:
1. Round-trip conversion without data loss
2. Platform-specific features to be preserved
3. Future migration back to the original platform

## JSON Schema Example

```json
{
  "version": "1.0",
  "created_at": "2025-01-15T10:00:00Z",
  "source_platform": "google_tasks",
  "projects": [
    {
      "id": "proj_001",
      "name": "My Tasks",
      "color": null,
      "archived": false
    }
  ],
  "tasks": [
    {
      "id": "task_001",
      "title": "Complete project",
      "description": "Finish the documentation",
      "status": "todo",
      "priority": "high",
      "due_date": "2025-01-20T17:00:00Z",
      "project": "proj_001",
      "tags": [
        {"name": "urgent", "color": "red"}
      ],
      "subtasks": [
        {"title": "Write docs", "completed": false}
      ]
    }
  ],
  "metadata": {}
}
```

## TOML Schema Example

```toml
version = "1.0"
created_at = "2025-01-15T10:00:00Z"
source_platform = "todoist"

[[projects]]
id = "proj_001"
name = "Work Projects"
archived = false

[[tasks]]
id = "task_001"
title = "Important task"
status = "in_progress"
priority = "high"
project = "proj_001"

[[tasks.tags]]
name = "work"
color = "blue"

[[tasks.subtasks]]
title = "Step 1"
completed = true
```

## Validation

All data models use Pydantic for validation:

```python
from task_backup.models import Task, TaskStatus, TaskPriority

# Valid task
task = Task(
    title="My Task",
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH
)

# Invalid task (missing required field)
# task = Task(status=TaskStatus.TODO)  # Raises ValidationError

# Type coercion
task = Task(title="Test", status="todo")  # String is coerced to enum
```

## Extension

To add new fields to the common model:

1. Add field to the appropriate model class
2. Update adapters to map the field
3. Update this documentation
4. Ensure backward compatibility with existing backups
