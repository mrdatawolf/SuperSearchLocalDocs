"""Configuration file for document search system"""

# Network share path where documents are located
DOCUMENT_PATH = r"\\192.168.203.207\Shared Folders"

# SQLite database file
DATABASE_PATH = "documents.sqlite3"

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    '.docx': 'Word Document',
    '.csv': 'CSV File',
    '.xlsx': 'Excel Spreadsheet',
    '.pdf': 'PDF Document',
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
