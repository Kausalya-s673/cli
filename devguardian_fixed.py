#!/usr/bin/env python3
"""
DevGuardian - Optimized CLI tool for developer guidance with DeepSeek AI
FIXED VERSION - Resolves AI response issues
"""

import os
import sys
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import requests
import openai
import asyncio

class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


def print_colored(msg, color=Colors.RESET): 
    print(f"{color}{msg}{Colors.RESET}")

def print_success(msg): 
    print_colored(f"✅ {msg}", Colors.GREEN)

def print_warning(msg): 
    print_colored(f"⚠️  {msg}", Colors.YELLOW)

def print_error(msg): 
    print_colored(f"❌ {msg}", Colors.RED)

def print_info(msg): 
    print_colored(f"ℹ️  {msg}", Colors.CYAN)


class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            print("✅ OpenAI API key loaded successfully")
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            print("⚠️ No OpenAI API key found. AI features disabled.")
            self.client = None

    async def ask_ai(self, prompt: str, sys_prompt="You are a helpful developer assistant.", max_tokens=400) -> str:
        if not self.client:
            return """🔑 OpenAI API key not configured!

To enable AI features:
1. Get your OpenAI API key from: https://platform.openai.com/account/api-keys
2. Set your environment variable: export OPENAI_API_KEY=your_actual_key_here
3. Or add it to your .env file: OPENAI_API_KEY=your_actual_key_here
"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.2
            )
            return response.choices[0].message.content.strip() if response.choices else ""
        except Exception as e:
            return f"❌ AI request failed: {str(e)}"


# Example usage
async def main():
    client = OpenAIClient()
    answer = await client.ask_ai("Explain the async/await concept in Python in simple terms.")
    print(answer)

# Run it
asyncio.run(main())

class DocumentChecker:
    def __init__(self, path):
        self.path = Path(path)

    def check_readme(self) -> Dict:
        patterns = ['README.md', 'README.rst', 'README.txt', 'readme.md']
        for p in patterns:
            readme = self.path / p
            if readme.exists():
                try:
                    content = readme.read_text(encoding='utf-8', errors='ignore')
                    words = len(content.split())
                    sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
                    expected = ['installation', 'usage', 'license']
                    missing = [s for s in expected if not any(s.lower() in sec.lower() for sec in sections)]
                    score = min(100, (20 if True else 0) + (20 if words >= 200 else 10 if words >= 100 else 0) + 
                              (40 * (len(expected) - len(missing)) // len(expected)) + (20 if '[![' in content else 0))
                    return {'exists': True, 'file': p, 'score': score, 'missing': missing, 'words': words}
                except:
                    pass
        return {'exists': False, 'file': None, 'score': 0, 'missing': ['installation', 'usage', 'license'], 'words': 0}

    def check_license(self) -> Dict:
        patterns = ['LICENSE', 'LICENSE.md', 'license', 'license.txt']
        for p in patterns:
            if (self.path / p).exists():
                return {'exists': True, 'file': p}
        return {'exists': False, 'file': None}


class TodoTracker:
    def __init__(self, path):
        self.path = Path(path)
        self.patterns = {
            'BUG': [r'#\s*BUG:?\s*(.+)', r'//\s*BUG:?\s*(.+)'],
            'FIXME': [r'#\s*FIXME:?\s*(.+)', r'//\s*FIXME:?\s*(.+)'],
            'TODO': [r'#\s*TODO:?\s*(.+)', r'//\s*TODO:?\s*(.+)'],
            'HACK': [r'#\s*HACK:?\s*(.+)', r'//\s*HACK:?\s*(.+)']
        }
        self.extensions = ['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.php', '.rb']

    def find_todos(self) -> List[Dict]:
        todos = []
        for ext in self.extensions:
            for file_path in list(self.path.rglob(f'*{ext}'))[:50]:
                if any(ex in str(file_path) for ex in ['.git', 'node_modules', '__pycache__']):
                    continue
                try:
                    lines = file_path.read_text(encoding='utf-8', errors='ignore').split('\n')
                    for line_num, line in enumerate(lines, 1):
                        for todo_type, patterns in self.patterns.items():
                            for pattern in patterns:
                                for match in re.finditer(pattern, line, re.IGNORECASE):
                                    text = match.group(1).strip() if match.groups() else match.group(0).strip()
                                    if text:
                                        todos.append({'type': todo_type, 'text': text, 'file': str(file_path), 
                                                    'line': line_num, 'priority': {'BUG': 1, 'FIXME': 2, 'TODO': 3, 'HACK': 4}[todo_type]})
                except:
                    continue
        return sorted(todos, key=lambda x: (x['priority'], x['file']))

    def get_summary(self, todos) -> Dict:
        by_type = {}
        for todo in todos:
            by_type[todo['type']] = by_type.get(todo['type'], 0) + 1
        return {'total': len(todos), 'by_type': by_type, 'files': len(set(t['file'] for t in todos))}


class DependencyChecker:
    def __init__(self, path):
        self.path = Path(path)

    def detect_languages(self) -> List[str]:
        langs = []
        patterns = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml'],
            'nodejs': ['package.json'],
            'go': ['go.mod'],
            'java': ['pom.xml', 'build.gradle'],
            'rust': ['Cargo.toml']
        }
        for lang, files in patterns.items():
            if any((self.path / f).exists() for f in files):
                langs.append(lang)
        return langs if langs else ['unknown']

    def check_python(self) -> Dict:
        req_file = self.path / 'requirements.txt'
        if req_file.exists():
            try:
                deps = [line.strip().split('==')[0].split('>=')[0].split('<=')[0] 
                       for line in req_file.read_text().split('\n') 
                       if line.strip() and not line.startswith('#')]
                return {'total': len(deps), 'deps': deps[:10], 'file': 'requirements.txt'}
            except:
                pass
        return {'total': 0, 'deps': [], 'file': None}

    def check_nodejs(self) -> Dict:
        pkg_file = self.path / 'package.json'
        if pkg_file.exists():
            try:
                data = json.loads(pkg_file.read_text())
                deps = list(data.get('dependencies', {}).keys()) + list(data.get('devDependencies', {}).keys())
                return {'total': len(deps), 'deps': deps[:10], 'file': 'package.json'}
            except:
                pass
        return {'total': 0, 'deps': [], 'file': None}

class SecurityScanner:
    def __init__(self, path):
        self.path = Path(path)

    def scan(self) -> Dict:
        issues = []
        sensitive_files = ['.env', '.env.local', 'id_rsa', 'id_dsa', 'config.json', 'secrets.json']

        for pattern in sensitive_files:
            for match in self.path.rglob(pattern):
                if '.git' not in str(match):
                    issues.append(f"Sensitive file: {match.name}")

        code_files = []
        for ext in ['.py', '.js', '.ts', '.java', '.yaml', '.yml']:
            code_files.extend(list(self.path.rglob(f'*{ext}'))[:20])

        secret_patterns = [
            (r"password\s*[=:]\s*['\"](.{8,})['\"]", 'password'),
            (r"api[_-]?key\s*[=:]\s*['\"](.{16,})['\"]", 'API key'),
            (r"secret[_-]?key\s*[=:]\s*['\"](.{16,})['\"]", 'secret')
        ]
#To-Do

        for file_path in code_files:
            if any(ex in str(file_path) for ex in ['.git', 'node_modules']):
                continue
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                for pattern, desc in secret_patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE):
                        value = match.group(1) if match.groups() else match.group(0)
                        if value.lower() not in ['password', 'your_api_key', 'example', 'test']:
                            issues.append(f"Potential {desc} in {file_path.name}")
            except:
                continue

        score = max(0, 100 - len(issues) * 15)
        return {'score': score, 'issues': issues[:5]}


class DevGuardianScanner:
    def __init__(self, path="."):
        self.path = Path(path).resolve()
        self.doc_checker = DocumentChecker(self.path)
        self.todo_tracker = TodoTracker(self.path)
        self.dep_checker = DependencyChecker(self.path)
        self.security_scanner = SecurityScanner(self.path)
        self.ai = DeepSeekAI()

    def build_context(self) -> str:
        context = f"Project: {self.path.name}\n"
        readme = self.doc_checker.check_readme()
        if readme['exists']:
            try:
                readme_content = (self.path / readme['file']).read_text(encoding='utf-8', errors='ignore')
                context += f"README content:\n{readme_content[:1000]}...\n"
            except:
                pass

        langs = self.dep_checker.detect_languages()
        context += f"Languages: {', '.join(langs)}\n"

        if 'python' in langs:
            py_deps = self.dep_checker.check_python()
            context += f"Python dependencies: {', '.join(py_deps['deps'][:5])}\n"

        if 'nodejs' in langs:
            js_deps = self.dep_checker.check_nodejs()
            context += f"Node.js dependencies: {', '.join(js_deps['deps'][:5])}\n"

        return context

    def scan(self) -> Dict:
        start_time = time.time()
        print_info(f"🔍 Scanning project: {self.path.name}")

        readme = self.doc_checker.check_readme()
        license_info = self.doc_checker.check_license()
        todos = self.todo_tracker.find_todos()
        todo_summary = self.todo_tracker.get_summary(todos)
        languages = self.dep_checker.detect_languages()
        security = self.security_scanner.scan()

        health_score = min(100, (readme['score'] * 0.4) + (20 if license_info['exists'] else 0) + 
                          max(0, 40 - min(todo_summary['total'] * 2, 40)))

        grade = ("A" if health_score >= 90 else "B" if health_score >= 80 else 
                "C" if health_score >= 70 else "D" if health_score >= 60 else "F")

        badges = []
        if readme['exists'] and readme['score'] >= 80: badges.append("📚 Documentation Master")
        if todo_summary['total'] == 0: badges.append("✨ Clean Code Champion")
        if security['score'] >= 95: badges.append("🔐 Security Champion")
        if health_score >= 90: badges.append("🏆 Project Excellence")

        return {
            'project': self.path.name,
            'languages': languages,
            'scan_time': round(time.time() - start_time, 2),
            'health_score': {'score': round(health_score, 1), 'grade': grade},
            'badges': badges,
            'readme': readme,
            'license': license_info,
            'todos': {'items': todos[:10], 'summary': todo_summary},
            'security': security,
            'dependencies': {
                'python': self.dep_checker.check_python() if 'python' in languages else None,
                'nodejs': self.dep_checker.check_nodejs() if 'nodejs' in languages else None
            }
        }

    def display_results(self, results):
        print("\n" + "=" * 60)
        print_colored("📊 DEVGUARDIAN SCAN RESULTS", Colors.BLUE)
        print(f"Project: {results['project']}")
        print(f"Languages: {', '.join(results['languages'])}")
        print(f"Scan Time: {results['scan_time']}s")
        print("=" * 60)

        health = results['health_score']
        color = Colors.GREEN if health['grade'] in ['A', 'B'] else Colors.YELLOW if health['grade'] == 'C' else Colors.RED
        print_colored(f"\n🎯 Health Score: {health['score']}% (Grade: {health['grade']})", color)

        if results['badges']:
            print_colored(f"\n🏆 Badges:", Colors.YELLOW)
            for badge in results['badges']:
                print(f"  🎖️  {badge}")

        print_colored(f"\n📋 DOCUMENTATION", Colors.BLUE)
        readme = results['readme']
        if readme['exists']:
            print_success(f"README: {readme['file']} (Score: {readme['score']}/100)")
            if readme['missing']: print_warning(f"Missing: {', '.join(readme['missing'])}")
        else:
            print_error("No README found")

        if results['license']['exists']:
            print_success(f"License: {results['license']['file']}")
        else:
            print_warning("No LICENSE found")

        print_colored(f"\n📝 TODO ANALYSIS", Colors.BLUE)
        todo_sum = results['todos']['summary']
        if todo_sum['total'] == 0:
            print_success("No TODOs found!")
        else:
            print(f"Total: {todo_sum['total']}")
            for t_type, count in todo_sum['by_type'].items():
                emoji = {'BUG': '🐛', 'FIXME': '🔧', 'TODO': '📝', 'HACK': '⚡'}[t_type]
                print(f"  {emoji} {t_type}: {count}")

        print_colored(f"\n🔒 SECURITY", Colors.BLUE)
        sec = results['security']
        color = Colors.GREEN if sec['score'] >= 90 else Colors.YELLOW if sec['score'] >= 70 else Colors.RED
        print_colored(f"Score: {sec['score']}/100", color)
        if sec['issues']:
            for issue in sec['issues']:
                print_warning(issue)

        deps = results['dependencies']
        if deps.get('python') and deps['python']['total'] > 0:
            print_colored(f"\n📦 PYTHON DEPENDENCIES", Colors.BLUE)
            print(f"Total: {deps['python']['total']}")

        if deps.get('nodejs') and deps['nodejs']['total'] > 0:
            print_colored(f"\n📦 NODE.JS DEPENDENCIES", Colors.BLUE)
            print(f"Total: {deps['nodejs']['total']}")

        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="🛡️ DevGuardian - Developer guidance with DeepSeek AI")
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    scan_parser = subparsers.add_parser('scan', help='Scan project')
    scan_parser.add_argument('--path', '-p', default='.', help='Project path')
    scan_parser.add_argument('--json', action='store_true', help='JSON output')

    todo_parser = subparsers.add_parser('todos', help='Find TODOs')
    todo_parser.add_argument('--path', '-p', default='.', help='Project path')

    ai_parser = subparsers.add_parser('ai', help='Ask AI')
    ai_parser.add_argument('question', help='Question')
    ai_parser.add_argument('--path', '-p', default='.', help='Project path')

    shell_parser = subparsers.add_parser('shell', help='AI shell')
    shell_parser.add_argument('--path', '-p', default='.', help='Project path')

    parser.add_argument('--version', action='version', version='DevGuardian 2.0')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    scanner = DevGuardianScanner(args.path)

    try:
        if args.command == 'scan':
            results = scanner.scan()
            if args.json:
                print(json.dumps(results, indent=2, default=str))
            else:
                scanner.display_results(results)
            sys.exit(0 if results['health_score']['score'] >= 80 else 1 if results['health_score']['score'] >= 60 else 2)

        elif args.command == 'todos':
            todos = scanner.todo_tracker.find_todos()
            summary = scanner.todo_tracker.get_summary(todos)
            print_colored("📝 TODO Analysis", Colors.BLUE)
            print(f"Total: {summary['total']}, Files: {summary['files']}")
            for t_type, count in summary['by_type'].items():
                emoji = {'BUG': '🐛', 'FIXME': '🔧', 'TODO': '📝', 'HACK': '⚡'}[t_type]
                print(f"{emoji} {t_type}: {count}")
            for todo in todos[:5]:
                print(f"  {todo['type']} in {Path(todo['file']).name}:{todo['line']} - {todo['text'][:50]}...")

        elif args.command == 'ai':
            context = scanner.build_context()
            answer = scanner.ai.ask_question(args.question, context)
            print_colored("🤖 AI Assistant:", Colors.GREEN)
            print(answer)

        elif args.command == 'shell':
            print_colored("🤖 DevGuardian AI Shell (DeepSeek)", Colors.GREEN)
            print("Ask questions about your project. Type 'exit' to quit.\n")
            context = scanner.build_context()

            while True:
                try:
                    question = input(f"{Colors.BLUE}❓ You: {Colors.RESET}")
                    if question.lower() in ['exit', 'quit', 'bye']:
                        print("👋 Goodbye!")
                        break

                    answer = scanner.ai.ask_question(question, context)
                    print_colored(f"🤖 AI: {answer}\n", Colors.GREEN)
                except (KeyboardInterrupt, EOFError):
                    print("\n👋 Goodbye!")
                    break

    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
