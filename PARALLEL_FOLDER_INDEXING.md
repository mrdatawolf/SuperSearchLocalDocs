# Parallel Folder Indexing with Dynamic Reallocation

## Overview

The indexer now supports **two levels of parallelism** with **dynamic worker reallocation**:

1. **Folder-level parallelism** - Index multiple folders simultaneously
2. **File-level parallelism** - Process multiple files within each folder simultaneously

Both can be enabled together for maximum performance!

## How It Works

### Architecture

```
Main GUI Thread
    ↓
ProcessPoolExecutor (2-4 folder workers)
    ↓
Each worker indexes one folder
    ↓
Within each folder: Multiprocessing pool for files (uses remaining cores)
```

### Dynamic Reallocation

The system uses a **work-stealing pool** that automatically redistributes work:

```
Example with 12 cores, 5 folders:

Initial State (3 folder workers):
Worker 1: Folder A [======= 4 cores =======]
Worker 2: Folder B [======= 4 cores =======]
Worker 3: Folder C [======= 4 cores =======]
Queue: [Folder D, Folder E]

Worker 1 finishes Folder A:
Worker 1: Folder D [======= 4 cores =======]  ← Automatically picks up next folder!
Worker 2: Folder B [====== still working ====]
Worker 3: Folder C [====== still working ====]
Queue: [Folder E]

Worker 3 finishes Folder C:
Worker 1: Folder D [====== still working ====]
Worker 2: Folder B [====== still working ====]
Worker 3: Folder E [======= 4 cores =======]  ← Automatically picks up Folder E!
Queue: []

No pauses or manual reallocation needed - it's completely automatic!
```

## Configuration

### GUI Options

**Performance Options section has two checkboxes:**

1. **⚡ Enable Fast Mode (parallel file processing)**
   - Processes multiple files within each folder simultaneously
   - Uses ~75% of CPU cores when enabled
   - Recommended: Always enabled

2. **🚀 Index Multiple Folders Simultaneously**
   - Indexes multiple folders at the same time
   - Dynamically reallocates workers as folders complete
   - Recommended: Enable if you have 8+ cores and 2+ folders

### CPU Allocation Strategy

The system intelligently allocates cores based on configuration:

**Example 1: 12 cores, 3 folders, both parallel modes enabled**
```
Folder workers: 3 (one per folder)
Cores per folder: 4
Total utilization: 100%

All 3 folders index simultaneously, each using 4 cores for file processing
```

**Example 2: 16 cores, 5 folders, both parallel modes enabled**
```
Folder workers: 4 (max workers limited)
Cores per folder: 4
Total utilization: 100%

4 folders index simultaneously, 5th waits then automatically starts when one finishes
```

**Example 3: 8 cores, 4 folders, both parallel modes enabled**
```
Folder workers: 2
Cores per folder: 4
Total utilization: 100%

2 folders at a time, workers automatically pick up remaining folders as they finish
```

## Performance Gains

### Speedup Examples

**Without folder-level parallelism (old behavior):**
```
Folder A: 10 minutes (using 6 cores)
Folder B: 15 minutes (using 6 cores)
Folder C: 8 minutes (using 6 cores)
Total: 33 minutes
```

**With folder-level parallelism (new behavior, 8 cores):**
```
Folder A & B start simultaneously:
  Folder A: 10 minutes (using 4 cores) → finishes, Worker 1 picks up Folder C
  Folder B: 15 minutes (using 4 cores) → still running
  Folder C: 8 minutes (using 4 cores) → starts at minute 10, finishes at minute 18

Total: ~18 minutes (45% faster!)
```

**With folder-level parallelism (16 cores):**
```
All 3 folders start simultaneously:
  Folder A: 10 minutes (using 5 cores)
  Folder B: 15 minutes (using 5 cores)
  Folder C: 8 minutes (using 5 cores)

Total: ~15 minutes (55% faster!)
```

### When to Use

**Enable folder-level parallelism when:**
- ✅ You have 8+ CPU cores
- ✅ You have 2+ folders to index
- ✅ Folders are on different drives (avoids I/O bottleneck)
- ✅ You want maximum indexing speed

**Disable folder-level parallelism when:**
- ⚠️ You have < 8 cores (file-level parallelism is more efficient)
- ⚠️ You only have 1 folder
- ⚠️ Your computer is doing other CPU-intensive tasks
- ⚠️ All folders are on the same slow drive (I/O bottleneck)

## Implementation Details

### Code Architecture

**Worker Function (runs in separate process):**
```python
def index_folder_worker(folder_path, db_path, use_parallel):
    """
    Indexes a single folder - runs in separate process
    Uses file-level parallelism if use_parallel=True
    Returns: (folder_path, indexed_count, error_count, success, error_message)
    """
    indexer = DocumentIndexer(document_path=folder_path, db_path=db_path)
    indexed_count, error_count = indexer.scan_and_index(use_parallel=use_parallel)
    return (folder_path, indexed_count, error_count, True, None)
```

