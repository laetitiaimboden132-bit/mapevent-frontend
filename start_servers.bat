@echo off
echo ========================================
echo   Demarrage MapEventAI - Frontend + Backend
echo ========================================
echo.

echo [1/2] Demarrage du Backend Flask (port 5005)...
start "Backend Flask - Port 5005" cmd /k "cd /d c:\MapEventAI_NEW\backend && python main.py"

timeout /t 2 /nobreak >nul

echo [2/2] Demarrage du Frontend HTTP (port 8000)...
start "Frontend HTTP - Port 8000" cmd /k "cd /d c:\MapEventAI_NEW\frontend\public && python -m http.server 8000"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   Serveurs demarres !
echo ========================================
echo.
echo Frontend: http://localhost:8000/mapevent.html
echo Backend:  http://localhost:5005
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul

































