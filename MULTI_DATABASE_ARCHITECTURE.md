# Multi-Database Architecture

## Overview

SuperSearch Local Docs now supports indexing multiple folders, with each folder getting its own dedicated database. This allows you to:

- Index documents from different locations (e.g., "My Documents" + network share)
- Keep separate databases for different document collections
- Search across all indexed folders simultaneously
- Manage indexed folders independently

## Architecture

### Folder Structure

```
SuperSearchDocs/ (root folder)
├── databases/
│   ├── db_a1b2c3d4e5f6.sqlite3  (database for first folder)
│   ├── db_f6e5d4c3b2a1.sqlite3  (database for second folder)
│   └── index.json                (mapping of folders to databases)
├── DocumentIndexer/
│   └── DocumentIndexer.exe
└── DocumentSearch/
    └── DocumentSearch.exe
```

### Database Naming

- Each indexed folder gets a unique database file in the `databases/` subfolder
- Database filenames are generated using MD5 hash of the folder path
- Format: `db_<12-char-hash>.sqlite3`
- Example: `db_a1b2c3d4e5f6.sqlite3`

### Index Mapping (`index.json`)

The `index.json` file maps each indexed folder to its database:

```json
{
  "C:\\Users\\YourName\\Documents": {
    "db_path": "C:\\SuperSearchDocs\\databases\\db_a1b2c3d4e5f6.sqlite3",
    "db_filename": "db_a1b2c3d4e5f6.sqlite3",
    "added_date": "2024-01-15 10:30:00"
  },
  "\\\\server\\share\\Documents": {
    "db_path": "C:\\SuperSearchDocs\\databases\\db_f6e5d4c3b2a1.sqlite3",
    "db_filename": "db_f6e5d4c3b2a1.sqlite3",
    "added_date": "2024-01-15 10:35:00"
  }
}
```

## Components

### 1. Database Manager (`database_manager.py`)

Central module that handles all database-related operations:

**Key Functions:**
- `get_databases_folder()` - Returns path to databases folder
- `add_indexed_folder(folder_path)` - Adds folder to index, returns database path
- `remove_indexed_folder(folder_path)` - Removes folder from index
- `get_all_indexed_folders()` - Returns list of all indexed folders with metadata
- `get_all_database_paths()` - Returns list of all database file paths
- `get_database_path(folder_path)` - Gets database path for specific folder

**Usage Example:**
```python
from database_manager import add_indexed_folder, get_all_database_paths

# Add a folder to index
db_path = add_indexed_folder("C:\\My Documents")
print(f"Database created at: {db_path}")

# Get all database paths for searching
db_paths = get_all_database_paths()
for path in db_paths:
    print(f"Database: {path}")
```

### 2. Document Indexer (`indexer.py`)

Updated to accept specific document_path and db_path:

```python
from indexer import DocumentIndexer

# Create indexer for specific folder and database
indexer = DocumentIndexer(
    document_path="C:\\My Documents",
    db_path="C:\\SuperSearchDocs\\databases\\db_a1b2c3d4e5f6.sqlite3"
)

# Index the documents
indexed_count, error_count = indexer.scan_and_index(use_parallel=True)
```

### 3. Indexer GUI (`indexer_gui.py`)

New multi-folder interface:

**Features:**
- Listbox showing all indexed folders
- "Add Folder" button to add new folders
- "Remove Selected" button to remove folders
- "Index All Folders" button to index all added folders
- Shows database status for each folder (indexed or not)
- Statistics across all databases

**Workflow:**
1. Click "Add Folder" to browse and select a folder
2. Repeat to add multiple folders
3. Click "Index All Folders" to index all added folders sequentially
4. Each folder is indexed into its own database

### 4. Search Server (`server.py`)

Updated to query all databases and merge results:

**How It Works:**

1. **Get All Databases:**
   ```python
   db_connections = get_all_db_connections()
   # Returns list of (db_path, connection) tuples
   ```

2. **Query Each Database:**
   ```python
   all_results = []
   for db_path, conn in db_connections:
       cursor = conn.cursor()
       cursor.execute(search_sql, params)
       # Collect results from this database
       all_results.extend(results)
   ```

3. **Merge and Sort:**
   ```python
   # Sort all results together
   if sort_by == 'date':
       all_results.sort(key=lambda x: x['modified_date'], reverse=True)
   elif sort_by == 'name':
       all_results.sort(key=lambda x: x['file_name'].lower())
   # ... etc
   ```

4. **Apply Pagination:**
   ```python
   # Paginate merged results
   total_count = len(all_results)
   start_idx = (page - 1) * per_page
   end_idx = start_idx + per_page
   paginated_results = all_results[start_idx:end_idx]
   ```

**Updated Endpoints:**

