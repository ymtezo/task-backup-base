"""Notion adapter."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseAdapter
from ..models import Task, Project, TaskStatus, TaskPriority, Tag


class NotionAdapter(BaseAdapter):
    """Adapter for Notion.
    
    This adapter provides methods to export and import tasks
    from Notion database format to the common format.
    """
    
    platform_name = "notion"
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        """Initialize the adapter.
        
        Args:
            data: Optional dict containing Notion data structure
        """
        self.data = data or {"databases": [], "pages": []}
    
    def export_tasks(self) -> List[Task]:
        """Export tasks from Notion format."""
        tasks = []
        
        for page in self.data.get("pages", []):
            props = page.get("properties", {})
            
            # Extract title
            title_prop = props.get("Name") or props.get("Title") or {}
            title = self._extract_text(title_prop.get("title", []))
            
            # Extract status
            status_prop = props.get("Status", {})
            status_value = status_prop.get("status", {}).get("name", "")
            status_map = {
                "Done": TaskStatus.COMPLETED,
                "Completed": TaskStatus.COMPLETED,
                "In Progress": TaskStatus.IN_PROGRESS,
                "Not Started": TaskStatus.TODO,
                "": TaskStatus.TODO
            }
            status = status_map.get(status_value, TaskStatus.TODO)
            
            # Extract priority
            priority_prop = props.get("Priority", {})
            priority_value = priority_prop.get("select", {}).get("name", "")
            priority_map = {
                "Low": TaskPriority.LOW,
                "Medium": TaskPriority.MEDIUM,
                "High": TaskPriority.HIGH,
                "Urgent": TaskPriority.URGENT,
                "": TaskPriority.NONE
            }
            priority = priority_map.get(priority_value, TaskPriority.NONE)
            
            # Extract tags
            tags = []
            tags_prop = props.get("Tags", {})
            for tag_item in tags_prop.get("multi_select", []):
                tags.append(Tag(
                    name=tag_item.get("name", ""),
                    color=tag_item.get("color")
                ))
            
            # Extract dates
            due_date = None
            due_prop = props.get("Due", {})
            if due_prop.get("date"):
                due_date = self._parse_datetime(due_prop["date"].get("start"))
            
            # Extract database (project)
            project = page.get("parent", {}).get("database_id")
            
            task = Task(
                id=page.get("id"),
                title=title,
                status=status,
                priority=priority,
                created_at=self._parse_datetime(page.get("created_time")),
                updated_at=self._parse_datetime(page.get("last_edited_time")),
                due_date=due_date,
                project=project,
                tags=tags,
                platform_data={"notion": page}
            )
            tasks.append(task)
        
        return tasks
    
    def export_projects(self) -> List[Project]:
        """Export databases from Notion format."""
        projects = []
        
        for db in self.data.get("databases", []):
            title_prop = db.get("title", [])
            name = self._extract_text(title_prop)
            
            project = Project(
                id=db.get("id"),
                name=name,
                created_at=self._parse_datetime(db.get("created_time")),
                updated_at=self._parse_datetime(db.get("last_edited_time")),
                archived=db.get("archived", False),
                platform_data={"notion": db}
            )
            projects.append(project)
        
        return projects
    
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to Notion format."""
        pages = []
        
        for task in tasks:
            # Map status
            status_map = {
                TaskStatus.TODO: "Not Started",
                TaskStatus.IN_PROGRESS: "In Progress",
                TaskStatus.COMPLETED: "Done",
                TaskStatus.CANCELLED: "Cancelled"
            }
            status_name = status_map.get(task.status, "Not Started")
            
            # Map priority
            priority_map = {
                TaskPriority.NONE: "",
                TaskPriority.LOW: "Low",
                TaskPriority.MEDIUM: "Medium",
                TaskPriority.HIGH: "High",
                TaskPriority.URGENT: "Urgent"
            }
            priority_name = priority_map.get(task.priority, "")
            
            # Build properties
            properties = {
                "Name": {
                    "title": [{"text": {"content": task.title}}]
                }
            }
            
            if status_name:
                properties["Status"] = {
                    "status": {"name": status_name}
                }
            
            if priority_name:
                properties["Priority"] = {
                    "select": {"name": priority_name}
                }
            
            if task.tags:
                properties["Tags"] = {
                    "multi_select": [{"name": tag.name} for tag in task.tags]
                }
            
            if task.due_date:
                properties["Due"] = {
                    "date": {"start": task.due_date.isoformat()}
                }
            
            page = {
                "id": task.id,
                "properties": properties,
                "parent": {"database_id": task.project} if task.project else None
            }
            
            # Restore platform-specific data if available
            if "notion" in task.platform_data:
                page.update(task.platform_data["notion"])
            
            pages.append(page)
        
        self.data["pages"] = pages
    
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects to Notion format."""
        databases = []
        
        for project in projects:
            db = {
                "id": project.id,
                "title": [{"text": {"content": project.name}}],
                "archived": project.archived
            }
            
            # Restore platform-specific data if available
            if "notion" in project.platform_data:
                db.update(project.platform_data["notion"])
            
            databases.append(db)
        
        self.data["databases"] = databases
    
    @staticmethod
    def _extract_text(rich_text_array: List[Dict]) -> str:
        """Extract plain text from Notion rich text array."""
        if not rich_text_array:
            return ""
        return "".join(item.get("text", {}).get("content", "") for item in rich_text_array)
    
    @staticmethod
    def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
