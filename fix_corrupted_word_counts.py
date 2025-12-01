"""
Emergency fix for corrupted word_counts table
This will clear all word counts and shrink the database back down
"""
import sqlite3
import os
import time
from pathlib import Path

# Path to databases folder
databases_folder = r"C:\Users\patrick\DocumentSearch\databases"

print("=" * 80)
print("CORRUPTED WORD COUNTS - EMERGENCY FIX")
print("=" * 80)
print()
print("This script will:")
print("  1. Delete ALL word counts from all databases")
print("  2. Vacuum databases to reclaim disk space")
print("  3. You can then rebuild word counts with the fixed code")
print()

# Find all database files
db_files = list(Path(databases_folder).glob("*.sqlite3"))

if not db_files:
    print(f"No database files found in {databases_folder}")
    exit(1)

print(f"Found {len(db_files)} database file(s)")
print()

# Confirm
response = input("This will DELETE all word counts. Continue? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled")
    exit(0)

print()
total_space_before = 0
total_space_after = 0

for i, db_file in enumerate(db_files, 1):
    db_path = str(db_file)
    db_name = db_file.name

    # Get size before
    size_before = db_file.stat().st_size
    size_before_mb = size_before / (1024 * 1024)
    total_space_before += size_before

    print(f"[{i}/{len(db_files)}] Processing: {db_name}")
    print(f"  Size before: {size_before_mb:.2f} MB")

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get word count before deletion
        cursor.execute("SELECT COUNT(*) FROM word_counts")
        word_count = cursor.fetchone()[0]
        print(f"  Word count entries: {word_count:,}")

        # Delete all word counts
        print(f"  Deleting word counts... ", end="", flush=True)
        cursor.execute("DELETE FROM word_counts")
        conn.commit()
        print("Done!")

        # Vacuum to reclaim space
        print(f"  Vacuuming... ", end="", flush=True)

        # Disable WAL mode if enabled
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.commit()

        # Execute VACUUM
        conn.execute("VACUUM")
        conn.commit()

        # Switch back to WAL mode
        conn.execute("PRAGMA journal_mode=WAL")
        conn.commit()
        conn.close()

        # Force file system to update
        time.sleep(0.2)

        print("Done!")

        # Get size after
        size_after = db_file.stat().st_size
        size_after_mb = size_after / (1024 * 1024)
        total_space_after += size_after

        saved = size_before - size_after
        saved_mb = saved / (1024 * 1024)
        percent = (saved / size_before * 100) if size_before > 0 else 0

        print(f"  Size after: {size_after_mb:.2f} MB")
        print(f"  Space saved: {saved_mb:.2f} MB ({percent:.1f}%)")
        print()

    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
total_before_gb = total_space_before / (1024 * 1024 * 1024)
total_after_gb = total_space_after / (1024 * 1024 * 1024)
total_saved = total_space_before - total_space_after
total_saved_gb = total_saved / (1024 * 1024 * 1024)
percent_saved = (total_saved / total_space_before * 100) if total_space_before > 0 else 0

print(f"Total size before: {total_before_gb:.2f} GB")
print(f"Total size after:  {total_after_gb:.2f} GB")
print(f"Total space saved: {total_saved_gb:.2f} GB ({percent_saved:.1f}%)")
print()
print("✓ All word counts have been deleted and databases vacuumed!")
print()
print("NEXT STEPS:")
print("  1. Run: python build_all.py  (to rebuild executables with the fix)")
print("  2. Open DocumentIndexer.exe")
print("  3. Click '🔨 Rebuild Word Counts' to rebuild with corrected code")
print()
