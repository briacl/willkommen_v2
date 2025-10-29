#!/usr/bin/env bash
# run.sh - script d'aide pour Linux/macOS (robuste pour macOS)
set -euo pipefail

# Crée le venv seulement s'il n'existe pas, en préférant python3
if [ ! -d ".venv" ]; then
	if command -v python3 >/dev/null 2>&1; then
		python3 -m venv .venv
	elif command -v python >/dev/null 2>&1; then
		python -m venv .venv
	else
		echo "Python 3 introuvable. Installez Python 3 et réessayez." >&2
		exit 1
	fi
fi

# Utiliser le Python du venv directement (plus robuste que l'activation dans des shells non interactifs)
VENV_PY=".venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
	# fallback si l'exécutable s'appelle python3
	if [ -f ".venv/bin/python3" ]; then
		VENV_PY=".venv/bin/python3"
	fi
fi

"$VENV_PY" -m pip install --upgrade pip
if [ -f requirements.txt ]; then
	"$VENV_PY" -m pip install -r requirements.txt
fi

# Lancer le script principal avec le Python du venv
"$VENV_PY" willkommen_v2.py "$@"
