"""
Database Manager - Handles multiple databases for different indexed folders
Each indexed folder gets its own database in the databases/ subfolder
"""

import json
import hashlib
from pathlib import Path
import sys
import os


def get_databases_folder():
    """Get the databases folder path"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # sys.executable points to DocumentIndexer.exe or DocumentSearch.exe
        exe_dir = Path(sys.executable).parent
        parent_dir = exe_dir.parent
        databases_folder = parent_dir / "databases"
    else:
        # Running from source - use databases subfolder in current directory
        databases_folder = Path(__file__).parent / "databases"

    # Create databases folder if it doesn't exist
    databases_folder.mkdir(exist_ok=True)

    return databases_folder


def get_index_file():
    """Get path to the index.json file that maps folders to databases"""
    return get_databases_folder() / "index.json"


def load_index():
    """Load the index mapping folder paths to database files"""
    index_file = get_index_file()
    if index_file.exists():
        try:
            with open(index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading database index: {e}")
            return {}
    return {}


def save_index(index_data):
    """Save the index mapping folder paths to database files"""
    index_file = get_index_file()
    try:
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving database index: {e}")
        return False


def generate_db_filename(folder_path):
    """Generate a unique database filename for a folder path"""
    # Create a hash of the folder path for uniqueness
    path_hash = hashlib.md5(folder_path.encode('utf-8')).hexdigest()[:12]
    return f"db_{path_hash}.sqlite3"


def get_database_path(folder_path):
    """Get the database path for a specific indexed folder"""
    databases_folder = get_databases_folder()
    db_filename = generate_db_filename(folder_path)
    return str(databases_folder / db_filename)


def add_indexed_folder(folder_path, existing_db_path=None):
    """
    Add a folder to the index and return its database path

    Args:
        folder_path: Path to the folder containing documents
        existing_db_path: Optional path to existing database file to link (instead of creating new one)

    Returns:
        Database path for this folder
    """
    folder_path = str(Path(folder_path).resolve())  # Normalize path
    index = load_index()

    # Check if already indexed
    if folder_path in index:
        return index[folder_path]['db_path']

    # Determine database path
    if existing_db_path:
        # User is linking to an existing database
        db_path = str(Path(existing_db_path).resolve())
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")
    else:
        # Create new database path
        db_path = get_database_path(folder_path)

    # Add new entry
    index[folder_path] = {
        'db_path': db_path,
        'db_filename': Path(db_path).name,
        'added_date': str(Path(db_path).stat().st_mtime) if Path(db_path).exists() else None
    }

    save_index(index)
    return db_path


def remove_indexed_folder(folder_path):
    """Remove a folder from the index (optionally delete the database)"""
    folder_path = str(Path(folder_path).resolve())
    index = load_index()

    if folder_path in index:
        del index[folder_path]
        save_index(index)
        return True
    return False


def get_all_indexed_folders():
    """Get list of all indexed folders with their database info"""
    index = load_index()
    result = []

    for folder_path, info in index.items():
        db_path = info['db_path']
        db_exists = Path(db_path).exists()

        result.append({
            'folder_path': folder_path,
            'db_path': db_path,
            'db_filename': info['db_filename'],
            'db_exists': db_exists
        })

    return result


def get_all_database_paths():
    """Get list of all database file paths"""
    index = load_index()
    return [info['db_path'] for info in index.values()]


def cleanup_orphaned_databases():
    """Remove database files that are not in the index"""
    databases_folder = get_databases_folder()
    index = load_index()
    indexed_dbs = {info['db_filename'] for info in index.values()}

    removed = []
    for db_file in databases_folder.glob("db_*.sqlite3"):
        if db_file.name not in indexed_dbs:
            try:
                db_file.unlink()
                removed.append(db_file.name)
            except Exception as e:
                print(f"Error removing {db_file.name}: {e}")

    return removed


if __name__ == '__main__':
    # Test the module
    print("Database Manager Test")
    print("=" * 80)
    print(f"Databases folder: {get_databases_folder()}")
    print(f"Index file: {get_index_file()}")
    print("\nIndexed folders:")
    for folder_info in get_all_indexed_folders():
        print(f"  {folder_info['folder_path']}")
        print(f"    DB: {folder_info['db_filename']} (exists: {folder_info['db_exists']})")
