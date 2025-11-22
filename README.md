# SuperSearchLocalDocs

A powerful full-text search system for local document collections. Search across DOCX, PDF, XLSX, CSV, and image files using a fast web interface powered by SQLite FTS5.

## 🚀 Standalone Applications - No Python Required!

SuperSearch Local Docs is distributed as **two standalone Windows applications**:

- **DocumentIndexer.exe** - GUI for setup, configuration, and indexing documents
- **DocumentSearch.exe** - Web server for searching your indexed documents

Both applications work together and require **no Python installation** on end-user computers!

**📖 See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) to build the executables**
**📖 See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for deployment instructions**

### Quick Start for End Users

1. **Run DocumentIndexer.exe** → Configure paths and index your documents
2. **Run DocumentSearch.exe** → Search your indexed documents via web browser
3. **Done!** No Python, no dependencies, no complicated setup.

### For Developers

If you want to run from source or customize the code, see the [Installation](#installation) section below for Python-based development setup.

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
- **Web-based Settings** ⚙️:
  - Configure database path through the UI
  - Support for shared network databases
  - No need to edit config files manually
- **Multi-user support** - point multiple computers to a shared database
- **Abbreviation expansion** - automatically expands abbreviations to keywords (CSV-based)
- **Popular words sidebar** 🔥 - click common words to add them to your search
- **GUI Indexer** - easy-to-use desktop application for initial setup and indexing
- **Pagination** - browse through unlimited results with page navigation
- **Sticky search bar** - stays visible when scrolling
- **Fast SQLite3 FTS5** indexing and search
- **Beautiful web interface** with collapsible filters
- **Network accessible** - server binds to all interfaces
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

## Standalone Executables (No Python Required)

Want to deploy without installing Python? You can create self-contained Windows executables:

### Search Server Executable

```bash
# Install PyInstaller (one-time)
pip install pyinstaller

# Build the search server executable
python build_exe.py
```

This creates a standalone application in `dist\DocumentSearch\` that can run on any Windows computer without Python installed.

### GUI Indexer Executable

```bash
# Build the GUI indexer executable
python build_indexer_exe.py
```

This creates a user-friendly desktop application in `dist\DocumentIndexer\` for easy initial setup and document indexing.

**📖 See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for complete details.**

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

You can index documents using either the **GUI application** (recommended for first-time setup) or the **command-line indexer**.

#### Option A - GUI Indexer (Recommended)

Launch the GUI indexer:

```bash
python indexer_gui.py
```

The GUI provides:
- Easy configuration of document path and database location
- Visual progress tracking
- Save configuration button
- Database statistics viewer
- Error reporting

Simply:
1. Click "Browse..." to select your document folder
2. Choose where to save/create the database file
3. Click "Save Configuration" to save your settings
4. Click "Start Indexing" to begin scanning documents

#### Option B - Command-Line Indexer

Run the command-line indexer to scan and extract text from all supported documents:

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

**Option A - Using Python:**
```bash
python server.py
```

**Option B - Using Batch File (Windows):**
```bash
start_server.bat
```

The server will start and be accessible from:
- **Local computer:** http://localhost:9000
- **Same network:** http://YOUR-IP-ADDRESS:9000

The server now binds to all network interfaces, making it accessible from other computers on your network!

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
- Search abbreviations - automatically expands to keywords (see Abbreviation Expansion below)

### Popular Words Sidebar 🔥

The left sidebar displays the 10 most common words found in your indexed documents:

- **Click any word** to add it to your search query
- **Already searched words** appear greyed out (read-only)
- Auto-updates after each search
- Hidden on smaller screens (< 1024px)

This feature helps you discover frequently used terms and speeds up common searches!

### Abbreviation Expansion

The system supports automatic abbreviation expansion using a CSV file. When you search for an abbreviation, it also searches for all associated keywords.

#### Setup

Create a file named `alternate_names.csv` in your document path with the following format:

```csv
abbreviation,keyword1,keyword2,keyword3,keyword4,keyword5,keyword6,keyword7,keyword8,keyword9,keyword10
API,interface,endpoint,service,rest,web,request
DB,database,sql,storage,query
UI,interface,frontend,display,screen,view
foo,bar,alice,bob,test,sample
```

- **Column 1**: The abbreviation
- **Columns 2-11**: Up to 10 keywords that the abbreviation represents

#### How It Works

When you search for "API", the system automatically searches for:
- "API" (the original term)
- "interface"
- "endpoint"
- "service"
- "rest"
- "web"
- "request"

This also works in reverse - searching for "interface" will also search for "API".

**Example file:** See [alternate_names_example.csv](alternate_names_example.csv) for a sample format.

## Configuration via Web Interface

Click the **⚙️ Settings** button in the top-right corner to configure:

### Database Path
Change where the application looks for the indexed documents database. Perfect for multi-user setups!

**Example use case:** Share a database across multiple computers
```
\\192.168.203.207\Shared Folders\Databases\documents.sqlite3
```

### Document Path
Set the root folder to scan when running the indexer.

**After changing settings:**
1. Click "Save Changes"
2. Refresh your browser page
3. The new settings take effect immediately

**For detailed configuration options, see [SETTINGS.md](SETTINGS.md)**

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
├── config.py                      # Configuration settings
├── config_manager.py              # User configuration manager
├── indexer.py                     # Command-line document indexer
├── indexer_gui.py                 # GUI document indexer (recommended)
├── server.py                      # Flask web server
├── company_abbreviations.py       # Abbreviation expansion system
├── build_exe.py                   # Build script for search server
├── build_indexer_exe.py           # Build script for GUI indexer
├── start_server.bat               # Windows batch file to start server
├── requirements.txt               # Python dependencies
├── user_config.json               # User settings (created after configuration)
├── documents.sqlite3              # SQLite3 database (created after indexing)
├── alternate_names.csv            # Abbreviation mappings (optional)
├── alternate_names_example.csv    # Example abbreviation file
├── templates/
│   └── index.html                # Web search interface
├── BUILD_INSTRUCTIONS.md          # Executable build documentation
├── SETTINGS.md                    # Configuration documentation
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