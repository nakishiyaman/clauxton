# MCP Server Guide

**Model Context Protocol (MCP) Server for Clauxton**

This guide explains how to use the Clauxton MCP Server to integrate Knowledge Base and Task Management with Claude Code.

---

## Overview

The Clauxton MCP Server provides comprehensive tools for Claude Code through the Model Context Protocol. This allows Claude to:

**Knowledge Base**:
- Search your Knowledge Base for relevant context
- Add new entries during conversations
- List and retrieve existing entries
- Filter by category and tags

**Task Management** (✅ Week 5):
- Create and manage tasks with dependencies
- Track task status and priority
- Get AI-recommended next task to work on
- Auto-infer dependencies from file overlap
- Update and delete tasks

**Status**: ✅ Available (Phase 1, Week 3-5)

---

## Installation

### 1. Install Clauxton with MCP Support

```bash
# Install from source
cd clauxton
pip install -e .

# Verify MCP server is available
clauxton-mcp --help
```

### 2. Configure Claude Code

Add the Clauxton MCP Server to your Claude Code configuration:

**Location**: `.claude-plugin/mcp-servers.json` in your project

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "python",
      "args": [
        "-m",
        "clauxton.mcp.server"
      ],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

### 3. Initialize Your Project

```bash
# In your project directory
clauxton init
```

---

## Available Tools

The MCP Server exposes **36 tools** across 8 categories:
- **6 Knowledge Base tools** (kb_*)
- **7 Task Management tools** (task_*)
- **3 Conflict Detection tools** (detect_conflicts, recommend_safe_order, check_file_conflicts)
- **4 Repository Map tools** (index_repository, search_symbols, kb_export_docs, get_recent_logs)
- **2 Proactive Monitoring tools** (watch_project_changes, get_recent_changes) - 🔥 **NEW v0.13.0 Week 1**
- **2 Proactive Suggestion tools** (suggest_kb_updates, detect_anomalies) - 🔥 **NEW v0.13.0 Week 2**
- **3 Semantic Search tools** (search_knowledge_semantic, search_tasks_semantic, search_files_semantic)
- **3 Git Analysis tools** (analyze_recent_commits, suggest_next_tasks, extract_decisions_from_commits)
- **4 Context & Intelligence tools** (get_project_context, generate_project_summary, get_knowledge_graph, find_related_entries)
- **2 Operation tools** (undo_last_operation, get_recent_operations)

### 1. kb_search

Search the Knowledge Base for entries matching a query using **TF-IDF relevance ranking**.

**Search Algorithm**: TF-IDF (Term Frequency-Inverse Document Frequency)
- Results are automatically ranked by **relevance score** (0.0-1.0)
- More relevant entries appear first
- Considers keyword frequency and rarity across all entries
- Filters common words ("the", "a", "is") automatically

**Parameters**:
- `query` (string, required): Search query
- `category` (string, optional): Filter by category (architecture, constraint, decision, pattern, convention)
- `limit` (integer, optional): Max results (default: 10)

**Returns**: List of matching entries **ranked by relevance**, with:
- `id` - Entry ID (e.g., "KB-20251019-001")
- `title` - Entry title
- `category` - Category type
- `content` - Full entry content
- `tags` - Associated tags
- `created_at`, `updated_at` - Timestamps
- Results ordered by relevance (most relevant first)

**Example**:
```python
# Claude Code uses this internally
kb_search(query="FastAPI", category="architecture", limit=5)

# Returns entries ranked by relevance:
# [
#   {"id": "KB-001", "title": "FastAPI framework", ...},  # Most relevant
#   {"id": "KB-003", "title": "API design patterns", ...},  # Less relevant
#   ...
# ]
```

**Use Cases**:
- "Find all architecture decisions about APIs" - Gets most relevant API decisions first
- "Search for database-related constraints" - Ranks by database relevance
- "Show recent decisions about testing" - Finds testing-related entries

**Fallback Behavior**:
If `scikit-learn` is not installed, search automatically falls back to simple keyword matching (still functional but less sophisticated ranking).

See [Search Algorithm Documentation](search-algorithm.md) for technical details.

---

### 2. kb_add

Add a new entry to the Knowledge Base.

**Parameters**:
- `title` (string, required): Entry title (max 50 chars)
- `category` (string, required): Category (architecture, constraint, decision, pattern, convention)
- `content` (string, required): Detailed description
- `tags` (list[string], optional): Tags for categorization

**Returns**: Entry ID and success message

**Example**:
```python
kb_add(
    title="Use FastAPI framework",
    category="architecture",
    content="All backend APIs use FastAPI for async support and automatic docs.",
    tags=["backend", "api", "fastapi"]
)
# Returns: {"id": "KB-20251019-001", "message": "Successfully added entry: KB-20251019-001"}
```

**Use Cases**:
- "Remember that we use PostgreSQL for production"
- "Add this constraint to the Knowledge Base"
- "Save this architecture decision"

