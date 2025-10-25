# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clauxton is a Claude Code plugin providing **persistent project context** through:
- **Knowledge Base**: Store architecture decisions, patterns, constraints, and conventions
- **Task Management**: Auto-inferred task dependencies with DAG validation
- **Conflict Detection**: Pre-merge conflict prediction (Phase 2)
- **Repository Map**: Code intelligence with multi-language symbol extraction (v0.11.0+)

**Status**: v0.11.2 - Production ready (1,370 tests, 85% coverage, Optimized test execution)
**Latest Release**: v0.11.2 - Test optimization (97% faster execution: 52min → 1m46s), CI improvements for all language parsers

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

# Conflict Detection commands (Phase 2 - v0.9.0-beta)
clauxton conflict detect TASK-001           # Check conflicts for a task
clauxton conflict order TASK-001 TASK-002   # Get safe execution order
clauxton conflict check src/api/users.py    # Check file availability

# Undo commands (v0.10.0 - Week 1 Day 3)
clauxton undo                               # Undo last operation (with confirmation)
clauxton undo --history                     # Show operation history
clauxton undo --history --limit 20          # Show last 20 operations

# Usability commands (v0.11.1)
clauxton daily                              # Show daily activity summary
clauxton daily --date 2025-10-24            # Show summary for specific date
clauxton daily --json                       # JSON output
clauxton weekly                             # Weekly summary with velocity
clauxton weekly --week -1                   # Last week's summary
clauxton weekly --json                      # JSON output
clauxton morning                            # Interactive morning planning
clauxton trends                             # Productivity trends (30 days)
clauxton trends --days 7                    # Last week's trends
clauxton focus TASK-001                     # Set focus on a task
clauxton focus                              # View current focus
clauxton focus --clear                      # Clear focus
clauxton search "query"                     # Cross-search KB/Tasks/Files
clauxton search "API" --limit 10            # Search with custom limit
clauxton search "auth" --kb-only            # Search KB only
clauxton search "bug" --tasks-only          # Search tasks only
clauxton search "function" --files-only     # Search files only
clauxton pause "Meeting"                    # Pause work with reason
clauxton pause --note "Working on bug"      # Pause with additional notes
clauxton pause --history                    # Show pause statistics
clauxton continue                           # Resume work after pause
clauxton resume                             # Show where you left off
clauxton resume --yesterday                 # Show yesterday's work too
clauxton task add --start                   # Add task and set focus
clauxton stats --json                       # Project stats as JSON
clauxton kb templates                       # Show KB entry templates
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
│   ├── conflicts.py               # Conflict detection commands
│   └── repository.py              # Repository map commands (v0.11.0+)
├── mcp/                           # MCP Server integration
│   └── server.py                  # 17 MCP tools (kb_*, task_*, conflict_*, repository_*)
├── intelligence/                  # Code intelligence (v0.11.0+)
│   ├── symbol_extractor.py        # Multi-language symbol extraction (Python, JavaScript, TypeScript)
│   ├── parser.py                  # Tree-sitter parsers (Python, JavaScript, TypeScript)
│   └── repository_map.py          # Repository indexing and symbol search
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

5. **MCP Integration**: 15 tools exposed to Claude Code
   - Knowledge Base: kb_search, kb_add, kb_list, kb_get, kb_update, kb_delete
   - Task Management: task_add, task_list, task_get, task_update, task_next, task_delete
   - Conflict Detection: detect_conflicts, recommend_safe_order, check_file_conflicts

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

### API Usage Examples

#### Correct Way to Add KB Entry
```python
from datetime import datetime
from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import KnowledgeBaseEntry

kb = KnowledgeBase(project_root)
now = datetime.now()

# Create KnowledgeBaseEntry object
entry = KnowledgeBaseEntry(
    id=f"KB-{now.strftime('%Y%m%d')}-001",
    title="API Design Pattern",
    category="architecture",
    content="Use RESTful API design",
    tags=["api", "rest"],
    created_at=now,
    updated_at=now,
)

# Add to knowledge base
entry_id = kb.add(entry)
```

#### Correct Way to Add Task
```python
from datetime import datetime
from clauxton.core.task_manager import TaskManager
from clauxton.core.models import Task

tm = TaskManager(project_root)

# Create Task object
task = Task(
    id=tm.generate_task_id(),  # Generates TASK-NNN format
    name="Implement authentication",
    priority="high",
    status="pending",
    estimated_hours=5.0,
    created_at=datetime.now(),
)

# Add to task manager
task_id = tm.add(task)
```

