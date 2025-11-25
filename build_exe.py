"""
Build script to create a standalone executable for Document Search
This will create a self-contained .exe that includes Python and all dependencies

Usage:
    1. Install PyInstaller: pip install pyinstaller
    2. Run this script: python build_exe.py
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

print("Building Document Search executable...")
print("This may take a few minutes...\n")

# PyInstaller arguments
PyInstaller.__main__.run([
    'server.py',                          # Main script to bundle
    '--name=DocumentSearch',              # Name of the executable
    '--onedir',                           # Create a directory with all dependencies (faster startup)
    '--console',                          # Show console window so users can see status
    '--icon=NONE',                        # Add an icon later if desired
    '--add-data=templates;templates',     # Include templates folder
    '--add-data=config.py;.',            # Include config
    '--add-data=config_manager.py;.',    # Include config manager
    '--add-data=database_manager.py;.',  # Include database manager
    '--add-data=company_abbreviations.py;.',  # Include company abbreviations module
    '--add-data=END_USER_README.md;.',   # Include user documentation
    '--add-data=DISTRIBUTION_README.txt;.',  # Include distribution readme
    '--hidden-import=flask',
    '--hidden-import=sqlite3',
    '--hidden-import=openpyxl',
    '--hidden-import=pandas',
    '--hidden-import=docx',
    '--hidden-import=PyPDF2',
    '--hidden-import=PIL',
    '--hidden-import=pytesseract',
    '--collect-all=flask',
    '--collect-all=werkzeug',
    '--noconfirm',                       # Replace output without asking
])

print("\n" + "="*80)
print("✅ Build Complete!")
print("="*80)
print(f"\nYour application is located at: {script_dir / 'dist' / 'DocumentSearch'}")
print(f"Main executable: {script_dir / 'dist' / 'DocumentSearch' / 'DocumentSearch.exe'}")
print("\nIMPORTANT NOTES:")
print("  1. Copy your database (documents.sqlite3) to the same folder as the .exe")
print("  2. The entire 'DocumentSearch' folder can be copied to any Windows computer")
print("  3. No Python installation needed on the target computer!")
print("  4. Double-click DocumentSearch.exe to start the server")
print("\nTo create a single-file executable instead, change --onedir to --onefile in build_exe.py")
