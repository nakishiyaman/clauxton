# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clauxton is a Claude Code plugin providing **persistent project context** through:
- **Knowledge Base**: Store architecture decisions, patterns, constraints, and conventions
- **Task Management**: Auto-inferred task dependencies with DAG validation
- **Conflict Detection**: Pre-merge conflict prediction (Phase 2)

**Status**: v0.8.0 - Production ready (94% test coverage, 267 tests)

## Build/Test Commands

### Testing
```bash
# Run all tests with coverage
pytest

# Run with HTML coverage report
pytest --cov=clauxton --cov-report=html --cov-report=term

# Run specific test file
pytest tests/core/test_knowledge_base.py

# Run specific test function
pytest tests/core/test_knowledge_base.py::test_add_entry -v

# Run tests by keyword
pytest -k "search" -v
```

### Code Quality
```bash
# Type checking (strict mode enabled)
mypy clauxton

# Linting and formatting
ruff check clauxton tests
ruff check --fix clauxton tests  # Auto-fix issues

# Run all quality checks
mypy clauxton && ruff check clauxton tests && pytest
```

### Building
```bash
# Build package (creates wheel + sdist)
python -m build

# Validate package
twine check dist/*

# Install in editable mode for development
pip install -e .
```

### Running CLI
```bash
# Initialize Clauxton in a project
clauxton init

# Knowledge Base commands
clauxton kb add                    # Interactive add
clauxton kb search "query"         # TF-IDF relevance search
clauxton kb list                   # List all entries
clauxton kb get KB-20251019-001    # Get specific entry
clauxton kb update KB-20251019-001 --title "New title"
clauxton kb delete KB-20251019-001

# Task Management commands
clauxton task add --name "Task name" --priority high
clauxton task list                 # List all tasks
clauxton task get TASK-001         # Get specific task
clauxton task update TASK-001 --status in_progress
clauxton task next                 # Get AI-recommended next task
clauxton task delete TASK-001

# Conflict Detection commands (Phase 2 - Week 12)
clauxton conflicts check           # Check for conflicts between tasks
clauxton conflicts check --task-id TASK-001 TASK-002
```

## High-Level Architecture

### Package Structure
```
clauxton/
├── core/                          # Core business logic
│   ├── models.py                  # Pydantic data models (Entry, Task, etc.)
│   ├── knowledge_base.py          # KB CRUD operations (add, search, update, delete)
│   ├── task_manager.py            # Task lifecycle + DAG validation
│   ├── search.py                  # TF-IDF search implementation
│   └── conflict_detector.py       # Conflict detection (Phase 2)
├── cli/                           # Click-based CLI interface
│   ├── main.py                    # Main CLI + KB commands
│   ├── tasks.py                   # Task management commands
│   └── conflicts.py               # Conflict detection commands
├── mcp/                           # MCP Server integration
│   └── server.py                  # 12 MCP tools (kb_*, task_*)
└── utils/                         # Utility modules
    ├── yaml_utils.py              # Safe YAML I/O with atomic writes
    └── file_utils.py              # Secure file operations

Storage: .clauxton/
├── knowledge-base.yml             # All KB entries (YAML)
├── tasks.yml                      # All tasks (YAML)
└── backups/                       # Automatic backups
```

### Key Design Patterns

1. **Pydantic Models**: All data validated with strict typing
   - `KnowledgeBaseEntry`: id, title, category, content, tags, timestamps
   - `Task`: id, name, status, priority, depends_on, files_to_edit
   - Categories: architecture, constraint, decision, pattern, convention
   - Statuses: pending, in_progress, completed, blocked
   - Priorities: critical, high, medium, low

2. **YAML Storage**: Human-readable, Git-friendly
   - All writes are atomic (temp file → rename)
   - Automatic backups before modifications
   - Safe loading with `yaml.safe_load()` (no code execution)

3. **DAG Validation**: Tasks form a Directed Acyclic Graph
   - Cycle detection using DFS
   - Topological sort for execution order
   - Auto-inference of dependencies from file overlap

4. **TF-IDF Search**: Intelligent relevance ranking
   - Powered by scikit-learn
   - Graceful fallback to keyword search if unavailable
   - Multi-field search (title, content, tags)

5. **MCP Integration**: 12 tools exposed to Claude Code
   - Knowledge Base: kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete
   - Task Management: task_add, task_list, task_get, task_update, task_next, task_delete

### Data Flow

**KB Add Flow**:
1. CLI/MCP → `KnowledgeBase.add(entry)`
2. Validate with Pydantic → Generate ID (KB-YYYYMMDD-NNN)
3. Backup existing YAML → Atomic write
4. Store in `.clauxton/knowledge-base.yml`

**Task Creation with Auto-Dependencies**:
1. CLI/MCP → `TaskManager.add(task)`
2. Validate task → Infer dependencies from file overlap
3. DAG validation (cycle detection) → Add to graph
4. Store in `.clauxton/tasks.yml`

**Search Flow**:
1. CLI/MCP → `Search.tfidf_search(query)`
2. Build TF-IDF matrix from all entries
3. Calculate cosine similarity → Rank by relevance
4. Return top N results

## Code Style Guidelines

### Python Type Hints (Required)
```python
# All functions must have type hints
def search_kb(query: str, limit: int = 10) -> List[KnowledgeBaseEntry]:
    """Search Knowledge Base by query."""
    pass
```

### Pydantic Models
```python
# Use Pydantic for data validation
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: str = Field(..., pattern=r"^TASK-\d{3}$")
    name: str = Field(..., min_length=1)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
```

