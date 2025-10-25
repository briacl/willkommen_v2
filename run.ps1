<#
run.ps1 - Crée un venv local .venv, installe les dépendances et lance `willkommen_v2.py`.
Usage: Ouvrir PowerShell dans ce dossier et exécuter `.
un.ps1`
#>

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    $ArgsToPass
)

# run.ps1 - helper: crée un .venv si nécessaire, installe les dépendances et lance le script

function Find-Python {
    # Préfère le launcher py -3 si disponible, sinon python
    if (Get-Command py -ErrorAction SilentlyContinue) { return 'py -3' }
    if (Get-Command python -ErrorAction SilentlyContinue) { return 'python' }
    return $null
}

$pythonCmd = Find-Python
if (-not $pythonCmd) {
    Write-Error "Aucun interpréteur Python trouvé dans le PATH. Installez Python 3.8+ et réessayez."
    exit 1
}

# Si aucun venv, appelle setup.ps1 pour créer et installer les dépendances
if (-not (Test-Path .venv)) {
    if (Test-Path .\setup.ps1) {
        Write-Host ".venv introuvable — exécution de .\setup.ps1 pour préparer l'environnement..."
        try {
            & .\setup.ps1
        } catch {
            Write-Error "Échec de setup.ps1 : $_"
            exit 1
        }
    } else {
        # fallback : créer venv localement
        & $pythonCmd -m venv .venv
    }
}

# Utiliser directement l'exécutable du venv pour éviter les problèmes d'activation
$venvPython = Join-Path -Path (Get-Item .venv).FullName -ChildPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Impossible de trouver $venvPython. Le venv semble corrompu."
    exit 1
}

# Installer requirements si nécessaire
if (Test-Path .\requirements.txt) {
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r .\requirements.txt
}

# Lancer le script principal en transmettant les arguments
& $venvPython .\willkommen_v2.py @ArgsToPass
