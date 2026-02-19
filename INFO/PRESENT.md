# SuperSearchLocalDocs - Technical Presentation

## Elevator Pitch

SuperSearchLocalDocs is a full-text search engine for local and network document collections. It indexes Word, PDF, Excel, CSV, text, and image files into SQLite FTS5 databases and serves results through a Flask web interface. It ships as standalone Windows executables — no Python required on end-user machines.

---

## Key Features at a Glance

- **Full-text search** across file names, folder paths, and document content
- **Multi-format support**: DOCX, PDF, XLSX/XLS, CSV, TXT, PS1, and images (via OCR)
- **Web UI** with filters (scope, file type, date range, size), sorting, and pagination
- **Standalone executables** built with PyInstaller — zero-dependency deployment
- **Three apps**: DocumentIndexer (GUI setup/indexing), DocumentSearchGUI (desktop search), DocumentSearch (web server)
- **Multi-database architecture** — each indexed folder gets its own SQLite database, all searched simultaneously
- **Parallel processing** — multiprocessing-based indexing using 75% of CPU cores
- **Parallel folder indexing** — index multiple folders simultaneously with dynamic worker reallocation
- **Abbreviation expansion** — CSV-driven synonym/keyword expansion
- **Pre-calculated word counts** — popular words sidebar loads in <100ms
- **Network-ready** — server binds to 0.0.0.0, supports UNC paths and shared databases
- **REST API** — full programmatic access for integration

---

## Development Timeline (from the commits)

### Phase 1: Foundation (Nov 20, 2025)

