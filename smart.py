#!/usr/bin/env python3
import os
import sys
import re
import webbrowser
import importlib.util
import subprocess
from pathlib import Path
from rich import print
from rich.prompt import Prompt
from dotenv import load_dotenv
from openai import OpenAI

# ----------------------------
# Environment Setup
# ----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

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
def detect_language_from_file(file_path: Path):
    ext = file_path.suffix.lower()
    if ext == ".py":
        return "python"
    elif ext == ".js":
        return "nodejs"
    elif ext == ".java":
        return "java"
    else:
        return "unknown"

# ----------------------------
# Dependency Detection
# ----------------------------
def detect_python_dependencies(code: str):
    deps = set()
    for line in code.splitlines():
        line = line.strip()
        if line.startswith("import "):
            deps.add(line.split()[1].split('.')[0])
        elif line.startswith("from "):
            deps.add(line.split()[1].split('.')[0])
    return list(deps)

def detect_node_dependencies(code: str):
    return list(set(re.findall(r'require\([\'"](\w+)[\'"]\)', code)))

# ----------------------------
# AI-Powered Fix (File Only)
# ----------------------------
def ai_fix_file(file_path: Path, language: str, error_text: str):
    if not OPENAI_API_KEY:
        print("[yellow]⚠️ OpenAI API key not set. AI fix disabled.[/yellow]")
        return
    if not file_path.exists() or not file_path.is_file():
        print(f"[red]File not found: {file_path}[/red]")
        return

    code = file_path.read_text(encoding="utf-8")

    prompt = f"""
You are an AI assistant. I have the following {language} file:

{code}

It produced the following error:

{error_text}

Suggest fixes, missing imports, or dependency installations needed to fix this error.
Provide a concise explanation.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3   )
        suggestion = response.choices[0].message.content
        print(f"[cyan]AI Suggestion:[/cyan]\n{suggestion}")

    except Exception as e:
        print(f"[red]AI request failed: {e}[/red]")

# ----------------------------
# File Setup
# ----------------------------
BUILTIN_MODULES = {
    "os", "sys", "json", "asyncio", "subprocess", "re", "math", "time",
    "pathlib", "typing", "logging", "itertools", "functools", "datetime",
    "unittest", "argparse", "shutil", "http", "io", "random", "string",}

def setup_python_file(file_path: Path):
    code = file_path.read_text(encoding="utf-8")
    deps = detect_python_dependencies(code)
    deps = [pkg for pkg in deps if pkg not in BUILTIN_MODULES]
    missing = [pkg for pkg in deps if importlib.util.find_spec(pkg) is None]

    if not missing:
        print("[green]✅ All Python dependencies are installed.[/green]")
        return
    print(f"[yellow]⚠️ Missing Python dependencies: {missing}[/yellow]")
    print(f"[cyan]👉 To install manually: pip install {' '.join(missing)}[/cyan]")

def setup_node_file(file_path: Path):
    code = file_path.read_text(encoding="utf-8")
    deps = detect_node_dependencies(code)
    if not deps:
        print("[green]✅ No Node.js dependencies detected.[/green]")
        return
    print(f"[yellow]⚠️ Detected Node.js dependencies: {deps}[/yellow]")
    print("[cyan]👉 To install manually: npm install <package_name>[/cyan]")

def run_setup_file(file_path: Path, language: str):
    if language == "python":
        setup_python_file(file_path)
    elif language == "nodejs":
        setup_node_file(file_path)
    else:
        print("[yellow]⚠️ Setup for this language requires Docker/manual config.[/yellow]")

# ----------------------------
# File Execution
# ----------------------------
def print_output(stdout: str, stderr: str):
    if stdout.strip():
        print(f"[green]Output:[/green]\n{stdout}")
    if stderr.strip():
        print(f"[red]Error:[/red]\n{stderr}")

def run_file(file_path: Path, language: str):
    global last_output, last_error
    print("[blue]Running file...[/blue]")
    try:
        if language == "python":
            result = subprocess.run([sys.executable, str(file_path)], capture_output=True, text=True)
        elif language == "nodejs":
            result = subprocess.run(["node", str(file_path)], capture_output=True, text=True)
        elif language == "java":
            result = subprocess.run(["java", str(file_path)], capture_output=True, text=True)
        elif file_path.suffix.lower() in [".html", ".htm"]:
            print(f"[green]Opening HTML file in default browser: {file_path}[/green]")
            webbrowser.open(f"file://{file_path.resolve()}")
            last_output = f"Opened {file_path} in browser"
            last_error = ""
            return
        else:
            print("[yellow]⚠️ Execution requires Docker or manual run.[/yellow]")
            last_output = ""
            last_error = ""
            return

        last_output = result.stdout
        last_error = result.stderr
        if result.returncode != 0 and not last_error and last_output:
            last_error = last_output
        print_output(last_output, last_error)

    except Exception as e:
        print(f"[red]Execution failed: {e}[/red]")
        last_output = ""
        last_error = str(e)

# ----------------------------
# Code Optimization Suggestions
# ----------------------------
def optimize_file(file_path: Path, language: str):
    if not file_path.exists():
        print(f"[red]File not found: {file_path}[/red]")
        return
    code = file_path.read_text(encoding="utf-8")
    prompt = f"""
