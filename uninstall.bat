@echo off
title Quick Uninstall - Uninstall

echo ============================================
echo    Quick Uninstall - Uninstall
echo ============================================
echo.

:: Check admin
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting admin permission...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Removing right-click menu...

:: Remove from registry
reg delete "HKEY_CLASSES_ROOT\lnkfile\shell\QuickUninstall" /f >nul 2>&1

if errorlevel 1 (
    echo Menu not found. Already uninstalled?
) else (
    echo.
    echo ============================================
    echo    Uninstall Success!
    echo ============================================
    echo.
    echo Right-click menu removed.
    echo.
)

pause
