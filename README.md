# Willkommen_v2 — guide d'installation et d'exécution

Ce dossier contient le script `willkommen_v2.py` (générateur multi-langages). Ce README rassemble toutes les commandes pour qu'un utilisateur puisse cloner, installer et lancer le programme facilement.

## Pré-requis
- Python 3.8+ installé (vérifier avec `python --version`)
- Git installé (`git --version`)
- (optionnel) `gh` CLI si tu veux créer le dépôt GitHub depuis la ligne de commande

---

## Installation & exécution (Windows PowerShell)

Ouvre PowerShell dans `c:\hello-world-python\willkommen_v2` puis :

```powershell
# 1) Créer et activer un environnement virtuel local
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Mettre pip à jour et installer les dépendances
python -m pip install --upgrade pip
if (Test-Path .\requirements.txt) { pip install -r .\requirements.txt }

# 3) Lancer le script interactif
python .\willkommen_v2.py

# ou utiliser le script helper qui fait les étapes 1-2 automatiquement
.\run.ps1
```

Si l'exécution des scripts PowerShell est bloquée :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Installation & exécution (Linux / macOS)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
[ -f requirements.txt ] && pip install -r requirements.txt
python willkommen_v2.py
# ou ./run.sh
```

---

## Dépannage rapide
- Si le script réclame `rich` ou `questionary`, installe-les explicitement :

```powershell
pip install rich questionary
```

- Si tu vois une erreur liée à `questionary` sur le style, c'est normal : le script surcharge des paramètres de style.
- Si tu as des erreurs de permission, lance PowerShell en administrateur pour ajuster la politique d'exécution.

---

## Git — initialiser, committer et pousser sur GitHub

1) Initialiser le dépôt local et faire un commit :

```powershell
# depuis c:\hello-world-python\willkommen_v2
git init
git add .
git commit -m "Initial commit: willkommen_v2"
git branch -M main
```

2) Ajouter le remote et pousser (après avoir créé le repo sur GitHub)

Option HTTPS :

```powershell
git remote add origin https://github.com/TON_USER/TON_REPO.git
git push -u origin main
```

Option SSH (si clé configurée) :

```powershell
git remote add origin git@github.com:TON_USER/TON_REPO.git
git push -u origin main
```

Créer et pousser via `gh` :

```powershell
gh auth login
gh repo create TON_USER/TON_REPO --public --source=. --remote=origin --push
```

Après `git push`, les fichiers sont visibles immédiatement sur la page GitHub.

---

## Annuler un `git init` fait au mauvais endroit

Si tu as initialisé Git dans un dossier parent par erreur :

```powershell
# vérifier la racine du repo actuel
git rev-parse --show-toplevel

# sauvegarder (renommer) le dossier .git (méthode sûre)
$root = git rev-parse --show-toplevel
$bakName = ".git.bak.$((Get-Date).ToString('yyyyMMddHHmmss'))"
Rename-Item -LiteralPath (Join-Path $root '.git') -NewName $bakName

# puis initialiser correctement dans ce dossier
Set-Location -Path 'c:\hello-world-python\willkommen_v2'
git init
git add .
git commit -m "Initial commit: willkommen_v2"
git branch -M main
```

Si tu es certain et que tu veux supprimer `.git` définitivement dans le parent :

```powershell
Remove-Item -LiteralPath (Join-Path $root '.git') -Recurse -Force
```

---

## Tester depuis un clone propre

1) Depuis un autre dossier :

```powershell
git clone https://github.com/TON_USER/TON_REPO.git
Set-Location -Path .\TON_REPO
.\run.ps1   # ou activer .venv et pip install -r requirements.txt puis python
```

2) L'utilisateur non technique peut simplement lancer `.
un.ps1` après clonage.

---

## Contenu des fichiers importants
- `requirements.txt` : liste des packages Python nécessaires (`rich`, `questionary`).
- `.gitignore` : ignore `.venv`, `__pycache__`, etc.
- `run.ps1` / `run.sh` : scripts pour créer/activer venv et lancer le script.
- `LICENSE` : MIT par défaut.

---

Si tu veux, je peux :
- remplir automatiquement `requirements.txt` avec des versions précises (en inspectant l'environnement),
- ajouter un petit workflow GitHub Actions pour tester l'installation après chaque push,
- ou initialiser et committer ces fichiers pour toi (je peux exécuter `git add`/`git commit` localement si tu le souhaites).
