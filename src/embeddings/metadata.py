import os
import json
from typing import Dict, Any, Optional, Tuple

def format_file_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def count_lines(content: str) -> int:
    """Count lines in text content."""
    if not content:
        return 0
    return content.count('\n') + (1 if not content.endswith('\n') else 0)

def analyze_json_structure(content: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Analyze JSON content structure.
    
    Returns:
        (is_valid_json, structure_type, item_count)
    """
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return True, "array", len(data)
        elif isinstance(data, dict):
            return True, "object", len(data)
        else:
            return True, "scalar", None
    except json.JSONDecodeError:
        return False, None, None

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """
    Get comprehensive metadata for a file.
    
    Returns dict with:
        - size_bytes: File size in bytes
        - size_formatted: Human-readable file size
        - line_count: Number of lines
        - is_json: Whether file is JSON
        - json_type: Type of JSON structure (if applicable)
        - json_items: Number of items/keys (if applicable)
        - error: Any error encountered
    """
    metadata = {
        "size_bytes": None,
        "size_formatted": None,
        "line_count": None,
        "is_json": False,
        "json_type": None,
        "json_items": None,
        "error": None
    }
    
    try:
        # Get file size
        metadata["size_bytes"] = os.path.getsize(file_path)
        metadata["size_formatted"] = format_file_size(metadata["size_bytes"])
        
        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count lines
        metadata["line_count"] = count_lines(content)
        
        # Analyze JSON if applicable
        if file_path.endswith('.json'):
            is_valid, json_type, item_count = analyze_json_structure(content)
            metadata["is_json"] = is_valid
            metadata["json_type"] = json_type
            metadata["json_items"] = item_count
            
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata

def format_metadata_display(filename: str, metadata: Dict[str, Any]) -> str:
    """Format metadata for display."""
    if metadata["error"]:
        return f"  {filename}: Error - {metadata['error']}"
    
    parts = [f"  {filename}: {metadata['size_formatted']}"]
    parts.append(f"{metadata['line_count']:,} lines")
    
    if metadata["is_json"] and metadata["json_items"] is not None:
        if metadata["json_type"] == "array":
            parts.append(f"{metadata['json_items']:,} items")
        elif metadata["json_type"] == "object":
            parts.append(f"{metadata['json_items']:,} keys")
    
    return ", ".join(parts)