#### ⚠️ Common Mistake (Don't Do This)
```python
# ❌ WRONG: Passing keyword arguments directly
kb.add(
    title="API Design",  # TypeError!
    category="architecture",
    content="...",
)

# ❌ WRONG: Passing keyword arguments directly
tm.add(
    name="Task name",  # TypeError!
    priority="high",
)

# ✅ CORRECT: Create model objects first (shown above)
```

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
- Jobs: Test (390 tests, ~50s), Lint (ruff + mypy, ~18s), Build (twine check, ~17s)
- All jobs run in parallel (~52s total)

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

## Clauxton Integration Philosophy

### Core Principle: "Transparent Yet Controllable"

Clauxton follows Claude Code's philosophy:
- **Do the Simple Thing First**: YAML + Markdown (human-readable, Git-friendly)
- **Composable**: MCP integration (seamless with Claude Code)
- **User Control**: CLI override always available
- **Safety-First**: Read-only by default, explicit writes with undo capability
- **Human-in-the-Loop**: Configurable confirmation levels (v0.10.0+)

### When to Use Clauxton (Transparent Integration)

#### 🔍 Phase 1: Requirements Gathering

**Trigger**: User mentions constraints, tech stack, or design decisions

**Action**: Automatically add to Knowledge Base via MCP

**Examples**:

| User Statement | MCP Call | Category |
|----------------|----------|----------|
| "Use FastAPI" | `kb_add(title="FastAPI Adoption", category="architecture", ...)` | architecture |
| "Maximum 1000 items" | `kb_add(title="Data Limit", category="constraint", ...)` | constraint |
| "JWT Authentication" | `kb_add(title="JWT Auth", category="decision", ...)` | decision |
| "Prefer snake_case" | `kb_add(title="Naming Convention", category="convention", ...)` | convention |

**Implementation Pattern**:
```python
# When user mentions technical decisions
if user_mentioned_tech_decision:
    kb_add(
        title=extract_title(user_message),
        category=infer_category(user_message),
        content=user_message,
        tags=extract_tags(user_message)
    )
```

---

#### 📋 Phase 2: Task Planning

**Trigger**: User requests feature implementation or breaks down work

**Action**: Generate tasks and import via YAML (v0.10.0+)

**Example Workflow**:

```
User: "I want to create a Todo app. Build backend with FastAPI and frontend with React."

↓ Claude Code Thought Process ↓

1. Feature breakdown:
   - Backend: FastAPI initialization, API design, DB setup
   - Frontend: React initialization, UI implementation
   - Integration: API integration

2. Generate YAML:
   ```yaml
   tasks:
     - name: "FastAPI Initialization"
       description: "Setup FastAPI project"
       priority: high
       files_to_edit: [backend/main.py, backend/requirements.txt]
       estimate: 1
     - name: "API Design"
       description: "Define Todo CRUD API endpoints"
       priority: high
       files_to_edit: [backend/api/todos.py]
       depends_on: [TASK-001]
       estimate: 2
     ...
   ```

3. Import via MCP:
   ```python
   result = task_import_yaml(yaml_content)
   # → 10 tasks created: TASK-001 to TASK-010
   ```

4. Verify:
   ```python
   tasks = task_list(status="pending")
   # → Confirm all tasks registered
   ```

5. Start implementation:
   ```python
   next_task = task_next()
   # → TASK-001 (FastAPI Initialization)
   ```

↓ User sees ↓

"Created 10 tasks.TASK-001(FastAPI Initialization)Starting from."
```

**Key Points**:
- User doesn't see YAML generation (transparent)
- All tasks created in single operation (efficient)
- Dependencies auto-inferred from file overlap
- Claude Code manages workflow (user just confirms if needed)

---

#### ⚠️ Phase 3: Conflict Detection (Before Implementation)

**Trigger**: Before starting a task

**Action**: Check conflicts via MCP

**Example Workflow**:

```python
# Before implementing TASK-003
conflicts = detect_conflicts("TASK-003")

if conflicts["risk"] == "HIGH":
    # Warn user
    print(f"⚠️ Warning: TASK-003 has HIGH conflict risk with TASK-002")
    print(f"Files: {conflicts['files']}")
    print(f"Recommendation: Complete TASK-002 first")

    # Ask user
    proceed = ask_user("Proceed anyway?")
    if not proceed:
        # Work on another task
        next_task = task_next()
```

**Key Points**:
- Automatic conflict checking (transparent)
- User is warned if HIGH risk
- User decides whether to proceed (control)

---

#### 🛠️ Phase 4: Implementation

**During Implementation**: Update task status

