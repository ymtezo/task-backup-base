# task-backup-base

A unified task management framework grounded in scholarly research and practical expertise. Inheriting Emacs and GTD principles, it realizes multidimensional filtering and progressive clarification through thought externalization and minimal operational overhead for stress-free productivity.

## Overview

**Task Backup Base** is a comprehensive solution for backing up and migrating tasks between different task management platforms. It provides:

- **Universal Data Model**: A common format that preserves task information across platforms
- **Multiple Format Support**: Export/import in JSON and TOML formats
- **Platform Coverage**: Support for major task management tools:
  - Google Tasks
  - Microsoft To Do
  - Todoist
  - TickTick
  - Notion
  - Asana

## Features

- 📦 **Local Backups**: Create local backups of your tasks in a standardized format
- 🔄 **Cross-Platform Migration**: Migrate tasks between different platforms seamlessly
- 💾 **Multiple Formats**: Support for JSON and TOML file formats
- 🔌 **Extensible Architecture**: Easy to add new platform adapters
- 🎯 **Data Preservation**: Platform-specific data is preserved during migration
- 🛡️ **Type Safety**: Built with Pydantic for robust data validation

## Installation

```bash
# Clone the repository
git clone https://github.com/ymtezo/task-backup-base.git
cd task-backup-base

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

### Creating a Backup

```bash
# Backup from Google Tasks
python -m task_backup backup google_tasks examples/google_tasks_sample.json --format json

# Backup from Todoist to TOML format
python -m task_backup backup todoist examples/todoist_sample.json --format toml
```

### Migrating Between Platforms

```bash
# Migrate from Google Tasks to Todoist
python -m task_backup migrate backup_google_tasks.json google_tasks todoist --output todoist_migrated.json

# Migrate from Microsoft To Do to Notion
python -m task_backup migrate backup_microsoft_todo.json microsoft_todo notion --format json
```

### List Supported Platforms

```bash
python -m task_backup list
```

## Usage Examples

### Python API

```python
from task_backup.adapters import get_adapter
from task_backup.formats import get_handler

# Load data from a platform
google_adapter = get_adapter('google_tasks', platform_data)
backup = google_adapter.create_backup()

# Save to JSON
json_handler = get_handler('json')
json_handler.save(backup, 'my_backup.json')

# Load backup and migrate to another platform
backup = json_handler.load('my_backup.json')
todoist_adapter = get_adapter('todoist')
todoist_adapter.restore_backup(backup)
```

### Working with the Common Data Model

```python
from task_backup.models import Task, TaskStatus, TaskPriority, Tag

# Create a task
task = Task(
    title="Complete project documentation",
    description="Write comprehensive docs for the new feature",
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH,
    tags=[Tag(name="documentation"), Tag(name="urgent")]
)

# Export to dict
task_dict = task.model_dump()
```

## Data Model

The common data model supports:

- **Task Fields**:
  - Basic: title, description, status, priority
  - Dates: created_at, updated_at, due_date, completed_at, start_date
  - Organization: project, parent_id, tags
  - Advanced: subtasks, recurrence, assignees, location, url
  
- **Project/List Fields**:
  - Basic: name, description, color
  - Metadata: created_at, updated_at, archived

- **Platform Preservation**:
  - Platform-specific data is stored in `platform_data` field
  - Allows round-trip migration without data loss

## Supported Platforms

### Google Tasks
- Task lists and tasks
- Due dates and completion status
- Hierarchical task structure (parent/child)

### Microsoft To Do
- Lists and tasks
- Priority levels (importance)
- Checklist items (subtasks)
- Due dates and completion

### Todoist
- Projects and tasks
- Priority levels (1-4)
- Labels/tags
- Due dates and hierarchical structure

### TickTick
- Projects and tasks
- Priority levels (0-5)
- Tags and subtasks
- Start dates and due dates

### Notion
- Databases and pages (tasks)
- Status, priority, and tags
- Rich text properties
- Due dates

### Asana
- Projects and tasks
- Tags and subtasks
- Assignees
- Due dates and completion tracking

## File Format Examples

### JSON Format
```json
{
  "version": "1.0",
  "source_platform": "google_tasks",
  "created_at": "2025-01-15T10:00:00",
  "projects": [...],
  "tasks": [...]
}
```

### TOML Format
```toml
version = "1.0"
source_platform = "todoist"
created_at = "2025-01-15T10:00:00"

[[projects]]
id = "proj_001"
name = "My Project"

[[tasks]]
id = "task_001"
title = "Sample Task"
```

## Architecture

```
task-backup-base/
├── src/task_backup/
│   ├── models/          # Common data models
│   ├── adapters/        # Platform-specific adapters
│   ├── formats/         # JSON/TOML handlers
│   └── cli/            # Command-line interface
└── examples/           # Sample data files
```

## Contributing

Contributions are welcome! To add support for a new platform:

1. Create a new adapter in `src/task_backup/adapters/`
2. Inherit from `BaseAdapter`
3. Implement `export_tasks()`, `export_projects()`, `import_tasks()`, and `import_projects()`
4. Register the adapter in `adapters/__init__.py`
5. Add example data file in `examples/`

## License

MIT License - see LICENSE file for details

## Acknowledgments

This project is inspired by GTD (Getting Things Done) methodology and builds upon the principles of:
- Thought externalization
- Minimal operational overhead
- Cross-platform compatibility
- Data ownership and portability
