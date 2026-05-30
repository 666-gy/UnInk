@echo off
title Quick Uninstall - Install

echo ============================================
echo    Quick Uninstall - Install
echo ============================================
echo.

:: Check admin
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting admin permission...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set "INSTALL_DIR=%~dp0"
set "EXE_PATH=%INSTALL_DIR%uninstall_helper.exe"

:: Check exe exists
if not exist "%EXE_PATH%" (
    echo Error: uninstall_helper.exe not found!
    echo Please run build.bat first.
    pause
    exit /b 1
)

echo Install dir: %INSTALL_DIR%
echo.
echo Registering right-click menu...

:: Add to .lnk right-click menu
reg add "HKEY_CLASSES_ROOT\lnkfile\shell\QuickUninstall" /ve /d "Uninstall This App" /f >nul
reg add "HKEY_CLASSES_ROOT\lnkfile\shell\QuickUninstall" /v "Icon" /d "imageres.dll,-98" /f >nul
reg add "HKEY_CLASSES_ROOT\lnkfile\shell\QuickUninstall\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul

if errorlevel 1 (
    echo Install failed! Check permission.
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Install Success!
echo ============================================
echo.
echo Now you can:
echo   Right-click any shortcut (.lnk file)
echo   Select "Uninstall This App" to uninstall
echo.

pause