---

### 3. kb_list

List all Knowledge Base entries.

**Parameters**:
- `category` (string, optional): Filter by category

**Returns**: List of all entries (or filtered by category)

**Example**:
```python
# List all entries
kb_list()

# List only architecture entries
kb_list(category="architecture")
```

**Use Cases**:
- "Show all Knowledge Base entries"
- "List all architecture decisions"
- "What constraints do we have?"

---

### 4. kb_get

Get a specific Knowledge Base entry by ID.

**Parameters**:
- `entry_id` (string, required): Entry ID (format: KB-YYYYMMDD-NNN)

**Returns**: Complete entry details including version

**Example**:
```python
kb_get(entry_id="KB-20251019-001")
```

**Use Cases**:
- "Show me details of entry KB-20251019-001"
- "What does KB-20251019-005 say?"

---

### 5. kb_update

Update an existing Knowledge Base entry.

**Parameters**:
- `entry_id` (string, required): Entry ID to update
- `title` (string, optional): New title
- `content` (string, optional): New content
- `category` (string, optional): New category
- `tags` (list[string], optional): New tags

**Returns**: Updated entry with incremented version number

**Example**:
```python
kb_update(
    entry_id="KB-20251019-001",
    title="Updated Title",
    content="Updated content with new information"
)
```

**Use Cases**:
- "Update entry KB-20251019-001 with new requirements"
- "Change the category of KB-20251019-005 to decision"
- "Add tags to this Knowledge Base entry"

**Notes**:
- Version number automatically increments
- At least one field must be updated
- Original created_at is preserved, updated_at is set to now

---

### 6. kb_delete

Delete a Knowledge Base entry.

**Parameters**:
- `entry_id` (string, required): Entry ID to delete

**Returns**: Success message with deleted entry ID and title

**Example**:
```python
kb_delete(entry_id="KB-20251019-001")
```

**Use Cases**:
- "Delete the outdated entry KB-20251019-003"
- "Remove KB-20251019-007 from the Knowledge Base"

**Notes**:
- This is a hard delete (entry is permanently removed)
- No confirmation prompt in MCP (CLI has confirmation)

---

## Usage Examples

### Example 1: Search for Context

**User**: "What's our API architecture?"

**Claude Code**:
1. Uses `kb_search(query="API architecture", category="architecture")`
2. Retrieves entries about API design
3. Provides answer based on Knowledge Base

**Response**: "According to your Knowledge Base (KB-20251019-001), all backend APIs use FastAPI framework for async support and automatic OpenAPI documentation."

---

### Example 2: Add Decision

**User**: "Remember that we decided to use PostgreSQL 15+ for production."

**Claude Code**:
1. Uses `kb_add(title="PostgreSQL for production", category="decision", content="Use PostgreSQL 15+ for production databases.", tags=["database", "postgresql"])`
2. Returns entry ID

**Response**: "I've added this decision to your Knowledge Base as entry KB-20251019-002."

---

### Example 3: List Constraints

**User**: "What constraints do we have?"

**Claude Code**:
1. Uses `kb_list(category="constraint")`
2. Retrieves all constraint entries
3. Formats as a list

**Response**: "You have 3 constraints in your Knowledge Base:
1. KB-20251019-003: Support IE11
2. KB-20251019-007: Max response time 200ms
3. KB-20251019-012: GDPR compliance required"

---

## Technical Details

### Server Implementation

The MCP Server is built using the official `mcp` Python SDK:

```python
from mcp.server.fastmcp import FastMCP
from clauxton.core.knowledge_base import KnowledgeBase

mcp = FastMCP("Clauxton Knowledge Base")

@mcp.tool()
def kb_search(query: str, category: Optional[str] = None, limit: int = 10):
    """Search the Knowledge Base."""
    kb = KnowledgeBase(Path.cwd())
    results = kb.search(query, category=category, limit=limit)
    return [entry.model_dump() for entry in results]
```

**Key Features**:
- **FastMCP**: Simplified MCP server creation with decorators
- **Type Safety**: Full Pydantic validation
- **Error Handling**: Proper error propagation to Claude Code
- **JSON Serialization**: Automatic datetime conversion

---

### Transport

The server uses **stdio transport** for communication with Claude Code:

- **Input**: JSON-RPC requests via stdin
- **Output**: JSON-RPC responses via stdout
- **Protocol**: Model Context Protocol v1.0

---

### Project Context

The MCP Server operates in the **current working directory**:

```python
kb = KnowledgeBase(Path.cwd())
```

