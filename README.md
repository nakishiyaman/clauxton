# Clauxton

**Context that persists for Claude Code**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/nakishiyaman/clauxton)

> ⚠️ **Alpha Status**: Clauxton is currently in Phase 0 development. Core features are being implemented. Not yet ready for production use.

Clauxton is a Claude Code plugin that provides **persistent project context** to solve AI-assisted development pain points.

**Vision** (Roadmap):
1. ✅ **Session Context Loss** → Persistent Knowledge Base (Phase 0 - In Progress)
2. 🔄 **Manual Dependency Tracking** → Auto-inferred task dependencies (Phase 1 - Planned)
3. 🔄 **Post-hoc Conflict Detection** → Pre-merge conflict prediction (Phase 2 - Planned)

---

## 🎯 Quick Start

> **Note**: CLI installation only. Full Claude Code plugin integration coming in Phase 1.

```bash
# Install from source (PyPI release coming soon)
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
pip install -e .

# Initialize in your project
cd your-project
clauxton init

# Add knowledge to your Knowledge Base
clauxton kb add

# Search your Knowledge Base
clauxton kb search "architecture"
```

---

## ✨ Features

### ✅ Phase 0: Foundation (In Progress)

#### Knowledge Base Management
- ✅ **Persistent Context**: Store architecture decisions, patterns, constraints, conventions
- ✅ **Category System**: Organize entries by type (architecture, constraint, decision, pattern, convention)
- ✅ **YAML Storage**: Human-readable, Git-friendly YAML format
- ✅ **Search**: Keyword, category, and tag-based search
- ✅ **CRUD Operations**: Add, get, update, delete, list entries
- ✅ **Atomic Writes**: Safe file operations with automatic backups
- ✅ **Secure Permissions**: 700/600 permissions for privacy

### 🔄 Phase 1: Core Engine (Planned)

#### Task Management
- 🔄 **Auto Dependency Inference**: Infer dependencies from code edits
- 🔄 **DAG Validation**: Prevent circular dependencies
- 🔄 **Next Task Suggestions**: AI recommends what to work on next
- 🔄 **MCP Integration**: Knowledge Base & Task Management MCP servers

### 🔄 Phase 2: Conflict Prevention (Planned)

#### Pre-merge Conflict Detection
- 🔄 **File Overlap Detection**: Detect potential merge conflicts
- 🔄 **Risk Scoring**: Calculate conflict risk (0.0-1.0)
- 🔄 **Safe Execution Order**: Recommend optimal task order
- 🔄 **Drift Detection**: Detect scope expansion

---

## 📦 Installation

### Development Installation (Current)

```bash
# Clone repository
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install in editable mode
pip install -e .

# Verify installation
clauxton --version
```

### PyPI Installation (Coming Soon)

```bash
pip install clauxton
```

---

## 🚀 Usage

### Current Commands (Phase 0)

```bash
# Initialize Clauxton in your project
clauxton init

# Add knowledge entry (interactive)
clauxton kb add

# Search Knowledge Base
clauxton kb search "architecture"
clauxton kb search "API" --category architecture

# List all entries
clauxton kb list
clauxton kb list --category decision

# Get entry by ID
clauxton kb get KB-20251019-001
```

### Coming in Phase 1

```bash
# Slash commands (via MCP)
/kb-search <query>
/task-add
/task-next
/deps-graph
```

### Coming in Phase 2

```bash
# Conflict detection
/conflicts-check
```

### Knowledge Base YAML Structure

After running `clauxton kb add`, your entries are stored in `.clauxton/knowledge-base.yml`:

```yaml
version: '1.0'
project_name: my-project

entries:
  - id: KB-20251019-001
    title: Use FastAPI framework
    category: architecture
    content: |
      All backend APIs use FastAPI framework.

      Reasons:
      - Async/await support
      - Automatic OpenAPI docs
      - Excellent performance
    tags:
      - backend
      - api
      - fastapi
    created_at: '2025-10-19T10:30:00'
    updated_at: '2025-10-19T10:30:00'
    version: 1
```