**Main Indexing Loop (in GUI thread):**
```python
with ProcessPoolExecutor(max_workers=max_workers) as executor:
    # Submit all folder tasks to pool
    future_to_folder = {
        executor.submit(index_folder_worker, path, db, parallel): info
        for path, db, info in folders
    }

    # Process results as they complete (dynamic reallocation!)
    for future in as_completed(future_to_folder):
        result = future.result()  # Worker automatically picks up next folder
        # Update GUI with results
```

### Worker Allocation Algorithm

```python
cpu_count = os.cpu_count()
num_folders = len(folders)

# Calculate optimal number of folder workers
max_workers = min(
    num_folders,              # Don't create more workers than folders
    max(2, cpu_count // 4)    # Use 2-4 workers (25% of cores each)
)

# Each worker gets roughly equal cores for file processing
cores_per_folder = cpu_count // max_workers
```

**Examples:**
- 4 cores → 2 workers (2 cores each)
- 8 cores → 2 workers (4 cores each)
- 12 cores → 3 workers (4 cores each)
- 16 cores → 4 workers (4 cores each)
- 32 cores → 4 workers (8 cores each) - capped at 4 workers

### Benefits of This Approach

1. **Automatic Load Balancing**
   - Fast folders don't wait for slow ones
   - Workers always have something to do
   - No idle CPU time

2. **No Manual Configuration**
   - System automatically calculates optimal workers
   - Adapts to folder count and CPU count
   - No need to specify thread counts

3. **Fault Tolerance**
   - If one folder fails, others continue
   - Failed folders don't block the queue
   - Clear error reporting per folder

4. **Scalability**
   - Works efficiently with 1 folder or 100 folders
   - CPU utilization stays near 100%
   - Memory usage is bounded by worker count

## GUI Behavior

### Progress Display

**Sequential mode (old):**
```
================================================================================
INDEXING FOLDER 1/3
================================================================================
Folder: C:\Documents
[detailed file-by-file progress...]

================================================================================
INDEXING FOLDER 2/3
================================================================================
...
```

**Parallel mode (new):**
```
🚀 Using 3 worker processes for folder-level parallelism
   Workers will dynamically pick up folders as they complete

✓ [1/3] Completed: Documents (523 documents, 2 errors)
✓ [2/3] Completed: NetworkShare (1024 documents, 0 errors)
✓ [3/3] Completed: Desktop (87 documents, 1 errors)
```

Much cleaner output with parallel processing!

### CPU Info Label

The GUI dynamically updates to show current configuration:

- **Both parallel modes:** "Using all 12 cores: 3 folders in parallel, ~4 cores per folder"
- **File-level only:** "Using 9 of 12 cores (folders indexed sequentially)"
- **Sequential:** "Sequential mode - using 1 core (slowest but lowest CPU usage)"

## Advanced: Custom Worker Count

For power users who want to override the automatic calculation:

```python
# In indexer_gui.py, line ~415, change:
max_workers = min(len(valid_folders), max(2, cpu_count // 4))

# To a fixed value:
max_workers = 3  # Always use 3 folder workers

# Or a custom formula:
max_workers = min(len(valid_folders), cpu_count // 2)  # Use 50% of cores per folder
```

## Logging

### Worker Process Output

Worker processes can't directly access the GUI. Their console output goes to the terminal (if running from command line) or is suppressed (if running as .exe).

The GUI only shows:
- Start message with worker count
- Completion message for each folder
- Final summary

This keeps the GUI responsive and the output clean.

### Debugging

To see detailed output from worker processes during development:

```python
# Run from command line:
python indexer_gui.py

# Worker stdout/stderr will appear in the console
# GUI log shows high-level progress
```

## Limitations

1. **Minimum Core Count:** Folder-level parallelism only makes sense with 8+ cores
2. **I/O Bottleneck:** Multiple folders on same disk may not get full speedup
3. **Memory Usage:** Each folder worker loads files into memory, increasing RAM usage
4. **GUI Logging:** Detailed per-file progress not shown in parallel mode (by design)

## Future Enhancements

Possible improvements:
- Priority queue for larger folders
- Real-time progress updates from workers
- Automatic I/O bottleneck detection
- Adaptive worker count based on folder sizes
- Network bandwidth awareness for remote folders

## Summary

The new parallel folder indexing with dynamic reallocation provides:

✅ **Massive speedup** for multi-folder indexing (up to 55% faster)
✅ **Automatic load balancing** - no manual configuration
✅ **Dynamic worker reallocation** - fast folders don't wait for slow ones
✅ **Configurable via GUI** - two simple checkboxes
✅ **Fault tolerant** - one folder failure doesn't block others
✅ **Scalable** - works from 1 to 100 folders efficiently

Perfect for users with modern multi-core CPUs indexing multiple document collections!
