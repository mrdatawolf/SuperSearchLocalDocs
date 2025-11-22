# Deployment Guide - Standalone Executables

This guide shows how to deploy SuperSearch Local Docs to computers **without Python installed**.

## Overview

SuperSearch Local Docs consists of two standalone Windows applications:

1. **DocumentIndexer.exe** - GUI application for setup and indexing
2. **DocumentSearch.exe** - Web server for searching documents

Both applications are completely self-contained and require **no Python installation** on the target computer.

## Building the Executables

### Prerequisites (Build Computer Only)

On the computer where you'll build the executables:

```bash
pip install pyinstaller
pip install -r requirements.txt
```

### Build Both Applications

```bash
python build_all.py
```

This creates:
- `dist\DocumentIndexer\` - GUI indexer application
- `dist\DocumentSearch\` - Search server application

### Build Individually (Optional)

If you prefer to build them separately:

```bash
# Build GUI indexer
python build_indexer_exe.py

# Build search server
python build_exe.py
```

## Deployment to End Users

### What to Distribute

Copy these two folders to the target computer:

```
📁 DocumentIndexer\
   ├── DocumentIndexer.exe
   └── [various DLL and dependency files]

📁 DocumentSearch\
   ├── DocumentSearch.exe
   ├── templates\
   └── [various DLL and dependency files]
```

You can distribute via:
- Network share
- USB drive
- Zip file download
- Installer package (optional)

### Installation Steps

1. **Copy folders** to the target computer (e.g., `C:\Program Files\SuperSearchDocs\`)

2. **Create desktop shortcuts** (optional but recommended):
   - Right-click `DocumentIndexer.exe` → Send to → Desktop (create shortcut)
   - Right-click `DocumentSearch.exe` → Send to → Desktop (create shortcut)
   - Rename shortcuts to "Document Indexer" and "Document Search"

## First-Time Setup (End User)

### Step 1: Index Your Documents

1. **Double-click** `DocumentIndexer.exe` (or the shortcut)

2. In the GUI:
   - Click **"Browse..."** next to "Document Folder to Index"
   - Select the folder containing your documents
   - Optionally change the database path (default is fine for single user)
   - Click **"💾 Save Configuration"**
   - Click **"▶ Start Indexing"**
   - Wait for indexing to complete

3. **Close** the indexer when done

### Step 2: Search Your Documents

1. **Double-click** `DocumentSearch.exe` (or the shortcut)

2. A console window will appear showing:
   ```
   Starting server on all network interfaces at port 9000
   Access locally at: http://127.0.0.1:9000
   ```

3. **Open your web browser** to: http://localhost:9000

4. **Start searching!**
   - Type search terms
   - Click results to copy file paths
   - Use filters for advanced searches

5. **Keep the console window open** while searching
   - Minimize it if needed
   - Close it to stop the server

## Multi-User Setup (Shared Database)

For teams sharing the same document database across multiple computers:

### Setup on First Computer

1. **Create network share** for the database:
   - Example: `\\SERVER\Shared\Databases\`

2. **Run DocumentIndexer.exe**:
   - Document Folder: `\\SERVER\Shared\Documents`
   - Database Path: `\\SERVER\Shared\Databases\documents.sqlite3`
   - Click "Save Configuration"
   - Click "Start Indexing"

3. **Run DocumentSearch.exe**:
   - Open browser to http://localhost:9000
   - Click ⚙️ Settings button
   - Set Database Path: `\\SERVER\Shared\Databases\documents.sqlite3`
   - Click "Save Changes"
   - Refresh page

### Setup on Other Computers

1. **Deploy** the DocumentSearch folder to each computer

2. **Run DocumentSearch.exe**

3. **Configure settings**:
   - Open browser to http://localhost:9000
   - Click ⚙️ Settings
   - Set Database Path: `\\SERVER\Shared\Databases\documents.sqlite3`
   - Click "Save Changes"
   - Refresh page

4. All computers now search the same database!

**Note:** Only one computer needs DocumentIndexer.exe for maintaining the shared database.

## Regular Maintenance

### Adding New Documents

To update the index after adding new documents:

1. **Run DocumentIndexer.exe**
2. Click **"▶ Start Indexing"**
3. The indexer will:
   - Add new documents
   - Update modified documents
   - Keep existing documents

### Viewing Statistics

1. **Run DocumentIndexer.exe**
2. Click **"📊 Show Statistics"**
3. See total documents and breakdown by file type

## Network Access

### Access from Other Computers on Same Network

The search server is accessible from other computers on your network:

1. **Find your computer's IP address**:
   - Open Command Prompt
   - Type: `ipconfig`
   - Look for "IPv4 Address" (e.g., 192.168.1.100)

2. **On another computer**, open browser to:
   ```
   http://YOUR-IP-ADDRESS:9000
   ```
   Example: http://192.168.1.100:9000

3. **Configure firewall** (if needed):
   - Allow inbound connections on port 9000
   - Windows Defender Firewall → Allow an app

## Abbreviation Expansion (Optional)

To enable abbreviation expansion:

1. **Create** `alternate_names.csv` in your document folder

2. **Format** (see example below):
   ```csv
   abbreviation,keyword1,keyword2,keyword3,keyword4,keyword5,keyword6,keyword7,keyword8,keyword9,keyword10
   API,interface,endpoint,service,rest,web,request
   DB,database,sql,storage,query
   UI,interface,frontend,display,screen,view
   ```

3. **Re-run indexer** for changes to take effect

4. Now searching "API" also searches for "interface", "endpoint", etc.

## Troubleshooting

### "Database file not found"

**Problem:** Search server can't find the database

**Solution:**
1. Ensure you've run the indexer first
2. Check database path in ⚙️ Settings matches indexer configuration
3. For network paths, ensure you have access permissions

### Indexer says "Path not accessible"

**Problem:** Can't access document folder or database location

**Solution:**
1. Verify the path exists
2. Check you have read/write permissions
3. For network paths, try opening in Windows Explorer first
4. Use UNC paths (`\\server\share`) not mapped drives (Z:\)

### Port 9000 already in use

**Problem:** Another application is using port 9000

**Solution:**
1. Close other applications using that port
2. Or change the port (requires editing config inside executable - contact support)

### No search results

**Problem:** Search returns no results

**Solution:**
1. Verify indexing completed successfully (check statistics)
2. Try simpler search terms
3. Change search scope to "All" in Filters & Options
4. Ensure database path in Settings is correct

### Indexer crashes or freezes

**Problem:** Indexer stops responding

**Solution:**
1. Close and restart the indexer
2. Try indexing a smaller folder first to test
3. Check if any documents are corrupted
4. Ensure enough disk space for the database

## System Requirements

### Minimum Requirements
- Windows 7 or later (64-bit)
- 2 GB RAM
- 100 MB disk space (plus space for database)
- Modern web browser (Chrome, Firefox, Edge)

### Recommended Requirements
- Windows 10/11 (64-bit)
- 4 GB RAM
- SSD with sufficient space
- Chrome or Edge browser

### Network Requirements (for multi-user)
- Network share access
- SMB/CIFS file sharing enabled
- Appropriate permissions on shared folders

## File Locations

### Single-User Setup

Default locations when using defaults:

```
C:\Program Files\SuperSearchDocs\
├── DocumentIndexer\
│   └── DocumentIndexer.exe
├── DocumentSearch\
│   └── DocumentSearch.exe
└── Data\
    ├── documents.sqlite3          (created by indexer)
    └── user_config.json           (created after first config)