**Categories**:
- `architecture`: System design decisions
- `constraint`: Technical/business constraints
- `decision`: Important project decisions with rationale
- `pattern`: Coding patterns and best practices
- `convention`: Team conventions and code style

See [YAML Format Reference](docs/yaml-format.md) for complete schema documentation.

---

## 🏗️ Architecture

### Current (Phase 0)

```
clauxton/
├── core/
│   ├── models.py          # Pydantic data models ✅
│   └── knowledge_base.py  # KB CRUD operations ✅
├── utils/
│   ├── yaml_utils.py      # Safe YAML I/O ✅
│   └── file_utils.py      # Secure file operations ✅
└── cli/
    └── main.py            # CLI commands 🔄
```

**Storage**: `.clauxton/knowledge-base.yml` (YAML format)

### Planned (Phase 1-2)

- **MCP Servers**: Knowledge Base & Task Management servers
- **Subagents**: Dependency Analyzer, Conflict Detector
- **Hooks**: Auto-update on file edits
- **Slash Commands**: `/kb-*`, `/task-*`, `/deps-*`, `/conflicts-*`

See [docs/architecture.md](docs/architecture.md) for complete design.

---

## 📚 Documentation

### User Guides
- [Quick Start Guide](docs/quick-start.md) - Get started in 5 minutes
- [Installation Guide](docs/installation.md) - Complete installation instructions
- [YAML Format Reference](docs/yaml-format.md) - Complete Knowledge Base YAML specification

### Developer Guides
- [Architecture Overview](docs/architecture.md) - System design and data flow
- [Development Guide](docs/development.md) - Setup and contribution guide
- [Technical Design](docs/technical-design.md) - Implementation details
- [Roadmap](docs/roadmap.md) - 16-week development plan
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

### Coming Soon
- API Reference (Phase 1)
- Configuration Guide (Phase 1)
- MCP Server Guide (Phase 1)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📊 Project Status

| Phase | Status | Completion | Target Date |
|-------|--------|------------|-------------|
| **Phase 0: Foundation** | ✅ Complete | 95% | Week 2 (2025-11-02) |
| Phase 1: Core Engine | 📋 Ready to Start | 0% | Week 3-8 |
| Phase 2: Conflict Prevention | 📋 Planned | 0% | Week 9-12 |
| Beta Testing | 📋 Planned | 0% | Week 13-14 |
| Public Launch | 📋 Planned | 0% | Week 15-16 |

**Phase 0 Progress**:
- ✅ Pydantic data models (100%)
- ✅ YAML utilities (100%)
- ✅ Knowledge Base core (100%)
- ✅ CLI implementation (100% - init, add, get, list, search)
- ⏳ Basic MCP Server (0% - deferred to Phase 1)
- ✅ Tests & Documentation (100% - 111 tests, 93% coverage)

See [Phase 0 Completion Summary](docs/PHASE_0_COMPLETE.md) for detailed results.
See [docs/roadmap.md](docs/roadmap.md) for overall timeline.
See [docs/phase-1-plan.md](docs/phase-1-plan.md) for next steps.

---

## 🔗 Links

- **GitHub**: [https://github.com/nakishiyaman/clauxton](https://github.com/nakishiyaman/clauxton)
- **Issues**: [https://github.com/nakishiyaman/clauxton/issues](https://github.com/nakishiyaman/clauxton/issues)
- **Discussions**: [https://github.com/nakishiyaman/clauxton/discussions](https://github.com/nakishiyaman/clauxton/discussions)
- **PyPI**: Coming after Phase 0 completion

---

## 🙏 Acknowledgments

This project was inspired by the need for persistent context in AI-assisted development. Special thanks to the Claude Code team for building an extensible platform.

**Note**: Clauxton is an independent project and is not officially affiliated with Anthropic or Claude Code.

---

**Built with ❤️ for Claude Code users**
