# SuperSearchLocalDocs

A powerful full-text search system for local document collections. Search across DOCX, PDF, XLSX, CSV, and image files using a fast web interface powered by SQLite FTS5.

## Standalone Applications - No Python Required!

SuperSearch Local Docs is distributed as **three standalone Windows applications**:

- **DocumentIndexer.exe** - GUI for setup, configuration, and indexing documents
- **DocumentSearchGUI.exe** - Desktop application for searching (recommended)
- **DocumentSearch.exe** - Web server for searching (browser-based)

All applications work together and require **no Python installation** on end-user computers!

See [BUILD_INSTRUCTIONS.md](INFO/BUILD_INSTRUCTIONS.md) to build the executables.
See [DEPLOYMENT_GUIDE.md](INFO/DEPLOYMENT_GUIDE.md) for deployment instructions.
See [END_USER_README.md](INFO/END_USER_README.md) for the end-user guide.

### Quick Start for End Users

1. **Run DocumentIndexer.exe** - Configure server IP and index your documents
2. **Run DocumentSearchGUI.exe** - Search your documents in a desktop app
3. **Done!** No Python, no dependencies, no complicated setup.

**Alternative:** Run `DocumentSearch.exe` to use the browser-based interface instead.

**Network Access:** Configure your server IP address in DocumentIndexer.exe to allow access from other computers on your network.

For a more detailed walkthrough, see [QUICK_START.md](INFO/QUICK_START.md).

### For Developers

