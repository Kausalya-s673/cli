### requirements.txt
rich
openai
python-dotenv

### README.md
# Smart CLI: AI-Powered Code Assistant

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)

Smart CLI is an AI-powered command-line tool that helps developers **run, debug, optimize, search, and lookup documentation** for their code files. It supports Python, Node.js, Java, HTML, and more.

---

## 🚀 Features

- **Load & Detect Language**
  Load any code file and automatically detect its language (`Python`, `Node.js`, `Java`, `HTML`).

- **Run Code**
  Execute Python, Node.js, Java files, or open HTML files in your default browser.

- **Setup Checker**
  Detect missing dependencies for Python and Node.js and suggest installation commands.

- **AI-Powered Error Fix**
  Capture runtime errors and get AI-generated suggestions to fix them.

- **Code Optimization**
  Get AI recommendations to improve readability, performance, and remove redundant code.

- **Search Codebase**
  Search for specific functions, classes, or variables across your project directory.

- **Documentation Lookup**
  Quickly get clear, concise explanations and usage examples for programming concepts, functions, or modules.

---

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/smart-cli.git
cd smart-cli
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key in a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. Make the script executable (optional):
```bash
chmod +x smart.py
```

---

## 💻 Usage

Start the CLI:
```bash
python smart.py
```

### Commands:

| Command | Description |
|---------|-------------|
| `/file <path>` | Load a code file |
| `/run` | Execute the loaded file |
| `/setup` | Suggest setup instructions for dependencies |
| `/fix` | AI-powered suggestions for runtime errors |
| `/optimize` | AI-powered code optimization suggestions |
| `/search <term>` | Search across the codebase |
| `/doc <query>` | Lookup documentation with examples |
| `/help` | Show all available commands |
| `/exit` | Quit CLI |

---

## ⚡ Examples

**Load and run a Python file:**
```bash
/file app.py
/run
```

**Optimize your code:**
```bash
/optimize
```

**Search codebase for a function:**
```bash
/search calculate_total
```

**Get documentation for a function or module:**
```bash
/doc pathlib.Path
```

---

## 📌 Requirements

- Python 3.10+
- `rich` for CLI formatting
- `openai` for AI features
- `python-dotenv` to load environment variables

---

## 🔧 Contributing

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature-name`)  
3. Commit your changes (`git commit -m "Add feature"`)  
4. Push to branch (`git push origin feature-name`)  
5. Open a pull request  

---

## ⚠️ Notes

- AI features require a valid OpenAI API key.  
- Currently supports Python, Node.js, Java, and HTML files.  
- `/search` and `/doc` rely on AI for suggestions and documentation.

---

## 📄 License

MIT License © 2025 [Your Name]