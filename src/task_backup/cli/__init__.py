"""Command-line interface for task backup tool."""

import argparse
import sys
from pathlib import Path
from typing import Optional
import json
import toml

from ..adapters import get_adapter, list_supported_platforms
from ..formats import get_handler
from ..models import Backup


def backup_command(args):
    """Execute backup command."""
    print(f"Creating backup from {args.platform}...")
    
    # Load platform data from input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Determine input format
    if input_path.suffix == '.json':
        with open(input_path, 'r', encoding='utf-8') as f:
            platform_data = json.load(f)
    elif input_path.suffix == '.toml':
        with open(input_path, 'r', encoding='utf-8') as f:
            platform_data = toml.load(f)
    else:
        print(f"Error: Unsupported input format. Use .json or .toml")
        sys.exit(1)
    
    # Create adapter and backup
    adapter = get_adapter(args.platform, platform_data)
    backup = adapter.create_backup()
    
    # Save backup
    handler = get_handler(args.format)
    output_path = args.output or f"backup_{args.platform}.{args.format}"
    handler.save(backup, output_path)
    
    print(f"Backup saved to {output_path}")
    print(f"  - {len(backup.tasks)} tasks")
    print(f"  - {len(backup.projects)} projects")


def migrate_command(args):
    """Execute migration command."""
    print(f"Migrating from {args.source} to {args.target}...")
    
    # Load backup
    backup_path = Path(args.backup)
    if not backup_path.exists():
        print(f"Error: Backup file not found: {args.backup}")
        sys.exit(1)
    
    # Determine backup format from extension
    if backup_path.suffix == '.json':
        handler = get_handler('json')
    elif backup_path.suffix == '.toml':
        handler = get_handler('toml')
    else:
        print(f"Error: Unsupported backup format. Use .json or .toml")
        sys.exit(1)
    
    backup = handler.load(backup_path)
    
    # Create target adapter and import
    target_adapter = get_adapter(args.target)
    target_adapter.restore_backup(backup)
    
    # Save target data
    output_format = args.format or 'json'
    output_path = args.output or f"migrated_{args.target}.{output_format}"
    
    if output_format == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(target_adapter.data, f, indent=2, ensure_ascii=False)
    elif output_format == 'toml':
        with open(output_path, 'w', encoding='utf-8') as f:
            toml.dump(target_adapter.data, f)
    else:
        print(f"Error: Unsupported output format: {output_format}")
        sys.exit(1)
    
    print(f"Migration completed and saved to {output_path}")
    print(f"  - {len(backup.tasks)} tasks migrated")
    print(f"  - {len(backup.projects)} projects migrated")


def list_command(args):
    """List supported platforms."""
    print("Supported platforms:")
    for platform in list_supported_platforms():
        print(f"  - {platform}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Task Backup Base - Unified task management backup and migration tool"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup from a platform')
    backup_parser.add_argument('platform', help='Source platform name')
    backup_parser.add_argument('input', help='Input file containing platform data')
    backup_parser.add_argument('--format', default='json', choices=['json', 'toml'],
                               help='Output format (default: json)')
    backup_parser.add_argument('--output', help='Output file path')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate tasks between platforms')
    migrate_parser.add_argument('backup', help='Backup file to migrate from')
    migrate_parser.add_argument('source', help='Source platform name')
    migrate_parser.add_argument('target', help='Target platform name')
    migrate_parser.add_argument('--format', choices=['json', 'toml'],
                                help='Output format (default: same as input)')
    migrate_parser.add_argument('--output', help='Output file path')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List supported platforms')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'backup':
        backup_command(args)
    elif args.command == 'migrate':
        migrate_command(args)
    elif args.command == 'list':
        list_command(args)


if __name__ == '__main__':
    main()
