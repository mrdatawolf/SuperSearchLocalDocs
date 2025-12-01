"""
Vacuum all database files to reclaim disk space and improve performance.

Run this AFTER rebuilding word counts to compress the database files.
"""
import sqlite3
import os
import time
from pathlib import Path

# Path to databases folder
databases_folder = r"C:\Users\patrick\DocumentSearch\databases"

print("=" * 80)
print("DATABASE VACUUM UTILITY")
print("=" * 80)
print("\nThis will compact all database files to reclaim disk space.")
print("Run this AFTER rebuilding word counts to get the most benefit.\n")

# Get all .sqlite3 files
db_files = list(Path(databases_folder).glob("*.sqlite3"))

if not db_files:
    print(f"No database files found in {databases_folder}")
    exit()

print(f"Found {len(db_files)} database(s) to vacuum:\n")

total_space_before = 0
total_space_after = 0

for db_file in db_files:
    db_path = str(db_file)
    db_name = db_file.name

    # Get size before
    size_before = db_file.stat().st_size
    size_before_mb = size_before / (1024 * 1024)
    total_space_before += size_before

    print(f"Processing: {db_name}")
    print(f"  Size before: {size_before_mb:.2f} MB")

    try:
        # Connect and vacuum
        conn = sqlite3.connect(db_path)
        print(f"  Vacuuming... ", end="", flush=True)

        # Disable WAL mode if enabled (WAL prevents VACUUM from shrinking the main db file)
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.commit()

        # Execute VACUUM
        conn.execute("VACUUM")
        conn.commit()

        # Switch back to WAL mode for better performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.commit()
        conn.close()

        # Force file system to update (Windows caching issue)
        time.sleep(0.2)

        print("Done!")

        # Get size after
        size_after = db_file.stat().st_size
        size_after_mb = size_after / (1024 * 1024)
        total_space_after += size_after

        saved = size_before - size_after
        saved_mb = saved / (1024 * 1024)
        percent_saved = (saved / size_before * 100) if size_before > 0 else 0

        print(f"  Size after:  {size_after_mb:.2f} MB")
        print(f"  Space saved: {saved_mb:.2f} MB ({percent_saved:.1f}%)")
        print()

    except Exception as e:
        print(f"\n  ERROR: {e}\n")

# Summary
print("=" * 80)
print("SUMMARY")
print("=" * 80)

total_before_mb = total_space_before / (1024 * 1024)
total_after_mb = total_space_after / (1024 * 1024)
total_saved_mb = (total_space_before - total_space_after) / (1024 * 1024)
total_percent = ((total_space_before - total_space_after) / total_space_before * 100) if total_space_before > 0 else 0

print(f"Total size before: {total_before_mb:.2f} MB")
print(f"Total size after:  {total_after_mb:.2f} MB")
print(f"Total space saved: {total_saved_mb:.2f} MB ({total_percent:.1f}%)")
print("\n✓ Vacuum complete!\n")