You are an AI code optimization assistant. Analyze the following {language} file:

{code}

Suggest improvements to make the code cleaner, faster, or more Pythonic/idiomatic.
Highlight unused imports, redundant code, or long functions.
Provide a concise optimization plan.
"""
    if not OPENAI_API_KEY:
        print("[yellow]⚠️ OpenAI API key not set. Optimization disabled.[/yellow]")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3 )
        suggestion = response.choices[0].message.content
        print(f"[cyan]Optimization Suggestions:[/cyan]\n{suggestion}")
    except Exception as e:
        print(f"[red]AI optimization failed: {e}[/red]")



def search_codebase(query: str, directory: Path = Path(".")):
    if not directory.exists() or not directory.is_dir():
        print(f"[red]Directory not found: {directory}[/red]")
        return
    print(f"[blue]Searching for '{query}' in {directory}...[/blue]")
    for file_path in directory.rglob("*.*"):
        if file_path.suffix.lower() not in [".py",".js",".java",".txt",".md"]:
            continue
        try:
            for i, line in enumerate(file_path.read_text(errors="ignore").splitlines(), 1):
                if query in line:
                    print(f"[green]{file_path}:{i}[/green] {line.strip()}")
        except Exception as e:
            print(f"[yellow]Cannot read {file_path}: {e}[/yellow]")
def doc_lookup(query: str):
    """AI-powered documentation lookup for a given programming term or function."""
    if not OPENAI_API_KEY:
        return print("[yellow]⚠️ OpenAI API key not set. Documentation lookup disabled.[/yellow]")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": (
                f"You are a programming documentation assistant.\n"
                f"Provide clear, concise explanation, usage, and examples for: {query}\n"
                "Include Python, JavaScript, or Java examples if applicable.")}],
            temperature=0.3)
        explanation = response.choices[0].message.content
        print(f"[cyan]Documentation for '{query}':[/cyan]\n{explanation}")

    except Exception as e:
        print(f"[red]AI documentation lookup failed: {e}[/red]")


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
            print("""Available commands:
/file <path>   - Load a code file
/run           - Execute loaded file
/setup         - Suggest setup instructions for file
/fix           - AI-powered suggestions for errors
/optimize      - AI-powered code optimization suggestions
/exit          - Quit CLI  /doc <query>   - AI-powered documentation lookup /search <query> - Search codebase for query
/help          - Show this help """)

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
            if not last_error or not last_error.strip():
                print("[yellow]No captured error. Run /run first to generate errors.[/yellow]")
                continue
            ai_fix_file(last_file, last_language, last_error)

        elif command.startswith("/optimize"):
            if not last_file:
                print("[red]No file loaded. Use /file first.[/red]")
                continue
            optimize_file(last_file, last_language)
        elif command.startswith("/search"):
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                print("[red]Please provide a search query.[/red]")
                continue
            query = parts[1]
            search_codebase(query)
        elif command.startswith("/doc"):
            parts = command.split(maxsplit=1)
            if len(parts) < 2:
                 print("[red]Please provide a documentation query.[/red]")
                 continue
            
            query = parts[1]
            doc_lookup(query)
        else: print("[yellow]Unknown command. Type /help for options.[/yellow]")

# ----------------------------
# Entrypoint
# ----------------------------
if __name__ == "__main__":cli_loop()