```

### Multi-User Setup

Recommended locations:

```
Server:
\\SERVER\Shared\
├── Documents\                     (your document collection)
│   └── alternate_names.csv        (optional)
└── Databases\
    └── documents.sqlite3          (shared database)

Each Computer:
C:\Program Files\SuperSearchDocs\
└── DocumentSearch\
    ├── DocumentSearch.exe
    └── user_config.json           (points to network database)
```

## Advanced Configuration

### Changing Default Settings

Each application stores settings in `user_config.json` in its own folder:

- **DocumentIndexer**: Stores document path and database path
- **DocumentSearch**: Stores database path and server settings

To reset to defaults, delete `user_config.json` and restart the application.

### Automating Indexing

To schedule automatic re-indexing:

1. Create a batch file `run_indexer.bat`:
   ```batch
   @echo off
   cd /d "C:\Program Files\SuperSearchDocs\DocumentIndexer"
   DocumentIndexer.exe
   ```

2. Use Windows Task Scheduler to run it periodically

**Note:** GUI requires manual interaction. For fully automated indexing, contact support for command-line version.

## Support

For issues not covered in this guide:

1. Check the console output for error messages
2. Ensure all file permissions are correct
3. Verify network paths are accessible
4. Try with a small test folder first
5. Review the application logs (if available)

## Security Considerations

### Network Security

- The search server binds to all network interfaces (0.0.0.0)
- Anyone on your network can access the search interface
- For sensitive documents, consider:
  - Running on localhost only (requires code modification)
  - Using firewall rules to restrict access
  - Placing behind a VPN

### File Permissions

- The indexer needs read access to all documents
- The database file needs read/write permissions
- For network shares, ensure appropriate permissions are set
- Never grant excessive permissions for convenience

### Data Privacy

- Document content is stored in the SQLite database
- The database contains full text of all indexed documents
- Protect the database file appropriately
- Consider encryption for sensitive data

## Best Practices

1. **Regular Re-indexing**: Run indexer weekly or after major document changes
2. **Backup Database**: Periodically backup the .sqlite3 file
3. **Network Performance**: For large databases, use local database with network documents
4. **Disk Space**: Monitor database size (typically 10-30% of document size)
5. **Test First**: Try on a small folder before indexing large collections

## Licensing and Distribution

When distributing to end users:

- Include appropriate license information
- Document any third-party components
- Provide contact information for support
- Consider version numbering for updates

## Updates

To update to a newer version:

1. **Build** new executables from updated source
2. **Backup** existing database and config files
3. **Replace** executable folders with new versions
4. **Test** with existing database
5. **Re-index** if needed (check release notes)

Settings and database are preserved between updates.
