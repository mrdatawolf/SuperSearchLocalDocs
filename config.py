"""Configuration file for document search system"""
import sys
from pathlib import Path

# Detect if running as PyInstaller executable
def _get_databases_folder():
    """Get databases folder path - parent/databases if running as exe, ./databases otherwise"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # sys.executable points to DocumentIndexer.exe or DocumentSearch.exe
        # We want parent directory (e.g., C:\Program Files\SuperSearchDocs\)
        exe_dir = Path(sys.executable).parent
        parent_dir = exe_dir.parent
        databases_folder = parent_dir / "databases"
    else:
        # Running from source - use databases subfolder in current directory
        databases_folder = Path(__file__).parent / "databases"

    # Create databases folder if it doesn't exist
    databases_folder.mkdir(exist_ok=True)

    return str(databases_folder)

# Network share path where documents are located (default for backward compatibility)
DOCUMENT_PATH = r"\\192.168.203.207\Shared Folders"

# SQLite database folder - all databases stored here
# When running as .exe, uses parent/databases directory (shared between both apps)
# When running from source, uses ./databases directory
# Individual databases are managed by database_manager.py
DATABASES_FOLDER = _get_databases_folder()

# Legacy - kept for backward compatibility
# New code should use database_manager.py instead
DATABASE_PATH = str(Path(DATABASES_FOLDER) / "documents.sqlite3")

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.docx': 'Word Document',
    '.csv': 'CSV File',
    '.xlsx': 'Excel Spreadsheet',
    '.xls': 'Excel Spreadsheet (Legacy)',
    '.pdf': 'PDF Document',
    '.txt': 'Text File',
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
