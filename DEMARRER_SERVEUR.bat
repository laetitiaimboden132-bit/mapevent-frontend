@echo off
chcp 65001 >nul
echo ========================================
echo   DÉMARRAGE DU SERVEUR MAP EVENT
echo ========================================
echo.
cd /d "%~dp0public"
echo Dossier actuel: %CD%
echo.
echo Démarrage du serveur HTTP sur le port 3000...
echo.
echo Ouvrez votre navigateur et allez sur:
echo   http://localhost:3000/mapevent.html
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.
python -m http.server 3000
pause
































