#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Create Universal Project - Générateur multi-langages

Mélange les approches de:
- willkommen_modern.py (UI stylée Rich + Questionary, saisie guidée)
- npm_create_vite_clean.py (sélections rapides façon Vite)

Objectif: Créer un squelette de projet quel que soit le langage (sélection),
demander le dossier de destination, le nom du programme, son objectif, le nom
du fichier principal, afficher un résumé, puis scaffolder les fichiers.

Modes:
- Interactif (par défaut)
- Non-interactif via arguments CLI (voir --help)
"""

from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Callable, List, Tuple
from typing import Union

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import questionary
from questionary import Style

# Style (reprend la patte de willkommen_modern)
CUSTOM_STYLE = Style([
    ("qmark", "fg:#06b6d4 bold"),  # '>' au lieu de '?'
    ("question", "bold fg:#ffffff"),
    ("answer", "fg:#06b6d4 bold"),
    ("pointer", "fg:#06b6d4 bold"),
    ("highlighted", "fg:#06b6d4 bold"),
    ("selected", "fg:#d946ef bold"),
    ("separator", "fg:#6c7086"),
    ("instruction", "fg:#94a3b8"),
    ("text", "fg:#ffffff"),
    ("disabled", "fg:#6c7086 italic"),
])

console = Console()

# Surcharge du symbole de question (qmark) pour afficher '>' au lieu de '?'
questionary.prompts.common.PROMPTS_STYLE_OVERRIDES = {"qmark": ">"}
questionary.prompts.common.DEFAULT_QUESTION_PREFIX = ">"


# -----------------------------
# BANNIERE
# -----------------------------
def afficher_banniere() -> None:
    # Utiliser un Panel Rich pour garantir un cadre propre quel que soit le contenu
    title = Text("✨ WILLKOMMEN v2 ✨", style="bold magenta", justify="center")
    subtitle = Text("pour créer n'importe quel fichier", style="bold white", justify="center")

    content = Text.assemble(title, "\n", subtitle)

    panel = Panel(
        content,
        box=box.ROUNDED,
        border_style="cyan",
        padding=(1, 4),
    )

    console.print()
    console.print(panel)
    console.print()


# -----------------------------
# TEMPLATES PAR LANGAGE
# -----------------------------
def tpl_python(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    """Retourne une liste (chemin relatif, contenu) à créer pour Python."""
    # Construire exactement les mêmes 8 lignes que celles utilisées
    # dans la logique interactive pour l'entête. L'édition commencera
    # à la ligne 9 lorsque l'utilisateur ajoutera du contenu.
    header_lines = [
        "",
        "",
        "#!python3",
        "",
        f"# but : {objective}",
        "",
        f"# Bienvenue dans le programme {prog_name}",
        "",
    ]

    main = "\n".join(header_lines) + "\n"

    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
python {filename}
```
"""

    req = "# Ajoutez ici vos dépendances Python (ex: rich==13.7.1)\n"

    return [
        (filename, main),
        ("README.md", readme),
        ("requirements.txt", req),
        (".gitignore", "__pycache__/\n.env\n.venv/\n"),
    ]


