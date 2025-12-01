"""
Build script for Document Search GUI executable
Creates a standalone .exe for the desktop search application
"""

import PyInstaller.__main__
import sys
from pathlib import Path

def build_exe():
    """Build the search GUI executable"""

    # Get the directory containing this script
    script_dir = Path(__file__).parent
    search_gui_script = script_dir / "search_gui.py"

    print("=" * 80)
    print("BUILDING DOCUMENT SEARCH GUI EXECUTABLE")
    print("=" * 80)
    print()

    # PyInstaller arguments
    args = [
        str(search_gui_script),
        '--name=DocumentSearchGUI',
        '--onefile',
        '--windowed',  # No console window
        '--icon=NONE',

        # Include necessary files
        '--add-data=templates;templates',
        '--add-data=config.py;.',
        '--add-data=config_manager.py;.',
        '--add-data=database_manager.py;.',
        '--add-data=company_abbreviations.py;.',
        '--add-data=server.py;.',

        # Hidden imports
        '--hidden-import=flask',
        '--hidden-import=jinja2',
        '--hidden-import=sqlite3',
        '--hidden-import=webbrowser',
        '--hidden-import=threading',
        '--hidden-import=subprocess',

        # Clean build
        '--clean',
        '--noconfirm',
    ]

    print("Building executable with PyInstaller...")
    print()

    try:
        PyInstaller.__main__.run(args)
        print()
        print("=" * 80)
        print("✓ BUILD COMPLETE")
        print("=" * 80)
        print()
        print(f"Executable location: {script_dir / 'dist' / 'DocumentSearchGUI.exe'}")
        print()
        print("USAGE:")
        print("  Double-click DocumentSearchGUI.exe to launch the search interface")
        print()
        print("OPTIONAL:")
        print("  Install pywebview for embedded browser view:")
        print("    pip install pywebview")
        print()
        print("  Without pywebview, the app will open in your default web browser")
        print("=" * 80)

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ BUILD FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    build_exe()
