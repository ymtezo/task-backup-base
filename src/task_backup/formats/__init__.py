"""Format handlers for JSON and TOML."""

import json
import toml
from pathlib import Path
from typing import Union
from ..models import Backup


class FormatHandler:
    """Base class for format handlers."""
    
    def save(self, backup: Backup, filepath: Union[str, Path]) -> None:
        """Save backup to file."""
        raise NotImplementedError
    
    def load(self, filepath: Union[str, Path]) -> Backup:
        """Load backup from file."""
        raise NotImplementedError


class JSONHandler(FormatHandler):
    """JSON format handler."""
    
    def save(self, backup: Backup, filepath: Union[str, Path]) -> None:
        """Save backup to JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(
                backup.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False,
                default=str
            )
    
    def load(self, filepath: Union[str, Path]) -> Backup:
        """Load backup from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Backup(**data)


class TOMLHandler(FormatHandler):
    """TOML format handler."""
    
    def save(self, backup: Backup, filepath: Union[str, Path]) -> None:
        """Save backup to TOML file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and handle datetime objects
        data = backup.model_dump(mode='json')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
    
    def load(self, filepath: Union[str, Path]) -> Backup:
        """Load backup from TOML file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = toml.load(f)
        return Backup(**data)


def get_handler(format_type: str) -> FormatHandler:
    """Get the appropriate format handler.
    
    Args:
        format_type: 'json' or 'toml'
        
    Returns:
        FormatHandler instance
        
    Raises:
        ValueError: If format_type is not supported
    """
    handlers = {
        'json': JSONHandler,
        'toml': TOMLHandler,
    }
    
    format_type = format_type.lower()
    if format_type not in handlers:
        raise ValueError(f"Unsupported format: {format_type}. Supported formats: {list(handlers.keys())}")
    
    return handlers[format_type]()
