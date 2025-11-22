@echo off
REM Start Document Indexer GUI
REM This batch file starts the GUI indexer for easy document configuration

echo ================================================================================
echo   Document Indexer - GUI Setup
echo ================================================================================
echo.
echo Starting GUI indexer...
echo.
echo Use this application to:
echo   - Configure document path
echo   - Set database location
echo   - Index your documents
echo   - View database statistics
echo.

python indexer_gui.py

pause
