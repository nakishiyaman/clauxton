# Clauxton

**Context that persists for Claude Code**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Clauxton is a Claude Code plugin that solves the three major pain points of AI-assisted development:

1. **Session Context Loss** → Persistent Knowledge Base via MCP
2. **Manual Dependency Tracking** → Auto-inferred task dependencies
3. **Post-hoc Conflict Detection** → Pre-merge conflict prediction

---

## 🎯 Quick Start

```bash
# Install from PyPI
pip install clauxton

# Initialize in your project
cd your-project
clauxton init

# Use with Claude Code
# Plugin is auto-detected in .claude-plugin/
```

---

## ✨ Features

### Knowledge Base Management
- **Persistent Context**: Store architecture decisions, patterns, constraints
- **Smart Search**: Keyword and category-based search
- **Auto-Categorization**: AI-powered categorization

### Task Management
- **Auto Dependency Inference**: Infer dependencies from code edits
- **DAG Visualization**: Visualize task dependency graphs
- **Next Task Suggestions**: AI recommends what to work on next

### Conflict Prevention
- **Pre-merge Detection**: Detect file conflicts before they happen
- **Risk Scoring**: Calculate conflict risk (0.0-1.0)
- **Safe Execution Order**: Recommend optimal task order

---

## 📦 Installation

### As a Claude Code Plugin (Recommended)

```bash
pip install clauxton
cd your-project
clauxton init
# Restart Claude Code
```

### As a Standalone CLI

```bash
pip install clauxton
clauxton --help
```

---

## 🚀 Usage

### Knowledge Base Commands

```bash
# Add knowledge
/kb-add

# Search knowledge
/kb-search <query>
```

### Task Commands

```bash
# Create task
/task-add

# Get next task
/task-next

# View dependency graph
/deps-graph
```

### Conflict Detection

```bash
# Check for conflicts
/conflicts-check
```

---

## 🏗️ Architecture

Clauxton is built as a Claude Code Plugin with:

- **MCP Servers**: Knowledge Base & Task Management servers
- **Subagents**: Dependency Analyzer, Conflict Detector
- **Hooks**: Auto-update on file edits
- **Slash Commands**: `/kb-*`, `/task-*`, `/deps-*`, `/conflicts-*`

See [docs/architecture.md](docs/architecture.md) for details.

---

## 📚 Documentation

- [Quick Start Guide](docs/quick-start.md)
- [Configuration](docs/configuration.md)
- [API Reference](docs/api-reference.md)
- [Architecture Overview](docs/architecture.md)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Documentation**: [https://clauxton.dev](https://clauxton.dev) (coming soon)
- **GitHub**: [https://github.com/nakishiyaman/clauxton](https://github.com/nakishiyaman/clauxton)
- **PyPI**: [https://pypi.org/project/clauxton/](https://pypi.org/project/clauxton/)

---

## 🙏 Acknowledgments

This project was inspired by the need for persistent context in AI-assisted development. Special thanks to the Claude Code team for building an extensible platform.

---

**Built with ❤️ for Claude Code users**