This means:
- ✅ Works with `.clauxton/knowledge-base.yml` in your project
- ✅ No configuration needed (uses project's Knowledge Base)
- ✅ Multiple projects = isolated Knowledge Bases

---

## Troubleshooting

### "Server not found"

**Problem**: Claude Code can't find the MCP server.

**Solution**:
1. Check `.claude-plugin/mcp-servers.json` exists
2. Verify `python -m clauxton.mcp.server` works
3. Ensure Clauxton is installed (`pip list | grep clauxton`)

---

### "Knowledge Base not initialized"

**Problem**: MCP tools return errors about missing `.clauxton/`.

**Solution**:
```bash
clauxton init
```

---

### "Module not found: mcp"

**Problem**: MCP SDK not installed.

**Solution**:
```bash
pip install mcp
```

---

### "Permission denied"

**Problem**: Can't write to Knowledge Base.

**Solution**:
Check file permissions:
```bash
ls -la .clauxton/
# Should be: drwx------ (700) for directory
#            -rw------- (600) for knowledge-base.yml
```

---

## Testing

### Unit Tests

Test the MCP server locally:

```bash
pytest tests/mcp/test_server.py -v
```

**Coverage**:
- Server instantiation
- Tool registration
- Tool execution (mocked)
- Error handling

---

### Manual Testing

Test the server manually:

```bash
# Start server (stdio mode)
python -m clauxton.mcp.server

# Server is now waiting for JSON-RPC requests on stdin
```

Send a test request (JSON-RPC format):
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "kb_search",
    "arguments": {
      "query": "API"
    }
  },
  "id": 1
}
```

---

## Task Management Tools (✅ Week 5)

The MCP Server provides 6 tools for complete task management:

### `task_add`

Create a new task with dependencies, files, and Knowledge Base references.

**Parameters**:
- `name` (string, required): Task name
- `description` (string, optional): Detailed description
- `priority` (string, optional): low | medium | high | critical (default: medium)
- `depends_on` (array, optional): List of task IDs this depends on
- `files` (array, optional): List of files this task will modify
- `kb_refs` (array, optional): Related Knowledge Base entry IDs
- `estimate` (float, optional): Estimated hours to complete

**Returns**: Task ID and success message

**Example**:
```json
{
  "name": "task_add",
  "arguments": {
    "name": "Add user authentication",
    "description": "Implement JWT-based authentication",
    "priority": "high",
    "depends_on": ["TASK-001"],
    "files": ["src/auth.py", "tests/test_auth.py"],
    "kb_refs": ["KB-20251019-005"],
    "estimate": 4.5
  }
}
```

### `task_list`

List all tasks with optional filters.

**Parameters**:
- `status` (string, optional): pending | in_progress | completed | blocked
- `priority` (string, optional): low | medium | high | critical

**Returns**: List of tasks with details

**Example**:
```json
{
  "name": "task_list",
  "arguments": {
    "status": "pending",
    "priority": "high"
  }
}
```

### `task_get`

Get detailed information about a specific task.

**Parameters**:
- `task_id` (string, required): Task ID (e.g., TASK-001)

**Returns**: Complete task details

**Example**:
```json
{
  "name": "task_get",
  "arguments": {
    "task_id": "TASK-001"
  }
}
```

### `task_update`

Update task fields (status, priority, name, description).

**Parameters**:
- `task_id` (string, required): Task ID to update
- `status` (string, optional): New status
- `priority` (string, optional): New priority
- `name` (string, optional): New task name
- `description` (string, optional): New description

**Note**: Timestamps (`started_at`, `completed_at`) are set automatically when status changes.

**Example**:
```json
{
  "name": "task_update",
  "arguments": {
    "task_id": "TASK-001",
    "status": "in_progress"
  }
}
```

### `task_next`

Get AI-recommended next task to work on.

Returns the highest priority task whose dependencies are completed.

**Parameters**: None

**Returns**: Next task details or null if no tasks available

**Example**:
```json
{
  "name": "task_next",
  "arguments": {}
}
```

### `task_delete`

Delete a task.

**Parameters**:
- `task_id` (string, required): Task ID to delete

**Returns**: Success message

**Note**: Cannot delete tasks that have dependents. Delete dependent tasks first.

**Example**:
```json
{
  "name": "task_delete",
  "arguments": {
    "task_id": "TASK-001"
  }
}
```

---

## Auto-Dependency Inference (✅ Week 5)

Clauxton automatically infers task dependencies based on file overlap:

1. When multiple tasks edit the same files
2. Earlier tasks (by `created_at`) become dependencies
3. Inferred dependencies merge with manual dependencies
4. No duplicates in the final dependency list

**Example**:
```
TASK-001: Edit src/main.py, src/utils.py
TASK-002: Edit src/main.py
→ TASK-002 automatically depends on TASK-001 (file overlap)
```

This ensures tasks that modify the same files are executed in the correct order, preventing conflicts.

---

## Repository Map Tools (v0.11.0+)

### 1. index_repository

Index a repository to build a symbol map for fast code navigation and search.

**Parameters**:
- `root_path` (string, optional): Root directory to index (defaults to current working directory)

**Returns**: Dictionary with:
- `status` - "success" or "error"
- `files_indexed` - Number of files processed
- `symbols_found` - Number of symbols extracted
- `duration` - Indexing duration in seconds
- `by_type` - Files breakdown by type (source/test/config/docs/other)
- `by_language` - Files breakdown by language (python/javascript/etc)
- `indexed_at` - Timestamp of indexing

**Example**:
```python
# Index current project
result = index_repository()
# → {"status": "success", "files_indexed": 50, "symbols_found": 200, ...}

