"""Asana adapter."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter
from ..models import Task, Project, TaskStatus, TaskPriority, Tag, Subtask


class AsanaAdapter(BaseAdapter):
    """Adapter for Asana.
    
    This adapter provides methods to export and import tasks
    from Asana format to the common format.
    """
    
    platform_name = "asana"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize the adapter.
        
        Args:
            data: Optional dict containing Asana data structure
        """
        self.data = data or {"projects": [], "tasks": []}
    
    def export_tasks(self) -> List[Task]:
        """Export tasks from Asana format."""
        tasks = []
        
        for asana_task in self.data.get("tasks", []):
            # Extract tags from Asana tags
            tags = []
            for tag_item in asana_task.get("tags", []):
                tags.append(Tag(
                    name=tag_item.get("name", ""),
                    color=tag_item.get("color")
                ))
            
            # Extract subtasks
            subtasks = []
            for subtask_data in asana_task.get("subtasks", []):
                subtasks.append(Subtask(
                    title=subtask_data.get("name", ""),
                    completed=subtask_data.get("completed", False)
                ))
            
            # Get project IDs
            project_ids = [p.get("gid") for p in asana_task.get("projects", [])]
            project = project_ids[0] if project_ids else None
            
            task = Task(
                id=asana_task.get("gid"),
                title=asana_task.get("name", ""),
                description=asana_task.get("notes"),
                status=TaskStatus.COMPLETED if asana_task.get("completed", False) else TaskStatus.TODO,
                created_at=self._parse_datetime(asana_task.get("created_at")),
                updated_at=self._parse_datetime(asana_task.get("modified_at")),
                due_date=self._parse_datetime(asana_task.get("due_on")),
                completed_at=self._parse_datetime(asana_task.get("completed_at")),
                start_date=self._parse_datetime(asana_task.get("start_on")),
                project=project,
                parent_id=asana_task.get("parent", {}).get("gid"),
                tags=tags,
                subtasks=subtasks,
                assignees=[assignee.get("gid", "") for assignee in asana_task.get("assignee", [])],
                platform_data={"asana": asana_task}
            )
            tasks.append(task)
        
        return tasks
    
    def export_projects(self) -> List[Project]:
        """Export projects from Asana format."""
        projects = []
        
        for proj in self.data.get("projects", []):
            project = Project(
                id=proj.get("gid"),
                name=proj.get("name", ""),
                description=proj.get("notes"),
                color=proj.get("color"),
                created_at=self._parse_datetime(proj.get("created_at")),
                updated_at=self._parse_datetime(proj.get("modified_at")),
                archived=proj.get("archived", False),
                platform_data={"asana": proj}
            )
            projects.append(project)
        
        return projects
    
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to Asana format."""
        asana_tasks = []
        
        for task in tasks:
            # Convert tags
            tag_list = []
            for tag in task.tags:
                tag_list.append({
                    "name": tag.name,
                    "color": tag.color
                })
            
            # Convert subtasks
            subtask_list = []
            for subtask in task.subtasks:
                subtask_list.append({
                    "name": subtask.title,
                    "completed": subtask.completed
                })
            
            asana_task = {
                "gid": task.id,
                "name": task.title,
                "notes": task.description,
                "completed": task.status == TaskStatus.COMPLETED,
                "due_on": task.due_date.date().isoformat() if task.due_date else None,
                "start_on": task.start_date.date().isoformat() if task.start_date else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "tags": tag_list,
                "subtasks": subtask_list
            }
            
            if task.project:
                asana_task["projects"] = [{"gid": task.project}]
            
            if task.parent_id:
                asana_task["parent"] = {"gid": task.parent_id}
            
            # Restore platform-specific data if available
            if "asana" in task.platform_data:
                asana_task.update(task.platform_data["asana"])
            
            asana_tasks.append(asana_task)
        
        self.data["tasks"] = asana_tasks
    
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects to Asana format."""
        asana_projects = []
        
        for project in projects:
            proj = {
                "gid": project.id,
                "name": project.name,
                "notes": project.description,
                "color": project.color,
                "archived": project.archived
            }
            
            # Restore platform-specific data if available
            if "asana" in project.platform_data:
                proj.update(project.platform_data["asana"])
            
            asana_projects.append(proj)
        
        self.data["projects"] = asana_projects
    
    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
