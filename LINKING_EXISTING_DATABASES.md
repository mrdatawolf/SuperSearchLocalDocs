# Linking Existing Databases

## Overview

The "Link Existing Database" feature allows you to connect a folder to a pre-indexed database **without re-indexing**. This is useful for:

- 🌐 **Sharing databases** - Use a database indexed on another computer
- 👥 **Multi-user scenarios** - Everyone uses the same pre-indexed database
- 💾 **Backup/restore** - Link to a database backup without re-indexing
- 📁 **Moved folders** - Folder path changed but database is still valid
- ⚡ **Save time** - Skip re-indexing large document collections

## How It Works

When you link a folder to an existing database:

1. The folder path is added to the system
2. It's associated with the existing database file
3. The database immediately becomes searchable
4. **No indexing is performed**

The system simply creates a mapping in `databases/index.json`:

```json
{
  "C:\\Users\\John\\Documents": {
    "db_path": "\\\\server\\shared\\databases\\documents.sqlite3",
    "db_filename": "documents.sqlite3"
  }
}
```

## Usage Guide

### In DocumentIndexer GUI

1. **Click "🔗 Link Existing DB" button**

2. **Select the folder** containing documents:
   - This is where the documents are (or will be) located
   - Example: `C:\My Documents`

3. **Select the existing database file**:
   - Browse to the pre-indexed `.sqlite3` file
   - Can be on network share, external drive, etc.
   - Example: `\\server\shared\databases\documents.sqlite3`

4. **Confirm the link**:
   - Review folder and database paths
   - Click "Yes" to create the link

5. **Done!**:
   - Folder appears in the list
   - Database is immediately searchable
   - No indexing needed

### Visual Workflow

```
┌─────────────────────────┐
│  DocumentIndexer.exe    │
└─────────────────────────┘
           │
           ▼
    Click "Link Existing DB"
           │
           ▼
┌───────────────────────────────┐
│ Select folder:                │
│ C:\My Documents               │
└───────────────────────────────┘
           │
           ▼
┌───────────────────────────────┐
│ Select database:              │
│ \\server\shared\my_docs.db    │
└───────────────────────────────┘
           │
           ▼
    Confirm link (Yes/No)
           │
           ▼
┌───────────────────────────────┐
│ ✓ Link created!               │
│ Ready to search               │
└───────────────────────────────┘
```

## Use Cases

### 1. Sharing a Database Between Computers

**Scenario:** You indexed documents on Computer A and want to search them from Computer B.

**Solution:**
1. Copy the database file to a shared location (network share or USB drive)
2. On Computer B, run DocumentIndexer.exe
3. Click "Link Existing DB"
4. Select the documents folder (can be same or different path)
5. Select the copied database file
6. Run DocumentSearch.exe - database is searchable!

**Example:**
```
Computer A:
- Folder: C:\Work\Documents
- Database: C:\SuperSearchDocs\databases\db_abc123.sqlite3
- Action: Copy database to \\server\shared\databases\

Computer B:
- Folder: C:\Work\Documents (same relative location)
- Action: Link to \\server\shared\databases\db_abc123.sqlite3
- Result: Searches work without re-indexing!
```

### 2. Multi-User Shared Database

**Scenario:** Team wants to share one indexed database for network documents.

**Solution:**
1. Admin indexes documents on main computer
2. Places database in shared network location
3. Each team member runs DocumentIndexer.exe
4. Links their local folder to the shared database
5. Everyone searches the same database

**Example:**
```
Admin Computer:
- Indexes: \\server\TeamDocuments
- Database: \\server\shared\databases\team_docs.sqlite3

User 1:
- Links: \\server\TeamDocuments → \\server\shared\databases\team_docs.sqlite3

User 2:
- Links: \\server\TeamDocuments → \\server\shared\databases\team_docs.sqlite3

Result: Everyone searches the same database, only indexed once!
```

### 3. Database Backup/Restore

**Scenario:** You have a database backup and don't want to re-index.

**Solution:**
1. Restore database file from backup
2. Run DocumentIndexer.exe
3. Link folder to restored database
4. Resume searching immediately

### 4. Moved or Renamed Folders

**Scenario:** Documents moved from `C:\OldPath` to `D:\NewPath` but database is still valid.

**Solution:**
1. Move documents to new location
2. Run DocumentIndexer.exe
3. Remove old folder from list
4. Link new folder to existing database
5. Searches still work with updated path

### 5. Network Path Changes

**Scenario:** Network share path changed from `\\oldserver\docs` to `\\newserver\docs`.

