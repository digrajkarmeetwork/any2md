@echo off
echo ========================================
echo Building any2md Windows Executable
echo ========================================
echo.

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller any2md.spec

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\any2md.exe
echo.
echo You can now distribute this .exe file!
echo ========================================
pause

