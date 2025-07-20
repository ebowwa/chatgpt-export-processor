#!/usr/bin/env python3
"""
Main orchestrator for ChatGPT export processing pipeline.

Data Flow:
1. Input: ChatGPT export ZIP file
2. Extraction: Unzip and analyze file metadata
3. Processing: Parse and structure the data
4. (Future) Embeddings: Generate embeddings for conversations
5. (Future) Storage: Store processed data and embeddings
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add uploading module to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'uploading'))

from unzip_export import unzip_file
from metadata import get_file_metadata, format_metadata_display

class ChatGPTExportProcessor:
    """Main processor for ChatGPT export data."""
    
    def __init__(self, base_path: str = None):
        """Initialize processor with base path."""
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.extracted_data = None
        self.processed_data = None
        
    def process_zip(self, zip_path: str) -> Dict[str, Any]:
        """
        Process a ChatGPT export ZIP file.
        
        Args:
            zip_path: Path to the ZIP file
            
        Returns:
            Dict containing processing results
        """
        print(f"Starting ChatGPT export processing...")
        print(f"ZIP file: {zip_path}")
        print("-" * 60)
        
        # Create timestamped extraction folder
        timestamp = datetime.now()
        day_name = timestamp.strftime("%A")
        folder_name = timestamp.strftime(f"%Y-%m-%d_{day_name}_%H-%M-%S")
        extract_path = os.path.join(self.base_path, "extracted_data", folder_name)
        
        # Step 1: Extract and analyze
        print("\n[Step 1/2] Extracting and analyzing files...")
        extracted_files = unzip_file(zip_path, extract_path)
        
        # Store extraction results
        self.extracted_data = {
            "timestamp": timestamp.isoformat(),
            "source_zip": zip_path,
            "extraction_path": extract_path,
            "files": extracted_files
        }
        
        # Step 2: Initial data structure analysis
        print("\n[Step 2/2] Analyzing data structure...")
        self._analyze_data_structure()
        
        print("\n" + "-" * 60)
        print("Processing complete!")
        print(f"Data extracted to: {extract_path}")
        
        return {
            "status": "success",
            "extraction": self.extracted_data,
            "analysis": self.processed_data
        }
    
    def _analyze_data_structure(self):
        """Analyze the structure of extracted data."""
        self.processed_data = {
            "file_count": len(self.extracted_data["files"]),
            "total_size": 0,
            "file_types": {}
        }
        
        for file_info in self.extracted_data["files"]:
            metadata = file_info["metadata"]
            
            # Calculate total size
            if metadata["size_bytes"]:
                self.processed_data["total_size"] += metadata["size_bytes"]
            
            # Track file types
            ext = os.path.splitext(file_info["filename"])[1]
            if ext not in self.processed_data["file_types"]:
                self.processed_data["file_types"][ext] = []
            
            self.processed_data["file_types"][ext].append({
                "filename": file_info["filename"],
                "size": metadata["size_formatted"],
                "lines": metadata["line_count"],
                "json_items": metadata.get("json_items")
            })
        
        # Display summary
        print(f"\nData Structure Summary:")
        print(f"  Total files: {self.processed_data['file_count']}")
        print(f"  Total size: {self._format_size(self.processed_data['total_size'])}")
        print(f"\n  File types:")
        for ext, files in self.processed_data["file_types"].items():
            print(f"    {ext or 'no extension'}: {len(files)} file(s)")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    """Main entry point."""
    # Default ZIP path (update this or pass as argument)
    default_zip = "/Users/ebowwa/Downloads/chatgpt-export/9e791f54d7ad85e80e868d01b7da9356a75cc2a94068a0c9e74f68ee4852dbac-2025-07-20-15-53-05-737327da5c0e460baabc72e2abfccfc6.zip"
    
    # Use command line argument if provided
    zip_path = sys.argv[1] if len(sys.argv) > 1 else default_zip
    
    if not os.path.exists(zip_path):
        print(f"Error: ZIP file not found: {zip_path}")
        print("\nUsage: python main.py [path_to_chatgpt_export.zip]")
        sys.exit(1)
    
    # Process the export
    processor = ChatGPTExportProcessor()
    result = processor.process_zip(zip_path)
    
    # Future integration points
    print("\n[Future Integration Points]")
    print("  • Embedding generation for conversations")
    print("  • Vector database storage")
    print("  • Search and retrieval capabilities")
    print("  • Export to other formats")


if __name__ == "__main__":
    main()