- `/api/search` - Queries all databases, merges and sorts results
- `/api/stats` - Aggregates statistics across all databases
- `/api/top-words` - Samples from all databases to find top words

## User Workflow

### Initial Setup

1. **Run DocumentIndexer.exe**
2. **Add Folders:**
   - Click "Add Folder"
   - Select first folder (e.g., `C:\My Documents`)
   - Click "Add Folder" again
   - Select second folder (e.g., `\\server\share\Documents`)
   - Repeat for all folders you want to index

3. **Index Documents:**
   - Click "Index All Folders"
   - Wait for indexing to complete
   - Each folder is indexed into its own database

### Searching

1. **Run DocumentSearch.exe**
2. **Search Interface:**
   - Automatically searches across all databases
   - Results from all folders are merged and sorted
   - Status bar shows how many databases were queried

### Maintenance

**Adding New Folders:**
1. Run DocumentIndexer.exe
2. Click "Add Folder" and select new folder
3. Click "Index All Folders" (will re-index existing folders too)

**Re-indexing:**
1. Run DocumentIndexer.exe
2. Click "Index All Folders"
3. Existing documents are updated, new documents are added

**Removing Folders:**
1. Run DocumentIndexer.exe
2. Select folder in list
3. Click "Remove Selected"
4. Database file remains but won't be used for searches

## Benefits

### 1. Separation of Concerns
- Each document collection has its own database
- No path conflicts between different folders
- Easy to manage individual collections

### 2. Performance
- Smaller databases per collection (faster queries)
- Parallel indexing still works for each folder
- Cached connections for repeated searches

### 3. Flexibility
- Add/remove folders without affecting others
- Different update schedules for different folders
- Easy to share specific databases

### 4. Scalability
- Add as many folders as needed
- Each database remains manageable size
- Search performance scales well

## Migration from Single Database

If you have an existing `documents.sqlite3` file:

1. **Option A: Start Fresh**
   - Delete old `documents.sqlite3`
   - Add folders and re-index

2. **Option B: Keep Old Database**
   - Old database will be ignored by new system
   - Add folders and index with new system
   - Both can coexist

The new system automatically creates the `databases/` folder and `index.json` when you add your first folder.

## Technical Details

### Database Schema
Each database has identical schema:
- `documents` table with FTS5 virtual table
- Same structure as single-database version
- No cross-database references

### Search Algorithm
1. Build FTS5 query from user input
2. Execute query on ALL databases in parallel
3. Collect all results in memory
4. Sort by relevance/date/name/size across all results
5. Apply pagination to merged results
6. Return paginated subset

### Error Handling
- If one database fails, others continue
- Search works even if some databases are corrupted
- Clear error messages for troubleshooting

## Configuration

### Default Paths

**When running as .exe:**
```
C:\SuperSearchDocs\
├── databases\
├── DocumentIndexer\
└── DocumentSearch\
```

**When running from source:**
```
<project_root>\
└── databases\
```

### Customization

All database management is handled automatically. No manual configuration needed for database paths.

## Troubleshooting

### Problem: "No databases found" error

**Solution:**
1. Run DocumentIndexer.exe
2. Add at least one folder
3. Click "Index All Folders"
4. Run DocumentSearch.exe again

### Problem: Search returns no results

**Check:**
1. Run DocumentIndexer.exe
2. Click "Show All Statistics"
3. Verify databases have documents
4. Verify file types are indexed

### Problem: Database file location

**Location:**
- Databases are ALWAYS in `databases/` subfolder
- Never in the same folder as the .exe
- Check `databases/index.json` for mapping

### Problem: Orphaned databases

**Cleanup:**
```python
from database_manager import cleanup_orphaned_databases
removed = cleanup_orphaned_databases()
print(f"Removed {len(removed)} orphaned databases")
```

## API Changes

### Old Code (Single Database)
```python
from indexer import DocumentIndexer

# Relied on global DATABASE_PATH
indexer = DocumentIndexer()
indexer.scan_and_index()
```

### New Code (Multi-Database)
```python
from indexer import DocumentIndexer
from database_manager import get_database_path

# Specify paths explicitly
db_path = get_database_path("C:\\My Documents")
indexer = DocumentIndexer(
    document_path="C:\\My Documents",
    db_path=db_path
)
indexer.scan_and_index()
```

## Future Enhancements

Possible improvements:
1. Database compression/archival
2. Incremental indexing (only changed files)
3. Database synchronization across computers
4. Export/import database functionality
5. Database merging tools
6. Per-database search filters

## Summary

The multi-database architecture provides:
- ✅ Multiple folder support
- ✅ Automatic database management
- ✅ Unified search across all folders
- ✅ Easy folder management (add/remove)
- ✅ Better organization and scalability
- ✅ Backward compatible code structure
- ✅ No manual database path configuration needed

All databases are automatically discovered and queried when searching, making it completely transparent to the end user!
