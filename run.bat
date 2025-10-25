@echo off
REM run.bat - helper Windows batch to create venv (if missing) and run the tool
SETLOCAL

IF NOT EXIST .venv\Scripts\python.exe (
    echo ".venv not found — creating virtual environment..."
    python -m venv .venv
)

REM Use the venv python to run the script so activation policies are not required
.venv\Scripts\python.exe willkommen_v2.py %*

ENDLOCAL
