# Quick Start Guide

Get started with Document Search in 5 minutes!

## Prerequisites

- Python 3.7 or higher installed
- Access to documents you want to search

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Optional (for image OCR):
- Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Configure and Index Documents

#### Easy Way - Use the GUI (Recommended)

```bash
# Windows
start_indexer_gui.bat

# Or directly
python indexer_gui.py
```

In the GUI:
1. Click "Browse..." next to "Document Folder to Index"
2. Select the folder containing your documents
3. Optionally change the database path (default is fine)
4. Click "💾 Save Configuration"
5. Click "▶ Start Indexing"
6. Wait for indexing to complete

#### Command Line Way

Edit `config.py` and set your document path:

```python
DOCUMENT_PATH = r"C:\Users\YourName\Documents"
```

Then run:

```bash
python indexer.py
```

### 3. Start the Search Server

```bash
# Windows
start_server.bat

# Or directly
python server.py
```

The server will display:
```
Starting server on all network interfaces at port 9000
Access locally at: http://127.0.0.1:9000
Access from network at: http://YOUR-IP:9000
```

### 4. Search Your Documents

1. Open your browser to: http://localhost:9000
2. Enter a search term (e.g., "invoice", "contract", "report")
3. Browse results
4. Click any result to copy its file path
5. Paste in Windows Explorer to open the document

## Advanced Features

### Popular Words Sidebar

The left sidebar shows the 10 most common words in your documents:
- Click any word to add it to your search
- Already-searched words appear greyed out

### Abbreviation Expansion

Create `alternate_names.csv` in your document folder:

```csv
abbreviation,keyword1,keyword2,keyword3,keyword4,keyword5,keyword6,keyword7,keyword8,keyword9,keyword10
API,interface,endpoint,service,rest,web
DB,database,sql,storage,query
UI,interface,frontend,display,screen
```

Now searching for "API" will also search for "interface", "endpoint", etc.

### Web-Based Settings

Click the **⚙️ Settings** button to:
- Change database path (for multi-user setups)
- Configure document path
- Point to network shares

Example network setup:
```
Database Path: \\192.168.1.100\Shared\databases\documents.sqlite3
Document Path: \\192.168.1.100\Shared\Documents
```

### Advanced Filters

Click **"Filters & Options"** to access:
- **Search Scope**: All, filenames only, folders only, content only
- **File Types**: Filter by Word, PDF, Excel, CSV, Images
- **Sort By**: Relevance, date, name, size
- **Date Range**: Filter by modification date
- **File Size**: Filter by min/max size

## Multi-User Setup

To share one database across multiple computers:

**On Computer 1:**
1. Create network share: `\\SERVER\Shared\Databases`
2. Run indexer GUI and save database to: `\\SERVER\Shared\Databases\documents.sqlite3`
3. Index your documents
4. In web interface, click ⚙️ Settings
5. Set database path to network location
6. Save changes

**On Other Computers:**
1. Start the search server
2. Click ⚙️ Settings
3. Set database path to: `\\SERVER\Shared\Databases\documents.sqlite3`
4. Save changes
5. Refresh page

Now all computers search the same database!

## Creating Standalone Executables

No Python installation needed on deployment computers:

### Build Search Server

```bash
python build_exe.py
```

Creates: `dist\DocumentSearch\DocumentSearch.exe`

### Build GUI Indexer

```bash
python build_indexer_exe.py
```

Creates: `dist\DocumentIndexer\DocumentIndexer.exe`

Copy entire folder to any Windows PC and run!

## Common Tasks

### Update Index with New Documents

Just re-run the indexer:
```bash
python indexer.py
# or
start_indexer_gui.bat
```

Existing documents are updated; new documents are added.

### View Database Statistics

**GUI Method:**
1. Run `start_indexer_gui.bat`
2. Click "📊 Show Statistics"

**Command Line:**
```bash
python indexer.py
# Statistics shown at end
```

### Reset Configuration

Delete `user_config.json` or click "Reset to Defaults" in Settings.

## Troubleshooting

### "Database not found"
- Run the indexer first to create the database
- Check database path in Settings

### "Path not accessible"
- Verify network share permissions
- Try accessing path in Windows Explorer first
- Use UNC paths (`\\server\share`) not mapped drives

### No search results
- Ensure indexer completed successfully
- Check search scope (try "All" instead of specific scopes)
- Verify documents were actually indexed (check statistics)

### Server won't start
- Check if port 9000 is already in use
- Try changing `SERVER_PORT` in config.py

## Next Steps

- Read [SETTINGS.md](SETTINGS.md) for detailed configuration options
- See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for deployment info
- Check [README.md](README.md) for complete feature documentation

## Support

For issues or questions:
- Check the documentation files in this repository
- Review error messages in the console output
- Ensure all dependencies are installed correctly