```python
# Start task
task_update("TASK-001", status="in_progress")

# ... implementation ...

# Complete task
task_update("TASK-001", status="completed")

# Move to next
next_task = task_next()
```

---

### Manual Override (User Control)

**Important**: User can always override with CLI

```bash
# View all KB entries
clauxton kb list

# Add entry manually
clauxton kb add --title "..." --category architecture

# Delete incorrect entry
clauxton kb delete KB-20251020-001

# View all tasks
clauxton task list

# Manually update task
clauxton task update TASK-001 --status completed

# Check conflicts manually
clauxton conflict detect TASK-003
```

**Philosophy**: Claude Code uses MCP (transparent), but user has CLI (control)

---

### Transparency & Inspection

**User can inspect at any time**:

```bash
# View internal state
cat .clauxton/knowledge-base.yml
cat .clauxton/tasks.yml

# Git diff
git diff .clauxton/

# Search
clauxton kb search "authentication"
clauxton task list --status pending
```

**Key Points**:
- All data is human-readable (YAML)
- All data is Git-friendly (version control)
- User can manually edit if needed (last resort)

---

### Error Handling

**If Clauxton operations fail**:

```python
try:
    result = kb_add(...)
except Exception as e:
    # Graceful degradation
    print(f"Failed to add to KB: {e}")
    print("Continuing without KB registration...")
    # Implementation continues
```

**Philosophy**: Clauxton is helpful but not blocking

---

### Human-in-the-Loop (v0.10.0+)

**Configurable Confirmation Modes**:

1. **"always" mode** (100% HITL):
   - Every write operation requires confirmation
   - Maximum safety, stricter workflow
   - Use: Team development, production environments

2. **"auto" mode** (75% HITL, default):
   - Threshold-based confirmation (10+ tasks, 5+ KB entries)
   - Balanced approach
   - Use: Most development workflows

3. **"never" mode** (25% HITL):
   - No confirmation prompts
   - Undo capability available
   - Use: Rapid prototyping, personal projects

**Configuration**:
```bash
# Set confirmation mode
clauxton config set confirmation_mode always   # Strict
clauxton config set confirmation_mode auto     # Balanced (default)
clauxton config set confirmation_mode never    # Fast

# View current mode
clauxton config get confirmation_mode
```

**All modes include**:
- ✅ Undo capability (`undo_last_operation()`)
- ✅ Operation logging (`.clauxton/logs/`)
- ✅ Automatic backups (`.clauxton/backups/`)

---

## 🎯 Best Practices

### DO:
✅ Use Clauxton transparently during natural conversation
✅ Register decisions/constraints as they're mentioned
✅ Generate tasks in bulk (YAML import, v0.10.0+)
✅ Check conflicts before implementation
✅ Update task status as you work
✅ Trust user to inspect/override if needed
✅ Respect user's confirmation_mode setting

### DON'T:
❌ Ask user to run CLI commands manually (breaks flow)
❌ Show YAML generation details (too technical)
❌ Skip conflict detection (causes merge issues)
❌ Leave task status outdated (confuses workflow)
❌ Override user's confirmation_mode preference

---

## 🔧 Technical Notes

### MCP Tools Available

**Knowledge Base** (6 tools):
- `kb_search(query, limit)` - Search KB entries
- `kb_add(title, category, content, tags)` - Add entry
- `kb_list(category)` - List entries
- `kb_get(entry_id)` - Get specific entry
- `kb_update(entry_id, ...)` - Update entry
- `kb_delete(entry_id)` - Delete entry

**Task Management** (6 tools + 1 in v0.10.0):
- `task_add(name, priority, files, ...)` - Add single task
- `task_import_yaml(yaml_content, skip_confirmation=False, on_error="rollback")` - ⭐ Bulk import (v0.10.0+)
  - **Confirmation Prompts** (✅ Week 1 Day 4): 14 tests
    - Returns `status: "confirmation_required"` when ≥10 tasks (configurable)
    - Preview includes: task count, estimated hours, priority/status breakdown
    - Use `skip_confirmation=True` for trusted operations
  - **Error Recovery** (✅ Week 1 Day 5): 15 tests
    - `on_error="rollback"` (default): Revert all on error (transactional)
    - `on_error="skip"`: Skip invalid tasks, continue (returns `status: "partial"`)
    - `on_error="abort"`: Stop immediately on first error
  - **YAML Safety** (✅ Week 1 Day 5): 10 tests
    - Blocks dangerous tags: `!!python`, `!!exec`, `!!apply`
    - Blocks dangerous patterns: `__import__`, `eval()`, `exec()`, `compile()`
