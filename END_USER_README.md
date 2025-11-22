# SuperSearch Local Docs - User Guide

Welcome to SuperSearch Local Docs! This guide will help you get started searching your document collection.

## What's Included

You have two applications:

### 📁 DocumentIndexer.exe
**Use this to:**
- Configure where your documents are located
- Index your documents (first-time setup)
- Re-index when you add new documents
- View statistics about your indexed documents

### 🔍 DocumentSearch.exe
**Use this to:**
- Search through your indexed documents
- Browse search results
- Find documents quickly across your entire collection

## First-Time Setup

### Step 1: Index Your Documents

1. **Double-click DocumentIndexer.exe**

2. Click the **"Browse..."** button next to "Document Folder to Index"

3. Select the folder containing your documents (can be local or network path)
   - Example: `C:\Users\YourName\Documents`
   - Example: `\\Server\Shared\Documents`

4. (Optional) Click "Browse..." next to "Database File Path" to change where the database is saved
   - Default location is fine for most users

5. Click **"💾 Save Configuration"**

6. Click **"▶ Start Indexing"**

7. Wait while your documents are indexed
   - You'll see progress messages
   - This may take a few minutes depending on how many documents you have

8. When complete, **close the indexer**

### Step 2: Search Your Documents

1. **Double-click DocumentSearch.exe**

2. A black console window will appear showing:
   ```
   Starting server on all network interfaces at port 9000
   Access locally at: http://127.0.0.1:9000
   ```
   **Keep this window open!** (minimize it if you like)

3. **Open your web browser** and go to: **http://localhost:9000**

4. You'll see the search interface!

## Using the Search Interface

### Basic Search

1. Type your search term in the search box
   - Example: "invoice"
   - Example: "project report"
   - Example: "meeting notes"

2. Press **Enter** or click the **Search** button

3. Browse your results:
   - Each result shows the file name, location, and a preview
   - Click any result to **copy the file path** to your clipboard
   - Paste in Windows Explorer (Ctrl+V) to open the document

### Advanced Features

#### Filters & Options

Click **"Filters & Options"** to access:

**Search Scope:**
- **All** - Search everywhere (filenames, folders, content)
- **Filenames Only** - Search only file names
- **Folder Names Only** - Search only folder paths
- **File Content Only** - Search only inside documents

**File Types:**
- Filter by Word, PDF, Excel, CSV, or Images
- Check/uncheck types you want to include

**Sort By:**
- Relevance (best matches first)
- Date Modified (newest first)
- File Name (A-Z)
- File Size (largest first)

**Date Range:**
- Filter by when files were last modified

**File Size:**
- Filter by minimum or maximum file size

#### Popular Words Sidebar 🔥

The left sidebar shows the 10 most common words in your documents:

- **Click any word** to add it to your search
- Already-searched words appear greyed out
- Great for discovering common terms in your collection

## Daily Use

### Searching Documents

1. Make sure **DocumentSearch.exe is running** (check for the black console window)
2. Open your browser to **http://localhost:9000**
3. Search away!

### Adding New Documents

When you add new files to your document folder:

1. **Run DocumentIndexer.exe**
2. Click **"▶ Start Indexing"**
3. New documents will be added automatically
4. Modified documents will be updated

**How often to re-index:** Weekly, or whenever you add important documents

## Stopping the Search Server

To stop the search server:

1. Find the black console window (where you ran DocumentSearch.exe)
2. Click on it
3. Press **Ctrl+C**
4. Or simply close the window

You can restart it anytime by running DocumentSearch.exe again.

## Tips & Tricks

### Create Desktop Shortcuts

For quick access:

1. Right-click **DocumentIndexer.exe**
2. Select **"Send to" → "Desktop (create shortcut)"**
3. Repeat for **DocumentSearch.exe**
4. Rename shortcuts to "Index Documents" and "Search Documents"

### Start with Windows (Optional)

To have DocumentSearch.exe start automatically:

1. Press **Win+R**
2. Type: `shell:startup`
3. Press Enter
4. Copy a shortcut to DocumentSearch.exe into this folder

Now the search server starts when you log in!

### Bookmark the Search Page

In your web browser:

1. Go to http://localhost:9000
2. Press **Ctrl+D** to bookmark
3. Name it "Document Search"

Now you can access search from your bookmarks!

## Network Access

### Accessing from Other Computers

If you want to search from other computers on your network:

1. Find your computer's IP address:
   - Open Command Prompt
   - Type: `ipconfig`
   - Note your "IPv4 Address" (e.g., 192.168.1.100)

2. On another computer, open browser to:
   ```
   http://YOUR-IP:9000
   ```
   Example: http://192.168.1.100:9000

3. You can now search from any computer on your network!

**Note:** Make sure DocumentSearch.exe is running on the main computer.

## Multi-User Setup (Shared Database)

To share one database across multiple computers:

### On the Main Computer (Administrator)

1. **Create a network share** for the database:
   - Example: `\\MainPC\Shared\Databases`

2. **Run DocumentIndexer.exe**:
   - Document Folder: `\\MainPC\Shared\Documents`
   - Database Path: `\\MainPC\Shared\Databases\documents.sqlite3`
   - Save Configuration
   - Start Indexing

3. **Run DocumentSearch.exe**:
   - Open browser to http://localhost:9000
   - Click ⚙️ **Settings** button
   - Set Database Path: `\\MainPC\Shared\Databases\documents.sqlite3`
   - Click "Save Changes"

### On Other Computers

1. Copy the **DocumentSearch** folder to each computer

2. **Run DocumentSearch.exe**

3. **Open browser** to http://localhost:9000

4. Click ⚙️ **Settings**:
   - Set Database Path: `\\MainPC\Shared\Databases\documents.sqlite3`
   - Click "Save Changes"
   - Refresh page

Now everyone searches the same database!

**Only the main computer needs to run the indexer.**

## Troubleshooting

### "Database not found" error

**Fix:**
- Run DocumentIndexer.exe first to create the database
- Make sure you ran "Start Indexing"
- Check Settings (⚙️) to ensure database path is correct

### Can't access DocumentSearch in browser

**Fix:**
- Make sure DocumentSearch.exe is running (check for console window)
- Use http://localhost:9000 (not https)
- Try http://127.0.0.1:9000 instead
- Check if another program is using port 9000

### No search results

**Fix:**
- Verify indexing completed successfully
- Click "📊 Show Statistics" in DocumentIndexer to see if documents were indexed
- Try a simple search like "the" to verify database has content
- Check "Filters & Options" - make sure file types are selected

### Network path not accessible

**Fix:**
- Ensure you have permission to access the network share
- Try opening the path in Windows Explorer first
- Use the full UNC path (e.g., `\\Server\Share\Folder`)
- Don't use mapped drives (like Z:\), use UNC paths instead

### Indexer runs but finds no documents

**Fix:**
- Verify the document path is correct
- Check that the folder contains supported file types:
  - Word (.docx)
  - PDF (.pdf)
  - Excel (.xlsx)
  - CSV (.csv)
  - Images (.jpg, .png, etc.)

### Slow indexing

**Normal behavior:**
- Large collections take time
- Images require OCR processing (slower)
- Network paths are slower than local paths

**You can:**
- Index smaller folders
- Leave it running and come back
- Close other programs while indexing

## What File Types Are Supported?

The indexer can extract text from:

- **Word Documents:** .docx
- **PDFs:** .pdf
- **Excel Spreadsheets:** .xlsx
- **CSV Files:** .csv
- **Images:** .jpg, .jpeg, .png, .gif, .bmp, .tiff (with OCR)

Other file types are skipped during indexing.

## Privacy & Security

### Your Data

- All your document data stays on your computer
- Nothing is sent to the internet
- The search runs entirely locally

### Network Sharing

If you enable network access:
- Anyone on your network can search your documents
- Make sure you trust your network
- Use appropriate folder permissions
- Consider firewall rules if needed

## Getting Help

If you continue to have issues:

1. Check the console window for error messages
2. Try with a small test folder first
3. Ensure your documents aren't password-protected or corrupted
4. Verify you have sufficient disk space
5. Contact your system administrator if using network shares

## System Requirements

- Windows 7 or later (64-bit)
- 2 GB RAM minimum (4 GB recommended)
- Modern web browser (Chrome, Firefox, Edge)
- Sufficient disk space for the database
- Network access (for multi-user setups)

## About This Software

SuperSearch Local Docs provides fast full-text search across your document collection using SQLite FTS5 technology. The web interface makes it easy to find documents by name, location, or content.

**Version:** 1.0
**License:** See LICENSE file

---

**Need more help?** Contact your system administrator or refer to the technical documentation.

**Happy Searching! 🔍**
