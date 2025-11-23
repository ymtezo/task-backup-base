"""Adapter registry and factory."""

from typing import Dict, Any, Type
from .base import BaseAdapter
from .google_tasks import GoogleTasksAdapter
from .microsoft_todo import MicrosoftToDoAdapter
from .todoist import TodoistAdapter
from .ticktick import TickTickAdapter
from .notion import NotionAdapter
from .asana import AsanaAdapter


# Registry of all available adapters
ADAPTERS: Dict[str, Type[BaseAdapter]] = {
    "google_tasks": GoogleTasksAdapter,
    "microsoft_todo": MicrosoftToDoAdapter,
    "todoist": TodoistAdapter,
    "ticktick": TickTickAdapter,
    "notion": NotionAdapter,
    "asana": AsanaAdapter,
}


def get_adapter(platform: str, data: Dict[str, Any] = None) -> BaseAdapter:
    """Get an adapter instance for the specified platform.
    
    Args:
        platform: Platform name (e.g., 'google_tasks', 'todoist')
        data: Optional platform-specific data structure
        
    Returns:
        BaseAdapter instance for the platform
        
    Raises:
        ValueError: If platform is not supported
    """
    platform = platform.lower()
    if platform not in ADAPTERS:
        raise ValueError(
            f"Unsupported platform: {platform}. "
            f"Supported platforms: {list(ADAPTERS.keys())}"
        )
    
    adapter_class = ADAPTERS[platform]
    return adapter_class(data)


def list_supported_platforms() -> list:
    """Get list of all supported platforms.
    
    Returns:
        List of platform names
    """
    return list(ADAPTERS.keys())
