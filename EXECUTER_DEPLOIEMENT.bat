@echo off
chcp 65001 >nul
echo ========================================
echo   DEPLOIEMENT FRONTEND
echo ========================================
echo.

cd /d "%~dp0"

echo Execution du script de deploiement...
echo.

powershell -ExecutionPolicy Bypass -File "deploy-force-cache-bust.ps1"

echo.
echo ========================================
echo   FIN
echo ========================================
echo.
pause
