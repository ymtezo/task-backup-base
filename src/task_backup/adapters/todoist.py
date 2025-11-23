"""Todoist adapter."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter
from ..models import Task, Project, TaskStatus, TaskPriority, Tag


class TodoistAdapter(BaseAdapter):
    """Adapter for Todoist.
    
    This adapter provides methods to export and import tasks
    from Todoist format to the common format.
    """
    
    platform_name = "todoist"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize the adapter.
        
        Args:
            data: Optional dict containing Todoist data structure
        """
        self.data = data or {"projects": [], "items": [], "labels": []}
    
    def export_tasks(self) -> List[Task]:
        """Export tasks from Todoist format."""
        tasks = []
        labels_map = {label["id"]: label["name"] for label in self.data.get("labels", [])}
        
        for item in self.data.get("items", []):
            # Map priority (Todoist uses 1-4, where 4 is most urgent)
            priority_value = item.get("priority", 1)
            priority_map = {
                1: TaskPriority.NONE,
                2: TaskPriority.LOW,
                3: TaskPriority.MEDIUM,
                4: TaskPriority.HIGH
            }
            priority = priority_map.get(priority_value, TaskPriority.NONE)
            
            # Extract tags from labels
            tags = []
            for label_id in item.get("labels", []):
                if label_id in labels_map:
                    tags.append(Tag(name=labels_map[label_id]))
            
            task = Task(
                id=item.get("id"),
                title=item.get("content", ""),
                description=item.get("description"),
                status=TaskStatus.COMPLETED if item.get("checked", 0) == 1 else TaskStatus.TODO,
                priority=priority,
                created_at=self._parse_datetime(item.get("added_at")),
                due_date=self._parse_datetime(item.get("due", {}).get("date")) if item.get("due") else None,
                completed_at=self._parse_datetime(item.get("completed_at")),
                project=item.get("project_id"),
                parent_id=item.get("parent_id"),
                tags=tags,
                platform_data={"todoist": item}
            )
            tasks.append(task)
        
        return tasks
    
    def export_projects(self) -> List[Project]:
        """Export projects from Todoist format."""
        projects = []
        
        for proj in self.data.get("projects", []):
            project = Project(
                id=proj.get("id"),
                name=proj.get("name", ""),
                color=proj.get("color"),
                archived=proj.get("is_archived", False),
                platform_data={"todoist": proj}
            )
            projects.append(project)
        
        return projects
    
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to Todoist format."""
        items = []
        all_labels = []
        label_names = set()
        
        for task in tasks:
            # Map priority
            priority_map = {
                TaskPriority.NONE: 1,
                TaskPriority.LOW: 2,
                TaskPriority.MEDIUM: 3,
                TaskPriority.HIGH: 4,
                TaskPriority.URGENT: 4
            }
            priority = priority_map.get(task.priority, 1)
            
            # Handle labels/tags
            label_ids = []
            for tag in task.tags:
                if tag.name not in label_names:
                    label_id = f"label_{len(all_labels)}"
                    all_labels.append({
                        "id": label_id,
                        "name": tag.name,
                        "color": tag.color or "charcoal"
                    })
                    label_names.add(tag.name)
                    label_ids.append(label_id)
            
            item = {
                "id": task.id,
                "content": task.title,
                "description": task.description,
                "checked": 1 if task.status == TaskStatus.COMPLETED else 0,
                "priority": priority,
                "project_id": task.project,
                "parent_id": task.parent_id,
                "labels": label_ids,
            }
            
            if task.due_date:
                item["due"] = {"date": task.due_date.isoformat()}
            
            # Restore platform-specific data if available
            if "todoist" in task.platform_data:
                item.update(task.platform_data["todoist"])
            
            items.append(item)
        
        self.data["items"] = items
        if all_labels:
            self.data["labels"] = all_labels
    
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects to Todoist format."""
        projs = []
        
        for project in projects:
            proj = {
                "id": project.id,
                "name": project.name,
                "color": project.color or "charcoal",
                "is_archived": project.archived
            }
            
            # Restore platform-specific data if available
            if "todoist" in project.platform_data:
                proj.update(project.platform_data["todoist"])
            
            projs.append(proj)
        
        self.data["projects"] = projs
    
    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
