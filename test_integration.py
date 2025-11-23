#!/usr/bin/env python3
"""Simple test script to validate the task backup system."""

import json
from pathlib import Path
from task_backup.adapters import get_adapter, list_supported_platforms
from task_backup.formats import get_handler
from task_backup.models import Task, TaskStatus, TaskPriority, Tag, Project


def test_adapters():
    """Test that all adapters can be loaded."""
    print("Testing adapter loading...")
    platforms = list_supported_platforms()
    print(f"✓ Found {len(platforms)} supported platforms: {', '.join(platforms)}")
    
    for platform in platforms:
        adapter = get_adapter(platform)
        assert adapter.platform_name == platform, f"Platform name mismatch for {platform}"
    print("✓ All adapters loaded successfully\n")


def test_format_handlers():
    """Test JSON and TOML format handlers."""
    print("Testing format handlers...")
    
    # Create a sample backup
    task = Task(
        title="Test Task",
        description="This is a test",
        status=TaskStatus.TODO,
        priority=TaskPriority.HIGH,
        tags=[Tag(name="test")]
    )
    
    project = Project(
        name="Test Project",
        description="A test project"
    )
    
    from task_backup.models import Backup
    from datetime import datetime
    import tempfile
    
    backup = Backup(
        source_platform="test",
        tasks=[task],
        projects=[project]
    )
    
    # Test JSON
    json_handler = get_handler('json')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_path = Path(f.name)
    json_handler.save(backup, json_path)
    loaded_backup = json_handler.load(json_path)
    assert len(loaded_backup.tasks) == 1
    assert loaded_backup.tasks[0].title == "Test Task"
    json_path.unlink()  # Clean up
    print("✓ JSON format handler works")
    
    # Test TOML
    toml_handler = get_handler('toml')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        toml_path = Path(f.name)
    toml_handler.save(backup, toml_path)
    loaded_backup = toml_handler.load(toml_path)
    assert len(loaded_backup.tasks) == 1
    assert loaded_backup.tasks[0].title == "Test Task"
    toml_path.unlink()  # Clean up
    print("✓ TOML format handler works\n")


def test_google_tasks_adapter():
    """Test Google Tasks adapter with sample data."""
    print("Testing Google Tasks adapter...")
    
    sample_file = Path(__file__).parent / 'examples' / 'google_tasks_sample.json'
    if not sample_file.exists():
        print(f"⚠ Sample file not found: {sample_file}")
        return
    
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    adapter = get_adapter('google_tasks', data)
    backup = adapter.create_backup()
    
    print(f"✓ Exported {len(backup.tasks)} tasks and {len(backup.projects)} projects")
    assert len(backup.tasks) > 0, "Should have tasks"
    assert len(backup.projects) > 0, "Should have projects"
    print("✓ Google Tasks adapter works\n")


def test_round_trip():
    """Test round-trip conversion (export and import)."""
    print("Testing round-trip conversion...")
    
    sample_file = Path(__file__).parent / 'examples' / 'todoist_sample.json'
    if not sample_file.exists():
        print(f"⚠ Sample file not found: {sample_file}")
        return
    
    with open(sample_file, 'r') as f:
        original_data = json.load(f)
    
    # Export from Todoist
    todoist_adapter = get_adapter('todoist', original_data)
    backup = todoist_adapter.create_backup()
    
    # Import to Todoist (new adapter)
    new_adapter = get_adapter('todoist')
    new_adapter.restore_backup(backup)
    
    # Compare
    assert len(new_adapter.data['items']) == len(original_data['items'])
    print(f"✓ Round-trip successful: {len(backup.tasks)} tasks preserved\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Task Backup Base - Integration Tests")
    print("=" * 60 + "\n")
    
    try:
        test_adapters()
        test_format_handlers()
        test_google_tasks_adapter()
        test_round_trip()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