- `task_list(status, priority)` - List tasks
- `task_get(task_id)` - Get specific task
- `task_update(task_id, status, ...)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

**Conflict Detection** (3 tools):
- `detect_conflicts(task_id)` - Check conflicts for task
- `recommend_safe_order(task_ids)` - Get safe execution order
- `check_file_conflicts(file_paths)` - Check file availability

**KB Export** (v0.10.0+):
- `kb_export_docs(output_dir)` - ⭐ Export KB to Markdown docs

**Undo/History** (v0.10.0+ - ✅ Implemented in Week 1 Day 3):
- `undo_last_operation()` - ⭐ Reverse last operation (24 tests, 81% coverage)
- `get_recent_operations(limit)` - View operation history

**Configuration** (v0.10.0+ - Week 2):
- `get_recent_logs()` - View operation logs (planned)

Total: **17 tools** (15 current + 2 implemented in v0.10.0)

---

## 📊 Expected Behavior Changes

### Before Enhancement (Current v0.9.0-beta):

```
User: "I want to create a Todo app"
↓
Claude Code: "First, please run the following commands:
              clauxton task add --name 'FastAPI Initialization' ...
              clauxton task add --name 'API Design' ...
              ..."
↓
User: (manually run commands 10 times)
↓
Claude Code: "tasks registered. Let's begin."
```

**Problem**: Conversation flow is broken, too much manual work

---

### After Enhancement (v0.10.0):

```
User: "I want to create a Todo app"
↓
Claude Code: (internally generates YAML → task_import_yaml())
             "Created 10 tasks:
              - TASK-001: FastAPI Initialization
              - TASK-002: API Design
              - TASK-003: DB Setup
              ...
              TASK-001Starting from."
↓
User: "Yes, please proceed"
↓
Claude Code: (starts Implementation)
```

**Improvement**: Natural conversation, no manual work, efficient

---

## 📈 Success Metrics

**Quantitative Metrics**:
- task registration time: 5minutes → 10seconds(30times faster)
- User operation count: 10times → 0times(Fully automated)
- Claude Philosophy alignment: 70% → 95%(Composable + HITL Achieved)

**Qualitative Metrics**:
- Users can manage tasks through natural conversation only
- Claude CodeClaude Code autonomously utilizes Clauxton
- Manual override always available(User Control)
- Users can choose confirmation level(v0.10.0+)

---

## Development Roadmap

### ✅ Completed Phases

#### Phase 0: Foundation (Complete)
- Knowledge Base CRUD operations
- YAML storage with atomic writes
- CLI interface

#### Phase 1: Core Engine (Complete - v0.8.0)
- TF-IDF relevance search
- Task Management with DAG validation
- Auto-dependency inference
- MCP Server (12 tools)

#### Phase 2: Conflict Detection (Complete - v0.9.0-beta)
- File overlap detection
- Risk scoring (LOW/MEDIUM/HIGH)
- Safe execution order recommendations
- 3 CLI commands: `clauxton conflict detect/order/check`
- 3 MCP tools (15 tools total)

#### Phase 3: Advanced Workflows (Complete - v0.10.0)
- Bulk task operations (YAML import)
- Undo/History system (24 tests, 81% coverage)
- Human-in-the-Loop with configurable confirmation modes
- KB export to Markdown
- 7 new MCP tools (22 total)

#### Repository Intelligence (Complete - v0.11.0)
- Multi-language symbol extraction (12 languages)
- Repository map with 3 search modes
- Code intelligence integration

#### Daily Workflow Commands (Complete - v0.11.1)
- `morning`, `daily`, `weekly`, `trends`
- `focus`, `pause`, `resume`, `search`
- Productivity analytics

#### Test Optimization (Complete - v0.11.2)
- 97% faster test execution (52min → 1m46s)
- CI improvements for all language parsers
- 1,370 tests, 85% coverage

**Current Status**: v0.11.2 - Production Ready 🎉

---

### 🚀 Upcoming Phases (AI-First Strategy)

#### Phase 4: AI Integration - Foundation (v0.12.0) - 🔥 HIGHEST PRIORITY

**Goal**: Deep Claude Code integration and intelligent automation

**Release Target**: 2025-11-15 (3 weeks)

**Priority**: 🔥🔥🔥 Critical (Core Value Enhancement)

**Strategy**: AI統合こそがClaxtonの本質的価値。UIはその後。

**Core Features**:

1. **Smart Task Suggestions** (`clauxton task suggest`)
   - Analyze recent commits to suggest next tasks
   - Infer task priority from code changes
   - Auto-detect dependencies from file patterns
   - ML-based recommendation scoring

2. **Natural Language Query** (`clauxton ask "<question>"`)
   - Query KB/Tasks with natural language
   - Claude API for intelligent answering
   - Context-aware responses
   - Multi-turn conversation support

   Examples:
   ```bash
   clauxton ask "What were our database decisions?"
   clauxton ask "Why did we choose FastAPI?"
   clauxton ask "What tasks are blocking the auth feature?"
   ```

3. **Automatic KB Entry Generation from Commits**
   - Analyze commit messages and diffs
   - Extract architecture decisions
   - Auto-categorize (architecture/decision/pattern)
   - Suggest KB entries for review

   ```bash
   clauxton kb from-commits --since "1 week ago"
   # → Suggests 5 KB entries from recent commits
   ```

4. **Context-Aware Search Enhancement**
   - Current task influences search ranking
   - Recent activity boosts relevance
   - Semantic similarity (embeddings)
   - Learning from user behavior

**Technical Stack**:
- **Claude API**: Primary intelligence layer
- **Embeddings**: sentence-transformers OR Claude embeddings
- **Git Integration**: GitPython for commit analysis
- **Vector Store**: FAISS (lightweight, local-first)
- **Cache**: Embedding cache for performance

**Implementation Plan**:

**Week 1 (Oct 28 - Nov 3): Foundation**
- [ ] Create `clauxton/ai/` module structure
- [ ] Claude API client wrapper
- [ ] Embedding generation pipeline
- [ ] Vector store setup (FAISS)
- [ ] Basic `ask` command implementation
- [ ] Unit tests for AI module

**Week 2 (Nov 4 - 10): Task Suggestions**
- [ ] Git commit analyzer
- [ ] Task recommendation algorithm
- [ ] `task suggest` command
- [ ] Priority inference logic
- [ ] Dependency prediction
- [ ] Integration tests

**Week 3 (Nov 11 - 15): KB Auto-generation**
- [ ] Commit diff analysis
- [ ] Decision extraction from code
- [ ] `kb from-commits` command
- [ ] Auto-categorization logic
- [ ] Review/approval workflow
- [ ] Documentation + examples

**File Structure**:
```
clauxton/
├── ai/
│   ├── __init__.py
│   ├── client.py              # Claude API wrapper
│   ├── embeddings.py          # Embedding generation
│   ├── vector_store.py        # FAISS vector store
│   ├── task_suggester.py      # Task recommendation engine
│   ├── kb_generator.py        # Auto KB entry generation
│   ├── query_engine.py        # Natural language query
│   └── git_analyzer.py        # Git commit analysis
├── cli/
│   ├── ai_commands.py         # AI-related CLI commands
│   └── ...
└── mcp/
    └── server.py              # Add AI MCP tools
