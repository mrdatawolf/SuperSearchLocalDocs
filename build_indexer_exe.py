"""
Build script to create a standalone executable for the Document Indexer GUI
This will create a self-contained .exe that includes Python and all dependencies

Usage:
    1. Install PyInstaller: pip install pyinstaller
    2. Run this script: python build_indexer_exe.py
"""
import sys

try:
    import PyInstaller.__main__
except ImportError:
    print("ERROR: PyInstaller is not installed!")
    print("Please install it first: pip install pyinstaller")
    sys.exit(1)

from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent

print("Building Document Indexer GUI executable...")
print("This may take a few minutes...\n")

# PyInstaller arguments
PyInstaller.__main__.run([
    'indexer_gui.py',                     # Main script to bundle
    '--name=DocumentIndexer',             # Name of the executable
    '--onedir',                           # Create a directory with all dependencies
    '--windowed',                         # Hide console window (GUI app)
    '--icon=NONE',                        # Add an icon later if desired
    '--add-data=config.py;.',            # Include config
    '--add-data=config_manager.py;.',    # Include config manager
    '--add-data=database_manager.py;.',  # Include database manager
    '--add-data=indexer.py;.',           # Include indexer module
    '--add-data=company_abbreviations.py;.',  # Include abbreviations module
    '--add-data=END_USER_README.md;.',   # Include user documentation
    '--add-data=DISTRIBUTION_README.txt;.',  # Include distribution readme
    '--hidden-import=tkinter',
    '--hidden-import=sqlite3',
    '--hidden-import=openpyxl',
    '--hidden-import=pandas',
    '--hidden-import=docx',
    '--hidden-import=PyPDF2',
    '--hidden-import=PIL',
    '--hidden-import=pytesseract',
    '--collect-all=tkinter',
    '--noconfirm',                       # Replace output without asking
])

print("\n" + "="*80)
print("✅ Build Complete!")
print("="*80)
print(f"\nYour application is located at: {script_dir / 'dist' / 'DocumentIndexer'}")
print(f"Main executable: {script_dir / 'dist' / 'DocumentIndexer' / 'DocumentIndexer.exe'}")
print("\nIMPORTANT NOTES:")
print("  1. This is a GUI application - double-click DocumentIndexer.exe to launch")
print("  2. Configure your document path and database location in the GUI")
print("  3. Click 'Save Configuration' to save settings")
print("  4. Click 'Start Indexing' to scan and index documents")
print("  5. The entire 'DocumentIndexer' folder can be copied to any Windows computer")
print("  6. No Python installation needed on the target computer!")
print("\nTo create a single-file executable instead, change --onedir to --onefile in build_indexer_exe.py")
