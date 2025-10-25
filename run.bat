@echo off
REM run.bat - helper Windows batch to create venv (if missing) and run the tool
SETLOCAL

IF NOT EXIST .venv\Scripts\python.exe (
    echo ".venv not found — creating virtual environment..."
    python -m venv .venv
)

REM Ensure pip and requirements are installed using the venv python
IF EXIST .\requirements.txt (
    echo "Installing/Updating pip and requirements..."
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

REM Use the venv python to run the script so activation policies are not required
.venv\Scripts\python.exe willkommen_v2.py %*

ENDLOCAL
