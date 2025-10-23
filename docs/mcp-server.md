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

The MCP Server exposes 22 tools across 4 categories:
- **6 Knowledge Base tools** (kb_*)
- **7 Task Management tools** (task_*)
- **3 Conflict Detection tools** (detect_conflicts, recommend_safe_order, check_file_conflicts)
- **4 Repository Map tools** (index_repository, search_symbols, kb_export_docs, get_recent_logs)
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

## Troubleshooting

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

## Next Steps

- **Phase 1, Week 7**: Enhanced search with TF-IDF
- **Phase 1, Week 8**: Integration & Documentation
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
