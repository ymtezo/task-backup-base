"""Base adapter class for platform integrations."""

from abc import ABC, abstractmethod
from typing import List
from ..models import Task, Project, Backup


class BaseAdapter(ABC):
    """Base class for platform adapters."""
    
    platform_name: str = "unknown"
    
    @abstractmethod
    def export_tasks(self) -> List[Task]:
        """Export tasks from the platform.
        
        Returns:
            List of Task objects in common format
        """
        pass
    
    @abstractmethod
    def export_projects(self) -> List[Project]:
        """Export projects/lists from the platform.
        
        Returns:
            List of Project objects in common format
        """
        pass
    
    def create_backup(self) -> Backup:
        """Create a complete backup from the platform.
        
        Returns:
            Backup object containing all tasks and projects
        """
        tasks = self.export_tasks()
        projects = self.export_projects()
        
        return Backup(
            source_platform=self.platform_name,
            tasks=tasks,
            projects=projects
        )
    
    @abstractmethod
    def import_tasks(self, tasks: List[Task]) -> None:
        """Import tasks to the platform.
        
        Args:
            tasks: List of Task objects in common format
        """
        pass
    
    @abstractmethod
    def import_projects(self, projects: List[Project]) -> None:
        """Import projects/lists to the platform.
        
        Args:
            projects: List of Project objects in common format
        """
        pass
    
    def restore_backup(self, backup: Backup) -> None:
        """Restore a backup to the platform.
        
        Args:
            backup: Backup object to restore
        """
        self.import_projects(backup.projects)
        self.import_tasks(backup.tasks)