# Index specific directory
result = index_repository(root_path="/path/to/project")
```

**Features**:
- Respects `.gitignore` patterns
- Supports Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, and more
- Extracts functions, classes, methods with signatures and docstrings
- Stores index in `.clauxton/map/` directory
- Typical performance: 1000+ files in <2 seconds

**Use Cases**:
1. **Initial Setup**: Index repository when starting work on a project
2. **Refresh Index**: Re-index after major changes
3. **Symbol Discovery**: Find all functions/classes in codebase
4. **Codebase Understanding**: Get overview of project structure

---

### 2. search_symbols

Search for symbols (functions, classes, methods) in the indexed repository.

**Parameters**:
- `query` (string, required): Search query (symbol name or description)
- `mode` (string, optional): Search algorithm - "exact", "fuzzy", or "semantic" (default: "exact")
- `limit` (integer, optional): Maximum results to return (default: 10)
- `root_path` (string, optional): Root directory of indexed repository (defaults to cwd)

**Returns**: Dictionary with:
- `status` - "success" or "error"
- `count` - Number of results found
- `symbols` - List of matching symbols with metadata:
  - `name` - Symbol name
  - `type` - "function", "class", or "method"
  - `file_path` - Full path to source file
  - `line_start` - Starting line number
  - `line_end` - Ending line number
  - `docstring` - Symbol documentation (if available)
  - `signature` - Function/method signature

**Search Modes**:

**exact** (default): Fast substring matching with priority scoring
- Exact match: highest priority
- Starts with: high priority
- Contains: medium priority
- Docstring: low priority
- Example: "auth" finds "authenticate_user", "get_auth_token"

**fuzzy**: Typo-tolerant using Levenshtein distance
- Handles typos and misspellings
- Similarity threshold: 0.4
- Example: "authentcate" finds "authenticate_user"

**semantic**: Meaning-based search using TF-IDF
- Searches by concept, not just text
- Requires scikit-learn (falls back to exact if unavailable)
- Example: "user login" finds "authenticate_user", "verify_credentials"

**Examples**:
```python
# Exact search (default)
result = search_symbols(query="authenticate")
# → {"status": "success", "count": 2, "symbols": [...]}

# Fuzzy search (typo-tolerant)
result = search_symbols(query="authentcate", mode="fuzzy")
# → Finds "authenticate_user" despite typo

# Semantic search (by meaning)
result = search_symbols(query="user login", mode="semantic")
# → Finds "authenticate_user", "verify_credentials", etc.
```

**Use Cases**:
1. **Find Function**: Locate specific function by name
2. **Explore API**: Discover related functions (semantic search)
3. **Code Navigation**: Jump to symbol definition
4. **Refactoring**: Find all usages of a symbol
5. **Documentation**: Find functions by description

**Note**: Repository must be indexed first using `index_repository`.

---

## Repository Map Integration Workflow

Here's a typical workflow for using Repository Map with Claude Code:

### 1. Initial Setup
```python
# Claude Code automatically calls this when starting work
result = index_repository()
# → Indexes entire project in ~1-2 seconds
```

### 2. Exploration Phase
```python
# Find authentication-related code
symbols = search_symbols(query="authenticate", mode="exact")
# → Returns all functions/classes with "authenticate" in name

# Discover related functionality
symbols = search_symbols(query="user login", mode="semantic")
# → Returns authenticate_user, verify_credentials, check_session, etc.
```

### 3. Implementation Phase
```python
# Find specific function to modify
symbols = search_symbols(query="validate_password", mode="exact", limit=1)
# → Jump to line 45 in auth/validators.py

# After making changes, re-index if needed
result = index_repository()
# → Updates symbol map with new/modified functions
```

### Performance Notes
- **Indexing**: 1000+ files in <2 seconds
- **Search**: <0.01s for exact, <0.1s for semantic
- **Memory**: ~1MB per 1000 symbols
- **Storage**: JSON files in `.clauxton/map/` (~10-50KB per project)

### Transparent Usage in Claude Code
Claude Code automatically:
1. **Indexes on project open** (if not indexed recently)
2. **Searches when needed** (user mentions "find", "search", "where is")
3. **Re-indexes after major changes** (new files, bulk edits)

You don't need to manually call these tools - Claude Code handles it transparently.

---

## Proactive Monitoring Tools (v0.13.0+)

### 1. watch_project_changes

Enable or disable real-time file monitoring to track changes and detect patterns.

**Parameters**:
- `enabled` (boolean, required): True to start monitoring, False to stop

**Returns**: Dictionary with:
- `status` - "success" or "error"
- `monitoring` - Current monitoring state (true/false)
- `message` - Status message
- `config` - Monitoring configuration (when enabled):
  - `watch_patterns` - File patterns being watched
  - `ignore_patterns` - Ignored file patterns
  - `debounce_seconds` - Debounce interval

**Example**:
```python
# Enable monitoring
result = watch_project_changes(enabled=True)
# → {"status": "success", "monitoring": true, "message": "File monitoring started", ...}

