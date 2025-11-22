"""Configuration file for document search system"""
import sys
from pathlib import Path

# Detect if running as PyInstaller executable
def _get_default_db_path():
    """Get default database path - parent directory if running as exe, current dir otherwise"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # sys.executable points to DocumentIndexer.exe or DocumentSearch.exe
        # We want parent directory (e.g., C:\Program Files\SuperSearchDocs\)
        exe_dir = Path(sys.executable).parent
        parent_dir = exe_dir.parent
        return str(parent_dir / "documents.sqlite3")
    else:
        # Running from source - use current directory
        return "documents.sqlite3"

# Network share path where documents are located
DOCUMENT_PATH = r"\\192.168.203.207\Shared Folders"

# SQLite database file
# When running as .exe, defaults to parent directory (shared between both apps)
# When running from source, defaults to current directory
DATABASE_PATH = _get_default_db_path()

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.docx': 'Word Document',
    '.csv': 'CSV File',
    '.xlsx': 'Excel Spreadsheet',
    '.pdf': 'PDF Document',
    '.ps1': 'PowerShell Script',
    '.jpg': 'JPEG Image',
    '.jpeg': 'JPEG Image',
    '.png': 'PNG Image',
    '.gif': 'GIF Image',
    '.bmp': 'Bitmap Image',
    '.tiff': 'TIFF Image',
    '.tif': 'TIFF Image'
}

# Server configuration
SERVER_HOST = "192.168.203.29"
SERVER_PORT = 9000
