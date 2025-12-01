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
print("This will create three standalone applications:")
print("  1. DocumentIndexer.exe    - GUI for indexing documents")
print("  2. DocumentSearch.exe     - Web server for searching")
print("  3. DocumentSearchGUI.exe  - Desktop GUI search application")
print()
print("All applications will run on any Windows computer without Python installed!")
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
print()

# Build the search GUI
print("STEP 3: Building Search GUI...")
print("-" * 80)
try:
    result = subprocess.run([sys.executable, "build_search_gui_exe.py"], check=True)
    print("\n✅ Search GUI build complete!")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Search GUI build failed: {e}")
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
print(f"   Use for: Running the web search interface (browser-based)")
print()
print(f"📂 Search GUI:")
print(f"   Location: {script_dir / 'dist'}")
print(f"   Executable: DocumentSearchGUI.exe")
print(f"   Use for: Desktop application with embedded browser")
print()
print("=" * 80)
print("DEPLOYMENT INSTRUCTIONS:")
print("=" * 80)
print()
print("For end users (no Python needed):")
print()
print("1. Copy all executables to the target computer:")
print("   - dist\\DocumentIndexer\\")
print("   - dist\\DocumentSearch\\")
print("   - dist\\DocumentSearchGUI.exe")
print()
print("2. First-time setup:")
print("   a. Run DocumentIndexer.exe")
print("   b. Configure server IP address (use your network card IP for network access)")
print("   c. Click 'Save Server Config'")
print("   d. Add folders to index")
print("   e. Click 'Start Indexing' to index documents")
print()
print("3. Search your documents (choose one method):")
print()
print("   METHOD A - Desktop App (Recommended):")
print("     → Just run DocumentSearchGUI.exe")
print("     → Standalone app with embedded interface")
print("     → No browser needed!")
print()
print("   METHOD B - Web Browser:")
print("     a. Run DocumentSearch.exe")
print("     b. Browser opens automatically at http://localhost:9000")
print("     c. Start searching!")
print()
print("4. To re-index or add new documents:")
print("   a. Run DocumentIndexer.exe again")
print("   b. Click 'Start Indexing'")
print()
print("=" * 80)
print()
print("💡 TIPS:")
print("   • Create a desktop shortcut to DocumentSearchGUI.exe for quick access")
print("   • For embedded browser view, install: pip install pywebview")
print("   • Without pywebview, the GUI opens in your default browser")
print()
