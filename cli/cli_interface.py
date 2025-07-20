#!/usr/bin/env python3
"""
Command Line Interface for ChatGPT Export Processing

This CLI provides a structured interface to the existing ChatGPT export processing functionality
without modifying the core codebase. It acts as a wrapper around the existing main.py functionality.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path to import existing modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from main import ChatGPTExportProcessor

# Add uploading module to path for metadata functionality
sys.path.append(os.path.join(parent_dir, 'uploading'))
from metadata import get_file_metadata, format_metadata_display, format_file_size


class ChatGPTExportCLI:
    """CLI wrapper for ChatGPT export processing."""
    
    def __init__(self):
        self.processor = None
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser with all commands."""
        parser = argparse.ArgumentParser(
            prog='chatgpt-export',
            description='Process and analyze ChatGPT export files',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  chatgpt-export process export.zip
  chatgpt-export process export.zip --output ./my_extraction
  chatgpt-export analyze ./extracted_data/2025-07-20_Monday_10-30-00
  chatgpt-export metadata ./extracted_data/2025-07-20_Sunday_12-04-32
  chatgpt-export metadata ./extracted_data/2025-07-20_Sunday_12-04-32 --recursive
  chatgpt-export --help
            """
        )
        
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s 1.0.0'
        )
        
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help='Enable verbose output'
        )
        
        # Create subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands'
        )
        
        # Process command
        process_parser = subparsers.add_parser(
            'process',
            help='Process a ChatGPT export ZIP file'
        )
        process_parser.add_argument(
            'zip_file',
            type=str,
            help='Path to the ChatGPT export ZIP file'
        )
        process_parser.add_argument(
            '--output',
            '-o',
            type=str,
            help='Custom output directory for extraction (default: ./extracted_data/timestamp)'
        )
        
        # Analyze command (for future use)
        analyze_parser = subparsers.add_parser(
            'analyze',
            help='Analyze previously extracted data'
        )
        analyze_parser.add_argument(
            'data_path',
            type=str,
            help='Path to extracted data directory'
        )
        analyze_parser.add_argument(
            '--type',
            '-t',
            choices=['cognitive', 'psychological', 'patterns', 'insights'],
            default='insights',
            help='Type of analysis to perform'
        )
        
        # List command
        list_parser = subparsers.add_parser(
            'list',
            help='List available extracted datasets'
        )
        list_parser.add_argument(
            '--path',
            type=str,
            default='./extracted_data',
            help='Path to search for extracted data (default: ./extracted_data)'
        )
        
        # Metadata command
        metadata_parser = subparsers.add_parser(
            'metadata',
            help='Get metadata for files in extracted datasets'
        )
        metadata_parser.add_argument(
            'path',
            type=str,
            help='Path to file or directory to analyze'
        )
        metadata_parser.add_argument(
            '--recursive',
            '-r',
            action='store_true',
            help='Recursively analyze all files in directory'
        )
        metadata_parser.add_argument(
            '--json',
            action='store_true',
            help='Output metadata as JSON'
        )
        
        return parser
    
    def process_command(self, args):
        """Handle the process command."""
        zip_path = args.zip_file
        
        # Validate ZIP file exists
        if not os.path.exists(zip_path):
            print(f"Error: ZIP file not found: {zip_path}")
            sys.exit(1)
        
        if not zip_path.endswith('.zip'):
            print(f"Warning: File does not have .zip extension: {zip_path}")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
        
        # Initialize processor
        base_path = args.output if args.output else str(parent_dir)
        self.processor = ChatGPTExportProcessor(base_path=base_path)
        
        # Process the ZIP file
        try:
            result = self.processor.process_zip(zip_path)
            
            if args.verbose:
                print("\nDetailed Results:")
                print(f"  Status: {result['status']}")
                print(f"  Files extracted: {result['analysis']['file_count']}")
                print(f"  Total size: {result['analysis']['total_size']} bytes")
                
        except Exception as e:
            print(f"Error processing ZIP file: {e}")
            sys.exit(1)
    
    def analyze_command(self, args):
        """Handle the analyze command."""
        data_path = args.data_path
        
        if not os.path.exists(data_path):
            print(f"Error: Data path not found: {data_path}")
            sys.exit(1)
        
        # Import the appropriate analysis module based on type
        analysis_modules = {
            'cognitive': 'cognitive_patterns',
            'psychological': 'psychological_analysis',
            'patterns': 'deep_thought_pattern_analysis',
            'insights': 'conversation_insights'
        }
        
        module_name = analysis_modules.get(args.type)
        
        try:
            # Dynamically import from v001 directory
            v001_path = os.path.join(parent_dir, 'v001')
            sys.path.insert(0, v001_path)
            
            analysis_module = __import__(module_name)
            
            print(f"Running {args.type} analysis on: {data_path}")
            print("Note: This feature integrates with existing v001 analysis modules")
            print("Analysis functionality is preserved from the original codebase")
            
        except ImportError as e:
            print(f"Error: Could not import analysis module '{module_name}': {e}")
            print("Make sure the v001 directory contains the analysis modules")
            sys.exit(1)
    
    def list_command(self, args):
        """Handle the list command."""
        search_path = args.path
        
        if not os.path.exists(search_path):
            print(f"Error: Path not found: {search_path}")
            sys.exit(1)
        
        print(f"Searching for extracted datasets in: {search_path}")
        print("-" * 60)
        
        # Find all extraction directories
        found_dirs = []
        for root, dirs, files in os.walk(search_path):
            # Look for directories that contain conversation.json
            if 'conversations.json' in files:
                rel_path = os.path.relpath(root, search_path)
                found_dirs.append(rel_path)
        
        if found_dirs:
            print(f"Found {len(found_dirs)} extracted dataset(s):\n")
            for dir_path in sorted(found_dirs):
                print(f"  • {dir_path}")
        else:
            print("No extracted datasets found.")
            print("Use 'chatgpt-export process <zip_file>' to extract a dataset first.")
    
    def metadata_command(self, args):
        """Handle the metadata command."""
        target_path = args.path
        
        if not os.path.exists(target_path):
            print(f"Error: Path not found: {target_path}")
            sys.exit(1)
        
        results = {}
        
        if os.path.isfile(target_path):
            # Single file
            metadata = get_file_metadata(target_path)
            results[target_path] = metadata
        else:
            # Directory
            if args.recursive:
                # Recursive directory scan
                for root, _, files in os.walk(target_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        metadata = get_file_metadata(file_path)
                        rel_path = os.path.relpath(file_path, target_path)
                        results[rel_path] = metadata
            else:
                # Just files in the directory
                for file in os.listdir(target_path):
                    file_path = os.path.join(target_path, file)
                    if os.path.isfile(file_path):
                        metadata = get_file_metadata(file_path)
                        results[file] = metadata
        
        # Output results
        if args.json:
            import json
            print(json.dumps(results, indent=2))
        else:
            print(f"Metadata for: {target_path}")
            print("-" * 60)
            
            total_size = 0
            for file_name, metadata in sorted(results.items()):
                print(format_metadata_display(file_name, metadata))
                if metadata["size_bytes"]:
                    total_size += metadata["size_bytes"]
            
            if len(results) > 1:
                print("\n" + "-" * 60)
                print(f"Total files: {len(results)}")
                print(f"Total size: {format_file_size(total_size)}")
    
    def run(self):
        """Main entry point for the CLI."""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            sys.exit(0)
        
        # Route to appropriate command handler
        command_handlers = {
            'process': self.process_command,
            'analyze': self.analyze_command,
            'list': self.list_command,
            'metadata': self.metadata_command
        }
        
        handler = command_handlers.get(args.command)
        if handler:
            handler(args)
        else:
            print(f"Unknown command: {args.command}")
            self.parser.print_help()
            sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli = ChatGPTExportCLI()
    cli.run()


if __name__ == "__main__":
    main()