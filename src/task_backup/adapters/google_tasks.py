"""Google Tasks adapter."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter
from ..models import Task, Project, TaskStatus, TaskPriority, Subtask


class GoogleTasksAdapter(BaseAdapter):
    """Adapter for Google Tasks.
    
    This adapter provides methods to export and import tasks
    from Google Tasks format to the common format.
    """
    
    platform_name = "google_tasks"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize the adapter.
        
        Args:
            data: Optional dict containing Google Tasks data structure
        """
        self.data = data or {"taskLists": [], "tasks": []}
    
    def export_tasks(self) -> List[Task]:
        """Export tasks from Google Tasks format."""
        tasks = []
        
        for gtask in self.data.get("tasks", []):
            task = Task(
                id=gtask.get("id"),
                title=gtask.get("title", ""),
                description=gtask.get("notes"),
                status=TaskStatus.COMPLETED if gtask.get("status") == "completed" else TaskStatus.TODO,
                created_at=self._parse_datetime(gtask.get("created")),
                updated_at=self._parse_datetime(gtask.get("updated")),
                due_date=self._parse_datetime(gtask.get("due")),
                completed_at=self._parse_datetime(gtask.get("completed")),
                parent_id=gtask.get("parent"),
                project=gtask.get("taskListId"),
                platform_data={"google": gtask}
            )
            tasks.append(task)
        
        return tasks
    
    def export_projects(self) -> List[Project]:
        """Export task lists from Google Tasks format."""
        projects = []
        
        for tasklist in self.data.get("taskLists", []):
            project = Project(
                id=tasklist.get("id"),
                name=tasklist.get("title", ""),
                updated_at=self._parse_datetime(tasklist.get("updated")),
                platform_data={"google": tasklist}
            )
            projects.append(project)
        
        return projects
    
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to Google Tasks format."""
        gtasks = []
        
        for task in tasks:
            gtask = {
                "id": task.id,
                "title": task.title,
                "notes": task.description,
                "status": "completed" if task.status == TaskStatus.COMPLETED else "needsAction",
                "due": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed_at.isoformat() if task.completed_at else None,
                "parent": task.parent_id,
                "taskListId": task.project,
            }
            
            # Restore platform-specific data if available
            if "google" in task.platform_data:
                gtask.update(task.platform_data["google"])
            
            gtasks.append(gtask)
        
        self.data["tasks"] = gtasks
    
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects to Google Tasks format."""
        tasklists = []
        
        for project in projects:
            tasklist = {
                "id": project.id,
                "title": project.name,
            }
            
            # Restore platform-specific data if available
            if "google" in project.platform_data:
                tasklist.update(project.platform_data["google"])
            
            tasklists.append(tasklist)
        
        self.data["taskLists"] = tasklists
    
    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