# Disable monitoring
result = watch_project_changes(enabled=False)
# → {"status": "success", "monitoring": false, "message": "File monitoring stopped"}
```

**Features**:
- Real-time file change detection using `watchdog`
- Configurable file patterns (supports `.py`, `.js`, `.ts`, `.go`, etc.)
- Automatic ignore patterns (`.git/`, `node_modules/`, `__pycache__/`, etc.)
- Debouncing (500ms) to avoid duplicate events
- Background monitoring (non-blocking)

**Use Cases**:
1. **Continuous Monitoring**: Track ongoing development activity
2. **Pattern Detection**: Identify refactoring, bulk edits, new features
3. **Context Awareness**: Provide real-time suggestions based on changes
4. **Workflow Automation**: Auto-update KB entries from code changes

**Note**: Monitoring runs in background. Use `get_recent_changes()` to retrieve detected changes.

---

### 2. get_recent_changes

Get recent file changes and detected patterns from the monitoring system.

**Parameters**:
- `minutes` (integer, optional): Time window in minutes (default: 60)

**Returns**: Dictionary with:
- `status` - "success" or "error"
- `monitoring_active` - Whether monitoring is currently running
- `time_window` - Requested time window
- `changes` - List of file change events:
  - `timestamp` - When change occurred (ISO 8601)
  - `event_type` - "modified", "created", "deleted", "moved"
  - `file_path` - Affected file path
  - `metadata` - Additional event details
- `patterns` - Detected patterns with confidence scores:
  - `type` - Pattern type (bulk_edit, new_feature, refactoring, cleanup, config_change)
  - `confidence` - Confidence score (0.0-1.0)
  - `description` - Human-readable description
  - `files_involved` - List of affected files
  - `detected_at` - When pattern was detected

**Pattern Types**:
- **bulk_edit**: Same file modified multiple times rapidly
- **new_feature**: Multiple new files created in short time
- **refactoring**: Files renamed or moved together
- **cleanup**: Files deleted in bulk
- **config_change**: Configuration files modified

**Example**:
```python
# Get last hour of changes
result = get_recent_changes(minutes=60)
# → {
#   "status": "success",
#   "monitoring_active": true,
#   "changes": [
#     {"timestamp": "2025-10-26T10:30:00", "event_type": "modified", "file_path": "src/auth.py"},
#     {"timestamp": "2025-10-26T10:31:00", "event_type": "created", "file_path": "tests/test_auth.py"}
#   ],
#   "patterns": [
#     {
#       "type": "new_feature",
#       "confidence": 0.85,
#       "description": "New feature development detected",
#       "files_involved": ["src/auth.py", "tests/test_auth.py"],
#       "detected_at": "2025-10-26T10:31:30"
#     }
#   ]
# }

