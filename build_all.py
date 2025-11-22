"""
Master build script to create both standalone executables
Builds both the Document Indexer GUI and the Search Server

Usage:
    1. Install PyInstaller: pip install pyinstaller
    2. Run this script: python build_all.py
"""
import sys
import subprocess

try:
    import PyInstaller
except ImportError:
    print("ERROR: PyInstaller is not installed!")
    print("Please install it first: pip install pyinstaller")
    sys.exit(1)

from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

print("=" * 80)
print("Building SuperSearch Local Docs - Standalone Executables")
print("=" * 80)
print()
print("This will create two standalone applications:")
print("  1. DocumentIndexer.exe - GUI for indexing documents")
print("  2. DocumentSearch.exe   - Web server for searching")
print()
print("Both applications will run on any Windows computer without Python installed!")
print()
print("=" * 80)
print()

# Build the indexer GUI first
print("STEP 1: Building GUI Indexer...")
print("-" * 80)
try:
    result = subprocess.run([sys.executable, "build_indexer_exe.py"], check=True)
    print("\n✅ GUI Indexer build complete!")
except subprocess.CalledProcessError as e:
    print(f"\n❌ GUI Indexer build failed: {e}")
    sys.exit(1)

print()
print("=" * 80)
print()

# Build the search server
print("STEP 2: Building Search Server...")
print("-" * 80)
try:
    result = subprocess.run([sys.executable, "build_exe.py"], check=True)
    print("\n✅ Search Server build complete!")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Search Server build failed: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("🎉 ALL BUILDS COMPLETE!")
print("=" * 80)
print()
print("Your standalone applications are ready:")
print()
print(f"📂 GUI Indexer:")
print(f"   Location: {script_dir / 'dist' / 'DocumentIndexer'}")
print(f"   Executable: DocumentIndexer.exe")
print(f"   Use for: Initial setup, configuration, and indexing documents")
print()
print(f"📂 Search Server:")
print(f"   Location: {script_dir / 'dist' / 'DocumentSearch'}")
print(f"   Executable: DocumentSearch.exe")
print(f"   Use for: Running the web search interface")
print()
print("=" * 80)
print("DEPLOYMENT INSTRUCTIONS:")
print("=" * 80)
print()
print("For end users (no Python needed):")
print()
print("1. Copy both folders to the target computer:")
print("   - dist\\DocumentIndexer\\")
print("   - dist\\DocumentSearch\\")
print()
print("2. First-time setup:")
print("   a. Run DocumentIndexer.exe")
print("   b. Configure document path and database location")
print("   c. Click 'Save Configuration'")
print("   d. Click 'Start Indexing' to index documents")
print()
print("3. Search your documents:")
print("   a. Run DocumentSearch.exe")
print("   b. Open browser to http://localhost:9000")
print("   c. Start searching!")
print()
print("4. To re-index or add new documents:")
print("   a. Run DocumentIndexer.exe again")
print("   b. Click 'Start Indexing'")
print()
print("=" * 80)
print()
print("💡 TIP: You can create shortcuts to these .exe files for easy access!")
print()