**Solution:**
1. Remove old path from indexer
2. Link new path to existing database
3. Continue searching without re-indexing

## Important Notes

### Database Validity

⚠️ **The database must match the folder contents!**

If you link a folder to a database that was indexed from **different** documents:
- Search results will be wrong
- File paths in database won't match actual files
- Clicking results won't open the correct files

**Example of WRONG usage:**
```
Database indexed from: C:\Project1\Reports
Linked to folder: C:\Project2\Reports  ← Different documents!
Result: Search finds wrong files
```

**Example of CORRECT usage:**
```
Database indexed from: \\server\TeamDocs
Linked to folder: \\server\TeamDocs  ← Same documents!
Result: Search works perfectly
```

### Database Location

The database file can be:
- ✅ On network share: `\\server\shared\databases\docs.sqlite3`
- ✅ On external drive: `E:\Backups\databases\docs.sqlite3`
- ✅ In databases folder: `C:\SuperSearchDocs\databases\docs.sqlite3`
- ✅ Any readable location

**Network considerations:**
- Network databases may be slower to search
- Ensure reliable network connection
- Consider copying to local drive for better performance

### Multiple Folders, Same Database

⚠️ **Don't link multiple different folders to the same database**

This will cause confusion:
```
❌ WRONG:
Folder 1: C:\Documents   → database.sqlite3
Folder 2: C:\Downloads   → database.sqlite3 (SAME database)
Result: Search results will be mixed and confusing
```

Each folder should have its own database:
```
✓ CORRECT:
Folder 1: C:\Documents  → db_docs.sqlite3
Folder 2: C:\Downloads  → db_downloads.sqlite3
```

**Exception:** It's OK if multiple users link to the **same shared database** for the **same folder**:
```
✓ OK:
User 1: \\server\TeamDocs → \\server\shared\team.sqlite3
User 2: \\server\TeamDocs → \\server\shared\team.sqlite3
Same folder, shared database - this works!
```

## Verification

After linking, verify the connection:

1. **Check the folder list** in DocumentIndexer:
   - Folder should appear
   - Should NOT show "[NOT INDEXED YET]"
   - This means database exists

2. **Run DocumentSearch.exe**:
   - Click "Show Statistics"
   - Should show document count
   - Try a search

3. **Test a search**:
   - Search for a word you know exists
   - Click a result
   - File path should copy correctly
   - File should exist at that path

## Troubleshooting

### "Database file not found"

**Problem:** The database file doesn't exist at the specified path.

**Solution:**
- Check the database file exists
- Verify path is correct
- Ensure you have read permissions
- For network paths, check network connection

### Search returns no results

**Problem:** Database is empty or doesn't match folder.

**Solution:**
- Check database was properly indexed
- Use "Show All Statistics" to see document count
- If count is 0, the database is empty - need to re-index
- If count > 0 but no results, folder might not match database

### File paths don't work

**Problem:** Search results show files that don't exist.

**Solution:**
- Database was indexed from different location
- Need to re-index or link to correct folder
- Check if documents were moved/deleted

### Can't access network database

**Problem:** Database is on network share but can't be accessed.

**Solution:**
- Check network connection
- Verify permissions to network share
- Try accessing the file in Windows Explorer first
- Consider copying database to local drive

## Advanced: Manual Linking

For advanced users, you can manually edit `databases/index.json`:

```json
{
  "C:\\Users\\John\\Documents": {
    "db_path": "\\\\server\\shared\\databases\\docs.sqlite3",
    "db_filename": "docs.sqlite3",
    "added_date": null
  }
}
```

After editing, click "🔄 Refresh List" in DocumentIndexer GUI.

## Benefits

Using "Link Existing DB" provides:

✅ **Instant access** - No re-indexing wait time
✅ **Resource savings** - No CPU/disk usage for indexing
✅ **Database sharing** - Multiple users can use one database
✅ **Flexibility** - Connect any folder to any database
✅ **Backup/restore** - Quick recovery from backups

Perfect for scenarios where re-indexing is:
- ❌ Too slow (large document collections)
- ❌ Wasteful (database already exists)
- ❌ Unnecessary (documents haven't changed)
- ❌ Not allowed (read-only permissions)

## Summary

The "Link Existing DB" feature makes it easy to:
1. Share databases between computers
2. Set up multi-user searching
3. Restore from backups
4. Handle moved folders
5. Save time on re-indexing

Just remember: **The folder and database must match** - the database should contain the same documents that are in the folder!