```

**New CLI Commands**:
```bash
# Natural Language Query
clauxton ask "What database did we choose?"
clauxton ask "Show me all auth-related tasks"

# Task Suggestions
clauxton task suggest                    # AI suggests next tasks
clauxton task suggest --from-commits     # From recent commits
clauxton task suggest --priority high    # Only high priority

# KB Auto-generation
clauxton kb from-commits                 # Last 7 days
clauxton kb from-commits --since "2 weeks ago"
clauxton kb from-commits --approve-all   # Auto-approve

# Enhanced Search
clauxton search "authentication" --semantic  # Embedding-based
```

**New MCP Tools**:
```python
# Add to clauxton/mcp/server.py
- ask_question(question: str) -> str
- suggest_tasks(count: int, from_commits: bool) -> List[Task]
- generate_kb_from_commits(since: str, auto_approve: bool) -> List[KBEntry]
- semantic_search(query: str, limit: int) -> List[SearchResult]
```

**Dependencies**:
```toml
[project.dependencies]
# Add AI dependencies to main dependencies
anthropic = ">=0.8.0"
sentence-transformers = ">=2.3.0"
faiss-cpu = ">=1.7.4"  # or faiss-gpu for GPU support
GitPython = ">=3.1.40"

[project.optional-dependencies]
ai-full = [
    "torch>=2.1.0",  # For local embeddings
    "transformers>=4.36.0",
]
```

**Success Metrics**:
- 🤖 Task suggestion accuracy: >80%
- 🔍 Query answer relevance: >90%
- ⚡ KB auto-generation adoption: >60% of users
- 📈 User productivity: 2x improvement
- ❤️ User satisfaction: 4.5+/5.0

**Risks & Mitigations**:
- **Risk**: Claude API costs
  - **Mitigation**: Local embeddings as fallback, aggressive caching
- **Risk**: Answer quality variability
  - **Mitigation**: Extensive prompt engineering, user feedback loop
- **Risk**: Performance (embedding generation)
  - **Mitigation**: Incremental indexing, background processing

---

#### Phase 5: AI Integration - Advanced (v0.13.0) - 🔥 HIGH PRIORITY

**Goal**: Proactive AI assistance and learning

**Release Target**: 2025-12-06 (3 weeks)

**Priority**: 🔥🔥 High (AI Maturity)

**Core Features**:

1. **AI-Powered Code Review Integration**
   - Automatic commit analysis on every commit
   - Extract patterns and anti-patterns
   - Link code changes to KB entries
   - Suggest updates to existing KB entries

   ```bash
   clauxton review HEAD           # Review latest commit
   clauxton review --auto-kb      # Auto-create KB entries
   ```

2. **Proactive Suggestions**
   - Monitor file changes (watchdog)
   - Suggest relevant KB entries while coding
   - Alert about potential conflicts
   - Recommend tasks based on current work

3. **Learning from User Behavior**
   - Track which suggestions are accepted/rejected
   - Personalized recommendations
   - Adaptive priority inference
   - Improve over time

4. **Multi-turn Conversations**
   - `clauxton chat` - Interactive AI session
   - Context retention across questions
   - Clarifying questions from AI
   - Session history

**Implementation Plan**: 3 weeks

**New Commands**:
```bash
clauxton review <commit>          # AI code review
clauxton chat                     # Interactive AI session
clauxton suggest --proactive      # Enable background suggestions
```

**Success Metrics**:
- 🎯 Proactive suggestion usefulness: >70%
- 💬 Chat session completion rate: >85%
- 📚 KB coverage improvement: +40%
- 🚀 Development velocity: +50%

---

#### Phase 6: Interactive TUI (v0.14.0) - 🟡 MEDIUM PRIORITY

**Goal**: Modern terminal interface with AI integration

**Release Target**: 2025-12-27 (3 weeks)

**Priority**: 🟡 Medium (UX Enhancement)

**Core Features**:

1. **AI-Enhanced Dashboard** (`clauxton tui`)
   - Real-time AI suggestions panel
   - Interactive task recommendations
   - KB search with AI assistance
   - Smart quick actions

2. **Streamlined Interface**
   - Focus on AI features (not just data display)
   - One-key AI actions:
     - `a`: Ask AI question
     - `s`: AI task suggestions
     - `r`: AI code review
     - `k`: Generate KB from commits

3. **Visual Feedback**
   - AI confidence indicators
   - Relevance scoring visualization
   - Learning progress display
   - Real-time processing status

**Technical Stack**:
- Textual 0.47.0+
- Integration with AI module
- Async operations for responsiveness

**Implementation Plan**:

**Week 1 (Dec 2-8): Core UI**
- [ ] Textual app scaffold
- [ ] AI suggestion panel
- [ ] Interactive query modal
- [ ] Basic keyboard navigation

**Week 2 (Dec 9-15): AI Integration**
- [ ] Live task suggestions
- [ ] AI search interface
- [ ] Code review workflow
- [ ] KB generation UI

**Week 3 (Dec 16-20): Polish**
- [ ] Animations and transitions
- [ ] Error handling
- [ ] Performance optimization
- [ ] Testing + documentation

**File Structure**:
```
clauxton/
├── tui/
│   ├── __init__.py
│   ├── app.py                 # Main TUI app
│   ├── widgets/
│   │   ├── ai_panel.py        # AI suggestions panel
│   │   ├── kb_panel.py        # KB browser
│   │   ├── task_panel.py      # Task list
│   │   └── chat_modal.py      # AI chat interface
│   ├── modals/
│   │   ├── ask_modal.py       # Quick AI query
│   │   ├── review_modal.py    # Code review display
│   │   └── suggest_modal.py   # Task suggestions
│   └── theme.py               # Color scheme
```

**Dependencies**:
```toml
[project.optional-dependencies]
tui = [
    "textual>=0.47.0",
    "rich>=13.7.0",  # Already included
]
```

**Success Metrics**:
- ⚡ AI feature discovery: 90% of TUI users try AI features
- 🎯 User engagement: 5x increase vs CLI
- ❤️ User satisfaction: 4.7+/5.0
- 🚀 Daily active usage: 3x increase

---

#### Phase 7: Web Dashboard (v0.15.0) - 🟢 LOW-MEDIUM PRIORITY

**Goal**: Browser-based visualization with team features

**Release Target**: 2026-01-24 (4 weeks)

**Priority**: 🟢 Low-Medium (Advanced Visualization + Team)

**Core Features**:

1. **AI Insights Dashboard** (`clauxton serve`)
   - Knowledge graph visualization
   - AI suggestion history and trends
   - Query analytics
   - Learning progress metrics

2. **Team Collaboration**
   - Shared KB with AI-powered search
   - Team-wide AI insights
   - Collaborative task suggestions
   - Activity feed

3. **Advanced Analytics**
   - AI accuracy metrics over time
   - Popular queries and patterns
   - KB coverage heatmap
   - Task completion predictions

**Technical Stack**:
- Backend: FastAPI + Uvicorn
- Frontend: Streamlit (fastest) OR React
- Visualization: Plotly + D3.js
- WebSockets: Real-time updates

**Implementation Plan**: 4 weeks

**Success Metrics**:
- 👥 Team adoption: 50+ teams
- 📊 Insight actionability: >70%
- 🌐 Browser usage: 30% of user base
- 💡 AI discovery rate: +40%

---

#### Phase 8: Advanced AI Features (v0.16.0) - 🟢 LOW PRIORITY

**Goal**: Cutting-edge AI capabilities

**Release Target**: 2026-03-01 (4-5 weeks)

**Priority**: 🟢 Low (Advanced Features)

**Core Features**:

1. **Voice Interface** (Optional)
   - Speech-to-text (Whisper)
   - Voice commands
   - Hands-free operation

   ```bash
   clauxton voice
   > "Show me all high priority authentication tasks"
   ```

2. **Autonomous Agent Mode**
   - AI proposes AND executes tasks (with approval)
   - Automated KB maintenance
   - Self-optimizing workflow
   - Proactive conflict resolution

3. **Multi-Project Intelligence**
   - Learn from all projects
   - Cross-project pattern recognition
   - Best practice recommendations
   - Template suggestions

4. **Custom AI Models** (Optional)
   - Fine-tuned models on user data
   - Private deployment option
   - Specialized extractors

**Implementation Plan**: 4-5 weeks

**Success Metrics**:
- 🤖 Autonomous task completion: 30%
- 🎤 Voice interface adoption: 20%
- 📚 Cross-project insights: 50% find useful

---

### 🎯 Immediate Action Plan (This Week)

#### Day 1-2 (Oct 26-27): Setup

```bash
# Create feature branch
git checkout -b feature/ai-integration-v0.12.0

