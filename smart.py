#!/usr/bin/env python3
import os
import sys
import json
import re
import importlib.util
import tempfile
import subprocess
from pathlib import Path
from rich import print
from rich.prompt import Prompt

# ----------------------------
# Load or create .env for OpenAI API key
# ----------------------------
ENV_PATH = Path(".env")
if not ENV_PATH.exists():
    ENV_PATH.write_text("OPENAI_API_KEY=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\n")
    print("[yellow]⚠️ .env file created. Add your OpenAI API key and restart.[/yellow]")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Optional: AI integration
try:
    import openai
    if OPENAI_KEY and OPENAI_KEY != "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":
        openai.api_key = OPENAI_KEY
    else:
        print("[yellow]⚠️ OpenAI API key not set. AI features disabled.[/yellow]")
        OPENAI_KEY = None
except ImportError:
    print("[yellow]⚠️ OpenAI library not found. AI features disabled.[/yellow]")
    OPENAI_KEY = None

# ----------------------------
# Globals
# ----------------------------
last_file = None
last_language = None
last_output = None
last_error = None

# ----------------------------
# Language Detection
# ----------------------------
def detect_language_from_file(file_path):
    ext = file_path.suffix.lower()
    if ext == ".py": return "python"
    elif ext == ".js": return "nodejs"
    elif ext == ".java": return "java"
    else: return "unknown"

# ----------------------------
# Dependency Detection
# ----------------------------
def detect_python_dependencies(code):
    deps = set()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            deps.add(line.split()[1].split('.')[0])
        elif line.startswith("from "):
            deps.add(line.split()[1].split('.')[0])
    return list(deps)

def detect_node_dependencies(code):
    return list(set(re.findall(r'require\([\'"](\w+)[\'"]\)', code)))

# ----------------------------
# Folder Dependency Checks
# ----------------------------
def check_python_requirements(folder):
    req_file = Path(folder) / "requirements.txt"
    missing = []
    if req_file.exists():
        with open(req_file) as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        for pkg in packages:
            if importlib.util.find_spec(pkg) is None:
                missing.append(pkg)
    return missing

def check_node_requirements(folder):
    pkg_file = Path(folder) / "package.json"
    missing = []
    if pkg_file.exists():
        with open(pkg_file) as f:
            data = json.load(f)
            dependencies = data.get("dependencies", {})
            for pkg in dependencies:
                if not (Path(folder) / "node_modules" / pkg).exists():
                    missing.append(pkg)
    return missing

# ----------------------------
# Run Project Folder
# ----------------------------
def run_folder_code(folder):
    print("[blue]Running project folder...[/blue]")
    main_py = Path(folder) / "main.py"
    if main_py.exists():
        subprocess.run([sys.executable, str(main_py)])
        return

    pkg_file = Path(folder) / "package.json"
    if pkg_file.exists():
        with open(pkg_file) as f:
            data = json.load(f)
            main_js = data.get("main", "index.js")
            main_path = Path(folder) / main_js
            if main_path.exists():
                subprocess.run(["node", str(main_path)])
                return
            elif (Path(folder) / "index.js").exists():
                subprocess.run(["node", str(Path(folder) / "index.js")])
                return

    print("[yellow]⚠️ Could not detect entry point. Please run manually.[/yellow]")

# ----------------------------
# Folder Setup & Auto-Run
# ----------------------------
def setup_folder(folder):
    python_missing = check_python_requirements(folder)
    node_missing = check_node_requirements(folder)

    if not python_missing and not node_missing:
        print("[green]✅ All dependencies installed! Code should run.[/green]")
        run_folder_code(folder)
        return True

    print("[yellow]⚠️ Missing dependencies detected:[/yellow]")
    for pkg in python_missing:
        print(f"- [blue]{pkg}[/blue] (Python)")
    for pkg in node_missing:
        print(f"- [blue]{pkg}[/blue] (Node.js)")

    choice = Prompt.ask("Install missing dependencies now? (y/n)", choices=["y","n"])
    if choice == "y":
        if python_missing:
            print("[blue]Installing missing Python packages...[/blue]")
            for pkg in python_missing:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
            print("[green]✅ Python dependencies installed.[/green]")
        if node_missing:
            print("[blue]Installing missing Node.js packages...[/blue]")
            subprocess.run(["npm", "install"], cwd=folder, check=True)
            print("[green]✅ Node.js dependencies installed.[/green]")
        print("[green]✅ Folder setup completed.[/green]")
        run_folder_code(folder)
        return True
    else:
        print("[red]Execution blocked until dependencies are installed.[/red]")
        return False

# ----------------------------
# File Setup
# ----------------------------
def setup_python_file(file_path):
    code = file_path.read_text()
    deps = detect_python_dependencies(code)
    missing = [pkg for pkg in deps if importlib.util.find_spec(pkg) is None]
    if not missing:
        print("[green]✅ All Python dependencies are installed.[/green]")
        return
    print(f"[yellow]⚠️ Missing Python dependencies: {missing}[/yellow]")
    choice = Prompt.ask("Install missing packages now? (y/n)", choices=["y","n"])
    if choice == "y":
        for pkg in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
        print("[green]✅ Python setup completed.[/green]")

