@echo off
REM Windows batch file to start doc2mkdocs web UI

echo.
echo ========================================
echo   doc2mkdocs Web UI Launcher
echo ========================================
echo.

REM Try to find Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Found: python
    python start_web_ui.py
    goto :end
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Found: python3
    python3 start_web_ui.py
    goto :end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Found: py
    py start_web_ui.py
    goto :end
)

echo ERROR: Python not found!
echo.
echo Please install Python from:
echo   https://www.python.org/downloads/
echo.
pause

:end