# Directory structure
mkdir -p clauxton/ai
touch clauxton/ai/__init__.py
touch clauxton/ai/client.py
touch clauxton/ai/embeddings.py
touch clauxton/ai/vector_store.py
touch clauxton/ai/task_suggester.py
touch clauxton/ai/kb_generator.py
touch clauxton/ai/query_engine.py
touch clauxton/ai/git_analyzer.py

mkdir -p clauxton/cli
touch clauxton/cli/ai_commands.py

mkdir -p tests/ai
touch tests/ai/__init__.py
touch tests/ai/test_client.py
touch tests/ai/test_embeddings.py
touch tests/ai/test_task_suggester.py
```

#### Day 3-4 (Oct 28-29): Claude API Integration

**Tasks**:
1. Implement Claude API client wrapper
2. Add error handling and retry logic
3. Implement caching strategy
4. Write unit tests

**Deliverables**:
```python
# clauxton/ai/client.py
class ClaudeClient:
    def __init__(self, api_key: str):
        """Initialize Claude API client."""

    def ask_question(self, question: str, context: List[str]) -> str:
        """Ask Claude a question with context."""

    def analyze_commit(self, diff: str) -> Dict[str, Any]:
        """Analyze commit for decisions/patterns."""

    def suggest_tasks(self, context: Dict[str, Any]) -> List[Dict]:
        """Suggest tasks based on context."""
