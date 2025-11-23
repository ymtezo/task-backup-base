"""Microsoft To Do adapter."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter
from ..models import Task, Project, TaskStatus, TaskPriority, Subtask


class MicrosoftToDoAdapter(BaseAdapter):
    """Adapter for Microsoft To Do.
    
    This adapter provides methods to export and import tasks
    from Microsoft To Do format to the common format.
    """
    
    platform_name = "microsoft_todo"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize the adapter.
        
        Args:
            data: Optional dict containing MS To Do data structure
        """
        self.data = data or {"lists": [], "tasks": []}
    
    def export_tasks(self) -> List[Task]:
        """Export tasks from Microsoft To Do format."""
        tasks = []
        
        for mstask in self.data.get("tasks", []):
            # Map importance to priority
            importance = mstask.get("importance", "normal")
            priority_map = {
                "low": TaskPriority.LOW,
                "normal": TaskPriority.MEDIUM,
                "high": TaskPriority.HIGH
            }
            priority = priority_map.get(importance, TaskPriority.NONE)
            
            # Extract subtasks
            subtasks = []
            for item in mstask.get("checklistItems", []):
                subtasks.append(Subtask(
                    title=item.get("displayName", ""),
                    completed=item.get("isChecked", False)
                ))
            
            task = Task(
                id=mstask.get("id"),
                title=mstask.get("title", ""),
                description=mstask.get("body", {}).get("content"),
                status=TaskStatus.COMPLETED if mstask.get("status") == "completed" else TaskStatus.TODO,
                priority=priority,
                created_at=self._parse_datetime(mstask.get("createdDateTime")),
                updated_at=self._parse_datetime(mstask.get("lastModifiedDateTime")),
                due_date=self._parse_datetime(mstask.get("dueDateTime", {}).get("dateTime")),
                completed_at=self._parse_datetime(mstask.get("completedDateTime", {}).get("dateTime")),
                project=mstask.get("listId"),
                subtasks=subtasks,
                platform_data={"microsoft": mstask}
            )
            tasks.append(task)
        
        return tasks
    
    def export_projects(self) -> List[Project]:
        """Export lists from Microsoft To Do format."""
        projects = []
        
        for mslist in self.data.get("lists", []):
            project = Project(
                id=mslist.get("id"),
                name=mslist.get("displayName", ""),
                platform_data={"microsoft": mslist}
            )
            projects.append(project)
        
        return projects
    
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to Microsoft To Do format."""
        mstasks = []
        
        for task in tasks:
            # Map priority to importance
            priority_map = {
                TaskPriority.LOW: "low",
                TaskPriority.MEDIUM: "normal",
                TaskPriority.HIGH: "high",
                TaskPriority.URGENT: "high"
            }
            importance = priority_map.get(task.priority, "normal")
            
            # Convert subtasks
            checklist = []
            for subtask in task.subtasks:
                checklist.append({
                    "displayName": subtask.title,
                    "isChecked": subtask.completed
                })
            
            mstask = {
                "id": task.id,
                "title": task.title,
                "body": {"content": task.description} if task.description else None,
                "status": "completed" if task.status == TaskStatus.COMPLETED else "notStarted",
                "importance": importance,
                "dueDateTime": {"dateTime": task.due_date.isoformat()} if task.due_date else None,
                "completedDateTime": {"dateTime": task.completed_at.isoformat()} if task.completed_at else None,
                "listId": task.project,
                "checklistItems": checklist if checklist else None
            }
            
            # Restore platform-specific data if available
            if "microsoft" in task.platform_data:
                mstask.update(task.platform_data["microsoft"])
            
            mstasks.append(mstask)
        
        self.data["tasks"] = mstasks
    
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects to Microsoft To Do format."""
        mslists = []
        
        for project in projects:
            mslist = {
                "id": project.id,
                "displayName": project.name,
            }
            
            # Restore platform-specific data if available
            if "microsoft" in project.platform_data:
                mslist.update(project.platform_data["microsoft"])
            
            mslists.append(mslist)
        
        self.data["lists"] = mslists
    
    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
