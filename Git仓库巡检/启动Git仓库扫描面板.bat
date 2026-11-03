@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

set "PY_EXE=python"
if exist "C:\Software\Code\Python\python.exe" (
    set "PY_EXE=C:\Software\Code\Python\python.exe"
)

"%PY_EXE%" "%~dp0server.py" %*
if errorlevel 1 (
    echo.
    echo [ERROR] Server exited unexpectedly.
    pause
)