```

#### Day 5-7 (Oct 30 - Nov 1): Basic `ask` Command

**Tasks**:
1. Implement query engine
2. Context retrieval from KB/Tasks
3. CLI command implementation
4. Integration tests

**Deliverables**:
```bash
clauxton ask "What database did we choose?"
# → Searches KB, sends to Claude, returns answer
```

---

### 📋 Detailed Week-by-Week Plan (v0.12.0)

#### Week 1: Foundation (Oct 28 - Nov 3)

**Monday-Tuesday**: Claude API Client
- [ ] API wrapper with authentication
- [ ] Request/response handling
- [ ] Error handling and retries
- [ ] Rate limiting
- [ ] Caching layer (Redis/File-based)
- [ ] Unit tests (10+ tests)

**Wednesday-Thursday**: Embedding System
- [ ] sentence-transformers integration
- [ ] Embedding generation for KB/Tasks
- [ ] FAISS vector store setup
- [ ] Similarity search implementation
- [ ] Incremental indexing
- [ ] Unit tests (8+ tests)

**Friday**: Basic Query Engine
- [ ] Context retrieval logic
- [ ] Prompt engineering for Claude
- [ ] Response formatting
- [ ] `ask` command implementation
- [ ] Integration tests (5+ tests)

**Deliverable**: `clauxton ask` works end-to-end

---

#### Week 2: Task Suggestions (Nov 4 - 10)

**Monday-Tuesday**: Git Commit Analyzer
- [ ] GitPython integration
- [ ] Parse commit messages and diffs
- [ ] Extract modified files
- [ ] Identify patterns (new features, bugs, refactors)
- [ ] Unit tests (12+ tests)

**Wednesday-Thursday**: Task Recommendation Engine
- [ ] Analyze recent commits
- [ ] Infer next logical tasks
- [ ] Priority scoring algorithm
- [ ] Dependency prediction
- [ ] Confidence scoring
- [ ] Unit tests (15+ tests)

**Friday**: CLI Integration
- [ ] `task suggest` command
- [ ] Output formatting
- [ ] Interactive approval workflow
- [ ] MCP tool: `suggest_tasks()`
- [ ] Integration tests (8+ tests)

**Deliverable**: `clauxton task suggest` generates useful suggestions

---

#### Week 3: KB Auto-generation (Nov 11 - 15)

**Monday-Tuesday**: Decision Extraction
- [ ] Analyze commit diffs for decisions
- [ ] Identify architecture changes
- [ ] Extract patterns from code
- [ ] Categorization logic
- [ ] Unit tests (10+ tests)

**Wednesday-Thursday**: KB Generator
- [ ] Generate KB entry suggestions
- [ ] Auto-categorize (architecture/decision/pattern)
- [ ] Deduplication logic
- [ ] Review/approval workflow
- [ ] Unit tests (12+ tests)

**Friday**: Polish & Release
- [ ] `kb from-commits` command
- [ ] MCP tools: `generate_kb_from_commits()`
- [ ] Documentation (README, docs/ai.md)
- [ ] Integration tests (6+ tests)
- [ ] Performance testing
- [ ] Release preparation

**Deliverable**: v0.12.0 released 🚀

---

### 📊 Success Metrics & KPIs

#### v0.12.0 Targets:
- ✅ `ask` command accuracy: >85%
- ✅ `task suggest` usefulness: >75%
- ✅ `kb from-commits` adoption: >50%
- ✅ Test coverage: >90% for AI module
- ✅ API response time: <3s (95th percentile)
- ✅ PyPI downloads: 2x increase within 2 weeks

#### Long-term (6 months):
- 🤖 50% of tasks created by AI suggestions
- 🔍 70% of KB entries AI-assisted
- 💬 Daily AI query usage: 5+ per user
- ⭐ GitHub stars: 500+
- 📥 PyPI downloads: 50K+/month

---

### 🔧 Technical Decisions

#### Why Claude API?
- ✅ Best-in-class reasoning
- ✅ Long context window (200K tokens)
- ✅ Consistent with Claude Code integration
- ✅ Anthropic's alignment focus

#### Why sentence-transformers?
- ✅ Local-first (privacy)
- ✅ Fast inference (<100ms)
- ✅ No API costs
- ✅ Offline capability

#### Why FAISS?
- ✅ Lightweight (no server required)
- ✅ Fast similarity search (<10ms for 10K vectors)
- ✅ Persistent storage
- ✅ Industry standard

---

### 🎨 Design Philosophy (AI-First)

**Core Principles**:

1. **AI as Copilot, Not Autopilot**
   - AI suggests, user approves
   - Transparency in reasoning
   - Easy override/rejection

2. **Progressive Disclosure**
   - Simple commands by default
   - Advanced options available
   - Learning curve minimized

3. **Privacy-First**
   - Embeddings local by default
   - Claude API only when necessary
   - User data never leaves project

4. **Performance Conscious**
   - Aggressive caching
   - Async operations
   - Background processing
   - <3s response time target

---

この計画でv0.12.0の実装を開始しましょうか？それとも、さらに詳細を詰めたい部分がありますか？

## Links

- **PyPI**: https://pypi.org/project/clauxton/
- **GitHub**: https://github.com/nakishiyaman/clauxton
- **Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Documentation**: See `docs/` directory
