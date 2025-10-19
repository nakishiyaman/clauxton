# MCP Server Guide

**Model Context Protocol (MCP) Server for Clauxton Knowledge Base**

This guide explains how to use the Clauxton MCP Server to integrate Knowledge Base with Claude Code.

---

## Overview

The Clauxton MCP Server provides tools for Claude Code to interact with your Knowledge Base through the Model Context Protocol. This allows Claude to:

- Search your Knowledge Base for relevant context
- Add new entries during conversations
- List and retrieve existing entries
- Filter by category and tags

**Status**: ✅ Available (Phase 1, Week 3)

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
    "clauxton-kb": {
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

The MCP Server exposes 4 tools that Claude Code can use:

### 1. kb_search

Search the Knowledge Base for entries matching a query.

**Parameters**:
- `query` (string, required): Search query
- `category` (string, optional): Filter by category (architecture, constraint, decision, pattern, convention)
- `limit` (integer, optional): Max results (default: 10)

**Returns**: List of matching entries with id, title, category, content, tags, timestamps

**Example**:
```python
# Claude Code uses this internally
kb_search(query="FastAPI", category="architecture", limit=5)
```

**Use Cases**:
- "Find all architecture decisions about APIs"
- "Search for database-related constraints"
- "Show recent decisions about testing"

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

## Next Steps

- **Phase 1, Week 4**: Add Task Management tools
- **Phase 1, Week 5**: Add Dependency Analysis tools
- **Phase 1, Week 7**: Enhanced search with TF-IDF

See [Phase 1 Plan](phase-1-plan.md) for roadmap.

---

## References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Clauxton Architecture](architecture.md)
- [Knowledge Base Format](yaml-format.md)

---

**Status**: ✅ Week 3 Complete - MCP Server with Knowledge Base tools functional
