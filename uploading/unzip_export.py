import zipfile
import os
from datetime import datetime
from metadata import get_file_metadata, format_metadata_display

def unzip_file(zip_path, extract_to=None):
    """
    Unzip a file to the specified directory and analyze extracted files.
    
    Args:
        zip_path (str): Path to the zip file
        extract_to (str): Directory to extract files to. If None, extracts to the same directory as the zip file.
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    
    if extract_to is None:
        extract_to = os.path.dirname(zip_path)
    
    os.makedirs(extract_to, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Successfully extracted {zip_path} to {extract_to}")
        print(f"\nExtracted files with metadata:")
        
        extracted_files = []
        for filename in zip_ref.namelist():
            file_path = os.path.join(extract_to, filename)
            if os.path.isfile(file_path):
                metadata = get_file_metadata(file_path)
                print(format_metadata_display(filename, metadata))
                extracted_files.append({
                    "filename": filename,
                    "path": file_path,
                    "metadata": metadata
                })
        
        return extracted_files

if __name__ == "__main__":
    zip_file_path = "/Users/ebowwa/Downloads/chatgpt-export/9e791f54d7ad85e80e868d01b7da9356a75cc2a94068a0c9e74f68ee4852dbac-2025-07-20-15-53-05-737327da5c0e460baabc72e2abfccfc6.zip"
    
    # Create timestamped folder with day name
    timestamp = datetime.now()
    day_name = timestamp.strftime("%A")  # Full day name (e.g., "Monday")
    folder_name = timestamp.strftime(f"%Y-%m-%d_{day_name}_%H-%M-%S")
    extract_path = os.path.join(os.path.dirname(zip_file_path), folder_name)
    
    unzip_file(zip_file_path, extract_path)