**Commit:** `Initial commit` → `adding the sections we need` (PR #1)

Started from scratch and built the core in a single push:
- SQLite FTS5 indexer (`indexer.py`) with text extraction for DOCX, PDF, CSV, TXT
- Flask web server (`server.py`) with search API
- Full web interface (`templates/index.html`) — ~1000 lines of HTML/CSS/JS
- Abbreviation expansion system (`company_abbreviations.py`)
- Configuration management (`config.py`)

**Issue encountered:** `.xlsx` files weren't being found during indexing. Fixed the file type detection so Excel spreadsheets were properly picked up.

**QOL improvement:** Added handling for larger data sets — the initial indexer needed work to handle real-world document collections without choking.

### Phase 2: Deployment-Ready (Nov 21, 2025)

**Commit:** `initial deployment`

Made it distributable to non-technical users:
- PyInstaller build scripts (`build_exe.py`, `build_indexer_exe.py`, `build_all.py`)
- GUI indexer (`indexer_gui.py`) — full Tkinter application for point-and-click setup
- Web-based settings UI (`config_manager.py`, `SETTINGS.md`)
- **Parallel processing** added to the indexer using Python's `multiprocessing` module
- Wrote extensive documentation: BUILD_INSTRUCTIONS, DEPLOYMENT_GUIDE, QUICK_START, END_USER_README

**Key design decision:** Used `multiprocessing` instead of `threading` because text extraction is CPU-bound. Python's GIL makes threading useless for CPU-bound parallelism. Result: 10-20x speedup on multi-core machines.

**Key design decision:** Workers only do text extraction — all database writes happen in the main process. This avoids SQLite's concurrent write limitations entirely.

### Phase 3: Multi-Folder Support (Nov 24, 2025)

**Commit:** `adds multi-folder databases` (PR #2)

Major architecture change — moved from a single database to one-database-per-folder:
- New `database_manager.py` module handling folder-to-database mapping via `index.json`
- Database filenames generated from MD5 hash of folder path
- Search server queries all databases and merges/sorts/paginates results in memory
- GUI rewritten to support add/remove folders
- **Parallel folder indexing** with `ProcessPoolExecutor` and `as_completed()` for dynamic work-stealing
- Added "Link Existing DB" feature — connect to a pre-indexed database without re-indexing

**Why one-db-per-folder?** A single database had path conflicts when indexing multiple locations and made management harder. Separate databases keep collections isolated, are individually manageable, and remain smaller (faster queries).

**Also added:** File action buttons — open file in associated app, open containing folder in Explorer, or copy path to clipboard. The original version only copied paths.

### Phase 4: Bug Fixing & Polish (Nov 25 – Dec 1, 2025)

**Commits:** `working on fixing issues` → `updated the documentation and bugfixes` (PR #3)

This phase was about making it actually reliable:

- **Word counts optimization** — The "Popular Words" sidebar was taking 15+ seconds because it processed document content on every page load. Fixed by pre-calculating word frequencies during indexing and storing them in a `word_counts` table. Result: <100ms.
- **"nan" contamination** — Spreadsheet cells with no value produced "nan" strings that polluted the word counts. Added "nan" to the stop word list and created `fix_corrupted_word_counts.py` to clean existing databases.
- **Vacuum utility** — After cleaning up "nan" entries, databases had wasted space. Added `vacuum_databases.py` and a GUI button to run SQLite VACUUM.
- **Standalone search GUI** (`search_gui.py`, `build_search_gui_exe.py`) — Added a third executable, a desktop Tkinter app for searching, as an alternative to the browser-based interface.
- **API integration example** — Full HTML page (`api_integration_example.html`) demonstrating all REST endpoints with live testing.
- **More file types** — Added support for `.xls` (legacy Excel) and `.ps1` (PowerShell scripts).
- **Test scripts** — `test_word_counts.py`, `test_api_endpoints.py`, `check_word_sources.py`, `verify_content_purity.py` for validating data integrity.

---

## Architecture Overview

```
User                          Server Side
─────                         ───────────
Browser/GUI  ──HTTP──▶  Flask Server (server.py)
                              │
                              ├── Queries all databases in databases/
                              │     ├── db_<hash1>.sqlite3 (Folder A)
                              │     ├── db_<hash2>.sqlite3 (Folder B)
                              │     └── index.json (folder→db mapping)
                              │
                              ├── Merges results across databases
                              ├── Sorts by relevance/date/name/size
                              └── Paginates and returns JSON

Indexing Pipeline
─────────────────
DocumentIndexer GUI
    │
    ├── For each folder:
    │     ├── Create/lookup database via database_manager.py
    │     ├── Walk directory tree, collect files
    │     ├── Spawn multiprocessing pool (75% of cores)
    │     │     └── Workers extract text (CPU-bound)
    │     ├── Main process writes to SQLite (single writer)
    │     └── Update word_counts table
    │
    └── Optional: parallel folder indexing
          └── ProcessPoolExecutor indexes multiple folders simultaneously
```

## Technical Decisions Worth Discussing

### Why SQLite FTS5?
- Zero-config, serverless, single-file database
- FTS5 provides ranked full-text search out of the box
- Perfect for a local-first tool — no database server to install or maintain
- Handles hundreds of thousands of documents without issue

### Why multiprocessing over threading?
- Text extraction (PDF parsing, OCR, Excel reading) is CPU-bound
- Python's GIL prevents true parallelism with threads for CPU work
- Multiprocessing bypasses the GIL — each worker is a separate process
- Measured speedup: ~10-20x on 8+ core machines

### Why one database per folder?
- Avoids SQLite write contention when indexing multiple sources
- Each collection is independently manageable (delete, re-index, share)
- Searching across multiple small databases is still fast (<50ms overhead for 5 dbs)

### Why PyInstaller?
- Bundles Python runtime + all dependencies into a folder
- End users don't need to install Python, pip, or any packages
- Trade-off: larger file size (~50-80MB per app) and occasional antivirus false positives

### Pre-calculated word counts vs. on-the-fly
- Original approach: query 50 random docs, regex-extract words on every page load → 15+ seconds
- New approach: count words during indexing, store in `word_counts` table → <100ms
- Lesson: if you're computing the same expensive thing repeatedly, cache it

---

## Challenges & Lessons Learned

1. **The "nan" problem** — Pandas reads empty spreadsheet cells as `NaN`, which `str()` converts to `"nan"`. This string ended up as the #1 "popular word." Fix: add to stop words list + retroactive cleanup script.

2. **SQLite concurrent writes** — Early attempts at parallel indexing with multiple writers caused database lock errors. Solution: funnel all writes through a single main process; workers only return extracted data.

3. **PyInstaller + multiprocessing on Windows** — Requires `multiprocessing.freeze_support()` call at entry point, or you get a `RuntimeError`. Easy to miss.

4. **Network path performance** — Parallel indexing shows diminished returns on network shares because I/O becomes the bottleneck, not CPU. The tool handles this gracefully but it's worth noting for users.

5. **Excel format fragmentation** — `.xlsx` (openpyxl) and `.xls` (xlrd/pandas) require completely different libraries. The `.xls` format wasn't in the initial build and was a gap users noticed.

6. **Word count data integrity** — After adding the word counts feature to existing databases, a rebuild tool was needed. You can't assume all databases were created with the latest schema.

---

## Stats

- **Development timeline:** ~12 days (Nov 20 – Dec 1, 2025)
- **3 PRs**, each representing a major feature phase
- **Core codebase:** Python (Flask, SQLite, Tkinter, multiprocessing, PyInstaller)
- **Frontend:** Single-page HTML/CSS/JS (no framework)
- **Supported formats:** 8 file types across 5 extraction libraries
- **Indexing speed:** ~11x faster with parallel processing (1000 docs: 45min → 4min)

---

## Demo Talking Points

1. **Show the indexer GUI** — add a folder, start indexing, watch parallel processing in action
2. **Show the web search** — search a term, demonstrate filters, click through to open a file
3. **Show the popular words sidebar** — instant load thanks to pre-calculated counts
4. **Show multi-database** — add a second folder, search spans both automatically
5. **Show the API** — open `api_integration_example.html`, make live API calls
6. **Show the settings page** — change database path, demonstrate multi-user setup concept
