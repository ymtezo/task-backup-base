# Task Backup Base Examples

This directory contains sample data files for each supported platform. These files demonstrate the platform-specific data structures and can be used for testing the backup and migration functionality.

## Sample Files

### google_tasks_sample.json
Example of Google Tasks data structure including:
- Task lists
- Tasks with due dates
- Completed tasks
- Hierarchical task structure

### microsoft_todo_sample.json
Example of Microsoft To Do data structure including:
- Lists
- Tasks with importance levels
- Checklist items (subtasks)
- Due dates and body content

### todoist_sample.json
Example of Todoist data structure including:
- Projects
- Tasks with priority levels
- Labels/tags
- Due dates

### ticktick_sample.json
Example of TickTick data structure including:
- Projects
- Tasks with priority levels
- Tags
- Subtasks (items)
- Start and due dates

### notion_sample.json
Example of Notion database structure including:
- Databases (as projects)
- Pages (as tasks)
- Status, priority, and tags properties
- Rich text formatting

### asana_sample.json
Example of Asana data structure including:
- Projects
- Tasks with tags
- Subtasks
- Assignees
- Due dates

## Usage

These sample files can be used with the CLI:

```bash
# Create a backup from Google Tasks sample
python -m task_backup backup google_tasks examples/google_tasks_sample.json

# Migrate from one platform to another
python -m task_backup backup todoist examples/todoist_sample.json --output todoist_backup.json
python -m task_backup migrate todoist_backup.json todoist notion --output notion_migrated.json
```

## Customization

You can create your own sample files following the same structure, or export actual data from your task management platforms and use those files for backup and migration.
