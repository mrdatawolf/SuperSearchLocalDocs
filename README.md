# SuperSearchLocalDocs

A powerful full-text search system for local document collections. Search across DOCX, PDF, XLSX, CSV, and image files using a fast web interface powered by SQLite FTS5.

## Features

- **Comprehensive search** across:
  - File names
  - Folder and subfolder names
  - Document content (text inside files)
- **Advanced filtering**:
  - Search scope (all, filenames only, folders only, content only)
  - File type filters (Word, PDF, Excel, CSV, Images)
  - Date range filtering
  - File size filtering
  - Multiple sort options (relevance, date, name, size)
- **Fast SQLite3 FTS5** indexing and search
- **Beautiful web interface** with collapsible filters
- **Support for multiple formats**:
  - Word Documents (.docx)
  - PDF Documents (.pdf)
  - Excel Spreadsheets (.xlsx)
  - CSV Files (.csv)
  - Images (.jpg, .png, .gif, .bmp, .tiff) with OCR
- **Network share support** - index documents from network locations
- **Smart snippet preview** - see matching text highlighted in results
- **Simple update** - re-run indexer whenever you need to refresh

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (Optional - for image text extraction)

For image text extraction, you'll need Tesseract OCR:

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Or set the path in your environment

**Note:** If Tesseract is not installed, images will be skipped during indexing.

## Configuration

Edit [config.py](config.py) to set your document path:

```python
# Network share path where documents are located
DOCUMENT_PATH = r"\\192.168.203.207\Shared Folders"

# Or use a local path
# DOCUMENT_PATH = r"C:\Users\YourName\Documents"
```

## Usage

### Step 1: Index Your Documents

Run the indexer to scan and extract text from all supported documents:

```bash
python indexer.py
```

This will:
- Scan the configured document path
- Extract text from all supported files
- Store content in SQLite database with FTS5 indexing
- Show progress and statistics

**Note:** You can re-run this anytime to update the index with new or modified documents.

### Step 2: Start the Web Server

Launch the Flask web server:

```bash
python server.py
```

The server will start at: http://127.0.0.1:9000

### Step 3: Search Your Documents

1. Open your browser to http://127.0.0.1:9000
2. Enter your search query (searches file names, folder names, and content)
3. **Optional:** Click "Filters & Options" to refine your search
4. View results with highlighted snippets
5. Click any result to copy the file path to clipboard
6. Paste into Windows Explorer to open the document

**Search Examples:**
- Search "invoice" - finds files named invoice.pdf, folders called "Invoices", or text containing "invoice"
- Search "Acronis" - finds all files in the Acronis folder, files named Acronis*, or documents mentioning Acronis
- Search "security" - finds documents with "security" in the content, filename, or folder path

### Advanced Filtering

Click **"Filters & Options"** to access powerful filtering:

**Search Scope:**
- **All** - Search across filenames, folders, and content (default)
- **Filenames Only** - Search only in document names
- **Folder Names Only** - Search only in folder/subfolder names
- **File Content Only** - Search only inside document text

**File Type Filters:**
- Filter by Word, PDF, Excel, CSV, or Images
- Select multiple types or uncheck to exclude types

**Sort Options:**
- **Relevance** - Best matches first (default)
- **Date Modified** - Newest documents first
- **File Name** - Alphabetical order
- **File Size** - Largest files first

**Date Range:**
- Filter by modified date (from/to)

**File Size:**
- Filter by minimum or maximum file size in bytes
- Example: 1048576 = 1MB

## Project Structure

```
SuperSearchLocalDocs/
├── config.py              # Configuration settings
├── indexer.py             # Document indexer script
├── server.py              # Flask web server
├── requirements.txt       # Python dependencies
├── documents.sqlite3      # SQLite3 database (created after indexing)
├── templates/
│   └── index.html        # Web search interface
└── README.md
```

## How It Works

1. **Indexing**: The indexer walks through your document folder, extracts text from each file based on its type, and stores both metadata and content in SQLite3
2. **Database**: SQLite3 FTS5 (Full-Text Search 5) provides fast full-text search capabilities with ranking across file names, folder paths, and content
3. **Search**: The web interface sends queries to the Flask API, which uses FTS5 to find matching documents across all indexed fields
4. **Results**: Matching documents are displayed with snippets showing the search terms in context

## Updating the Index

To add new documents or refresh the index:

```bash
python indexer.py
```

The indexer will:
- Update existing documents if they've changed
- Add new documents
- Keep the database in sync with your document folder

## Supported File Types

| Format | Extension | Library Used |
|--------|-----------|--------------|
| Word | .docx | python-docx |
| PDF | .pdf | PyPDF2 |
| Excel | .xlsx | openpyxl |
| CSV | .csv | pandas |
| Images | .jpg, .png, .gif, .bmp, .tiff | Pillow + pytesseract |

## Troubleshooting

### Network path not accessible
- Ensure you have permissions to access the network share
- Try mapping the network drive first
- Check that the path in config.py is correct

### Tesseract not found
- Install Tesseract OCR from the link above
- Add Tesseract to your system PATH
- Or skip image indexing (other formats will still work)

### Database not found error
- Run `python indexer.py` first to create the database
- The database is created in the same folder as the scripts

## Future Enhancements

Potential improvements:
- Advanced search syntax (AND, OR, NOT operators)
- Filter by file type, date, size
- Export search results
- Document preview
- Multi-language support
- Scheduled automatic indexing
- Tag and categorize documents

## License

See [LICENSE](LICENSE) file for details.