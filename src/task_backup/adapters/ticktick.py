"""TickTick adapter."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter
from ..models import Task, Project, TaskStatus, TaskPriority, Tag, Subtask


class TickTickAdapter(BaseAdapter):
    """Adapter for TickTick.
    
    This adapter provides methods to export and import tasks
    from TickTick format to the common format.
    """
    
    platform_name = "ticktick"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize the adapter.
        
        Args:
            data: Optional dict containing TickTick data structure
        """
        self.data = data or {"projects": [], "tasks": []}
    
    def export_tasks(self) -> List[Task]:
        """Export tasks from TickTick format."""
        tasks = []
        
        for tttask in self.data.get("tasks", []):
            # Map priority (TickTick uses 0-5)
            priority_value = tttask.get("priority", 0)
            priority_map = {
                0: TaskPriority.NONE,
                1: TaskPriority.LOW,
                3: TaskPriority.MEDIUM,
                5: TaskPriority.HIGH
            }
            priority = priority_map.get(priority_value, TaskPriority.NONE)
            
            # Extract tags
            tags = []
            for tag_name in tttask.get("tags", []):
                tags.append(Tag(name=tag_name))
            
            # Extract subtasks
            subtasks = []
            for item in tttask.get("items", []):
                subtasks.append(Subtask(
                    title=item.get("title", ""),
                    completed=item.get("status", 0) == 2
                ))
            
            task = Task(
                id=tttask.get("id"),
                title=tttask.get("title", ""),
                description=tttask.get("content"),
                status=TaskStatus.COMPLETED if tttask.get("status", 0) == 2 else TaskStatus.TODO,
                priority=priority,
                created_at=self._parse_datetime(tttask.get("createdTime")),
                updated_at=self._parse_datetime(tttask.get("modifiedTime")),
                due_date=self._parse_datetime(tttask.get("dueDate")),
                completed_at=self._parse_datetime(tttask.get("completedTime")),
                start_date=self._parse_datetime(tttask.get("startDate")),
                project=tttask.get("projectId"),
                parent_id=tttask.get("parentId"),
                tags=tags,
                subtasks=subtasks,
                platform_data={"ticktick": tttask}
            )
            tasks.append(task)
        
        return tasks
    
    def export_projects(self) -> List[Project]:
        """Export projects from TickTick format."""
        projects = []
        
        for proj in self.data.get("projects", []):
            project = Project(
                id=proj.get("id"),
                name=proj.get("name", ""),
                color=proj.get("color"),
                archived=proj.get("closed", False),
                platform_data={"ticktick": proj}
            )
            projects.append(project)
        
        return projects
    
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to TickTick format."""
        tttasks = []
        
        for task in tasks:
            # Map priority
            priority_map = {
                TaskPriority.NONE: 0,
                TaskPriority.LOW: 1,
                TaskPriority.MEDIUM: 3,
                TaskPriority.HIGH: 5,
                TaskPriority.URGENT: 5
            }
            priority = priority_map.get(task.priority, 0)
            
            # Convert tags
            tag_names = [tag.name for tag in task.tags]
            
            # Convert subtasks
            items = []
            for subtask in task.subtasks:
                items.append({
                    "title": subtask.title,
                    "status": 2 if subtask.completed else 0
                })
            
            tttask = {
                "id": task.id,
                "title": task.title,
                "content": task.description,
                "status": 2 if task.status == TaskStatus.COMPLETED else 0,
                "priority": priority,
                "dueDate": task.due_date.isoformat() if task.due_date else None,
                "startDate": task.start_date.isoformat() if task.start_date else None,
                "completedTime": task.completed_at.isoformat() if task.completed_at else None,
                "projectId": task.project,
                "parentId": task.parent_id,
                "tags": tag_names,
                "items": items
            }
            
            # Restore platform-specific data if available
            if "ticktick" in task.platform_data:
                tttask.update(task.platform_data["ticktick"])
            
            tttasks.append(tttask)
        
        self.data["tasks"] = tttasks
    
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects to TickTick format."""
        projs = []
        
        for project in projects:
            proj = {
                "id": project.id,
                "name": project.name,
                "color": project.color,
                "closed": project.archived
            }
            
            # Restore platform-specific data if available
            if "ticktick" in project.platform_data:
                proj.update(project.platform_data["ticktick"])
            
            projs.append(proj)
        
        self.data["projects"] = projs
    
    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            # TickTick sometimes uses milliseconds
            if isinstance(dt_str, int):
                return datetime.fromtimestamp(dt_str / 1000)
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError, TypeError):
            return None