# Get last 10 minutes
result = get_recent_changes(minutes=10)
```

**Use Cases**:
1. **Progress Summary**: "What have I worked on in the last hour?"
2. **Pattern Recognition**: "Am I refactoring or adding features?"
3. **Context for Suggestions**: "Based on recent changes, suggest next tasks"
4. **Activity Log**: Track development patterns over time

**Note**: Returns empty lists if monitoring is not active or no changes in time window.

---

## Proactive Monitoring Workflow

Here's a typical workflow for using Proactive Monitoring with Claude Code:

### 1. Start Monitoring
```python
# Claude Code automatically calls this when starting a work session
result = watch_project_changes(enabled=True)
# → Monitoring starts in background
```

### 2. Development Phase
```python
# User edits multiple files...
# src/auth.py (10:30:00)
# src/auth.py (10:30:15) - quick fix
# tests/test_auth.py (10:31:00) - add tests
```

### 3. Check Recent Activity
```python
# Claude Code periodically calls this (or when user asks)
changes = get_recent_changes(minutes=30)
# → Returns:
#   - 3 file changes (2 edits to auth.py, 1 new test file)
#   - Pattern: "bulk_edit" (auth.py modified rapidly)
#   - Pattern: "new_feature" (new test file suggests feature work)
```

### 4. Proactive Suggestions
Based on detected patterns, Claude Code can:
- **Bulk Edit Pattern**: "I notice you're iterating on auth.py. Need help with the logic?"
- **New Feature Pattern**: "You're adding authentication. Should I check for related KB entries?"
- **Refactoring Pattern**: "Detected file moves. Want me to update import statements?"

### 5. End Session
```python
# Optional: Stop monitoring when done
result = watch_project_changes(enabled=False)
```

### Performance Characteristics
- **Event Processing**: <5ms per file change
- **Pattern Detection**: <10ms (runs after debounce)
- **Memory Footprint**: ~2MB for 1000 events
- **Background CPU**: <1% (idle when no changes)

### Transparent Usage in Claude Code
Claude Code can automatically:
1. **Start monitoring** when project opens
2. **Check patterns** periodically (every 5-10 minutes)
3. **Provide suggestions** based on detected patterns
4. **Stop monitoring** when project closes

You can also manually trigger these via natural language:
- "Start monitoring my files"
- "What have I changed in the last hour?"
- "Stop file monitoring"

---

## Troubleshooting

### Proactive Monitoring Issues

**Issue**: `watch_project_changes` returns "already running" error
- **Solution**: Call `watch_project_changes(enabled=False)` first to stop existing monitor
- **Alternative**: Check if monitoring is active with `get_recent_changes()`

**Issue**: `get_recent_changes` returns empty results
- **Solution**: Ensure monitoring is enabled with `watch_project_changes(enabled=True)`
- **Verify**: Check `monitoring_active` field in response

**Issue**: Too many events being captured
- **Solution**: Adjust `ignore_patterns` in MonitorConfig
- **Common patterns**: `*.pyc`, `*.log`, `.DS_Store`, `node_modules/`
- **Edit**: `.clauxton/monitor-config.json` (if exists)

**Issue**: Patterns not being detected
- **Verify**: Enough file changes occurred (patterns need ≥2 files or ≥3 edits)
- **Check**: Time window is sufficient (use `minutes=120` for longer history)
- **Debug**: Check event count in `changes` list

**Issue**: High CPU usage during monitoring
- **Solution**: Add more ignore patterns to reduce event volume
- **Verify**: Large directories like `node_modules/`, `.venv/` are ignored
- **Alternative**: Disable monitoring when not needed

### Repository Map Issues

**Issue**: `search_symbols` returns empty results
- **Solution**: Run `index_repository()` first to build the symbol map
- **Check**: Ensure `.clauxton/map/index.json` exists

**Issue**: Symbols not found after adding new code
- **Solution**: Re-run `index_repository()` to refresh the index
- **Tip**: Index is cached, rebuild after significant changes

**Issue**: Slow indexing performance
- **Check**: Project size (>10,000 files may take longer)
- **Solution**: Add large directories to `.gitignore` (node_modules, .venv, etc.)
- **Verify**: Run `du -sh .clauxton/map/` to check index size

**Issue**: Unicode errors during indexing
- **Solution**: Ensure files are UTF-8 encoded
- **Note**: Binary files are automatically skipped

**Issue**: `semantic` search mode not working
- **Solution**: Install scikit-learn: `pip install scikit-learn`
- **Fallback**: Automatically falls back to `exact` mode if unavailable

### General MCP Issues

**Issue**: MCP Server not connecting
- **Check**: `.claude-plugin/mcp-servers.json` configuration
- **Verify**: `clauxton-mcp --help` works
- **Solution**: Restart Claude Code after configuration changes

**Issue**: "Clauxton not initialized" error
- **Solution**: Run `clauxton init` in project root
- **Verify**: `.clauxton/` directory exists

**Issue**: Permission errors
- **Check**: `.clauxton/` directory permissions (should be 700)
- **Solution**: `chmod 700 .clauxton && chmod 600 .clauxton/*.yml`

---

---

## Context Intelligence Tools (v0.13.0 Week 3 Day 2) 🚀 NEW

### analyze_work_session

**Analyze current work session for productivity insights.**

Provides comprehensive analysis of the current work session including:
- Duration tracking (how long you've been working)
- Focus score based on file switching behavior (0.0-1.0)
- Break detection (gaps in activity)
- Active work periods (time between breaks)
- File switch count (unique files modified)

**Parameters**: None

**Returns**: Dictionary with:
- `status`: "success", "no_session", or "error"
- `duration_minutes`: Session duration in minutes
- `focus_score`: Focus score (0.0-1.0), higher = more focused
  - 0.8+ = high focus (few file switches)
  - 0.5-0.8 = medium focus
  - <0.5 = low focus (many file switches)
- `breaks`: List of detected breaks with:
  - `start`: Break start timestamp (ISO format)
  - `duration_minutes`: Break duration
- `file_switches`: Number of unique files modified
- `active_periods`: List of active work periods with:
  - `start`: Period start timestamp (ISO format)
  - `end`: Period end timestamp (ISO format)

**Example**:
```python
result = analyze_work_session()

if result["status"] == "success":
    print(f"Session duration: {result['duration_minutes']} minutes")
    print(f"Focus score: {result['focus_score']}")
    print(f"Breaks detected: {len(result['breaks'])}")
    print(f"Files modified: {result['file_switches']}")
```

**Use Cases**:
1. **Productivity Tracking**: Understand work patterns and session quality
2. **Break Reminders**: Detect long sessions without breaks
3. **Focus Analysis**: Identify high/low focus periods for optimization
4. **Session Planning**: Optimize work sessions based on historical data

---

### predict_next_action

**Predict likely next action based on project context.**

Uses rule-based prediction analyzing:
- File change patterns (test files, implementation files)
- Git context (uncommitted changes, branch status)
- Time context (morning, afternoon, evening, night)
- Work session patterns (focus, breaks, duration)

**Parameters**: None

**Returns**: Dictionary with:
- `status`: "success" or "error"
- `action`: Predicted action name (see below)
- `task_id`: Related task ID (if available)
- `confidence`: Confidence score (0.0-1.0)
  - 0.8+ = high confidence
  - 0.5-0.8 = medium confidence
  - <0.5 = low confidence
- `reasoning`: Explanation of why this action was predicted

**Possible Actions**:
- `run_tests`: Many files changed without recent test runs
- `write_tests`: Implementation files changed, no test files
- `commit_changes`: Changes ready, feature complete
- `create_pr`: Branch ahead of main, commits ready
- `take_break`: Long session without breaks detected
- `morning_planning`: Morning time, no activity yet
- `resume_work`: Coming back from break
- `review_code`: Many changes, might need review
- `no_clear_action`: No strong pattern detected

**Example**:
```python
result = predict_next_action()

if result["status"] == "success":
    print(f"Recommended action: {result['action']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Reasoning: {result['reasoning']}")

    if result['task_id']:
        print(f"Related task: {result['task_id']}")
```

**Use Cases**:
1. **Smart Suggestions**: Proactively suggest next steps in workflow
2. **Workflow Optimization**: Guide through development workflow automatically
3. **Context Switching**: Help resume work after breaks or interruptions
4. **Quality Assurance**: Remind to run tests or review code at appropriate times

---

### get_current_context

**Get comprehensive current project context.**

Provides real-time project context including:
- Git branch and status
- Active files (recently modified)
- Recent commits
- Current task (if available)
- Time context (morning/afternoon/evening/night)
- Work session analysis (duration, focus, breaks)
- Predicted next action
- Uncommitted changes and diff stats

**Parameters**:
- `include_prediction` (boolean, optional): Include next action prediction (default: True)
  - Set to False for faster response without prediction

**Returns**: Dictionary with:
- `status`: "success" or "error"
- `current_branch`: Git branch name
- `active_files`: List of recently modified files
- `recent_commits`: Recent commit information
- `current_task`: Current task ID (if available)
- `time_context`: "morning", "afternoon", "evening", or "night"
- `work_session_start`: Session start timestamp (ISO format)
- `last_activity`: Last detected activity timestamp (ISO format)
- `is_feature_branch`: Whether current branch is a feature branch
- `is_git_repo`: Whether project is a git repository
- `session_duration_minutes`: Current session duration
- `focus_score`: Focus score (0.0-1.0)
- `breaks_detected`: Number of breaks in session
- `predicted_next_action`: Predicted next action (if `include_prediction=True`):
  - `action`: Action name
  - `confidence`: Confidence score
  - `reasoning`: Explanation
- `uncommitted_changes`: Number of uncommitted changes
- `diff_stats`: Git diff statistics:
  - `additions`: Lines added
  - `deletions`: Lines deleted
  - `files_changed`: Number of files changed

**Example**:
```python
# Get full context with prediction
context = get_current_context()

print(f"Branch: {context['current_branch']}")
print(f"Session: {context['session_duration_minutes']} min")
print(f"Focus: {context['focus_score']}")
print(f"Changes: {context['uncommitted_changes']} uncommitted")

if context['predicted_next_action']:
    action = context['predicted_next_action']
    print(f"Next: {action['action']} ({action['confidence']:.2f})")

# Get context without prediction (faster)
context = get_current_context(include_prediction=False)
```

**Use Cases**:
1. **Context Awareness**: Understand current project state at a glance
2. **Smart Suggestions**: Provide context-aware recommendations
3. **Session Tracking**: Monitor work session progress
4. **Status Updates**: Quick overview of current work

**Performance**:
- Fast response (<100ms typical)
- Cached for 30 seconds for performance
- Prediction adds ~20ms if enabled

---

## Proactive Suggestion Tools (v0.13.0 Week 2) 🔥 NEW

### suggest_kb_updates

**Analyze recent file changes to suggest Knowledge Base documentation opportunities.**

Intelligently analyzes recent development activity and suggests KB entries for:
- Module-wide changes (architecture decisions)
- New features (feature documentation)
- Configuration changes (setup documentation)
- Documentation gaps (missing docs)

**Parameters**:
- `threshold` (float, optional): Minimum confidence threshold (default: 0.7, range: 0.0-1.0)
- `minutes` (int, optional): Time window to analyze in minutes (default: 10)
- `max_suggestions` (int, optional): Maximum number of suggestions to return (default: 5)

**Returns**: Dictionary with:
- `status`: "success", "no_suggestions", "no_changes", or "error"
- `suggestion_count`: Number of suggestions returned
- `time_window_minutes`: Time window analyzed
- `threshold`: Confidence threshold used
- `suggestions`: List of KB/documentation suggestions with:
  - `type`: "kb_entry" or "documentation"
  - `title`: Suggestion title
  - `description`: Detailed description
  - `confidence`: Confidence score (0.0-1.0)
  - `priority`: "low", "medium", "high", or "critical"
  - `affected_files`: List of relevant files
  - `reasoning`: Explanation of why this suggestion was made
  - `metadata`: Additional context
  - `created_at`: Timestamp

**Example**:
```python
# After refactoring authentication module
suggest_kb_updates(threshold=0.7, minutes=30, max_suggestions=5)

# Returns:
{
  "status": "success",
  "suggestion_count": 2,
  "suggestions": [
    {
      "type": "kb_entry",
      "title": "Document changes in src/auth",
      "description": "3 files modified in authentication module",
      "confidence": 0.85,
      "priority": "medium",
      "affected_files": ["src/auth/login.py", "src/auth/token.py"],
      "reasoning": "Multiple files in same module indicate architectural change"
    }
  ]
}
```

**Use Cases**:
- **Auto-Documentation**: "What should I document after this refactoring?"
- **Knowledge Capture**: "Any KB entries I should create based on recent work?"
- **Team Communication**: "What context should I share with the team?"

**Performance**: <200ms for 10 files, <500ms for 100 files

---

### detect_anomalies

**Detect unusual development activity patterns with severity levels.**

Analyzes recent file changes to identify anomalies that may require attention:
1. **Rapid changes** (many files in short time)
2. **Mass deletions** (5+ files deleted)
3. **Weekend activity** (work on Saturday/Sunday)
4. **Late-night activity** (work 10 PM - 6 AM)

**Parameters**:
- `minutes` (int, optional): Time window to analyze in minutes (default: 60)
- `severity_threshold` (string, optional): Minimum severity level to return
  Values: "low" (all), "medium" (medium+), "high" (high+), "critical" (critical only)

**Returns**: Dictionary with:
- `status`: "success", "no_anomalies", "no_changes", or "error"
- `anomaly_count`: Number of anomalies detected
- `time_window_minutes`: Time window analyzed
- `severity_threshold`: Severity threshold used
- `anomalies`: List of detected anomalies (sorted by severity: critical → high → medium → low) with:
  - `type`: "anomaly"
  - `title`: Anomaly description
  - `description`: Detailed explanation
  - `confidence`: Confidence score (0.0-1.0)
  - `priority`: Task priority level
  - `severity`: "low", "medium", "high", or "critical"
  - `affected_files`: List of relevant files
  - `reasoning`: Explanation
  - `metadata`: Additional data (e.g., change_count, deletion_count, ratios)
  - `created_at`: Timestamp

**Severity Levels**:
- **critical**: 20+ rapid changes (immediate attention required)
- **high**: 10+ rapid changes, mass deletions (review soon)
- **medium**: 5+ rapid changes, weekend work (worth noting)
- **low**: Late-night activity, minor patterns (informational)

**Example**:
```python
# Check for anomalies in last hour
detect_anomalies(minutes=60, severity_threshold="medium")

# Returns:
{
  "status": "success",
  "anomaly_count": 2,
  "anomalies": [
    {
      "type": "anomaly",
      "title": "Rapid changes: 15 changes in 10 minutes",
      "description": "15 files changed very quickly. This may indicate automated refactoring or mass find-replace.",
      "confidence": 0.82,
      "priority": "high",
      "severity": "high",
      "metadata": {"change_count": 15, "time_span_minutes": 10}
    },
    {
      "type": "anomaly",
      "title": "Mass deletion: 8 files deleted",
      "description": "8 files have been deleted. Ensure this is intentional and update documentation if needed.",
      "confidence": 0.77,
      "priority": "high",
      "severity": "medium"
    }
  ]
}
```

**Use Cases**:
- **Quality Assurance**: "Any unusual patterns in my recent work?"
- **Work-Life Balance**: "Am I working too much late at night?"
- **Risk Detection**: "Any potentially risky changes I should review?"
- **Team Health**: "How are team work patterns looking?"

**Performance**: <150ms for 20 files, <300ms for 100 files

---

## Next Steps

- **v0.13.0 Week 2**: Proactive suggestion tools (✅ Complete)
- **v0.13.0 Week 3-7**: User behavior tracking & enhanced context awareness
- **Phase 2**: Pre-merge conflict detection

See [Phase 1 Plan](phase-1-plan.md) for roadmap.

---

## References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Clauxton Architecture](architecture.md)
- [Knowledge Base Format](yaml-format.md)

---

**Status**: ✅ Week 3-5 Complete - MCP Server with Knowledge Base + Task Management tools functional
