@echo off
echo Test des serveurs MapEventAI
echo.

echo Test 1: Verification Python...
python --version
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo Test 2: Verification Flask...
python -c "import flask; print('Flask OK')"
if errorlevel 1 (
    echo ERREUR: Flask n'est pas installe
    echo Installez avec: pip install flask flask-cors
    pause
    exit /b 1
)

echo.
echo Test 3: Demarrage Backend (test 5 secondes)...
start "Backend Test" cmd /k "cd /d c:\MapEventAI_NEW\backend && python main.py"
timeout /t 5 /nobreak >nul

echo.
echo Test 4: Verification port 5005...
netstat -ano | findstr ":5005"
if errorlevel 1 (
    echo ATTENTION: Le backend ne semble pas ecouter sur le port 5005
) else (
    echo OK: Backend ecoute sur port 5005
)

echo.
echo Test 5: Demarrage Frontend (test 5 secondes)...
start "Frontend Test" cmd /k "cd /d c:\MapEventAI_NEW\frontend\public && python -m http.server 8000"
timeout /t 5 /nobreak >nul

echo.
echo Test 6: Verification port 8000...
netstat -ano | findstr ":8000"
if errorlevel 1 (
    echo ATTENTION: Le frontend ne semble pas ecouter sur le port 8000
) else (
    echo OK: Frontend ecoute sur port 8000
)

echo.
echo ========================================
echo Tests termines
echo ========================================
echo.
echo Si les ports sont OK, essayez:
echo - http://127.0.0.1:8000/mapevent.html
echo - http://localhost:8000/mapevent.html
echo.
echo Si Firefox bloque, desactivez le proxy:
echo Menu > Options > Reseau > Parametres > Aucun proxy
echo.
pause

































