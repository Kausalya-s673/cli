# 🛡️ DevGuardian

**Optimized CLI tool for developer guidance with DeepSeek AI integration**

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![DeepSeek AI](https://img.shields.io/badge/AI-DeepSeek-purple.svg)](https://platform.deepseek.com/)

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set your DeepSeek API key (get it from https://platform.deepseek.com/)
export DEEPSEEK_API_KEY="sk-your-actual-api-key-here"

# Run DevGuardian
python devguardian.py scan
```

### Basic Commands
```bash
# Full project analysis
python devguardian.py scan

# Find TODO/FIXME items
python devguardian.py todos

# Ask AI about your project (requires API key)
python devguardian.py ai "How do I run tests?"

# Interactive AI shell
python devguardian.py shell

# Scan specific directory
python devguardian.py scan --path /path/to/project

# JSON output
python devguardian.py scan --json
```

## 🎯 Features

### ✅ Core Analysis
- **Document Checker**: README, LICENSE validation with quality scoring
- **TODO Tracker**: Finds TODO, FIXME, BUG, HACK comments with prioritization
- **Multi-Language Support**: Python, Node.js, Go, Java, Rust detection
- **Security Scanner**: Detects sensitive files and potential secrets
- **Health Scoring**: Overall project grade A-F with achievement badges

### 🤖 AI Integration (DeepSeek)
- **Contextual AI**: Understands your project structure and dependencies
- **Interactive Shell**: Chat with AI about your codebase
- **Smart Answers**: Get project-specific guidance and recommendations
- **No Local Dependencies**: Uses cloud-based DeepSeek API

### 🎨 User Experience
- **Colorful Output**: Beautiful terminal interface with emojis
- **Fast Performance**: Optimized 250-line core (excluding comments)
- **CI/CD Ready**: Semantic exit codes (0=success, 1=warnings, 2=errors)
- **JSON Export**: Machine-readable results

## 🔧 Setup DeepSeek API

1. **Get API Key**: Visit [platform.deepseek.com](https://platform.deepseek.com/)
2. **Set Environment Variable**:
   ```bash
   # Linux/Mac
   export DEEPSEEK_API_KEY="sk-your-actual-key"
   
   # Windows
   set DEEPSEEK_API_KEY=sk-your-actual-key
   ```
3. **Test AI Feature**:
   ```bash
   python devguardian.py ai "What is this project about?"
   ```

## 📊 Example Output

```
============================================================
📊 DEVGUARDIAN SCAN RESULTS
Project: my-awesome-project
Languages: python, nodejs
Scan Time: 0.85s
============================================================

🎯 Health Score: 87.5% (Grade: B)

🏆 Badges:
  🎖️  📚 Documentation Master
  🎖️  🔐 Security Champion

📋 DOCUMENTATION
✅ README: README.md (Score: 85/100)
⚠️  Missing: contributing
✅ License: LICENSE

📝 TODO ANALYSIS
Total: 7
  📝 TODO: 5
  🔧 FIXME: 2

🔒 SECURITY
Score: 95/100

📦 PYTHON DEPENDENCIES
Total: 23

📦 NODE.JS DEPENDENCIES
Total: 45
============================================================
```

## 🤖 AI Assistant Examples

```bash
# Ask about installation
python devguardian.py ai "How do I install this project?"

# Ask about testing
python devguardian.py ai "What testing framework is used?"

# Ask about dependencies
python devguardian.py ai "Are there any security concerns?"

# Interactive mode
python devguardian.py shell
❓ You: How do I run the tests?
🤖 AI: Based on your package.json, you can run tests with `npm test`. 
      Your project uses Jest for testing...
```

## 🎯 Supported Languages

- **Python**: requirements.txt, setup.py, pyproject.toml
- **Node.js**: package.json, npm dependencies
- **Go**: go.mod detection
- **Java**: Maven (pom.xml), Gradle detection
- **Rust**: Cargo.toml detection

## 📋 File Structure

```
devguardian.py       # Main executable (250 lines optimized)
requirements.txt     # Python dependencies
README.md           # This documentation
```

## 🔍 What DevGuardian Analyzes

### Documentation Quality
- README existence and completeness
- LICENSE file detection
- Missing critical sections
- Word count and structure analysis

### Code Quality
- TODO/FIXME/BUG/HACK comments
- Priority-based sorting (BUG > FIXME > TODO > HACK)
- File and line location tracking
- Effort estimation

### Security Issues
- Sensitive file detection (.env, keys, configs)
- Secret pattern matching (API keys, passwords)
- Security score calculation
- Best practice recommendations

### Dependencies
- Language-specific dependency file parsing
- Total dependency counting
- Project structure analysis

### AI-Powered Insights
- Project understanding through context analysis
- Intelligent Q&A about your codebase
- Development guidance and recommendations
- Interactive assistance for complex questions

## 🚨 Error Codes

- **0**: Success - All checks passed
- **1**: Warnings - Minor issues found
- **2**: Errors - Critical issues detected

## 🤝 Contributing

1. Fork the repository
2. Make your changes to `devguardian.py`
3. Test with: `python devguardian.py scan`
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Powered by DeepSeek AI 🧠 | Built for developers, by developers 🛡️**