def tpl_node_js(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    main = f"""/* {objective} */
console.log("Hello from {prog_name}!");
"""
    package_json = f"""{{
  "name": "{prog_name.lower().replace(' ', '-')}",
  "version": "0.1.0",
  "description": "{objective}",
  "type": "module",
  "main": "{filename}",
  "scripts": {{
    "start": "node {filename}"
  }}
}}
"""
    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
npm install  # si besoin d'ajouter des deps
npm run start
```
"""
    gitignore = "node_modules/\n.DS_Store\n.env\n"
    return [
        (filename, main),
        ("package.json", package_json),
        ("README.md", readme),
        (".gitignore", gitignore),
    ]


def tpl_typescript(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    # TS: placer dans src/ par convention
    ts_main_rel = f"src/{filename}"
    ts_main = f"""// {objective}
export function main(): void {{
  console.log("Hello from {prog_name}!");
}}

if (require.main === module) {{
  main();
}}
"""
    tsconfig = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true
  }
}
"""
    package_json = f"""{{
  "name": "{prog_name.lower().replace(' ', '-')}",
  "version": "0.1.0",
  "description": "{objective}",
  "scripts": {{
    "build": "tsc",
    "start": "node dist/{Path(filename).stem}.js"
  }},
  "devDependencies": {{
    "typescript": "^5.0.0"
  }}
}}
"""
    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
npm install
npm run build
npm run start
```
"""
    gitignore = "node_modules/\ndist/\n.DS_Store\n.env\n"
    return [
        (ts_main_rel, ts_main),
        ("tsconfig.json", tsconfig),
        ("package.json", package_json),
        ("README.md", readme),
        (".gitignore", gitignore),
    ]


def tpl_go(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    # Go: forcer main.go et go.mod
    main = f"""// {objective}
package main

import "fmt"

func main() {{
    fmt.Println("Hello from {prog_name}!")
}}
"""
    gomod = f"""module {prog_name.lower().replace(' ', '-')}

go 1.21
"""
    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
go run .
```
"""
    gitignore = "bin/\n*.exe\n.DS_Store\n"
    return [
        ("main.go", main),
        ("go.mod", gomod),
        ("README.md", readme),
        (".gitignore", gitignore),
    ]


def tpl_rust(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    cargo = f"""[package]
name = "{prog_name.lower().replace(' ', '-')}"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
    main = f"""// {objective}
fn main() {{
    println!("Hello from {prog_name}!");
}}
"""
    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
cargo run
```
"""
    return [
        ("Cargo.toml", cargo),
        ("src/main.rs", main),
        ("README.md", readme),
        (".gitignore", "target/\n.DS_Store\n"),
    ]


def tpl_csharp(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    csproj_name = prog_name.replace(" ", ".")
    csproj = f"""<Project Sdk=\"Microsoft.NET.Sdk\">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
"""
    main = f"""// {objective}
using System;

class Program {{
    static void Main(string[] args) {{
        Console.WriteLine("Hello from {prog_name}!");
    }}
}}
"""
    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
dotnet build
dotnet run
```
"""
    return [
        (f"{csproj_name}.csproj", csproj),
        ("Program.cs", main),
        ("README.md", readme),
        (".gitignore", "bin/\nobj/\n.DS_Store\n"),
    ]


def tpl_java(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    # Projet simple sans build tool
    main = f"""// {objective}
public class Main {{
    public static void main(String[] args) {{
        System.out.println("Hello from {prog_name}!");
    }}
}}
"""
    readme = f"""# {prog_name}

Objectif: {objective}

## Lancer

```bash
javac Main.java && java Main
```
"""
    return [
        ("Main.java", main),
        ("README.md", readme),
        (".gitignore", ".DS_Store\n"),
    ]


def tpl_html(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    index = f"""<!doctype html>
<html lang=\"fr\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{prog_name}</title>
    <link rel=\"stylesheet\" href=\"style.css\" />
  </head>
  <body>
    <h1>{prog_name}</h1>
    <p>{objective}</p>
    <script src=\"script.js\"></script>
  </body>
</html>
"""
    style = """body{font-family:system-ui,Arial,sans-serif;margin:2rem}h1{color:#6d28d9}
"""
    script = """console.log('Hello from static site!');
"""
    readme = f"""# {prog_name}

Objectif: {objective}

Ouvrez `index.html` dans votre navigateur.
"""
    return [
        ("index.html", index),
        ("style.css", style),
        ("script.js", script),
        ("README.md", readme),
        (".gitignore", ".DS_Store\n"),
    ]


def tpl_markdown(prog_name: str, objective: str, filename: str) -> List[Tuple[str, str]]:
    date_creation = __import__('datetime').date.today().strftime('%d %B %Y')
    date_modification = __import__('datetime').date.today().strftime('%d %B %Y')
    main_md = f"""# {prog_name}

**Objectif:** {objective}

---

*Créé le: {date_creation}*  
*Dernière modification: {date_modification}*
"""
    
    readme = f"""# {prog_name}

Objectif: {objective}

## Fichiers

- `{filename}` : Document principal
- `assets/` : Dossier pour images et ressources

## Visualisation

Ouvrez `{filename}` dans votre éditeur Markdown ou utilisez un visualiseur comme:
- VS Code (avec prévisualisation intégrée)
- [Markdown Viewer](https://markdownlivepreview.com/)
- Obsidian, Typora, etc.
"""
    
    gitignore = ".DS_Store\n*.tmp\n"
    
    assets_readme = "# Assets\n\nPlacez ici vos images et fichiers de ressources.\n"
    
    return [
        (filename, main_md),
        ("README.md", readme),
        (".gitignore", gitignore),
        ("assets/README.md", assets_readme),
    ]


LANGUAGES: Dict[str, Dict[str, object]] = {
    "python": {
        "label": "Python 🐍",
        "default_file": "main.py",
        "scaffold": tpl_python,
    },
    "javascript": {
        "label": "JavaScript (Node) 🟨",
        "default_file": "index.js",
        "scaffold": tpl_node_js,
    },
    "typescript": {
        "label": "TypeScript 🟦",
        "default_file": "index.ts",
        "scaffold": tpl_typescript,
    },
    "go": {
        "label": "Go 🐹",
        "default_file": "main.go",
        "scaffold": tpl_go,
    },
    "rust": {
        "label": "Rust 🦀",
        "default_file": "src/main.rs",
        "scaffold": tpl_rust,
    },
    "csharp": {
        "label": "C# (.NET) ♯",
        "default_file": "Program.cs",
        "scaffold": tpl_csharp,
    },
    "java": {
        "label": "Java ☕",
        "default_file": "Main.java",
        "scaffold": tpl_java,
    },
    "html": {
        "label": "HTML/CSS/JS 🌐",
        "default_file": "index.html",
        "scaffold": tpl_html,
    },
    "markdown": {
        "label": "Markdown 📝",
        "default_file": "document.md",
        "scaffold": tpl_markdown,
    },
}


# -----------------------------
# UTILITAIRES
# -----------------------------
def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_files(base: Path, files: List[Tuple[str, str]]) -> None:
    for rel, content in files:
        target = base / rel
        ensure_dir(target.parent)
        target.write_text(content, encoding="utf-8")


def afficher_contenu_fichier(file_path: Path) -> None:
    """Affiche le contenu d'un fichier texte dans un Panel Rich."""
    try:
        contenu = file_path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"\n[red]Erreur lors de la lecture de '{file_path}': {e}[/red]\n")
        return

    console.print()
    console.print(Panel(
        contenu,
        title=f"📄 {file_path}",
        border_style="cyan",
        box=box.ROUNDED,
    ))
    console.print()


def ajouter_contenu(file_path: Path) -> None:
    """Ajoute du contenu (ligne par ligne) à la fin d'un fichier jusqu'à saisir FIN."""
    console.print("\n💡 [dim]Entrez votre texte (ligne par ligne). Tapez '[cyan]FIN[/cyan]' pour terminer.[/dim]")
    lignes: List[str] = []
    while True:
        try:
            ligne = input("│ ")
        except EOFError:
            break
        if ligne.strip().upper() == "FIN":
            break
        lignes.append(ligne)

    if not lignes:
        console.print("[yellow]Aucune ligne à ajouter.[/yellow]")
        return

    try:
        with file_path.open("a", encoding="utf-8") as f:
            f.write("\n".join(lignes) + "\n")
        console.print("✅ [cyan italic]Contenu ajouté avec succès ![/cyan italic]\n")
    except Exception as e:
        console.print(f"❌ [red]Erreur lors de l'écriture: {e}[/red]\n")



def menu_post_creation(primary_file: Path) -> None:
    """Menu interactif post-création: ajouter, afficher, terminer."""
    while True:
        choix = questionary.select(
            "Que voulez-vous faire ?",
            choices=[
                "✏️  Ajouter du contenu",
                "👀 Afficher le contenu",
                "✅ Terminer",
            ],
            style=CUSTOM_STYLE,
            qmark=">",
        ).ask()

        if not choix:
            # Considérer comme Terminer si annulation
            return
        if "Ajouter" in choix:
            ajouter_contenu(primary_file)
        elif "Afficher" in choix:
            afficher_contenu_fichier(primary_file)
        elif "Terminer" in choix:
            # Retourner pour permettre à l'appelant de proposer l'ouverture
            return


def open_path_target(path: Path, target: str = "file") -> None:
    """Ouvre un fichier ou dossier avec l'éditeur par défaut.

    target: 'file' pour ouvrir le fichier, 'folder' pour ouvrir le dossier.
    Préfère `code` (VS Code) si présent dans le PATH, sinon utilise
    os.startfile (Windows) ou les commandes `open` / `xdg-open` selon la plateforme.
    """
    try:
        # Priorité : VS Code CLI si disponible
        from shutil import which

        if which("code"):
            if target == "file":
                os.system(f"code " + f'"{str(path)}"')
            else:
                os.system(f"code " + f'"{str(path)}"')
            return

        if sys.platform.startswith("win"):
            os.startfile(str(path))
        elif sys.platform == "darwin":
            os.system(f"open " + f'"{str(path)}"')
        else:
            # Linux / other Unix
            os.system(f"xdg-open " + f'"{str(path)}"')
    except Exception:
        # Silencieux en cas d'échec
        pass


def find_hello_world_root_candidates(max_items: int = 30) -> List[Path]:
    """Retourne des dossiers candidats à la racine du disque courant dont le nom
    commence par 'hello-world-'. Si rien n'est trouvé, retourne une liste vide.

    - Limite le nombre d'éléments pour éviter des listes trop longues.
    - Tolère les erreurs de permission.
    """
    try:
        anchor = Path.cwd().anchor or os.path.splitdrive(str(Path.cwd()))[0] + os.sep
        root = Path(anchor)
        if not root.exists():
            return []
        items: List[Path] = []
        for p in root.iterdir():
            try:
                if p.is_dir() and p.name.lower().startswith("hello-world-"):
                    items.append(p)
            except Exception:
                # Ignore dossiers inaccessibles
                continue
        items.sort(key=lambda x: x.name.lower())
        return items[:max_items]
    except Exception:
        return []


def resume_panel(lang_key: str, dest_dir: Path, prog_name: str, objective: str, filename: str) -> Panel:
    label = LANGUAGES[lang_key]["label"]
    return Panel(
        f"[bold magenta]Langage :[/bold magenta] [cyan]{label}[/cyan]\n"
        f"[bold magenta]Dossier :[/bold magenta] [cyan]{dest_dir}[/cyan]\n"
        f"[bold magenta]Programme :[/bold magenta] [cyan]{prog_name}[/cyan]\n"
        f"[bold magenta]Objectif :[/bold magenta] [cyan]{objective}[/cyan]\n"
        f"[bold magenta]Fichier principal :[/bold magenta] [cyan]{filename}[/cyan]",
        title="📋 Résumé",
        border_style="magenta",
        box=box.ROUNDED,
    )


# -----------------------------
# INTERACTIF
# -----------------------------
def run_interactive() -> int:
    afficher_banniere()

    # 1) Sélection du langage
    choices = [questionary.Choice(LANGUAGES[k]["label"], value=k) for k in LANGUAGES]
    lang_key = questionary.select(
        "Sélectionnez le langage du programme:",
        choices=choices,
        style=CUSTOM_STYLE,
        qmark=">",
    ).ask()
    if not lang_key:
        console.print("[red]Opération annulée.[/red]")
        return 0

    # 2) Dossier de destination
    # 2) Dossier de destination (liste des dossiers 'hello-world-*' à la racine)
    candidates = find_hello_world_root_candidates()
    dest_str: Union[str, None]
    if candidates:
        dir_choices = [questionary.Choice(str(p), value=str(p)) for p in candidates]
        dir_choices.append(questionary.Choice("Autre chemin...", value="__custom__"))
        picked = questionary.select(
            "Dans quel dossier créer le projet?",
            choices=dir_choices,
            style=CUSTOM_STYLE,
            qmark=">",
        ).ask()
        if not picked:
            console.print("[yellow]Opération annulée.[/yellow]")
            return 0
        if picked == "__custom__":
            default_dir = str(Path.cwd())
            dest_str = questionary.text(
                "Entrez le chemin du dossier de destination:",
                default=default_dir,
                style=CUSTOM_STYLE,
                qmark=">",
            ).ask()
        else:
            dest_str = picked
    else:
        # Fallback: saisie libre si aucun dossier candidat trouvé
        default_dir = str(Path.cwd())
        dest_str = questionary.path(
            "Dans quel dossier créer le projet?",
            default=default_dir,
            only_directories=True,
            style=CUSTOM_STYLE,
            qmark=">",
        ).ask()
    if not dest_str:
        console.print("[yellow]Opération annulée.[/yellow]")
        return 0
    dest_dir = Path(dest_str)
    
    # Créer le dossier de destination s'il n'existe pas
    try:
        ensure_dir(dest_dir)
    except Exception as e:
        console.print(f"[red]Erreur lors de la création du dossier {dest_dir}: {e}[/red]")
        return 1

    # 3) Nom du programme
    prog_name = questionary.text(
        "Nom du programme:",
        style=CUSTOM_STYLE,
        qmark=">",
    ).ask()
    if not prog_name:
        console.print("[yellow]Opération annulée.[/yellow]")
        return 0

    # 4) Objectif
    objective = questionary.text(
        "Objectif du programme:",
        style=CUSTOM_STYLE,
        qmark=">",
    ).ask()
    if not objective:
        console.print("[yellow]Opération annulée.[/yellow]")
        return 0

    # 5) Nom du fichier principal (proposer un défaut adapté)
    default_file = LANGUAGES[lang_key]["default_file"]  # type: ignore[index]
    filename = questionary.text(
        "Nom du fichier principal:",
        default=default_file,
        style=CUSTOM_STYLE,
        qmark=">",
    ).ask()
    if not filename:
        console.print("[yellow]Opération annulée.[/yellow]")
        return 0

    # 6) Pour Markdown: choix entre fichier seul ou dossier complet
    markdown_mode = "folder"  # par défaut
    if lang_key == "markdown":
        choice = questionary.select(
            "Comment créer le fichier Markdown ?",
            choices=[
                "📁 Créer un dossier avec ressources (README, assets/)",
                "📄 Créer uniquement le fichier Markdown",
            ],
            style=CUSTOM_STYLE,
            qmark=">",
        ).ask()
        if not choice:
            console.print("[yellow]Opération annulée.[/yellow]")
            return 0
        markdown_mode = "folder" if "dossier" in choice else "single"

    # Résumé + confirmation
    console.print()
    console.print(resume_panel(lang_key, dest_dir, prog_name, objective, filename))
    console.print()

    if not questionary.confirm("Confirmer la création de ce projet?", default=True, style=CUSTOM_STYLE, qmark=">").ask():
        console.print("[yellow]Création annulée.[/yellow]")
        return 0

    # Scaffold
    # Demander si on veut créer un dossier pour le projet ou uniquement le fichier principal
    create_mode = questionary.select(
        "Voulez-vous créer un dossier pour ce projet ou uniquement le fichier principal ?",
        choices=[
            "📁 Créer un dossier (tous les fichiers du template)",
            "📄 Créer uniquement le fichier principal",
        ],
        style=CUSTOM_STYLE,
        qmark=">",
    ).ask()

    if not create_mode:
        console.print("[yellow]Opération annulée.[/yellow]")
        return 0

    if create_mode.startswith("📄"):
        # Mode fichier seul: on crée seulement le fichier principal dans dest_dir
        project_folder = dest_dir
        # Obtenir le contenu principal depuis le template (si disponible)
        template_files = LANGUAGES[lang_key]["scaffold"](prog_name, objective, filename)  # type: ignore[index]
        primary_rel, primary_content = template_files[0]

        # Si le fichier principal est un fichier Python, respecter l'entête demandé
        if Path(filename).suffix == ".py":
            # Construire un en-tête de 8 lignes; l'édition commence à la ligne 9
            header_lines = [
                "",
                "",
                "#!python3",
                "",
                f"# but : {objective}",
                "",
                f"# Bienvenue dans le programme {prog_name}",
                "",
            ]
            primary_content = "\n".join(header_lines) + "\n"
        else:
            # Pour d'autres langages, on utilise le contenu principal du template
            # (déjà dans primary_content)
            pass

        files = [(filename, primary_content)]
    else:
        # Mode dossier: créer un répertoire projet et écrire tous les fichiers du template
        project_folder = dest_dir / prog_name.lower().replace(" ", "-")
        ensure_dir(project_folder)
        files = LANGUAGES[lang_key]["scaffold"](prog_name, objective, filename)  # type: ignore[index]

    write_files(project_folder, files)
    console.print(Panel(f"✅ Projet [bold]{prog_name}[/bold] créé dans [cyan]{project_folder}[/cyan]", border_style="green", box=box.ROUNDED))

    # Déterminer le fichier principal (1er élément retourné par le template)
    try:
        primary_rel = files[0][0]
        primary_file = project_folder / primary_rel

        # D'abord proposer le menu post-création (ajout/affichage/terminer)
        if primary_file.exists():
            menu_post_creation(primary_file)

            # Une fois l'utilisateur a choisi Terminer, lui proposer d'ouvrir le projet
            open_choice = questionary.select(
                "Souhaitez-vous ouvrir le projet maintenant ?",
                choices=[
                    "📁 Ouvrir le dossier du projet",
                    "📄 Ouvrir le fichier principal",
                    "❌ Ne rien ouvrir",
                ],
                style=CUSTOM_STYLE,
                qmark=">",
            ).ask()

            if open_choice and "dossier" in open_choice.lower():
                open_path_target(project_folder, target="folder")
            elif open_choice and "fichier" in open_choice.lower():
                open_path_target(primary_file, target="file")
    except Exception:
        # Si problème, ignorer silencieusement
        pass

    console.print("✨ [cyan italic]À vous de jouer ![/cyan italic]\n")
    return 0


# -----------------------------
# CLI (non-interactif)
# -----------------------------
def run_cli(args: argparse.Namespace) -> int:
    # validations minimales
    if args.lang not in LANGUAGES:
        console.print(f"[red]Langage inconnu:[/red] {args.lang}\nChoix possibles: {', '.join(LANGUAGES.keys())}")
        return 2
    if not args.name:
        console.print("[red]--name est requis en mode non-interactif[/red]")
        return 2
    if not args.objective:
        console.print("[red]--objective est requis en mode non-interactif[/red]")
        return 2
    dest_dir = Path(args.dir or Path.cwd())
    filename = args.filename or LANGUAGES[args.lang]["default_file"]  # type: ignore[index]

    console.print(resume_panel(args.lang, dest_dir, args.name, args.objective, filename))
    if not args.yes:
        console.print("[yellow]Ajoutez --yes pour confirmer automatiquement.[/yellow]")
        return 0

    project_folder = dest_dir / args.name.lower().replace(" ", "-")
    ensure_dir(project_folder)
    files = LANGUAGES[args.lang]["scaffold"](args.name, args.objective, filename)  # type: ignore[index]
    write_files(project_folder, files)

    console.print(Panel(f"✅ Projet [bold]{args.name}[/bold] créé dans [cyan]{project_folder}[/cyan]", border_style="green", box=box.ROUNDED))
    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Générateur de projet multi-langages")
    sub = p.add_subparsers(dest="mode")

    # mode interactif (par défaut si aucun subcmd)
    sub.add_parser("interactive", help="Lancer l'assistant interactif")

    # mode non-interactif
    c = sub.add_parser("new", help="Créer un projet en mode non-interactif")
    c.add_argument("--lang", required=True, choices=list(LANGUAGES.keys()), help="Langage à utiliser")
    c.add_argument("--dir", help="Dossier de destination (défaut: cwd)")
    c.add_argument("--name", required=True, help="Nom du programme/projet")
    c.add_argument("--objective", required=True, help="Objectif du programme")
    c.add_argument("--filename", help="Nom du fichier principal (défaut selon langage)")
    c.add_argument("--yes", action="store_true", help="Confirmer sans poser de question")
    c.add_argument("--file-only", action="store_true", help="Créer uniquement le fichier principal (pas de dossier)")

    # Pas de subcmd => interactif
    if len(argv) == 0:
        return argparse.Namespace(mode="interactive")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    args = parse_args(argv)

    if args.mode == "interactive":
        return run_interactive()
    elif args.mode == "new":
        return run_cli(args)
    else:
        # fallback interactif
        return run_interactive()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Opération interrompue par l'utilisateur.[/yellow]\n")
        raise SystemExit(1)
