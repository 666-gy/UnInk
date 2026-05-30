@echo off
title Quick Uninstall - Build

echo ============================================
echo    Quick Uninstall - Build Tool
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python first.
    pause
    exit /b 1
)

:: Check PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: Check pywin32
python -c "import win32com" >nul 2>&1
if errorlevel 1 (
    echo Installing pywin32...
    pip install pywin32
)

echo.
echo Building...
echo.

:: Build single exe
pyinstaller --onefile --name "uninstall_helper" --console --clean uninstall_helper.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Build Success!
echo ============================================
echo.
echo Output: dist\uninstall_helper.exe
echo.
echo Next: Run install.bat to add right-click menu
echo.

:: Copy to current dir
copy /Y "dist\uninstall_helper.exe" "." >nul
echo Copied uninstall_helper.exe to current folder.

pause
