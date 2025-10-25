<#
run.ps1 - Crée un venv local .venv, installe les dépendances et lance `willkommen_v2.py`.
Usage: Ouvrir PowerShell dans ce dossier et exécuter `.
un.ps1`
#>

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

# Activer
. .\.venv\Scripts\Activate.ps1

# Mettre pip à jour et installer dépendances
python -m pip install --upgrade pip
if (Test-Path .\requirements.txt) { pip install -r .\requirements.txt }

# Lancer le script
python .\willkommen_v2.py
