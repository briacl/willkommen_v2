<#
setup.ps1 - Configure l'environnement pour `willkommen_v2`.

Usage: ouvrir PowerShell dans le dossier et exécuter `.uild.ps1` ou `.
un.ps1` qui invoque setup si nécessaire.

Ce script :
- vérifie la présence de Python 3
- crée un venv `.venv`
- met pip à jour
- installe `requirements.txt`
#>

function Find-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) { return 'py -3' }
    if (Get-Command python -ErrorAction SilentlyContinue) { return 'python' }
    return $null
}

$pythonCmd = Find-Python
if (-not $pythonCmd) {
    Write-Error "Aucun interpréteur Python trouvé dans le PATH. Installez Python 3.8+ depuis https://www.python.org/ et cochez 'Add to PATH'."
    exit 1
}

if (-not (Test-Path .venv)) {
    Write-Host "Création de l'environnement virtuel (.venv)..."
    & $pythonCmd -m venv .venv
} else {
    Write-Host ".venv existe déjà — vérification rapide..."
}

# pip via le python du venv
$venvPython = Join-Path -Path (Get-Item .venv).FullName -ChildPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Le binaire Python du venv est introuvable: $venvPython"
    exit 1
}

Write-Host "Mise à jour de pip et installation des dépendances..."
& $venvPython -m pip install --upgrade pip
if (Test-Path .\requirements.txt) {
    & $venvPython -m pip install -r .\requirements.txt
} else {
    Write-Host "Aucun requirements.txt trouvé — rien à installer."
}

Write-Host "Configuration terminée. Pour lancer le programme : .\run.ps1 ou .\run.bat"
