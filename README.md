# Clauxton

**Context that persists for Claude Code**

[![CI](https://github.com/nakishiyaman/clauxton/workflows/CI/badge.svg)](https://github.com/nakishiyaman/clauxton/actions)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security: Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![PyPI Version](https://img.shields.io/pypi/v/clauxton)](https://pypi.org/project/clauxton/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/clauxton)](https://pypi.org/project/clauxton/)
[![Development Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/nakishiyaman/clauxton)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/nakishiyaman/clauxton)
[![codecov](https://codecov.io/gh/nakishiyaman/clauxton/branch/main/graph/badge.svg)](https://codecov.io/gh/nakishiyaman/clauxton)

> ✅ **Production Ready**: Clauxton v0.13.0 is stable and ready for production use. Complete with Context Intelligence (work session analysis, action prediction, project awareness), Semantic Intelligence (embeddings, vector search), Git Analysis (pattern extraction, task suggestions), Repository Map (12-language support), and comprehensive testing (1,953+ tests, 90% coverage).
> 🔥 **v0.13.0** (2025-10-27): **Context Intelligence & Proactive Monitoring** - Real-time work session analysis with focus scoring, AI-powered next action prediction (9 actions), enhanced project context with time awareness, 3 new MCP tools (36 total)!
> 🤖 **v0.12.0** (2025-10-26): **Semantic Intelligence & Git Analysis** - Local semantic search (embeddings + FAISS), AI-powered task suggestions from commits, decision extraction, 10 new MCP tools (32 total)!
> ⚡ **v0.11.2** (2025-10-25): Test Optimization - 97% faster test execution (52min → 1m46s), CI improvements for all language parsers!
> 🚀 **v0.11.1** (2025-10-25): Daily Workflow Commands - `morning` briefing, `daily`/`weekly` summaries, `trends` analysis, `pause`/`resume` work tracking!
> 🎯 **v0.11.0** (2025-10-24): Repository Map - Multi-language symbol extraction (12 languages), 3 search modes (exact/fuzzy/semantic)!

Clauxton is a Claude Code plugin that provides **persistent project context** to solve AI-assisted development pain points.

**Vision** (Roadmap):
1. ✅ **Session Context Loss** → Persistent Knowledge Base with TF-IDF Search (Phase 0-1 - **Complete**)
2. ✅ **Manual Dependency Tracking** → Auto-inferred task dependencies (Phase 1 - **Complete**)
3. ✅ **Post-hoc Conflict Detection** → Pre-merge conflict prediction (Phase 2 - **Complete**)
4. ✅ **Manual CLI Operations** → Enhanced UX with Bulk Operations & Undo (Phase 3 - **Complete in v0.10.0**)

---

## 🎯 Quick Start

### Install from PyPI (Recommended)

```bash
# Basic installation (fast, ~30 seconds)
pip install clauxton

# Install with semantic features (recommended for v0.12.0+)
pip install clauxton[semantic]              # Semantic search + embeddings (~2 minutes)

# Or install with language parsers for Repository Map:
pip install clauxton[parsers-python]       # Python only
pip install clauxton[parsers-web]           # JavaScript/TypeScript/PHP
pip install clauxton[parsers-systems]       # Go/Rust/C++
pip install clauxton[parsers-enterprise]    # Java/C#/Kotlin
pip install clauxton[parsers-all]           # All 12 languages (~2 minutes)

# Verify installation
clauxton --version  # Should show: clauxton, version 0.12.0
```

**Note**: Language parsers are optional. Install only what you need for your project.

### Basic Usage

#### ⚡ Quick Start (Recommended)

```bash
# All-in-one setup - initialize, index, and configure MCP
cd your-project
clauxton quickstart

# Done! Your project is ready with:
# ✓ Knowledge Base initialized
# ✓ Codebase indexed (Repository Map)
# ✓ MCP server configured for Claude Code

# Optional: Skip certain steps
clauxton quickstart --skip-mcp     # Skip MCP setup (run later)
clauxton quickstart --skip-index   # Skip indexing (run later)
```

#### 📋 Manual Setup (Step-by-Step)

```bash
# Step 1: Initialize in your project
cd your-project
clauxton init

# Step 2: Index your codebase (Repository Map)
clauxton repo index
# → Indexed 50 files, found 200 symbols (Python, TypeScript, JavaScript)

# Step 3: Setup MCP server for Claude Code
clauxton mcp setup              # Auto-configure MCP server
clauxton mcp status             # Check MCP configuration

# Step 4: Check overall project status
clauxton status                 # Repository Map, Tasks, KB, MCP - all in one
```

#### 🔧 Daily Usage

```bash
# 🌅 Start your day (v0.11.1 NEW!)
clauxton morning
# → Shows yesterday's wins, suggests today's tasks, sets focus interactively

# ✅ Add and start a task immediately (v0.11.1 NEW!)
clauxton task add --name "Implement API" --start
# → Creates task and sets focus in one command

# ⏸️  Take a break (v0.11.1 NEW!)
clauxton pause "Meeting"
# → Records interruption with reason

clauxton pause --history
# → View all pause history and statistics

# 🔄 Resume work (v0.11.1 NEW!)
clauxton resume
# → Shows where you left off and suggests next actions

clauxton resume --yesterday
# → Also shows yesterday's activity for context

# 🔍 Unified search (v0.11.1 NEW!)
clauxton search "authentication"
# → Searches KB, Tasks, and Files all at once

clauxton search "API" --kb-only --limit 10
# → Search with filters and custom limits

# 📊 Daily summary (v0.11.1 NEW!)
clauxton daily
# → End-of-day review: completed tasks, time tracking, next actions

clauxton daily --date 2025-10-24
# → View specific date

clauxton daily --json
# → JSON output for integrations

# 📈 Weekly summary (v0.11.1 NEW!)
clauxton weekly
# → Week's accomplishments, velocity, trends

clauxton weekly --week -1
# → Last week's summary

# 📉 Productivity trends (v0.11.1 NEW!)
clauxton trends
# → 30-day productivity analysis with insights

clauxton trends --days 7
# → Last week's trends

# Add knowledge to your Knowledge Base
clauxton kb add
# Enter: Title, Category, Content, Tags

# Search with TF-IDF relevance ranking
clauxton kb search "FastAPI authentication"
# Results are ranked by relevance - most relevant first!

# Get next recommended task (AI-powered)
clauxton task next

# Search symbols across codebase
clauxton repo search "authenticate" --mode exact
# → authenticate_user (function) at auth.py:10-20
#   AuthService.verify (method) at auth.ts:45-60

clauxton repo search "user login" --mode semantic
# → Find symbols by meaning (requires scikit-learn)

# Undo last operation (v0.10.0 feature)
clauxton undo                   # Undo with confirmation
clauxton undo --history         # View operation history

# Configure confirmation mode (v0.10.0 feature)
clauxton config set confirmation_mode auto    # Balanced (default)
clauxton config set confirmation_mode always  # Maximum safety
clauxton config set confirmation_mode never   # Maximum speed
clauxton config list            # View all configuration
```

#### 🖥️ Interactive TUI (v0.14.0 NEW!)

Launch the Terminal User Interface for a visual, keyboard-driven experience:

```bash
# Launch Clauxton TUI
clauxton tui

# Key features:
# → Visual Knowledge Base browser with tree view
# → Fast search with autocomplete (4 modes: Normal/AI/File/Symbol)
# → AI suggestions panel with auto-refresh
# → Vim-style navigation (hjkl)
# → Quick actions (a=Ask AI, s=Suggestions, n=New Task, e=New Entry)
# → Context-aware help (F1 or ?)

# Essential shortcuts:
#   /        - Open search modal
#   a        - Ask AI question
#   s        - Toggle suggestions panel
#   h/l      - Navigate between panels
#   F1 or ?  - Show all keyboard shortcuts
#   q        - Quit
```

**Learn More**:
- 📖 **[TUI User Guide](docs/TUI_USER_GUIDE.md)** - Complete guide with workflows and troubleshooting
- ⌨️ **[Keyboard Shortcuts](docs/TUI_KEYBOARD_SHORTCUTS.md)** - Quick reference card (printable)

**TUI Features**:
- 🎨 Clean, organized interface with multiple panels
- ⚡ Fast file search with caching (no lag even with 10,000+ files)
- 🔍 Multi-mode search (Normal, AI, File, Symbol)
- 💡 Context-aware AI suggestions with auto-refresh
- ⌨️ Extensive keyboard shortcuts for power users
- 🎯 Vim-style navigation support
- 📊 Real-time statistics and status indicators

### Install from Source (Development)

```bash
git clone https://github.com/nakishiyaman/clauxton.git
cd clauxton
pip install -e .
```

### MCP Integration with Claude Code

Set up Clauxton as MCP tools in Claude Code (36 tools available):

```bash
# 🆕 v0.11.0: Automatic setup with single command
clauxton mcp setup
# → Detects your platform and Python environment
# → Generates .claude-plugin/mcp-servers.json automatically
# → Ready in seconds!

# Check configuration status
clauxton mcp status

# Alternative: Manual setup (Linux/macOS)
./setup-mcp.sh

# Or see detailed guide
docs/MCP_INTEGRATION_GUIDE.md
```

**With v0.10.0 (Released 2025-10-22)**, Claude Code uses Clauxton with enhanced features:

```
You: "Build a Todo app with FastAPI"

Claude Code: (Automatically creates 10 tasks via MCP, no manual commands needed)
             "Created 10 tasks. Starting with TASK-001: FastAPI setup"

You: "Sounds good!"

Claude Code: (Begins implementation)
```

**No more manual CLI commands** - just natural conversation! See `CLAUDE.md` for details.

---

## ✨ Features

- 🖥️ **Interactive TUI** - 🔥 **NEW v0.14.0**: Terminal UI with visual KB browser, multi-mode search, AI suggestions, Vim navigation
- 🧠 **Persistent Knowledge Base** - Store architecture decisions, patterns, constraints across sessions
- 📋 **Task Management** - AI-powered task tracking with automatic dependency inference
- ⚠️ **Conflict Detection** - Predict file conflicts before they occur, get safe execution order
- 🔍 **TF-IDF Search** - Relevance-based search with intelligent ranking (powered by scikit-learn)
- 🤖 **Semantic Search** - ⭐ **NEW v0.12.0**: Local embeddings + FAISS vector search (100% private, no API costs)
- 📊 **Git Analysis** - ⭐ **NEW v0.12.0**: Pattern extraction, decision detection, AI task suggestions from commits
- 🧠 **Context Intelligence** - 🔥 **NEW v0.13.0**: Work session analysis (duration, focus score, breaks), AI action prediction (9 actions), enhanced project awareness with time context
- 👁️ **Proactive Monitoring** - 🔥 **NEW v0.13.0**: Real-time file watching, pattern detection (bulk edits, new features, refactoring)
- 🗺️ **Repository Map** - Automatic codebase indexing with symbol search (12 languages, 3 modes)
- 🌅 **Daily Workflow Commands** - `morning` briefing, `daily`/`weekly` summaries, `trends` analysis, `pause`/`resume` tracking
- 🔒 **Privacy First** - 100% local by default, no cloud dependencies
- 🤖 **MCP Integration** - Seamless integration with Claude Code via Model Context Protocol (36 tools total)

### ✅ Core Features (v0.10.0)

#### 🔍 TF-IDF Relevance Search
- ✅ **Intelligent Ranking**: TF-IDF algorithm ranks results by relevance (powered by scikit-learn)
- ✅ **Automatic Fallback**: Gracefully falls back to keyword search if scikit-learn unavailable
- ✅ **Fast Performance**: Validated with 200+ knowledge base entries
- ✅ **Query Understanding**: Understands multi-word queries and technical terms
- ✅ **See**: [Search Algorithm Documentation](docs/search-algorithm.md)

#### 📚 Knowledge Base Management
- ✅ **Persistent Context**: Store architecture decisions, patterns, constraints, conventions
- ✅ **Category System**: 5 categories (architecture, constraint, decision, pattern, convention)
- ✅ **YAML Storage**: Human-readable, Git-friendly format
- ✅ **CRUD Operations**: Add, get, update, delete, list entries
- ✅ **Version Management**: Automatic versioning on updates
- ✅ **Atomic Writes**: Safe file operations with automatic backups
- ✅ **Secure Permissions**: 700/600 permissions for privacy

#### ✅ Task Management System
- ✅ **Full CRUD**: Add, get, update, delete, list tasks
- ✅ **Smart Dependencies**: Auto-inferred from file overlap + manual dependencies
- ✅ **DAG Validation**: Cycle detection prevents circular dependencies
- ✅ **Priority Management**: 4 levels (Critical > High > Medium > Low)
- ✅ **AI Recommendations**: `task next` suggests optimal next task
- ✅ **Progress Tracking**: Track status (pending, in_progress, completed, blocked)
- ✅ **Time Estimates**: Optional hour estimates for planning

#### 🚀 v0.10.0 Features (Transparent Integration)
**Bulk Operations**:
- ✅ **YAML Bulk Import**: Create multiple tasks from YAML file - 30x faster than manual
- ✅ **KB Export**: Export Knowledge Base to Markdown documentation
- ✅ **Progress Display**: Real-time progress bars for bulk operations (100+ items)

**Safety & Recovery**:
- ✅ **Undo/Rollback**: Reverse accidental operations with full history tracking
- ✅ **Error Recovery**: Transactional import with `rollback`/`skip`/`abort` strategies
- ✅ **YAML Safety**: Security checks to prevent code injection attacks
- ✅ **Backup Enhancement**: Automatic backups before every write operation (last 10 kept)
- ✅ **Enhanced Validation**: Pre-Pydantic validation with clear error messages

**User Experience**:
- ✅ **Confirmation Prompts**: Threshold-based warnings for bulk operations
- ✅ **Configurable Confirmation Mode**: Set HITL level (always/auto/never)
- ✅ **Operation Logging**: Structured logging with daily log files (30-day retention)
- ✅ **Better Error Messages**: Actionable errors with context + suggestion + commands
- ✅ **Performance Optimization**: 10x faster bulk operations

**Total**: 13 new features in v0.10.0

#### 🗺️ Repository Map (v0.11.0 - Released 2025-10-24)
**Automatic Codebase Intelligence**:
- ✅ **File Indexing**: Recursive scanning with `.gitignore` support (1000+ files in <2s)
- ✅ **Symbol Extraction**: Functions, classes, methods, interfaces, types with signatures
- ✅ **Multi-Language Support** (12 languages):
  - **Python** ✅ Complete (functions, classes, methods, docstrings, type hints)
  - **JavaScript** ✅ Complete (ES6+, classes, arrow functions, async/await)
  - **TypeScript** ✅ Complete (interfaces, type aliases, generics, type annotations)
  - **Go** ✅ Complete (functions, methods, structs, interfaces, type aliases, generics)
  - **Rust** ✅ Complete (functions, methods, structs, enums, traits, type aliases, generics)
  - **C++** ✅ Complete (functions, classes, structs, namespaces, templates)
  - **Java** ✅ Complete (classes, interfaces, methods, enums, annotations, constructors)
  - **C#** ✅ Complete (classes, interfaces, structs, methods, properties, records, extensions)
  - **PHP** ✅ Complete (classes, functions, methods, traits, enums, promoted properties, attributes)
  - **Ruby** ✅ Complete (classes, modules, methods, module mixins, singleton methods, attr_*)
  - **Swift** ✅ Complete (classes, structs, protocols, extensions, enums, init methods, properties)
  - **Kotlin** ✅ Complete (classes, data/sealed classes, interfaces, objects, companion objects, suspend functions)
- ✅ **3 Search Modes**:
  - **Exact**: Fast substring matching with priority scoring
  - **Fuzzy**: Typo-tolerant using Levenshtein distance
  - **Semantic**: TF-IDF meaning-based search (requires scikit-learn)
- ✅ **CLI Commands**: `repo index`, `repo search`, `repo status`
- ✅ **MCP Integration**: `index_repository()`, `search_symbols()` tools
- ✅ **Performance**: 1000+ files/1-2s indexing, <0.01s search
- ✅ **Storage**: JSON format in `.clauxton/map/` (~10-50KB per project)

**Example Usage**:
```bash
# Index your codebase (Python, JavaScript, TypeScript)
clauxton repo index
# → Indexed 50 files, found 200 symbols in 0.15s
#   - 15 Python files (50 functions, 20 classes)
#   - 20 TypeScript files (80 functions, 15 interfaces, 10 type aliases)
#   - 15 JavaScript files (40 functions, 10 classes)

# Search for functions
clauxton repo search "authenticate" --mode exact
# → authenticate_user (function) at auth.py:10-20
#   getAuthToken (function) at auth.ts:30-35
#   AuthService.verify (method) at auth-service.ts:45-60

# Search for TypeScript interfaces
clauxton repo search "User" --mode exact
# → User (interface) at types.ts:5-10
#   UserService (class) at user-service.ts:15-50
#   getUserById (function) at api.ts:100-110

# Semantic search by meaning
clauxton repo search "user login" --mode semantic
# → authenticate_user, verify_credentials, check_session...
#   AuthService, LoginRequest, validateToken...
```

**Programming API**:
```python
from pathlib import Path
from clauxton.intelligence.symbol_extractor import (
    PythonSymbolExtractor,
    JavaScriptSymbolExtractor,
    TypeScriptSymbolExtractor,
    GoSymbolExtractor,
)

# Extract TypeScript symbols
ts_extractor = TypeScriptSymbolExtractor()
symbols = ts_extractor.extract(Path("src/types.ts"))

for symbol in symbols:
    print(f"{symbol['name']} ({symbol['type']}) at line {symbol['line_start']}")
    # Output:
    # User (interface) at line 5
    # AuthRequest (type_alias) at line 10
    # AuthService (class) at line 15

# Extract Go symbols
go_extractor = GoSymbolExtractor()
go_symbols = go_extractor.extract(Path("pkg/user.go"))

for symbol in go_symbols:
    if symbol['type'] == 'method':
        print(f"{symbol['name']} (method on {symbol['receiver']})")
    else:
        print(f"{symbol['name']} ({symbol['type']})")
    # Output:
    # User (struct)
    # GetName (method on *User)
    # SetName (method on *User)
```

**Total**: Week 1 complete (81 tests, 92%/90% coverage)

#### 🔌 MCP Server Integration (22 Tools)
**Knowledge Base Tools** (7):
- ✅ `kb_search` - TF-IDF relevance-ranked search
- ✅ `kb_add` - Add new knowledge entry
- ✅ `kb_list` - List all entries (filterable by category)
- ✅ `kb_get` - Get entry by ID
- ✅ `kb_update` - Update existing entry
- ✅ `kb_delete` - Delete entry
- ✅ `kb_export_docs` - **NEW v0.10.0**: Export KB to Markdown docs

**Task Management Tools** (7):
- ✅ `task_add` - Create task with auto-dependency inference
- ✅ `task_import_yaml` - **NEW v0.10.0**: Bulk import tasks from YAML
- ✅ `task_list` - List tasks (filterable by status/priority)
- ✅ `task_get` - Get task details
- ✅ `task_update` - Update task fields
- ✅ `task_next` - Get AI-recommended next task
- ✅ `task_delete` - Delete task

**Conflict Detection Tools** (3):
- ✅ `detect_conflicts` - Detect file conflicts for a task
- ✅ `recommend_safe_order` - Get optimal task execution order
- ✅ `check_file_conflicts` - Check if files are being edited

**Operation Management Tools** (2) - **NEW v0.10.0**:
- ✅ `undo_last_operation` - Reverse accidental operations
- ✅ `get_recent_operations` - View operation history

**Logging Tools** (1) - **NEW v0.10.0**:
- ✅ `get_recent_logs` - View recent operation logs

**Repository Map Tools** (2) - **NEW v0.11.0**:
- ✅ `index_repository` - Index codebase with symbol extraction
- ✅ `search_symbols` - Search symbols with exact/fuzzy/semantic modes

**Semantic Search Tools** (3) - ⭐ **NEW v0.12.0**:
- ✅ `search_knowledge_semantic` - Semantic KB search with embeddings
- ✅ `search_tasks_semantic` - Semantic task search with filtering
- ✅ `search_files_semantic` - Semantic code search by meaning

**Git Analysis Tools** (3) - ⭐ **NEW v0.12.0**:
- ✅ `analyze_recent_commits` - Analyze commit patterns and statistics
- ✅ `suggest_next_tasks` - AI-powered task suggestions from commits
- ✅ `extract_decisions_from_commits` - Extract architecture decisions

**Context & Intelligence Tools** (4) - ⭐ **NEW v0.12.0**:
- ✅ `get_project_context` - Rich project context for Claude Code
- ✅ `generate_project_summary` - Auto-generated project summaries
- ✅ `get_knowledge_graph` - Knowledge graph visualization
- ✅ `find_related_entries` - Discover related KB/tasks

**Proactive Monitoring Tools** (2) - 🔥 **NEW v0.13.0**:
- ✅ `watch_project_changes` - Enable/disable real-time file monitoring
- ✅ `get_recent_changes` - Get recent changes and detected patterns

**Context Intelligence Tools** (3) - 🔥 **NEW v0.13.0**:
- ✅ `analyze_work_session` - Analyze work session (duration, focus score, breaks, file switches)
- ✅ `predict_next_action` - AI-powered next action prediction (9 supported actions with confidence)
- ✅ `get_current_context` - Enhanced project context (Git info, active files, time context, session + prediction)

**Total**: 36 tools (22 base + 10 v0.12.0 + 2 proactive + 3 context intelligence)

#### 📊 Quality Metrics
- ✅ **1,953+ Tests** - Comprehensive test coverage (1,228 → 1,637 in v0.12.0 → 1,953+ in v0.13.0, +316 tests):
  - Core modules: 87-96% coverage (knowledge_base, task_manager, conflict_detector, etc.)
  - Intelligence modules: 91-92% coverage (repository_map, symbol_extractor, parser)
    - 441 intelligence tests covering 12 languages (Python, JS, TS, Go, Rust, C++, Java, C#, PHP, Ruby, Swift, Kotlin)
  - **Semantic modules**: 91-98% coverage (embeddings, indexer, search, vector_store) - v0.12.0
    - 126 semantic tests (embeddings, vector store, indexer, search engine)
  - **Analysis modules**: 95-99% coverage (git_analyzer, pattern_extractor, decision_extractor, task_suggester) - v0.12.0
    - 82 analysis tests (commit analysis, pattern extraction, task suggestions)
  - **Proactive modules**: 89-100% coverage (file_monitor, event_processor, context_manager, suggestion_engine, behavior_tracker, config) - 🔥 **NEW v0.13.0**
    - 316 proactive tests (Week 1: 56, Week 2: 132, Week 3: 128) covering all Context Intelligence features
  - MCP server: 93% coverage (36 tools, all tested individually) - Updated v0.13.0
    - 54 total MCP integration tests (21 v0.12.0 + 15 proactive + 18 context intelligence)
  - CLI modules: 69-94% coverage (main, tasks, conflicts, config, repository, mcp)
  - Utils modules: 89-97% coverage (yaml, file, backup, logger)
- ✅ **90% Coverage** - High code quality maintained across all modules (including v0.13.0 Context Intelligence)
- ✅ **Type Safe** - Full Pydantic validation with strict mypy mode
- ✅ **Production Ready** - Stable v0.13.0 release with Context Intelligence & Proactive Monitoring

### 🧠 Context Intelligence (v0.13.0)

#### 🎯 Work Session Analysis
Automatically track and analyze your development sessions:
- ✅ **Session Duration**: Automatic tracking from first file change (30-minute session timeout)
- ✅ **Focus Score**: 0.0-1.0 score based on file switching patterns
  - High focus (0.8+): Concentrated work with few file switches
  - Medium focus (0.5-0.8): Moderate context switching
  - Low focus (<0.5): Scattered work across many files
- ✅ **Break Detection**: Automatically detect breaks ≥15 minutes (configurable)
- ✅ **Active Periods**: Track continuous work periods between breaks
- ✅ **Performance**: <50ms analysis, 30-second caching for speed

**Focus Score Formula**: `max(0, 1 - (file_switches / (duration_minutes / 10)))`

#### 🤖 AI Action Prediction
Get intelligent recommendations for what to do next:
- ✅ **9 Supported Actions**: run_tests, write_tests, commit_changes, create_pr, take_break, morning_planning, resume_work, review_code, no_clear_action
- ✅ **Confidence Scoring**: 0.0-1.0 confidence for each prediction
  - High (0.8+): Strong recommendation, follow it
  - Medium (0.5-0.8): Consider as suggestion
  - Low (<0.5): Informational only
- ✅ **Context-Aware**: Analyzes git status, file changes, session duration, time of day
- ✅ **Reasoning**: Human-readable explanations for each prediction

**Example Predictions**:
```
Action: run_tests (confidence: 0.87)
Reasoning: 15 files changed without recent test runs. Run tests before committing.

Action: take_break (confidence: 0.85)
Reasoning: Session duration 120 minutes with 0 breaks. Take a 10-minute break.

Action: commit_changes (confidence: 0.75)
Reasoning: 8 files modified, tests passing. Ready to commit.
```

#### 📊 Enhanced Project Context
Get rich context about your project state:
- ✅ **Git Information**: Current branch, recent commits, uncommitted changes, diff stats
- ✅ **Active Files**: Recently modified files (last 30 minutes) with timestamps
- ✅ **Time Context**: Morning (6-12), Afternoon (12-18), Evening (18-22), Night (22-6)
- ✅ **Work Session**: Duration, focus score, breaks, active periods
- ✅ **Predicted Action**: Next recommended action with confidence and reasoning (optional)
- ✅ **Performance**: 30-second caching, <100ms with prediction, <50ms without

**Use Cases**:
- 🌅 "What should I work on today?" → Morning planning with yesterday's context
- 🎯 "Am I ready to commit?" → Check if tests need to run first
- 📈 "How's my session going?" → Session analysis with focus score
- 🔄 "Where did I leave off?" → Project context with recent activity
- ⏸️  "Should I take a break?" → Break recommendations based on session duration

**CLI Usage** (coming soon):
```bash
# Analyze work session
clauxton session analyze
# → Duration: 87 minutes, Focus: 0.82 (high), Breaks: 0

# Get next action prediction
clauxton next-action
# → Recommendation: run_tests (85% confidence)
# → Reasoning: 12 files changed without recent test runs

# Get full project context
clauxton context
# → Git: feature/api-refactor (3 commits ahead)
# → Session: 87min, Focus: 0.82
# → Prediction: run_tests (0.85)
```

**MCP Tools** (3 new tools for Claude Code):
```python
# Analyze work session
analyze_work_session()
# → {
#   "status": "success",
#   "duration_minutes": 87,
#   "focus_score": 0.82,
#   "breaks": [],
#   "file_switches": 12
# }

# Predict next action
predict_next_action()
# → {
#   "action": "run_tests",
#   "confidence": 0.87,
#   "reasoning": "15 files changed without recent test runs"
# }

# Get current context (with prediction)
get_current_context(include_prediction=True)
# → {
#   "current_branch": "feature/api-refactor",
#   "uncommitted_changes": 8,
#   "session_duration_minutes": 87,
#   "focus_score": 0.82,
#   "predicted_next_action": {
#     "action": "run_tests",
#     "confidence": 0.87
#   }
# }
```

**Natural Language with Claude Code**:
```
You: "How's my work session going?"
Claude Code: → Calls analyze_work_session()
"Your session: 87 minutes with high focus (0.82).
You've modified 12 files without taking a break.
Consider taking a short break after 90 minutes."

You: "What should I do before committing?"
Claude Code: → Calls predict_next_action()
"Recommendation: Run tests (85% confidence).
You've changed 15 files without recent test runs."

You: "Give me full project context"
Claude Code: → Calls get_current_context(include_prediction=True)
"Working on: feature/api-refactor (3 commits ahead)
Session: 87 minutes, focus 0.82 (high)
Uncommitted: 8 files
Suggestion: run_tests (85% confidence)"
```

See [Context Intelligence Guide](docs/guides/CONTEXT_INTELLIGENCE_GUIDE.md) for complete documentation.

### 👁️ Proactive Monitoring (v0.13.0)

#### 🔥 Real-time File Monitoring
- ✅ **watchdog Integration**: Background file change detection
- ✅ **Debounced Events**: 500ms debounce to avoid duplicates
- ✅ **Configurable Patterns**: Watch specific file types, ignore directories
- ✅ **Performance**: <5ms event processing, <1% CPU when idle
- ✅ **MCP Tool**: `watch_project_changes(enabled)` - Start/stop monitoring

#### 🎯 Pattern Detection (5 Algorithms)
- ✅ **Bulk Edit Detection**: Same file modified 3+ times rapidly (confidence scoring)
- ✅ **New Feature Detection**: Multiple new files created in short time
- ✅ **Refactoring Detection**: Files renamed/moved together
- ✅ **Cleanup Detection**: Files deleted in bulk
- ✅ **Config Change Detection**: Configuration file modifications
- ✅ **MCP Tool**: `get_recent_changes(minutes)` - Retrieve changes and patterns

#### 📊 Event Processing
- ✅ **Event Types**: modified, created, deleted, moved
- ✅ **Metadata Tracking**: Timestamps, file paths, event details
- ✅ **Confidence Scoring**: 0.0-1.0 confidence for each pattern
- ✅ **Time Windows**: Flexible query by minutes (default: 60)
- ✅ **Pattern Descriptions**: Human-readable pattern explanations

**Use Cases**:
- 🤖 "What have I changed in the last hour?"
- 🎯 "Show me detected patterns in my recent work"
- 📈 "Based on my changes, suggest next tasks"
- 🔍 "I'm refactoring - did the system detect it?"

### ⚠️ Conflict Detection

#### ⚠️ Pre-merge Conflict Detection
- ✅ **File Overlap Detection**: Detects file conflicts between tasks
- ✅ **Risk Scoring**: Calculates risk (LOW <40%, MEDIUM 40-70%, HIGH >70%)
- ✅ **Safe Execution Order**: Recommends optimal task execution order
- ✅ **File Availability Check**: Check if files are currently being edited
- ✅ **CLI Commands**: `conflict detect`, `conflict order`, `conflict check`
- ✅ **MCP Tools**: Full integration for Claude Code

### 🔮 Future Enhancements

**v0.12.0 Complete** (Released 2025-10-26) ✅:
- ✅ **Semantic Intelligence**: Local embeddings + FAISS vector search (100% private, no API costs)
- ✅ **Git Analysis**: Pattern extraction, decision detection from commits
- ✅ **Task Suggestions**: AI-powered recommendations from commit history
- ✅ **Enhanced Context**: Project summaries, knowledge graphs, related entries
- ✅ **10 New MCP Tools**: Semantic search (3), Git analysis (3), Context (4)
- ✅ **208 New Tests**: 126 semantic + 82 analysis tests
- ✅ **Production Ready**: A grade (94.7/100) quality

**v0.13.0 Week 1 Complete** (2025-10-26) ✅:
- ✅ **Real-time File Monitoring**: watchdog-based change tracking
- ✅ **Pattern Detection**: 5 algorithms (bulk_edit, new_feature, refactoring, cleanup, config_change)
- ✅ **Event Processing**: Debounced events with confidence scoring
- ✅ **2 New MCP Tools**: watch_project_changes(), get_recent_changes()
- ✅ **56 New Tests**: 21 config + 20 event_processor + 15 MCP tests
- ✅ **96-100% Coverage**: High-quality implementation

**v0.13.0 Week 2-3 Roadmap** (Planned):
- 📋 **Proactive Suggestions**: Context-aware task and KB recommendations
- 📋 **Learning from Behavior**: Personalized suggestions based on patterns
- 📋 **Enhanced Context**: Activity-based context awareness

**v0.14.0+ Future Vision**:
- 📋 **Interactive TUI**: Modern terminal interface with AI panels
- 📋 **Web Dashboard**: Browser-based UI for team collaboration
- 📋 **Line-Level Conflict Detection**: Detect conflicts at code line level
- 📋 **Enhanced Event Logging**: Complete audit trail with events.jsonl
- 📋 **Lifecycle Hooks**: Pre-commit and post-edit hooks

---

## 📦 Installation

### PyPI Installation (Recommended)

```bash
# Install latest stable version (includes all features)
pip install clauxton

# Install with semantic features (recommended for v0.12.0+)
pip install clauxton[semantic]

# Verify installation
clauxton --version  # Should show: clauxton, version 0.12.0

# Install specific version (example)
pip install clauxton==0.12.0
```

**What's Included**:
- ✅ Knowledge Base management (CRUD + TF-IDF search + Markdown export)
- ✅ Task Management system with auto-dependencies + YAML bulk import
- ✅ Conflict Detection (pre-merge conflict prediction)
- ✅ Repository Map (12-language symbol extraction)
- ✅ Undo/Rollback functionality with operation history
- ✅ Configurable confirmation modes (always/auto/never)
- ✅ Operation logging with 30-day retention
- ✅ Automatic backups (last 10 retained)
- ✅ MCP Server (32 tools for Claude Code)
- ✅ All dependencies (scikit-learn, numpy, pydantic, click, pyyaml, gitpython, mcp, rich)

**Optional Semantic Features** (install with `pip install clauxton[semantic]`):
- ✅ Semantic Search (local embeddings with sentence-transformers)
- ✅ FAISS Vector Store (fast similarity search)
- ✅ Git Analysis (pattern extraction, task suggestions)
- ✅ Enhanced Context (project summaries, knowledge graphs)
- ✅ 10 Additional MCP Tools (semantic search, git analysis, context)

### Development Installation

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

# Run tests
pytest
```

### Requirements

- **Python**: 3.11 or higher
- **Dependencies** (auto-installed with pip):
  - `pydantic>=2.0` - Data validation
  - `click>=8.1` - CLI framework
  - `pyyaml>=6.0` - YAML parsing
  - `gitpython>=3.1` - Git integration
  - `mcp>=1.0` - MCP server
  - `scikit-learn>=1.3` - TF-IDF search
  - `numpy>=1.24` - Required by scikit-learn

**Note on Search**: Clauxton uses **TF-IDF algorithm** for intelligent relevance ranking. If scikit-learn is unavailable, it automatically falls back to keyword matching. See [Search Algorithm](docs/search-algorithm.md) for details.

---

## 🚀 Usage

### Daily Workflow Commands (NEW v0.11.1)

```bash
# Quick project overview - See everything at a glance
clauxton overview
clauxton overview --limit 5  # Show 5 entries per category

# Resume work - Get back into context after a break
clauxton resume

# Project statistics - Understand project health
clauxton stats
```

### Quick Add Shortcuts (NEW v0.11.1)

Faster than interactive commands - no prompts, just add!

```bash
# Quick Knowledge Base entries (10x faster)
clauxton add-architecture "Microservices" "Using Docker containers for each service"
clauxton add-decision "Use PostgreSQL" "Chosen for JSONB support" --tags database,backend
clauxton add-constraint "Max 1000 items" "API returns maximum 1000 items per request"
clauxton add-pattern "Repository Pattern" "All DB access through repositories"
clauxton add-convention "snake_case" "Use snake_case for Python variables"

# Quick task creation
clauxton quick-task "Setup backend"
clauxton quick-task "Fix authentication bug" --high
clauxton quick-task "Security patch CVE-2024-001" --critical
```

### Knowledge Base Commands

```bash
# Initialize Clauxton in your project
clauxton init

# Add knowledge entry (interactive)
clauxton kb add

# Search Knowledge Base (TF-IDF relevance ranking)
clauxton kb search "architecture"          # Results ranked by relevance
clauxton kb search "API" --category architecture
clauxton kb search "FastAPI" --limit 5     # Limit to top 5 results

# List all entries
clauxton kb list
clauxton kb list --category decision

# Get entry by ID
clauxton kb get KB-20251019-001

# Update entry
clauxton kb update KB-20251019-001 --title "New Title"
clauxton kb update KB-20251019-001 --content "New content" --category decision

# Delete entry
clauxton kb delete KB-20251019-001
clauxton kb delete KB-20251019-001 --yes  # Skip confirmation

# Export Knowledge Base to Markdown docs (v0.10.0)
clauxton kb export --output-dir ./docs/kb

# Export as compact summary - Perfect for team onboarding! (NEW v0.11.1)
clauxton kb export --output-dir ./docs/kb --summary
```

### Task Management Commands

```bash
# Add a new task
clauxton task add --name "Setup database" --priority high

# Add task with dependencies
clauxton task add \
  --name "Add API endpoint" \
  --depends-on TASK-001 \
  --files "src/api/users.py" \
  --estimate 3.5

# List all tasks
clauxton task list
clauxton task list --status pending
clauxton task list --priority high

# Get task details
clauxton task get TASK-001

# Update task
clauxton task update TASK-001 --status in_progress
clauxton task update TASK-001 --priority critical

# Get next recommended task (AI-powered)
clauxton task next

# Delete task
clauxton task delete TASK-001

# Bulk import tasks from YAML (NEW v0.10.0)
clauxton task import tasks.yml
clauxton task import tasks.yml --dry-run  # Validate without creating
```

**YAML Bulk Import Example** (`tasks.yml`):
```yaml
tasks:
  - name: "Setup FastAPI project"
    priority: high
    files_to_edit:
      - main.py
      - requirements.txt
    estimated_hours: 2.5

  - name: "Create database models"
    priority: high
    depends_on:
      - TASK-001
    files_to_edit:
      - models/user.py
      - models/post.py
    estimated_hours: 3.0

  - name: "Write API tests"
    priority: medium
    depends_on:
      - TASK-002
    estimated_hours: 4.0
```

See [YAML Task Format Guide](docs/YAML_TASK_FORMAT.md) for complete specification.

### MCP Server Integration

The Clauxton MCP Server provides full Knowledge Base and Task Management for Claude Code:

```json
// .claude-plugin/mcp-servers.json
{
  "mcpServers": {
    "clauxton": {
      "command": "python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Knowledge Base Tools**:
- `kb_search(query, category?, limit?)` - Search with TF-IDF relevance ranking
- `kb_add(title, category, content, tags?)` - Add new entry
- `kb_list(category?)` - List all entries
- `kb_get(entry_id)` - Get entry by ID
- `kb_update(entry_id, title?, content?, category?, tags?)` - Update entry
- `kb_delete(entry_id)` - Delete entry

> **Note**: Search results are automatically ranked by relevance using TF-IDF algorithm. Most relevant entries appear first.

**Task Management Tools**:
- `task_add(name, description?, priority?, depends_on?, files?, kb_refs?, estimate?)` - Add task
- `task_import_yaml(yaml_content, dry_run?, skip_validation?)` - **NEW v0.10.0**: Bulk import tasks from YAML
- `task_list(status?, priority?)` - List tasks with filters
- `task_get(task_id)` - Get task details
- `task_update(task_id, status?, priority?, name?, description?)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

See [MCP Documentation Index](docs/mcp-index.md) for complete MCP Server documentation (36 tools across 9 categories).

### Conflict Detection Commands

```bash
# Check conflicts before starting a task
clauxton conflict detect TASK-001

# Get safe execution order for multiple tasks
clauxton conflict order TASK-001 TASK-002 TASK-003

# Check if specific files are being edited
clauxton conflict check src/api/users.py src/models/user.py
```

See [Conflict Detection Guide](docs/conflict-detection.md) for complete documentation.

### Undo/History Commands (NEW v0.10.0)

```bash
# Undo last operation (with confirmation)
clauxton undo

# View operation history
clauxton undo --history
clauxton undo --history --limit 20  # Show last 20 operations

# Force undo without confirmation
clauxton undo --yes
```

See [Error Handling Guide](docs/ERROR_HANDLING_GUIDE.md) for recovery strategies.

### Configuration Commands (NEW v0.10.0)

```bash
# Set confirmation mode
clauxton config set confirmation_mode always   # Strict (confirm every operation)
clauxton config set confirmation_mode auto     # Balanced (threshold-based, default)
clauxton config set confirmation_mode never    # Fast (no confirmations)

# Get configuration value
clauxton config get confirmation_mode

# List all configuration
clauxton config list
```

See [Configuration Guide](docs/configuration-guide.md) for all available settings.

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

### Current Architecture (v0.12.0)

```
clauxton/
├── core/                      # Core business logic
│   ├── models.py              # Pydantic data models ✅
│   ├── knowledge_base.py      # KB CRUD operations ✅
│   ├── task_manager.py        # Task lifecycle + DAG validation ✅
│   ├── search.py              # TF-IDF search implementation ✅
│   ├── conflict_detector.py   # Conflict detection ✅
│   ├── operation_history.py   # Undo/history tracking ✅
│   └── confirmation_manager.py # HITL confirmations ✅
├── semantic/                  # Semantic Intelligence (v0.12.0) 🆕
│   ├── embeddings.py          # Local embedding generation ✅
│   ├── vector_store.py        # FAISS vector store ✅
│   ├── indexer.py             # Index KB/Tasks/Files ✅
│   └── search_engine.py       # Semantic search engine ✅
├── analysis/                  # Git Analysis (v0.12.0) 🆕
│   ├── git_analyzer.py        # Commit analysis ✅
│   ├── pattern_extractor.py   # Pattern recognition ✅
│   ├── task_suggester.py      # Task suggestions ✅
│   └── decision_extractor.py  # Decision extraction ✅
├── proactive/                 # Proactive Intelligence (v0.13.0) 🔥
│   ├── config.py              # MonitorConfig ✅
│   ├── models.py              # FileEvent, DetectedPattern ✅
│   ├── file_monitor.py        # Real-time file monitoring ✅
│   └── event_processor.py     # Pattern detection ✅
├── intelligence/              # Code Intelligence (v0.11.0)
│   ├── symbol_extractor.py    # Multi-language symbol extraction ✅
│   ├── parser.py              # Tree-sitter parsers ✅
│   └── repository_map.py      # Repository indexing ✅
├── utils/                     # Utility modules
│   ├── yaml_utils.py          # Safe YAML I/O ✅
│   ├── file_utils.py          # Secure file operations ✅
│   ├── backup_manager.py      # Backup management ✅
│   └── logger.py              # Operation logging ✅
├── cli/                       # CLI interface
│   ├── main.py                # Main CLI + KB commands ✅
│   ├── tasks.py               # Task management commands ✅
│   ├── conflicts.py           # Conflict detection commands ✅
│   └── config.py              # Configuration commands ✅
└── mcp/                       # MCP Server integration
    └── server.py              # 34 MCP tools ✅
```

**Storage**:
- `.clauxton/knowledge-base.yml` - Knowledge Base entries
- `.clauxton/tasks.yml` - Task definitions
- `.clauxton/operation-history.jsonl` - Operation history (undo)
- `.clauxton/logs/` - Daily operation logs
- `.clauxton/backups/` - Automatic backups (last 10)
- `.clauxton/semantic/` - Vector indexes for semantic search (v0.12.0) 🆕
  - `kb_index.faiss` - Knowledge Base embeddings
  - `tasks_index.faiss` - Task embeddings
  - `files_index.faiss` - File embeddings

See [docs/architecture.md](docs/architecture.md) for complete design.

---

## 📚 Documentation

### User Guides
- [Quick Start Guide](docs/quick-start.md) - Get started in 5 minutes (CLI)
- **[Developer Workflow Guide](docs/DEVELOPER_WORKFLOW_GUIDE.md)** - Complete development workflow with examples and diagrams ✨ v0.10.0
- **[Installation Guide](docs/INSTALLATION_GUIDE.md)** - Shell alias setup, virtual environment isolation explained
- **[MCP Integration Guide](docs/MCP_INTEGRATION_GUIDE.md)** - Step-by-step Claude Code integration (36 tools)
- **[Context Intelligence Guide](docs/guides/CONTEXT_INTELLIGENCE_GUIDE.md)** - Work session analysis, action prediction, project context ✨ v0.13.0 🔥
- **[Workflow Examples](docs/guides/WORKFLOW_EXAMPLES.md)** - Real-world workflows with Context Intelligence ✨ v0.13.0 🔥
- **[Best Practices](docs/guides/BEST_PRACTICES.md)** - Optimization tips and proven patterns ✨ v0.13.0 🔥
- **[Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md)** - Common issues and solutions ✨ v0.13.0 🔥
- **[Semantic Search Guide](docs/SEMANTIC_SEARCH_GUIDE.md)** - Local semantic search with embeddings and FAISS ✨ v0.12.0
- **[Git Analysis Guide](docs/GIT_ANALYSIS_GUIDE.md)** - Pattern extraction and task suggestions from commits ✨ v0.12.0
- **[Proactive Monitoring Guide](docs/PROACTIVE_MONITORING_GUIDE.md)** - Real-time file watching and pattern detection ✨ v0.13.0 🔥
- **[Repository Map Guide](docs/REPOSITORY_MAP_GUIDE.md)** - Multi-language symbol extraction and search ✨ v0.11.0
- **[Daily Workflow Guide](docs/DAILY_WORKFLOW_GUIDE.md)** - Morning briefing, summaries, and trends ✨ v0.11.1
- [Tutorial: Your First Knowledge Base](docs/tutorial-first-kb.md) - 30-minute beginner guide
- [Use Cases & Examples](docs/use-cases.md) - Real-world scenarios and implementations
- [MCP Server Quick Start](docs/mcp-server-quickstart.md) - Get started with Claude Code
- [Task Management Guide](docs/task-management-guide.md) - Complete task management documentation
- [YAML Task Format Guide](docs/YAML_TASK_FORMAT.md) - YAML bulk import specification ✨ v0.10.0
- [Search Algorithm](docs/search-algorithm.md) - TF-IDF search explanation
- [YAML Format Reference](docs/yaml-format.md) - Complete Knowledge Base YAML specification
- **[MCP Server Documentation](docs/mcp-index.md)** - Complete MCP Server documentation (36 tools, split into focused guides) ✨ **Reorganized v0.13.0**
- [Conflict Detection Guide](docs/conflict-detection.md) - Complete conflict detection documentation
- [Configuration Guide](docs/configuration-guide.md) - Configuration management ✨ v0.10.0
- [Logging Guide](docs/logging-guide.md) - Operation logging system ✨ v0.10.0
- [Backup Guide](docs/backup-guide.md) - Backup management ✨ v0.10.0

### Developer Guides
- [Architecture Overview](docs/architecture.md) - System design and data flow
- [Development Guide](docs/development.md) - Setup and contribution guide
- [Technical Design](docs/technical-design.md) - Implementation details (⚠️ Currently in Japanese, English version coming in v0.10.1)
- [Error Handling Guide](docs/ERROR_HANDLING_GUIDE.md) - Error handling patterns ✨ v0.10.0
- [Performance Guide](docs/performance-guide.md) - Performance optimization ✨ v0.10.0
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions ✨ v0.10.0
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

---

## 🧪 Testing

Clauxton has comprehensive test coverage (86%, 1,637 tests) with optimized execution time.

### Quick Tests (Default - Recommended)

```bash
pytest  # ~2-3 minutes, 1,617 tests
```

Automatically excludes performance tests for fast feedback during development.

### Performance Tests

```bash
pytest -m "performance"  # ~70 minutes, 20 tests
```

Run before releases or when optimizing performance. Also runs automatically every Sunday via CI.

### All Tests

```bash
pytest -m ""  # ~80 minutes, 1,637 tests
```

Complete test suite including all performance tests.

### Coverage Report

```bash
pytest --cov=clauxton --cov-report=html
open htmlcov/index.html  # View detailed coverage report
```

### Test Statistics

- **Total Tests**: 1,637 (+270 from v0.11.2)
- **Default Tests**: 1,617 (excludes 20 performance tests)
- **Coverage**: 86% overall
  - v0.12.0 features: 91-100% coverage
  - Semantic modules: 91-98%
  - Analysis modules: 95-99%
- **CI Execution Time**: ~5-8 minutes
- **Performance Tests**: Weekly (Sundays 02:00 UTC) + Manual trigger

### CI/CD

- **Push/PR**: Runs default tests automatically (~8 minutes)
- **Weekly Schedule**: Performance tests every Sunday at 02:00 UTC
- **Manual Trigger**: Run performance tests via GitHub Actions "Run workflow" button

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📊 Project Status

| Phase | Status | Completion | Release |
|-------|--------|------------|---------|
| **Phase 0: Foundation** | ✅ Complete | 100% | v0.1.0 |
| **Phase 1: Core Engine** | ✅ Complete | 100% | v0.8.0 |
| **Phase 2: Conflict Detection** | ✅ Complete | 100% | v0.9.0-beta |
| **Phase 3: Enhanced UX** | ✅ Complete | 100% | v0.10.0 (2025-10-22) |
| **Phase 4: Repository Map** | ✅ Complete | 100% | v0.11.0 (2025-10-24) |
| **Phase 5: Semantic Intelligence** | ✅ Complete | 100% | **v0.12.0** (Released 2025-10-26) |
| **Phase 6: Proactive Intelligence** | 📋 Planned | 0% | v0.13.0 (target) |
| v1.0 Public Launch | 📋 Planned | 0% | v1.0.0 (target) |

**Phase 1 Complete** (v0.8.0 - Released 2025-10-19) ✅:
- ✅ Knowledge Base CRUD (6 MCP tools + CLI)
- ✅ TF-IDF Relevance Search (scikit-learn powered)
- ✅ Task Management (6 MCP tools + CLI)
- ✅ Auto Dependency Inference (file overlap detection)
- ✅ DAG Validation (cycle detection)
- ✅ Full Documentation (20 guides)
- ✅ **267 tests, 94% coverage**

**Phase 2 Complete** (v0.9.0-beta - Released 2025-10-20) ✅:
- 🆕 Conflict Detection (file-based conflict prediction)
- 🆕 Risk Scoring (LOW/MEDIUM/HIGH)
- 🆕 Safe Execution Order (topological sort + conflict-aware)
- 🆕 3 CLI Commands (detect, order, check)
- 🆕 3 MCP Tools (15 tools total)
- 🆕 **390 tests (+123), 94% coverage maintained**
- 🆕 Comprehensive migration guide
- 🆕 **Production ready release**

**Phase 3 Complete** (v0.10.0 - Released 2025-10-22) ✅:
- 🆕 Bulk Task Import/Export (YAML format, 30x faster)
- 🆕 Undo Functionality (reverse operations, view history)
- 🆕 Human-in-the-Loop Confirmations (3 modes: always/auto/never)
- 🆕 KB Documentation Export (Markdown generation)
- 🆕 Enhanced Validation (YAML safety, dependency validation)
- 🆕 2 new MCP Tools (17 tools total: undo_last_operation, get_recent_operations)
- 🆕 **758 tests (+368), 91% coverage achieved**
- 🆕 **13 comprehensive documentation files**
- 🆕 **Production ready, stable release**

**Phase 4 Complete** (v0.11.0 - Released 2025-10-24) ✅:
- 🗺️ **Repository Map** - Automatic codebase intelligence
- 🆕 **12-Language Support**: Python, JavaScript, TypeScript, Go, Rust, C++, Java, C#, PHP, Ruby, Swift, Kotlin
- 🆕 **Multi-Language Symbol Extraction**: Functions, classes, methods, interfaces, types with full metadata
- 🆕 **3 Search Modes**: Exact (fast substring), Fuzzy (typo-tolerant), Semantic (TF-IDF meaning-based)
- 🆕 **CLI Commands**: `repo index`, `repo search`, `repo status`
- 🆕 **2 new MCP Tools** (22 tools total: index_repository, search_symbols)
- 🆕 **Performance**: 1000+ files in 1-2s indexing, <0.01s search
- 🆕 **441 intelligence tests** (12 languages, 91% coverage)
- 🆕 **1,228 total tests** (+470 from v0.10.0)
- 🆕 **Production ready with comprehensive error handling**

**Phase 5 Complete** (v0.12.0 - Released 2025-10-26) ✅:
- 🤖 **Semantic Intelligence** - 100% local, no API costs
- 🆕 **Semantic Search**: Local embeddings (sentence-transformers) + FAISS vector store
  - `search_knowledge_semantic`, `search_tasks_semantic`, `search_files_semantic`
  - 126 semantic tests (embeddings, vector store, indexer, search engine)
  - 91-98% coverage, <200ms search speed
- 🆕 **Git Analysis**: Pattern extraction, decision detection from commits
  - `analyze_recent_commits`, `suggest_next_tasks`, `extract_decisions_from_commits`
  - 82 analysis tests (commit analysis, pattern extraction, task suggestions)
  - 95-99% coverage, <5s analysis for 100 commits
- 🆕 **Enhanced Context**: Project intelligence for Claude Code
  - `get_project_context`, `generate_project_summary`, `get_knowledge_graph`, `find_related_entries`
  - Rich project context, knowledge graph visualization
- 🆕 **10 new MCP Tools** (32 tools total: +3 semantic, +3 analysis, +4 context)
- 🆕 **208 new tests** (126 semantic + 82 analysis)
- 🆕 **1,637 total tests** (+409 from v0.11.0), 86% coverage
- 🆕 **Quality Grade A** (94.7/100), production ready

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

## 🔒 Security

Clauxton takes security seriously and follows industry best practices:

### Security Measures

- **Static Analysis**: Automated security scanning with [Bandit](https://github.com/PyCQA/bandit) in CI/CD
- **Safe YAML Loading**: Uses `yaml.safe_load()` to prevent code execution
- **Secure File Permissions**:
  - `.clauxton/` directory: 700 (owner only)
  - Data files: 600 (owner read/write only)
- **Input Validation**: All inputs validated with Pydantic models
- **No Command Injection**: No `shell=True` without sanitization
- **Path Traversal Protection**: All file operations validated against project root

### Security Scanning Results

Latest scan (Session 8, 2025-10-21):
- **Lines Scanned**: 5,609
- **Issues Found**: 0
- **Severity**: MEDIUM or higher checked
- **Status**: ✅ **PASSED**

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, please:
1. Email security concerns to the maintainers
2. Include: description, reproduction steps, potential impact, suggested fix
3. We will respond within 48 hours

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

---

## 🔗 Links

- **PyPI**: [https://pypi.org/project/clauxton/](https://pypi.org/project/clauxton/)
- **GitHub**: [https://github.com/nakishiyaman/clauxton](https://github.com/nakishiyaman/clauxton)
- **GitHub Releases**: [https://github.com/nakishiyaman/clauxton/releases](https://github.com/nakishiyaman/clauxton/releases)
- **Issues**: [https://github.com/nakishiyaman/clauxton/issues](https://github.com/nakishiyaman/clauxton/issues)
- **Discussions**: [https://github.com/nakishiyaman/clauxton/discussions](https://github.com/nakishiyaman/clauxton/discussions)

---

## 🙏 Acknowledgments

This project was inspired by the need for persistent context in AI-assisted development. Special thanks to the Claude Code team for building an extensible platform.

**Note**: Clauxton is an independent project and is not officially affiliated with Anthropic or Claude Code.

---

**Built with ❤️ for Claude Code users**