### Error Handling
```python
# Use custom exceptions with clear messages
class ValidationError(Exception):
    """Validation failed."""
    pass

if not entry.title.strip():
    raise ValidationError(
        "Entry title cannot be empty. "
        "Please provide a descriptive title."
    )
```

### Docstrings (Google Style)
```python
def add_entry(entry: KnowledgeBaseEntry) -> str:
    """
    Add entry to Knowledge Base.

    Args:
        entry: KnowledgeBaseEntry to add

    Returns:
        Entry ID (e.g., "KB-20251019-001")

    Raises:
        ValidationError: If entry is invalid
        DuplicateError: If entry ID already exists
    """
    pass
```

### File Permissions
- `.clauxton/` directory: 700 (owner only)
- YAML files: 600 (owner read/write only)

## Testing Guidelines

### Test Structure
```
tests/
├── core/           # Unit tests for core modules (96% coverage target)
├── cli/            # CLI command tests (90% coverage target)
├── mcp/            # MCP server tests (95% coverage target)
├── utils/          # Utility tests (80% coverage target)
└── integration/    # End-to-end tests
```

### Writing Tests
- Use `tmp_path` fixture for file operations
- Test edge cases: Unicode, special characters, empty inputs
- Test error handling: Invalid inputs, missing files
- Test fallback behaviors: Search without scikit-learn

### Coverage Requirements
- Overall: 90% minimum (current: 94%)
- Core modules: 95%+ required
- New features: Must include comprehensive tests

## Configuration Files

### pyproject.toml
- Dependencies: pydantic>=2.0, click>=8.1, pyyaml>=6.0, scikit-learn>=1.3
- Dev dependencies: pytest, pytest-cov, mypy, ruff
- Python version: 3.11+
- Line length: 100 characters
- Entry points: `clauxton` CLI, `clauxton-mcp` server

### mypy.ini
- Strict mode enabled (`disallow_untyped_defs = True`)
- Python version: 3.11
- Ignores missing imports for third-party libs
- Tests directory has relaxed rules

### GitHub Actions (.github/workflows/ci.yml)
- Runs on: Python 3.11 & 3.12
- Jobs: Test (267 tests, ~42s), Lint (ruff + mypy, ~18s), Build (twine check, ~17s)
- All jobs run in parallel (~44s total)

## Important Patterns

### YAML Safety
```python
# ALWAYS use safe_load (never load)
import yaml
with open(path, "r") as f:
    data = yaml.safe_load(f)  # No code execution risk
```

### Atomic File Writes
```python
# Use temp file + rename for atomic writes
from clauxton.utils.yaml_utils import write_yaml

write_yaml(path, data)  # Automatic backup + atomic write
```

### Path Validation
```python
# Validate paths stay within project root
from pathlib import Path

def validate_path(path: Path, root: Path) -> None:
    if not path.resolve().is_relative_to(root.resolve()):
        raise SecurityError("Path traversal detected")
```

### ID Generation
```python
# KB entries: KB-YYYYMMDD-NNN (e.g., KB-20251019-001)
# Tasks: TASK-NNN (e.g., TASK-001)
```

## Common Development Tasks

### Add New CLI Command
1. Add Click command to `clauxton/cli/main.py` or submodule
2. Add corresponding test in `tests/cli/`
3. Update `README.md` usage section
4. Run: `pytest tests/cli/ && mypy clauxton/cli/`

### Add New MCP Tool
1. Add tool function to `clauxton/mcp/server.py` with `@server.call_tool()`
2. Add test in `tests/mcp/test_server.py`
3. Update `docs/mcp-server.md` documentation
4. Run: `pytest tests/mcp/ && mypy clauxton/mcp/`

### Add New Search Feature
1. Update `clauxton/core/search.py`
2. Add tests in `tests/core/test_search.py`
3. Ensure fallback behavior if scikit-learn unavailable
4. Run: `pytest tests/core/test_search.py -v`

### Release Checklist
1. Update version in `clauxton/__version__.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Run full test suite: `pytest --cov=clauxton`
4. Run quality checks: `mypy clauxton && ruff check clauxton`
5. Build package: `python -m build`
6. Create git tag: `git tag -a v0.X.0 -m "Release v0.X.0"`
7. Push tag: `git push origin v0.X.0`
8. Upload to PyPI: `twine upload dist/*`

## Troubleshooting

### Import Errors
```bash
# Install in editable mode
pip install -e .
```

### Test Failures
```bash
# Run with verbose output
pytest -v

# Run specific failing test
pytest tests/path/to/test.py::test_name -v

# Check coverage for missing tests
pytest --cov=clauxton --cov-report=term-missing
```

### mypy Errors
```bash
# Regenerate cache
rm -rf .mypy_cache
mypy --install-types
mypy clauxton
```

### YAML Parsing Errors
```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('.clauxton/knowledge-base.yml'))"

# Restore from backup
cp .clauxton/backups/knowledge-base.yml.bak .clauxton/knowledge-base.yml
```

## Development Roadmap

### Phase 0: Foundation (Complete)
- Knowledge Base CRUD operations
- YAML storage with atomic writes
- CLI interface

### Phase 1: Core Engine (Complete - v0.8.0)
- TF-IDF relevance search
- Task Management with DAG validation
- Auto-dependency inference
- MCP Server (12 tools)

### Phase 2: Conflict Detection (In Progress - Week 12)
- File overlap detection
- Risk scoring (0.0-1.0)
- Safe execution order recommendations
- CLI commands: `clauxton conflicts check`

## Links

- **PyPI**: https://pypi.org/project/clauxton/
- **GitHub**: https://github.com/nakishiyaman/clauxton
- **Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Documentation**: See `docs/` directory
