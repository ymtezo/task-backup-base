# Usage Guide

This guide provides detailed instructions for using the Task Backup Base system.

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

## Basic Usage

### Creating Backups

#### From the Command Line

```bash
# Backup from Google Tasks (JSON format)
python -m task_backup backup google_tasks my_google_tasks.json

# Backup from Todoist (TOML format)
python -m task_backup backup todoist my_todoist_data.json --format toml

# Specify output file
python -m task_backup backup microsoft_todo my_tasks.json --output my_backup.json
```

#### Using Python API

```python
from task_backup.adapters import get_adapter
from task_backup.formats import get_handler
import json

# Load your platform data
with open('my_google_tasks.json', 'r') as f:
    platform_data = json.load(f)

# Create adapter and backup
adapter = get_adapter('google_tasks', platform_data)
backup = adapter.create_backup()

# Save to file
handler = get_handler('json')
handler.save(backup, 'my_backup.json')
```

### Migrating Between Platforms

#### From the Command Line

```bash
# Migrate from Google Tasks to Todoist
python -m task_backup migrate my_backup.json google_tasks todoist

# Specify output format and file
python -m task_backup migrate my_backup.json todoist notion --format json --output notion_data.json
```

#### Using Python API

```python
from task_backup.adapters import get_adapter
from task_backup.formats import get_handler

# Load backup
handler = get_handler('json')
backup = handler.load('my_backup.json')

# Create target adapter
target_adapter = get_adapter('notion')
target_adapter.restore_backup(backup)

# Access the converted data
notion_data = target_adapter.data
```

### Working with Different Formats

#### JSON Format

```python
from task_backup.formats import JSONHandler
from task_backup.models import Backup

handler = JSONHandler()

# Save
handler.save(backup, 'backup.json')

# Load
backup = handler.load('backup.json')
```

#### TOML Format

```python
from task_backup.formats import TOMLHandler
from task_backup.models import Backup

handler = TOMLHandler()

# Save
handler.save(backup, 'backup.toml')

# Load
backup = handler.load('backup.toml')
```

## Advanced Usage

### Creating Tasks Programmatically

```python
from task_backup.models import Task, TaskStatus, TaskPriority, Tag, Subtask
from datetime import datetime

task = Task(
    title="Complete project documentation",
    description="Write comprehensive documentation for the new feature",
    status=TaskStatus.IN_PROGRESS,
    priority=TaskPriority.HIGH,
    due_date=datetime(2025, 1, 30),
    tags=[
        Tag(name="documentation", color="blue"),
        Tag(name="urgent", color="red")
    ],
    subtasks=[
        Subtask(title="Write API reference", completed=True),
        Subtask(title="Create usage examples", completed=False)
    ]
)
```

### Creating Complete Backups

```python
from task_backup.models import Backup, Project, Task
from datetime import datetime

# Create projects
project = Project(
    name="Work Projects",
    description="All work-related tasks",
    color="blue"
)

# Create tasks
task1 = Task(title="Task 1", project=project.id)
task2 = Task(title="Task 2", project=project.id)

# Create backup
backup = Backup(
    source_platform="custom",
    projects=[project],
    tasks=[task1, task2]
)
```

### Custom Data Processing

```python
from task_backup.adapters import get_adapter
import json

# Load and process data
with open('source_data.json', 'r') as f:
    data = json.load(f)

adapter = get_adapter('todoist', data)
backup = adapter.create_backup()

# Filter high-priority tasks
high_priority_tasks = [
    task for task in backup.tasks 
    if task.priority in [TaskPriority.HIGH, TaskPriority.URGENT]
]

# Create filtered backup
filtered_backup = Backup(
    source_platform=backup.source_platform,
    projects=backup.projects,
    tasks=high_priority_tasks
)
```

### Batch Processing

```python
from pathlib import Path
from task_backup.adapters import get_adapter
from task_backup.formats import get_handler
import json

# Process multiple files
source_files = Path('backups').glob('*.json')
handler = get_handler('json')

for source_file in source_files:
    with open(source_file, 'r') as f:
        data = json.load(f)
    
    # Detect platform (you might need custom logic)
    adapter = get_adapter('google_tasks', data)
    backup = adapter.create_backup()
    
    # Save processed backup
    output_file = f'processed_{source_file.name}'
    handler.save(backup, output_file)
```

## Platform-Specific Notes

### Google Tasks
- Supports hierarchical tasks (parent/child relationships)
- Due dates are in ISO 8601 format
- Status can be "needsAction" or "completed"

### Microsoft To Do
- Importance levels: low, normal, high
- Supports checklist items (subtasks)
- Body content uses content type (text/html)

### Todoist
- Priority levels: 1 (none) to 4 (urgent)
- Labels are separate entities
- Supports recurring tasks

### TickTick
- Priority levels: 0 (none), 1 (low), 3 (medium), 5 (high)
- Tags are simple strings
- Supports start dates and due dates

### Notion
- Uses database/page structure
- Rich text formatting in properties
- Status and priority as select properties

### Asana
- Tasks can belong to multiple projects
- Supports subtasks and assignees
- Tags have colors

## Troubleshooting

### Import Errors
Make sure the package is installed:
```bash
pip install -e .
```

### Data Format Issues
Validate your input data matches the expected platform format. Check the example files in the `examples/` directory.

### Migration Issues
Some platform-specific features may not have direct equivalents. The system preserves original data in the `platform_data` field.

## Best Practices

1. **Regular Backups**: Create backups regularly to avoid data loss
2. **Test Migrations**: Test migrations with sample data before applying to your full dataset
3. **Preserve Original Data**: Keep original backups when migrating between platforms
4. **Use Version Control**: Store backups in version control for history tracking
5. **Validate Results**: Check migrated data to ensure all important information was preserved

## Examples

See the `examples/` directory for sample data files and the `test_integration.py` file for code examples.