def setup_node_file(file_path):
    code = file_path.read_text()
    deps = detect_node_dependencies(code)
    if not deps:
        print("[green]✅ No Node.js dependencies detected.[/green]")
        return
    print(f"[yellow]⚠️ Missing Node.js dependencies: {deps}[/yellow]")
    choice = Prompt.ask("Install missing packages now? (y/n)", choices=["y","n"])
    if choice == "y":
        temp_dir = tempfile.mkdtemp()
        print(f"[blue]Creating temporary Node.js project in {temp_dir}[/blue]")
        subprocess.run(["npm", "init", "-y"], cwd=temp_dir, check=True)
        for pkg in deps:
            subprocess.run(["npm", "install", pkg], cwd=temp_dir, check=True)
        print("[green]✅ Node.js setup completed (temporary environment).[/green]")

def run_setup_file(file_path, language):
    if language == "python":
        setup_python_file(file_path)
    elif language == "nodejs":
        setup_node_file(file_path)
    else:
        print("[yellow]⚠️ Setup for this language requires Docker.[/yellow]")

# ----------------------------
# File Execution
# ----------------------------
def run_file(file_path, language):
    global last_output, last_error
    print("[blue]Running file...[/blue]")
    try:
        if language == "python":
            result = subprocess.run([sys.executable, str(file_path)], capture_output=True, text=True)
        elif language == "nodejs":
            result = subprocess.run(["node", str(file_path)], capture_output=True, text=True)
        else:
            print("[yellow]⚠️ Execution requires Docker or manual run.[/yellow]")
            return
        last_output = result.stdout
        last_error = result.stderr
        print_output(result.stdout, result.stderr)
    except Exception as e:
        print(f"[red]Execution failed: {e}[/red]")

def print_output(stdout, stderr):
    print("---------- [green]Output[/green] ----------")
    print(stdout if stdout else "(No output)")
    print("---------- [red]Errors[/red] ----------")
    print(stderr if stderr else "(No errors)")
    print("----------------------------------------")

# ----------------------------
# AI-Powered Fix
# ----------------------------
def ai_fix_file(file_path, language, error_text):
    if not OPENAI_KEY:
        print("[yellow]⚠️ OpenAI API key not set. AI fix disabled.[/yellow]")
        return
    code = file_path.read_text()
    prompt = f"""
You are an AI assistant. I have the following {language} file:

{code}

It produced the following error:

{error_text}

Suggest fixes, missing imports, or dependency installations needed to fix this error.
Provide a concise explanation.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        suggestion = response['choices'][0]['message']['content']
        print(f"[cyan]AI Suggestion:[/cyan]\n{suggestion}")
    except Exception as e:
        print(f"[red]AI request failed: {e}[/red]")

# ----------------------------
# CLI Loop
# ----------------------------
def cli_loop():
    global last_file, last_language, last_error
    print("[cyan]Welcome to Smart File Execution CLI with AI! Type /help for commands.[/cyan]")

    while True:
        command = Prompt.ask(">")

        if command.startswith("/exit"):
            print("[cyan]Goodbye! 👋[/cyan]")
            break

        elif command.startswith("/help"):
            print("""
Available commands:
/file <path>       - Load a code file
/run               - Execute loaded file
/setup             - Check/install dependencies for file
/fix               - AI-powered suggestions for errors
/setup_folder <folder_path> - Check/install folder dependencies & auto-run
/exit              - Quit CLI
/help              - Show this help
            """)

        elif command.startswith("/file"):
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                print("[red]Please provide a file path.[/red]")
                continue
            file_path = Path(parts[1])
            if not file_path.exists():
                print(f"[red]File not found: {file_path}[/red]")
                continue
            last_file = file_path
            last_language = detect_language_from_file(file_path)
            print(f"[green]File loaded: {file_path} (Detected language: {last_language})[/green]")

        elif command.startswith("/setup"):
            if not last_file:
                print("[red]No file loaded. Use /file first.[/red]")
                continue
            run_setup_file(last_file, last_language)

        elif command.startswith("/run"):
            if not last_file:
                print("[red]No file loaded. Use /file first.[/red]")
                continue
            run_file(last_file, last_language)

        elif command.startswith("/fix"):
            if not last_file:
                print("[red]No file loaded. Use /file first.[/red]")
                continue
            if not last_error:
                print("[yellow]No errors detected from last run.[/yellow]")
                continue
            ai_fix_file(last_file, last_language, last_error)

        elif command.startswith("/setup_folder"):
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                print("[red]Please provide a folder path.[/red]")
                continue
            folder = parts[1]
            if not Path(folder).exists():
                print(f"[red]Folder not found: {folder}[/red]")
                continue
            setup_folder(folder)

        else:
            print("[red]Unknown command. Type /help to see commands.[/red]")

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    cli_loop()
