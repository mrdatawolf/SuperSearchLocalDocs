@echo off
REM Start Document Search Server
REM This batch file starts the document search web server

echo ================================================================================
echo   Document Search Server
echo ================================================================================
echo.
echo Starting server...
echo.
echo The server will be accessible at:
echo   - Local:   http://localhost:9000
echo   - Network: http://YOUR-IP-ADDRESS:9000
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py

pause
