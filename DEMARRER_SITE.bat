@echo off
chcp 65001 >nul
echo ========================================
echo   DÉMARRAGE MAP EVENT AI
echo   Frontend + Backend + Ouverture navigateur
echo ========================================
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python et réessayer.
    pause
    exit /b 1
)

echo [1/3] Démarrage du Backend Flask (port 5005)...
start "Backend Flask - Port 5005" cmd /k "cd /d %~dp0..\backend && python main.py"

timeout /t 3 /nobreak >nul

echo [2/3] Démarrage du Frontend HTTP (port 3000)...
start "Frontend HTTP - Port 3000" cmd /k "cd /d %~dp0public && python -m http.server 3000"

timeout /t 3 /nobreak >nul

echo [3/3] Ouverture du navigateur...
timeout /t 2 /nobreak >nul
start http://localhost:3000/mapevent.html

echo.
echo ========================================
echo   ✅ SERVEURS DÉMARRÉS !
echo ========================================
echo.
echo 📍 Frontend: http://localhost:3000/mapevent.html
echo 📍 Backend:  http://localhost:5005
echo 📍 Health:   http://localhost:5005/health
echo.
echo Le navigateur devrait s'ouvrir automatiquement.
echo.
echo Pour arrêter les serveurs, fermez les fenêtres cmd.
echo.
pause






























