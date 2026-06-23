@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  GIT PUSH AUTOMÁTICO
::  Uso: git_push.bat ["Mensaje de commit"]
::  Si no se pasa mensaje, se genera uno automático con fecha/hora
:: ============================================================

:: Verificar que estamos dentro de un repositorio Git
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No estas dentro de un repositorio Git.
    echo Asegurate de ejecutar este script en la raiz del proyecto.
    pause
    exit /b 1
)

:: Verificar si hay cambios para commit
git status --porcelain | findstr . >nul
if errorlevel 1 (
    echo [INFO] No hay cambios para commit. Todo esta al dia.
    pause
    exit /b 0
)

:: Mostrar estado actual
echo.
echo ============================================================
echo   REPOSITORIO: %cd%
echo ============================================================
echo.
git status --short
echo.

:: Obtener mensaje de commit (argumento o generado automaticamente)
set "commit_msg=%~1"
if "%commit_msg%"=="" (
    :: Generar fecha y hora en formato YYYY-MM-DD HH:MM
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do (set mytime=%%a-%%b)
    set "commit_msg=Actualizacion automatica %mydate% %mytime%"
)

:: Preguntar si se desea continuar
echo Se va a realizar un commit con el mensaje:
echo   "%commit_msg%"
echo.
set /p confirm="¿Continuar? (s/n): "
if /i not "%confirm%"=="s" (
    echo Operacion cancelada.
    pause
    exit /b 0
)

:: Añadir todos los archivos
echo.
echo [1/3] Añadiendo archivos...
git add .

:: Realizar commit
echo [2/3] Realizando commit...
git commit -m "%commit_msg%"
if errorlevel 1 (
    echo [ERROR] Fallo el commit. Revisa los mensajes de error.
    pause
    exit /b 1
)

:: Subir cambios al remoto
echo [3/3] Subiendo cambios al repositorio remoto...
git push
if errorlevel 1 (
    echo [ERROR] Fallo el push. Puede que necesites hacer pull primero.
    echo Intenta: git pull --rebase
    pause
    exit /b 1
)

:: Mensaje de exito
echo.
echo ============================================================
echo   ¡TODO SUBIDO CORRECTAMENTE!
echo ============================================================
echo.
git log -1 --oneline
echo.
pause