If you want to run from source or customize the code, see the [Installation](#installation) section below for Python-based development setup.

## Features

- **Comprehensive search** across file names, folder/subfolder names, and document content
- **Advanced filtering**: search scope, file type filters, date range, file size, multiple sort options
- **Web-based Settings** - configure database path through the UI (see [SETTINGS.md](INFO/SETTINGS.md))
- **Multi-database support** - index multiple folders, each with its own database (see [Multi-Database Architecture](INFO/MULTI_DATABASE_ARCHITECTURE.md))
- **Parallel processing** - dramatically faster indexing using multiple CPU cores (see [Parallel Processing](INFO/PARALLEL_PROCESSING.md))
- **Parallel folder indexing** - index multiple folders simultaneously (see [Parallel Folder Indexing](INFO/PARALLEL_FOLDER_INDEXING.md))
- **Link existing databases** - connect to pre-indexed databases without re-indexing (see [Linking Existing Databases](INFO/LINKING_EXISTING_DATABASES.md))
- **Multi-user support** - point multiple computers to a shared database
- **Abbreviation expansion** - automatically expands abbreviations to keywords (CSV-based)
- **Popular words sidebar** - click common words to add them to your search
- **Pre-calculated word counts** - popular words load instantly (<100ms) (see [Word Counts Optimization](INFO/WORD_COUNTS_OPTIMIZATION.md))
- **GUI Indexer** - easy-to-use desktop application for initial setup and indexing
- **Pagination** - browse through unlimited results with page navigation
- **Sticky search bar** - stays visible when scrolling
- **Fast SQLite3 FTS5** indexing and search
- **Beautiful web interface** with collapsible filters
- **Network accessible** - server binds to all interfaces
- **Network share support** - index documents from network locations (including UNC paths)
- **Smart snippet preview** - see matching text highlighted in results
- **File action buttons** - open file, open folder, or copy path directly from search results
- **Configurable default action** - click search results to perform your preferred action (open/copy/folder)
- **Support for multiple formats**: Word (.docx), PDF (.pdf), Excel (.xlsx, .xls), CSV (.csv), Text (.txt), PowerShell (.ps1), Images (.jpg, .png, .gif, .bmp, .tiff) with OCR

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

**Note:** If Tesseract is not installed, images will be skipped during indexing.

## Configuration

Edit [config.py](config.py) to set your document path:

```python
# Network share path where documents are located
DOCUMENT_PATH = r"\\192.168.203.207\Shared Folders"

# Or use a local path
# DOCUMENT_PATH = r"C:\Users\YourName\Documents"
```

For web-based configuration options, see [SETTINGS.md](INFO/SETTINGS.md).

## Usage

### Step 1: Index Your Documents

#### Option A - GUI Indexer (Recommended)

```bash
python indexer_gui.py
```

The GUI provides easy configuration, visual progress tracking, and database statistics.

#### Option B - Command-Line Indexer

```bash
python indexer.py
```

### Step 2: Start the Web Server

```bash
python server.py
```

The server will start and be accessible from:
- **Local computer:** http://localhost:9000
- **Same network:** http://YOUR-IP-ADDRESS:9000

### Step 3: Search Your Documents

1. Open your browser to http://127.0.0.1:9000
2. Enter your search query (searches file names, folder names, and content)
3. **Optional:** Click "Filters & Options" to refine your search
4. View results with highlighted snippets
5. Use action buttons: **Open File**, **Copy Path**, or **Open Folder**

## API Integration

SuperSearch Local Docs provides a complete REST API. A ready-to-use example is included: **[api_integration_example.html](api_integration_example.html)**

### Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | POST | Search documents with filters and pagination |
| `/api/stats` | GET | Get database statistics (total docs, databases, last update) |
| `/api/top-words` | GET | Get the top 10 most common words across all documents |
| `/api/file/open` | POST | Open a file in its default application |
| `/api/file/open-folder` | POST | Open the folder containing a file |
| `/api/settings` | GET/POST | Get or update application settings |

### Abbreviation Expansion

The system supports automatic abbreviation expansion using a CSV file. Create `alternate_names.csv` in your document path:

```csv
abbreviation,keyword1,keyword2,keyword3,keyword4,keyword5,keyword6,keyword7,keyword8,keyword9,keyword10
API,interface,endpoint,service,rest,web,request
DB,database,sql,storage,query
```

See [alternate_names_example.csv](alternate_names_example.csv) for a sample format.

## Project Structure

```
SuperSearchLocalDocs/
├── config.py                      # Configuration settings
├── config_manager.py              # User configuration manager
├── database_manager.py            # Multi-database management
├── indexer.py                     # Command-line document indexer
├── indexer_gui.py                 # GUI document indexer (recommended)
├── server.py                      # Flask web server
├── search_gui.py                  # Desktop search application
├── company_abbreviations.py       # Abbreviation expansion system
├── build_exe.py                   # Build script for search server
├── build_indexer_exe.py           # Build script for GUI indexer
├── build_search_gui_exe.py        # Build script for search GUI
├── build_all.py                   # Build all executables
├── start_server.bat               # Windows batch file to start server
├── requirements.txt               # Python dependencies
├── user_config.json               # User settings (created after configuration)
├── vacuum_databases.py            # Database compaction utility
├── api_integration_example.html   # API integration example page
├── alternate_names.csv            # Abbreviation mappings (optional)
├── alternate_names_example.csv    # Example abbreviation file
├── templates/
│   └── index.html                # Web search interface
├── databases/                     # Database files (created after indexing)
│   └── *.sqlite3                 # One database per indexed folder
├── INFO/                          # Detailed documentation
│   ├── BUILD_INSTRUCTIONS.md      # Executable build documentation
│   ├── DEPLOYMENT_GUIDE.md        # Deployment instructions
│   ├── END_USER_README.md         # End-user guide
│   ├── SETTINGS.md                # Configuration documentation
│   ├── QUICK_START.md             # Detailed quick start guide
│   ├── QUICKSTART.md              # Short quick start guide
│   ├── MULTI_DATABASE_ARCHITECTURE.md  # Multi-database design docs
│   ├── PARALLEL_PROCESSING.md     # Parallel processing documentation
│   ├── PARALLEL_FOLDER_INDEXING.md # Parallel folder indexing docs
│   ├── IMPLEMENTATION_SUMMARY.md  # Implementation summary
│   ├── LINKING_EXISTING_DATABASES.md # Linking existing databases
│   └── WORD_COUNTS_OPTIMIZATION.md # Word counts optimization docs
└── README.md
```

## How It Works

1. **Indexing**: The indexer walks through your document folder, extracts text from each file based on its type, and stores both metadata and content in SQLite3
2. **Database**: SQLite3 FTS5 (Full-Text Search 5) provides fast full-text search capabilities with ranking across file names, folder paths, and content
3. **Search**: The web interface sends queries to the Flask API, which uses FTS5 to find matching documents across all indexed fields
4. **Results**: Matching documents are displayed with snippets showing the search terms in context

## Supported File Types

| Format | Extension | Library Used |
|--------|-----------|--------------|
| Word | .docx | python-docx |
| PDF | .pdf | PyPDF2 |
| Excel | .xlsx | openpyxl |
| Excel (Legacy) | .xls | pandas + xlrd |
| CSV | .csv | pandas |
| Text | .txt | Built-in |
| PowerShell | .ps1 | Built-in |
| Images | .jpg, .png, .gif, .bmp, .tiff | Pillow + pytesseract |

## Troubleshooting

### Network path not accessible
- Ensure you have permissions to access the network share
- Try mapping the network drive first
- Check that the path in config.py is correct

### Tesseract not found
- Install Tesseract OCR from the link above
- Add Tesseract to your system PATH

### Database not found error
- Run `python indexer.py` first to create the database

### Cannot access from other computers
- Open **DocumentIndexer.exe**
- Enter your computer's network IP address in "Server IP Address"
- Click **"Save Server Config"**
- Restart DocumentSearch.exe or DocumentSearchGUI.exe

## Documentation

Detailed documentation is available in the [INFO/](INFO/) folder:

| Document | Description |
|----------|-------------|
| [QUICK_START.md](INFO/QUICK_START.md) | Detailed quick start guide with step-by-step instructions |
| [QUICKSTART.md](INFO/QUICKSTART.md) | Short quick start reference |
| [BUILD_INSTRUCTIONS.md](INFO/BUILD_INSTRUCTIONS.md) | How to build standalone executables |
| [DEPLOYMENT_GUIDE.md](INFO/DEPLOYMENT_GUIDE.md) | Deploying to end users without Python |
| [END_USER_README.md](INFO/END_USER_README.md) | User guide for non-technical users |
| [SETTINGS.md](INFO/SETTINGS.md) | Web-based settings configuration |
| [MULTI_DATABASE_ARCHITECTURE.md](INFO/MULTI_DATABASE_ARCHITECTURE.md) | Multi-folder database architecture |
| [PARALLEL_PROCESSING.md](INFO/PARALLEL_PROCESSING.md) | Parallel processing for faster indexing |
| [PARALLEL_FOLDER_INDEXING.md](INFO/PARALLEL_FOLDER_INDEXING.md) | Parallel folder indexing with dynamic reallocation |
| [IMPLEMENTATION_SUMMARY.md](INFO/IMPLEMENTATION_SUMMARY.md) | Implementation summary of multi-db + parallel features |
| [LINKING_EXISTING_DATABASES.md](INFO/LINKING_EXISTING_DATABASES.md) | Linking to pre-indexed databases |
| [WORD_COUNTS_OPTIMIZATION.md](INFO/WORD_COUNTS_OPTIMIZATION.md) | Word counts performance optimization |
| [PRESENT.md](INFO/PRESENT.md) | Technical presentation notes and development history |

## Future Enhancements

Potential improvements:
- Advanced search syntax (AND, OR, NOT operators)
- Export search results to CSV/Excel
- Document preview in browser
- Multi-language support
- Scheduled automatic indexing
- Tag and categorize documents
- Search history and saved searches
- Duplicate file detection

## License

See [LICENSE](LICENSE) file for details.
