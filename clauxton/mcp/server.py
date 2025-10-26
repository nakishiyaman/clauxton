"""
MCP Server for Clauxton Knowledge Base.

Provides tools for interacting with the Knowledge Base through
the Model Context Protocol.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from mcp.server.fastmcp import FastMCP

from clauxton.core.conflict_detector import ConflictDetector
from clauxton.core.knowledge_base import KnowledgeBase
from clauxton.core.models import KnowledgeBaseEntry, Task
from clauxton.core.task_manager import TaskManager
from clauxton.intelligence.repository_map import RepositoryMap
from clauxton.proactive.config import MonitorConfig
from clauxton.proactive.event_processor import EventProcessor
from clauxton.proactive.file_monitor import FileMonitor

# Create MCP server instance
mcp = FastMCP("Clauxton")

# Global monitor instances (initialized when needed)
_file_monitor: Optional[FileMonitor] = None
_event_processor: Optional[EventProcessor] = None


def _get_project_root() -> Path:
    """Get project root directory."""
    return Path.cwd()


def _get_file_monitor() -> FileMonitor:
    """Get or create FileMonitor instance."""
    global _file_monitor

    if _file_monitor is None:
        project_root = _get_project_root()
        config_path = project_root / ".clauxton" / "monitoring_config.yml"
        config = MonitorConfig.load_from_file(config_path)
        _file_monitor = FileMonitor(project_root, config=config)

    return _file_monitor


def _get_event_processor() -> EventProcessor:
    """Get or create EventProcessor instance."""
    global _event_processor

    if _event_processor is None:
        project_root = _get_project_root()
        _event_processor = EventProcessor(project_root)

    return _event_processor


@mcp.tool()
def kb_search(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
) -> List[dict[str, Any]]:
    """
    Search the Knowledge Base for entries matching the query.

    Args:
        query: Search query string
        category: Optional category filter (architecture, constraint, decision, pattern, convention)
        limit: Maximum number of results to return (default: 10)

    Returns:
        List of matching Knowledge Base entries with id, title, category, content, tags
    """
    kb = KnowledgeBase(Path.cwd())
    results = kb.search(query, category=category, limit=limit)
    return [
        {
            "id": entry.id,
            "title": entry.title,
            "category": entry.category,
            "content": entry.content,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
        }
        for entry in results
    ]


@mcp.tool()
def kb_add(
    title: str,
    category: str,
    content: str,
    tags: Optional[List[str]] = None,
) -> dict[str, str]:
    """
    Add a new entry to the Knowledge Base.

    Args:
        title: Entry title (max 50 characters)
        category: Entry category (architecture, constraint, decision, pattern, convention)
        content: Entry content (detailed description)
        tags: Optional list of tags for categorization

    Returns:
        Dictionary with id and success message
    """
    kb = KnowledgeBase(Path.cwd())

    # Generate entry ID
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    entries = kb.list_all()
    same_day_entries = [e for e in entries if e.id.startswith(f"KB-{date_str}")]
    sequence = len(same_day_entries) + 1
    entry_id = f"KB-{date_str}-{sequence:03d}"

    # Create entry
    entry = KnowledgeBaseEntry(
        id=entry_id,
        title=title,
        category=category,  # type: ignore[arg-type]
        content=content,
        tags=tags or [],
        created_at=now,
        updated_at=now,
        author=None,
    )

    kb.add(entry)
    return {
        "id": entry_id,
        "message": f"Successfully added entry: {entry_id}",
    }


@mcp.tool()
def kb_list(category: Optional[str] = None) -> List[dict[str, Any]]:
    """
    List all Knowledge Base entries.

    Args:
        category: Optional category filter (architecture, constraint, decision, pattern, convention)

    Returns:
        List of all Knowledge Base entries
    """
    kb = KnowledgeBase(Path.cwd())
    entries = kb.list_all()

    # Filter by category if specified
    if category:
        entries = [e for e in entries if e.category == category]

    return [
        {
            "id": entry.id,
            "title": entry.title,
            "category": entry.category,
            "content": entry.content,
            "tags": entry.tags,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
        }
        for entry in entries
    ]


@mcp.tool()
def kb_get(entry_id: str) -> dict[str, Any]:
    """
    Get a specific Knowledge Base entry by ID.

    Args:
        entry_id: Entry ID (e.g., KB-20251019-001)

    Returns:
        Knowledge Base entry details
    """
    kb = KnowledgeBase(Path.cwd())
    entry = kb.get(entry_id)
    return {
        "id": entry.id,
        "title": entry.title,
        "category": entry.category,
        "content": entry.content,
        "tags": entry.tags,
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
        "version": entry.version,
    }


@mcp.tool()
def kb_update(
    entry_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> dict[str, Any]:
    """
    Update an existing Knowledge Base entry.

    Args:
        entry_id: Entry ID to update (e.g., KB-20251019-001)
        title: New title (optional)
        content: New content (optional)
        category: New category (optional)
        tags: New tags list (optional)

    Returns:
        Updated entry details including new version number
    """
    kb = KnowledgeBase(Path.cwd())

    # Prepare updates dictionary
    updates: dict[str, Any] = {}
    if title is not None:
        updates["title"] = title
    if content is not None:
        updates["content"] = content
    if category is not None:
        updates["category"] = category
    if tags is not None:
        updates["tags"] = tags

    if not updates:
        return {
            "error": "No fields to update",
            "message": "Provide at least one field to update",
        }

    # Update entry
    updated_entry = kb.update(entry_id, updates)

    return {
        "id": updated_entry.id,
        "title": updated_entry.title,
        "category": updated_entry.category,
        "content": updated_entry.content,
        "tags": updated_entry.tags,
        "version": updated_entry.version,
        "updated_at": updated_entry.updated_at.isoformat(),
        "message": f"Successfully updated entry: {entry_id}",
    }


@mcp.tool()
def kb_delete(entry_id: str) -> dict[str, str]:
    """
    Delete a Knowledge Base entry.

    Args:
        entry_id: Entry ID to delete (e.g., KB-20251019-001)

    Returns:
        Success message
    """
    kb = KnowledgeBase(Path.cwd())

    # Get entry title for confirmation message
    entry = kb.get(entry_id)
    entry_title = entry.title

    # Delete entry
    kb.delete(entry_id)

    return {
        "id": entry_id,
        "message": f"Successfully deleted entry: {entry_id} ({entry_title})",
    }


@mcp.tool()
def task_add(
    name: str,
    description: Optional[str] = None,
    priority: str = "medium",
    depends_on: Optional[List[str]] = None,
    files: Optional[List[str]] = None,
    kb_refs: Optional[List[str]] = None,
    estimate: Optional[float] = None,
) -> dict[str, Any]:
    """
    Add a new task to the task list.

    Args:
        name: Task name (required)
        description: Detailed task description
        priority: Task priority (low, medium, high, critical) - default: medium
        depends_on: List of task IDs this task depends on
        files: List of files this task will modify
        kb_refs: List of related Knowledge Base entry IDs
        estimate: Estimated hours to complete

    Returns:
        Dictionary with task_id and success message
    """
    tm = TaskManager(Path.cwd())

    # Generate task ID
    task_id = tm.generate_task_id()

    # Create task object
    task = Task(
        id=task_id,
        name=name,
        description=description,
        status="pending",
        priority=priority,  # type: ignore[arg-type]
        depends_on=depends_on or [],
        files_to_edit=files or [],
        related_kb=kb_refs or [],
        estimated_hours=estimate,
        actual_hours=None,
        created_at=datetime.now(),
        started_at=None,
        completed_at=None,
    )

    tm.add(task)
    return {
        "task_id": task_id,
        "message": f"Successfully added task: {task_id}",
        "name": name,
        "priority": priority,
    }


@mcp.tool()
def task_list(
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[dict[str, Any]]:
    """
    List all tasks with optional filters.

    Args:
        status: Filter by status (pending, in_progress, completed, blocked)
        priority: Filter by priority (low, medium, high, critical)

    Returns:
        List of tasks with details
    """
    tm = TaskManager(Path.cwd())
    tasks = tm.list_all(
        status=status,  # type: ignore[arg-type]
        priority=priority,  # type: ignore[arg-type]
    )

    return [
        {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "depends_on": task.depends_on,
            "files_to_edit": task.files_to_edit,
            "related_kb": task.related_kb,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        for task in tasks
    ]


@mcp.tool()
def task_get(task_id: str) -> dict[str, Any]:
    """
    Get detailed information about a specific task.

    Args:
        task_id: Task ID (e.g., TASK-001)

    Returns:
        Task details
    """
    tm = TaskManager(Path.cwd())
    task = tm.get(task_id)

    return {
        "id": task.id,
        "name": task.name,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "depends_on": task.depends_on,
        "files_to_edit": task.files_to_edit,
        "related_kb": task.related_kb,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@mcp.tool()
def task_update(
    task_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, str]:
    """
    Update a task's fields.

    Args:
        task_id: Task ID to update
        status: New status (pending, in_progress, completed, blocked)
        priority: New priority (low, medium, high, critical)
        name: New task name
        description: New task description

    Returns:
        Dictionary with success message and updated fields
    """
    tm = TaskManager(Path.cwd())

    updates: dict[str, Any] = {}
    if status:
        updates["status"] = status
        # Auto-set timestamps
        if status == "in_progress":
            updates["started_at"] = datetime.now()
        elif status == "completed":
            updates["completed_at"] = datetime.now()
    if priority:
        updates["priority"] = priority
    if name:
        updates["name"] = name
    if description:
        updates["description"] = description

    tm.update(task_id, updates)
    return {
        "task_id": task_id,
        "message": f"Successfully updated task: {task_id}",
        "updates": str(updates),
    }


@mcp.tool()
def task_next() -> Optional[dict[str, Any]]:
    """
    Get the next recommended task to work on.

    Returns highest priority task whose dependencies are completed.

    Returns:
        Next task details, or None if no tasks are available
    """
    tm = TaskManager(Path.cwd())
    next_task = tm.get_next_task()

    if not next_task:
        return None

    return {
        "id": next_task.id,
        "name": next_task.name,
        "description": next_task.description,
        "priority": next_task.priority,
        "files_to_edit": next_task.files_to_edit,
        "estimated_hours": next_task.estimated_hours,
        "related_kb": next_task.related_kb,
    }


@mcp.tool()
def task_delete(task_id: str) -> dict[str, str]:
    """
    Delete a task.

    Args:
        task_id: Task ID to delete

    Returns:
        Dictionary with success message
    """
    tm = TaskManager(Path.cwd())
    tm.delete(task_id)
    return {
        "task_id": task_id,
        "message": f"Successfully deleted task: {task_id}",
    }


@mcp.tool()
def task_import_yaml(
    yaml_content: str,
    dry_run: bool = False,
    skip_validation: bool = False,
    skip_confirmation: bool = False,
    on_error: str = "rollback",
) -> dict[str, Any]:
    """
    Import multiple tasks from YAML content.

    This tool enables bulk task creation from YAML format, with automatic
    validation, dependency checking, and circular dependency detection.

    Args:
        yaml_content: YAML string containing tasks
        dry_run: If True, validate only without creating tasks (default: False)
        skip_validation: If True, skip dependency validation (default: False)
        skip_confirmation: If True, skip confirmation prompt (default: False)
        on_error: Error recovery strategy (default: "rollback")
            - "rollback": Revert all changes on error (transactional)
            - "skip": Skip failed tasks, continue with others
            - "abort": Stop immediately on first error

    Returns:
        Dictionary with:
            - status: "success" | "error" | "confirmation_required" | "partial"
            - imported: Number of tasks imported (0 if dry_run)
            - task_ids: List of created task IDs
            - errors: List of error messages (if any)
            - next_task: Recommended next task ID
            - confirmation_required: True if confirmation needed (optional)
            - preview: Preview of tasks to import (optional)

    Example:
        >>> yaml_content = '''
        ... tasks:
        ...   - name: "Setup FastAPI"
        ...     priority: high
        ...     files_to_edit:
        ...       - main.py
        ...   - name: "Create API"
        ...     priority: high
        ...     depends_on:
        ...       - TASK-001
        ... '''
        >>> task_import_yaml(yaml_content)
        {
            "status": "success",
            "imported": 2,
            "task_ids": ["TASK-001", "TASK-002"],
            "errors": [],
            "next_task": "TASK-001"
        }

    YAML Format:
        tasks:
          - name: "Task name" (required)
            description: "Detailed description" (optional)
            priority: high | medium | low | critical (optional, default: medium)
            depends_on:  (optional)
              - TASK-001
            files_to_edit:  (optional)
              - src/file1.py
              - src/file2.py
            related_kb:  (optional)
              - KB-20251019-001
            estimated_hours: 4.5 (optional)

    Notes:
        - Task IDs are auto-generated (TASK-001, TASK-002, etc.)
        - Circular dependencies are automatically detected
        - Dependencies are validated to exist
        - Use dry_run=True to validate before creating tasks
    """
    tm = TaskManager(Path.cwd())
    result = tm.import_yaml(
        yaml_content=yaml_content,
        dry_run=dry_run,
        skip_validation=skip_validation,
        skip_confirmation=skip_confirmation,
        on_error=on_error,
    )
    return result


# ============================================================================
# Conflict Detection Tools (Phase 2)
# ============================================================================


@mcp.tool()
def detect_conflicts(task_id: str) -> dict[str, Any]:
    """
    Detect potential conflicts for a task.

    Analyzes the given task against all in_progress tasks to identify
    file overlap conflicts that could lead to merge issues.

    Args:
        task_id: Task ID to check for conflicts (e.g., TASK-001)

    Returns:
        Dictionary with conflict count and list of conflict details

    Example:
        >>> detect_conflicts("TASK-002")
        {
            "task_id": "TASK-002",
            "task_name": "Add OAuth support",
            "conflict_count": 1,
            "status": "conflicts_detected",
            "summary": "Found 1 conflict with in_progress tasks",
            "max_risk_level": "medium",
            "conflicts": [
                {
                    "task_a_id": "TASK-002",
                    "task_b_id": "TASK-001",
                    "task_b_name": "Refactor JWT authentication",
                    "conflict_type": "file_overlap",
                    "risk_level": "medium",
                    "risk_score": 0.67,
                    "overlapping_files": ["src/api/auth.py"],
                    "details": "Both tasks edit: src/api/auth.py. ...",
                    "recommendation": "Complete TASK-002 before starting TASK-001, ..."
                }
            ]
        }
    """
    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)

    # Get task to include its name in response
    task = tm.get(task_id)
    conflicts = detector.detect_conflicts(task_id)

    # Calculate max risk level
    max_risk = "low"
    if conflicts:
        risk_levels = [c.risk_level for c in conflicts]
        if "high" in risk_levels:
            max_risk = "high"
        elif "medium" in risk_levels:
            max_risk = "medium"

    # Determine status and summary message
    if not conflicts:
        status = "no_conflicts"
        summary = "No conflicts detected. Safe to start working on this task."
    else:
        status = "conflicts_detected"
        summary = (
            f"Found {len(conflicts)} conflict(s) with in_progress tasks. "
            f"Max risk: {max_risk}."
        )

    return {
        "task_id": task_id,
        "task_name": task.name,
        "conflict_count": len(conflicts),
        "status": status,
        "summary": summary,
        "max_risk_level": max_risk,
        "conflicts": [
            {
                "task_a_id": c.task_a_id,
                "task_b_id": c.task_b_id,
                "task_b_name": tm.get(c.task_b_id).name,  # Include conflicting task name
                "conflict_type": c.conflict_type,
                "risk_level": c.risk_level,
                "risk_score": c.risk_score,
                "overlapping_files": c.overlapping_files,
                "details": c.details,
                "recommendation": c.recommendation,
            }
            for c in conflicts
        ],
    }


@mcp.tool()
def recommend_safe_order(task_ids: List[str]) -> dict[str, Any]:
    """
    Recommend safe execution order for tasks.

    Uses topological sort based on dependencies and conflict analysis
    to suggest an order that minimizes merge conflicts.

    Args:
        task_ids: List of task IDs to order (e.g., ["TASK-001", "TASK-002"])

    Returns:
        Dictionary with recommended execution order

    Example:
        >>> recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])
        {
            "task_count": 3,
            "recommended_order": ["TASK-001", "TASK-002", "TASK-003"],
            "task_details": [
                {"id": "TASK-001", "name": "Task 1", "priority": "high"},
                {"id": "TASK-002", "name": "Task 2", "priority": "medium"},
                {"id": "TASK-003", "name": "Task 3", "priority": "low"}
            ],
            "has_dependencies": true,
            "message": "Execute tasks in the order shown to minimize conflicts"
        }
    """
    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)

    order = detector.recommend_safe_order(task_ids)

    # Get task details for better context
    task_details = []
    has_dependencies = False
    for task_id in order:
        task = tm.get(task_id)
        task_details.append({
            "id": task.id,
            "name": task.name,
            "priority": task.priority,
            "files_count": len(task.files_to_edit),
        })
        if task.depends_on:
            has_dependencies = True

    # Create descriptive message
    if not order:
        message = "No tasks to order"
    elif has_dependencies:
        message = "Execution order respects dependencies and minimizes conflicts"
    else:
        message = "Execution order minimizes file conflicts (no dependencies found)"

    return {
        "task_count": len(order),
        "recommended_order": order,
        "task_details": task_details,
        "has_dependencies": has_dependencies,
        "message": message,
    }


@mcp.tool()
def check_file_conflicts(files: List[str]) -> dict[str, Any]:
    """
    Check which tasks are currently editing specific files.

    Useful for determining if files are available for editing or
    if coordination with other tasks is needed.

    Args:
        files: List of file paths to check (e.g., ["src/api/auth.py"])

    Returns:
        Dictionary with conflicting task IDs and details

    Example:
        >>> check_file_conflicts(["src/api/auth.py", "src/models/user.py"])
        {
            "file_count": 2,
            "files": ["src/api/auth.py", "src/models/user.py"],
            "conflicting_tasks": ["TASK-001", "TASK-003"],
            "task_details": [
                {"id": "TASK-001", "name": "Refactor auth", "files": ["src/api/auth.py"]},
                {"id": "TASK-003", "name": "Update model", "files": ["src/models/user.py"]}
            ],
            "file_map": {
                "src/api/auth.py": ["TASK-001"],
                "src/models/user.py": ["TASK-003"]
            },
            "all_available": false,
            "message": "2 in_progress task(s) are editing these files"
        }
    """
    tm = TaskManager(Path.cwd())
    detector = ConflictDetector(tm)

    conflicting_tasks = detector.check_file_conflicts(files)

    # Get task details for conflicting tasks
    task_details = []
    file_map: dict[str, list[str]] = {file: [] for file in files}

    for task_id in conflicting_tasks:
        task = tm.get(task_id)
        # Find which files this task is editing from the checked files
        task_files = [f for f in files if f in task.files_to_edit]
        task_details.append({
            "id": task.id,
            "name": task.name,
            "files": task_files,
            "priority": task.priority,
        })
        # Update file map
        for file in task_files:
            file_map[file].append(task.id)

    # Determine status
    all_available = len(conflicting_tasks) == 0

    # Create descriptive message
    if not files:
        message = "No files specified"
    elif all_available:
        message = f"All {len(files)} file(s) are available for editing"
    else:
        locked_count = len([f for f in files if file_map[f]])
        message = (
            f"{len(conflicting_tasks)} in_progress task(s) "
            f"editing {locked_count}/{len(files)} file(s)"
        )

    return {
        "file_count": len(files),
        "files": files,
        "conflicting_tasks": conflicting_tasks,
        "task_details": task_details,
        "file_map": file_map,
        "all_available": all_available,
        "message": message,
    }


@mcp.tool()
def undo_last_operation() -> dict[str, Any]:
    """
    Undo the last operation performed by Clauxton.

    This tool allows users to revert the most recent operation such as:
    - task_import (deletes imported tasks)
    - task_add (deletes the task)
    - task_delete (restores the task)
    - task_update (restores previous state)
    - kb_add (deletes the entry)
    - kb_delete (restores the entry)
    - kb_update (restores previous state)

    Returns:
        Dictionary with undo result status and details

    Example:
        >>> # After importing 10 tasks
        >>> undo_last_operation()
        {
            "status": "success",
            "operation_type": "task_import",
            "description": "Imported 10 tasks from YAML",
            "details": {
                "deleted_tasks": 10,
                "task_ids": ["TASK-001", "TASK-002", ...]
            },
            "message": "Undone: Imported 10 tasks from YAML (deleted 10 tasks)"
        }
    """
    from clauxton.core.operation_history import OperationHistory

    history = OperationHistory(Path.cwd())
    result = history.undo_last_operation()

    return result


@mcp.tool()
def get_recent_operations(limit: int = 10) -> dict[str, Any]:
    """
    Get recent operations that can be undone.

    This tool shows the operation history, allowing users to see
    what operations have been performed recently.

    Args:
        limit: Maximum number of operations to return (default: 10)

    Returns:
        Dictionary with list of recent operations

    Example:
        >>> get_recent_operations(limit=5)
        {
            "status": "success",
            "count": 5,
            "operations": [
                {
                    "operation_type": "task_import",
                    "timestamp": "2025-10-20T15:30:00",
                    "description": "Imported 10 tasks from YAML"
                },
                ...
            ]
        }
    """
    from clauxton.core.operation_history import OperationHistory

    history = OperationHistory(Path.cwd())
    operations = history.list_operations(limit=limit)

    return {
        "status": "success",
        "count": len(operations),
        "operations": [
            {
                "operation_type": op.operation_type,
                "timestamp": op.timestamp,
                "description": op.description,
            }
            for op in operations
        ],
    }


@mcp.tool()
def kb_export_docs(
    output_dir: str,
    category: Optional[str] = None,
) -> dict[str, Any]:
    """
    Export Knowledge Base entries to Markdown documentation files.

    Creates one Markdown file per category (or a single file if category specified).
    Decision entries use ADR (Architecture Decision Record) format.
    Other categories use standard documentation format.

    Args:
        output_dir: Directory path to write Markdown files to (will be created if doesn't exist)
        category: Optional category filter to export only specific category
            Values: "architecture", "constraint", "decision", "pattern", "convention"

    Returns:
        Dictionary with export statistics and file list

    Example:
        >>> kb_export_docs(output_dir="./docs/kb")
        {
            "status": "success",
            "total_entries": 15,
            "files_created": 5,
            "categories": ["architecture", "decision", "constraint"],
            "output_dir": "./docs/kb",
            "files": [
                "architecture.md",
                "decision.md",
                "constraint.md"
            ],
            "message": "Exported 15 entries to 5 file(s) in ./docs/kb"
        }

        >>> kb_export_docs(output_dir="./docs/adr", category="decision")
        {
            "status": "success",
            "total_entries": 3,
            "files_created": 1,
            "categories": ["decision"],
            "output_dir": "./docs/adr",
            "files": ["decision.md"],
            "message": "Exported 3 decision entries to ./docs/adr/decision.md"
        }

    Use Cases:
        1. **Documentation Generation**: Export KB to readable Markdown docs for team
        2. **ADR Archive**: Export decision entries as Architecture Decision Records
        3. **Knowledge Sharing**: Share project context with new team members
        4. **Version Control**: Commit exported docs to Git for versioning
        5. **Static Site**: Use exported Markdown in documentation sites (MkDocs, etc.)

    Notes:
        - Decision entries use ADR format (Context, Decision, Consequences)
        - Other categories use standard format (Title, Content, Metadata)
        - Files are named by category (e.g., architecture.md, decision.md)
        - Output directory will be created if it doesn't exist
        - Existing files will be overwritten
        - Entries are sorted by creation date within each file
    """
    kb = KnowledgeBase(Path.cwd())
    output_path = Path(output_dir)

    try:
        stats = kb.export_to_markdown(output_path, category=category)

        # Generate list of created files
        files = [f"{cat}.md" for cat in stats["categories"]]

        # Create descriptive message
        if category:
            message = (
                f"Exported {stats['total_entries']} {category} entries "
                f"to {output_dir}/{category}.md"
            )
        else:
            message = (
                f"Exported {stats['total_entries']} entries "
                f"to {stats['files_created']} file(s) in {output_dir}"
            )

        return {
            "status": "success",
            "total_entries": stats["total_entries"],
            "files_created": stats["files_created"],
            "categories": stats["categories"],
            "output_dir": output_dir,
            "files": files,
            "message": message,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to export KB: {e}",
        }


# ============================================================================
# Logging Tools (v0.10.0 Week 2 Day 7)
# ============================================================================


@mcp.tool()
def get_recent_logs(
    limit: int = 100,
    operation: Optional[str] = None,
    level: Optional[str] = None,
    days: int = 7,
) -> dict[str, Any]:
    """
    Get recent log entries from Clauxton logs.

    Returns structured log entries from the last N days, with optional
    filtering by operation type and log level.

    Args:
        limit: Maximum number of entries to return (default: 100)
        operation: Filter by operation type (optional)
            Examples: "task_add", "kb_search", "task_import_yaml"
        level: Filter by log level (optional)
            Values: "debug", "info", "warning", "error"
        days: Number of days to look back (default: 7)

    Returns:
        Dictionary with status, count, and list of log entries

    Example:
        >>> get_recent_logs(limit=10, operation="task_add", level="info")
        {
            "status": "success",
            "count": 5,
            "logs": [
                {
                    "timestamp": "2025-10-21T10:30:00",
                    "operation": "task_add",
                    "level": "info",
                    "message": "Added task TASK-001",
                    "metadata": {"task_id": "TASK-001", "priority": "high"}
                },
                ...
            ]
        }

    Use Cases:
        1. **Debugging**: Review recent operations to troubleshoot issues
        2. **Audit Trail**: Track all modifications to KB and tasks
        3. **Operation History**: See what Claude Code has done recently
        4. **Error Investigation**: Filter error-level logs to diagnose problems

    Notes:
        - Log files are stored in .clauxton/logs/ directory
        - Logs are automatically rotated after 30 days
        - Logs use JSON Lines format for structured data
        - Timestamps are in ISO 8601 format
    """
    from clauxton.utils.logger import ClauxtonLogger

    logger = ClauxtonLogger(Path.cwd())
    logs = logger.get_recent_logs(
        limit=limit,
        operation=operation,
        level=level,
        days=days,
    )

    return {
        "status": "success",
        "count": len(logs),
        "logs": logs,
    }


@mcp.tool()
def index_repository(
    root_path: Optional[str] = None,
) -> dict[str, Any]:
    """
    Index a repository to build a symbol map.

    Scans the repository, extracts symbols (functions, classes, methods) from
    source files, and stores them for fast lookup. Respects .gitignore patterns.

    Args:
        root_path: Root directory to index (defaults to current working directory)

    Returns:
        Dictionary with indexing results including:
        - status: "success" or "error"
        - files_indexed: Number of files processed
        - symbols_found: Number of symbols extracted
        - duration: Indexing duration in seconds
        - by_type: Breakdown of files by type (source/test/config/docs/other)
        - by_language: Breakdown of files by language

    Example:
        >>> index_repository()
        {
            "status": "success",
            "files_indexed": 50,
            "symbols_found": 200,
            "duration": 0.73,
            "by_type": {"source": 30, "test": 15, "config": 5},
            "by_language": {"python": 45, "yaml": 5}
        }

    Use Cases:
        1. **Initial Setup**: Index repository when starting work on a project
        2. **Refresh Index**: Re-index after major changes (new files, refactoring)
        3. **Symbol Discovery**: Find all functions/classes in codebase
        4. **Codebase Understanding**: Get overview of project structure

    Notes:
        - Indexing is incremental-safe (can be re-run anytime)
        - Respects .gitignore patterns (won't index ignored files)
        - Supports Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, etc.
        - Index stored in .clauxton/map/ directory
        - Typical performance: 1000+ files in <2 seconds
    """
    import time

    try:
        # Determine root path
        if root_path is None:
            repo_root = Path.cwd()
        else:
            repo_root = Path(root_path).resolve()

        if not repo_root.exists():
            return {
                "status": "error",
                "message": f"Directory not found: {repo_root}",
            }

        # Initialize repository map
        repo_map = RepositoryMap(repo_root)

        # Index repository
        start_time = time.time()
        result = repo_map.index()
        duration = time.time() - start_time

        return {
            "status": "success",
            "files_indexed": result.files_indexed,
            "symbols_found": result.symbols_found,
            "duration": round(duration, 2),
            "by_type": result.by_type,
            "by_language": result.by_language,
            "indexed_at": result.indexed_at.isoformat(),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


@mcp.tool()
def search_symbols(
    query: str,
    mode: str = "exact",
    limit: int = 10,
    root_path: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search for symbols (functions, classes, methods) in the indexed repository.

    Searches through all extracted symbols using various algorithms (exact, fuzzy,
    semantic) to find relevant matches.

    Args:
        query: Search query (symbol name or description)
        mode: Search mode - "exact" (substring), "fuzzy" (typo-tolerant),
            or "semantic" (meaning-based)
        limit: Maximum number of results to return (default: 10)
        root_path: Root directory of indexed repository (defaults to cwd)

    Returns:
        Dictionary with search results including:
        - status: "success" or "error"
        - count: Number of results found
        - symbols: List of matching symbols with metadata

    Example:
        >>> search_symbols("authenticate", mode="exact")
        {
            "status": "success",
            "count": 2,
            "symbols": [
                {
                    "name": "authenticate_user",
                    "type": "function",
                    "file_path": "/path/to/auth.py",
                    "line_start": 10,
                    "line_end": 20,
                    "docstring": "Authenticate user with credentials.",
                    "signature": "def authenticate_user(username: str, password: str) -> bool"
                },
                ...
            ]
        }

    Search Modes:
        - **exact**: Fast substring matching with priority scoring
          - Exact match: highest priority
          - Starts with: high priority
          - Contains: medium priority
          - Docstring: low priority
          Example: "auth" finds "authenticate_user", "get_auth_token"

        - **fuzzy**: Typo-tolerant using Levenshtein distance
          - Handles typos and misspellings
          - Similarity threshold: 0.4
          Example: "authentcate" finds "authenticate_user"

        - **semantic**: Meaning-based search using TF-IDF
          - Searches by concept, not just text
          - Requires scikit-learn (falls back to exact if unavailable)
          Example: "user login" finds "authenticate_user", "verify_credentials"

    Use Cases:
        1. **Find Function**: Locate specific function by name
        2. **Explore API**: Discover related functions (semantic search)
        3. **Code Navigation**: Jump to symbol definition
        4. **Refactoring**: Find all usages of a symbol
        5. **Documentation**: Find functions by description

    Notes:
        - Repository must be indexed first (use index_repository)
        - Search is case-insensitive
        - Results are ranked by relevance
        - Includes docstrings and signatures in results
    """
    try:
        # Determine root path
        if root_path is None:
            repo_root = Path.cwd()
        else:
            repo_root = Path(root_path).resolve()

        if not repo_root.exists():
            return {
                "status": "error",
                "message": f"Directory not found: {repo_root}",
            }

        # Initialize repository map
        repo_map = RepositoryMap(repo_root)

        # Validate mode
        if mode not in ["exact", "fuzzy", "semantic"]:
            return {
                "status": "error",
                "message": f"Invalid search mode: {mode}. Must be 'exact', 'fuzzy', or 'semantic'",
            }

        # Search symbols
        symbols = repo_map.search(query, search_type=mode, limit=limit)  # type: ignore[arg-type]

        return {
            "status": "success",
            "count": len(symbols),
            "symbols": [
                {
                    "name": symbol.name,
                    "type": symbol.type,
                    "file_path": symbol.file_path,
                    "line_start": symbol.line_start,
                    "line_end": symbol.line_end,
                    "docstring": symbol.docstring,
                    "signature": symbol.signature,
                }
                for symbol in symbols
            ],
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


# ============================================================================
# Semantic Search Tools (v0.12.0 Week 1 Day 5)
# ============================================================================


@mcp.tool()
def search_knowledge_semantic(
    query: str,
    limit: int = 5,
    category: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search Knowledge Base entries using semantic search.

    Uses embedding-based semantic search for more intelligent matching
    compared to traditional keyword search. Finds entries by meaning,
    not just exact text matches.

    Args:
        query: Search query (can be natural language question or keywords)
        limit: Maximum number of results to return (default: 5)
        category: Optional category filter (architecture, constraint, decision, pattern, convention)

    Returns:
        Dictionary with search results including:
        - status: "success" or "error"
        - count: Number of results found
        - results: List of matching KB entries with relevance scores
        - query: Original query
        - search_type: "semantic"

    Example:
        >>> search_knowledge_semantic("How do we handle authentication?", limit=3)
        {
            "status": "success",
            "count": 3,
            "search_type": "semantic",
            "query": "How do we handle authentication?",
            "results": [
                {
                    "score": 0.892,
                    "source_type": "kb",
                    "source_id": "KB-20251020-001",
                    "title": "JWT Authentication",
                    "content": "Use JWT tokens for API authentication...",
                    "metadata": {
                        "id": "KB-20251020-001",
                        "category": "decision",
                        "tags": ["auth", "jwt", "api"]
                    }
                },
                ...
            ]
        }

    Search Examples:
        - "database design" → Finds "PostgreSQL Schema", "DB Migrations", etc.
        - "API authentication" → Finds "JWT Auth", "OAuth2 Implementation", etc.
        - "error handling pattern" → Finds "Exception Handling Strategy", etc.

    Notes:
        - Requires sentence-transformers and faiss-cpu packages
        - Falls back to TF-IDF search if semantic search unavailable
        - Search is case-insensitive and meaning-based
        - Results ranked by cosine similarity (0.0-1.0)
        - Scores >0.7 indicate strong relevance
    """
    try:
        from clauxton.semantic.search import SemanticSearchEngine

        engine = SemanticSearchEngine(Path.cwd())
        results = engine.search_kb(query, limit=limit, category=category)

        return {
            "status": "success",
            "count": len(results),
            "search_type": "semantic",
            "query": query,
            "results": results,
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": "Semantic search dependencies not installed",
            "error": str(e),
            "hint": "Install with: pip install clauxton[semantic]",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def search_tasks_semantic(
    query: str,
    limit: int = 5,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search tasks using semantic search.

    Uses embedding-based semantic search to find tasks by meaning,
    not just keyword matching. Ideal for finding related tasks or
    discovering tasks by description.

    Args:
        query: Search query (can be natural language question or keywords)
        limit: Maximum number of results to return (default: 5)
        status: Optional status filter (pending, in_progress, completed, blocked)
        priority: Optional priority filter (low, medium, high, critical)

    Returns:
        Dictionary with search results including:
        - status: "success" or "error"
        - count: Number of results found
        - results: List of matching tasks with relevance scores
        - query: Original query
        - search_type: "semantic"

    Example:
        >>> search_tasks_semantic("authentication bug fix", limit=3, status="pending")
        {
            "status": "success",
            "count": 2,
            "search_type": "semantic",
            "query": "authentication bug fix",
            "results": [
                {
                    "score": 0.857,
                    "source_type": "task",
                    "source_id": "TASK-001",
                    "title": "Fix JWT token validation",
                    "content": "Fix JWT token validation in auth middleware...",
                    "metadata": {
                        "id": "TASK-001",
                        "name": "Fix JWT token validation",
                        "status": "pending",
                        "priority": "high",
                        "estimated_hours": 2.5
                    }
                },
                ...
            ]
        }

    Search Examples:
        - "database migration" → Finds "Add user table migration", "Update schema", etc.
        - "API endpoint" → Finds "Create POST /users", "Fix GET /auth", etc.
        - "performance issue" → Finds "Optimize query", "Fix memory leak", etc.

    Use Cases:
        1. **Find Related Tasks**: Discover tasks related to current work
        2. **Task Discovery**: Find tasks by natural language description
        3. **Priority Planning**: Find high-priority tasks in specific area
        4. **Status Filtering**: Combine semantic search with status filters

    Notes:
        - Requires sentence-transformers and faiss-cpu packages
        - Falls back to TF-IDF search if semantic search unavailable
        - Results ranked by cosine similarity (0.0-1.0)
        - Can combine semantic search with status/priority filters
    """
    try:
        from clauxton.semantic.search import SemanticSearchEngine

        engine = SemanticSearchEngine(Path.cwd())
        results = engine.search_tasks(
            query,
            limit=limit,
            status=status,
            priority=priority,
        )

        return {
            "status": "success",
            "count": len(results),
            "search_type": "semantic",
            "query": query,
            "results": results,
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": "Semantic search dependencies not installed",
            "error": str(e),
            "hint": "Install with: pip install clauxton[semantic]",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def search_files_semantic(
    query: str,
    limit: int = 10,
    pattern: Optional[str] = None,
) -> dict[str, Any]:
    """
    Search repository files using semantic search.

    Uses embedding-based semantic search to find files by content meaning.
    Searches through symbol names, docstrings, and code structure to find
    relevant files.

    Args:
        query: Search query (can be natural language or keywords)
        limit: Maximum number of results to return (default: 10)
        pattern: Optional glob pattern filter (e.g., "**/*.py", "src/**/*.ts")

    Returns:
        Dictionary with search results including:
        - status: "success" or "error"
        - count: Number of results found
        - results: List of matching files with relevance scores
        - query: Original query
        - search_type: "semantic"

    Example:
        >>> search_files_semantic("authentication logic", limit=5, pattern="**/*.py")
        {
            "status": "success",
            "count": 3,
            "search_type": "semantic",
            "query": "authentication logic",
            "results": [
                {
                    "score": 0.823,
                    "source_type": "file",
                    "source_id": "src/api/auth.py",
                    "title": "src/api/auth.py",
                    "content": "def authenticate(token):\\n    # JWT authentication logic...",
                    "metadata": {
                        "file_path": "src/api/auth.py",
                        "language": "python",
                        "symbols": ["authenticate", "verify_token", "TokenValidator"]
                    }
                },
                ...
            ]
        }

    Search Examples:
        - "user authentication" → Finds auth.py, user.py, login.py
        - "database models" → Finds models.py, schema.py, migrations/*
        - "API endpoints" → Finds api/*.py, routes.py, controllers/*
        - "test utilities" → Finds test_utils.py, conftest.py, fixtures.py

    Use Cases:
        1. **Find Implementation**: Locate files implementing specific functionality
        2. **Code Discovery**: Find related files when working on feature
        3. **Refactoring**: Discover all files related to component
        4. **Documentation**: Find relevant code for documentation
        5. **Language Filter**: Combine semantic search with file pattern

    Notes:
        - Requires sentence-transformers and faiss-cpu packages
        - Repository must be indexed first (use index_repository)
        - Searches through symbols, docstrings, and code content
        - Results ranked by cosine similarity (0.0-1.0)
        - Can filter by glob pattern (e.g., "**/*.py" for Python only)
    """
    try:
        from clauxton.semantic.search import SemanticSearchEngine

        engine = SemanticSearchEngine(Path.cwd())
        results = engine.search_files(query, limit=limit, pattern=pattern)

        return {
            "status": "success",
            "count": len(results),
            "search_type": "semantic",
            "query": query,
            "results": results,
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": "Semantic search dependencies not installed",
            "error": str(e),
            "hint": "Install with: pip install clauxton[semantic]",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def analyze_recent_commits(
    since_days: int = 7,
    max_count: Optional[int] = None,
) -> dict[str, Any]:
    """
    Analyze recent Git commits to extract patterns and insights.

    This tool analyzes recent commit history to understand development activity,
    identify patterns, and provide insights for decision-making.

    Args:
        since_days: Number of days to look back (default: 7)
        max_count: Maximum number of commits to analyze

    Returns:
        Analysis results including commit patterns, categories, and statistics

    Example:
        >>> analyze_recent_commits(since_days=7)
        {
            "status": "success",
            "commit_count": 15,
            "analysis": {
                "category_distribution": {"feature": 5, "bugfix": 3, "refactor": 2},
                "module_distribution": {"core": 8, "cli": 4, "mcp": 3},
                "impact_distribution": {"high": 2, "medium": 8, "low": 5},
                "top_keywords": ["auth", "test", "api", "db"]
            },
            "commits": [...]
        }

    Use Cases:
        1. **Activity Summary**: Understand recent development activity
        2. **Pattern Detection**: Identify recurring patterns in commits
        3. **Team Insights**: Analyze team productivity and focus areas
        4. **Quality Metrics**: Track bug fixes vs features ratio

    Notes:
        - Requires GitPython package
        - Project must be a Git repository
        - Returns detailed commit metadata and pattern analysis
    """
    try:
        from clauxton.analysis.git_analyzer import GitAnalyzer, NotAGitRepositoryError
        from clauxton.analysis.pattern_extractor import PatternExtractor

        analyzer = GitAnalyzer(Path.cwd())
        extractor = PatternExtractor()

        # Get recent commits
        commits = analyzer.get_recent_commits(since_days=since_days, max_count=max_count)

        if not commits:
            return {
                "status": "success",
                "commit_count": 0,
                "message": f"No commits found in the last {since_days} days",
            }

        # Analyze patterns
        from collections import Counter
        categories = []
        modules = []
        keywords = []
        impacts = []
        commit_data = []

        for commit in commits:
            patterns = extractor.detect_patterns(commit)
            categories.append(patterns["category"])
            modules.append(patterns["module"])
            keywords.extend(patterns["keywords"])
            impacts.append(patterns["impact"])

            commit_data.append({
                "sha": commit.sha[:7],
                "message": commit.message.split("\n")[0][:100],
                "author": commit.author,
                "date": commit.date.isoformat(),
                "files_changed": len(commit.files),
                "category": patterns["category"],
                "module": patterns["module"],
                "impact": patterns["impact"],
            })

        return {
            "status": "success",
            "commit_count": len(commits),
            "analysis": {
                "category_distribution": dict(Counter(categories)),
                "module_distribution": dict(Counter(modules)),
                "impact_distribution": dict(Counter(impacts)),
                "top_keywords": dict(Counter(keywords).most_common(10)),
            },
            "commits": commit_data[:10],  # Limit to 10 most recent
        }

    except NotAGitRepositoryError as e:
        return {
            "status": "error",
            "message": "Not a Git repository",
            "error": str(e),
            "hint": "Initialize Git with: git init",
        }
    except ImportError as e:
        return {
            "status": "error",
            "message": "GitPython not installed",
            "error": str(e),
            "hint": "Install with: pip install gitpython",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def suggest_next_tasks(
    since_days: int = 7,
    max_suggestions: int = 5,
) -> dict[str, Any]:
    """
    Suggest next tasks based on recent commit patterns.

    This tool analyzes recent development activity and suggests logical next tasks
    using pattern-based heuristics.

    Args:
        since_days: Number of days to analyze (default: 7)
        max_suggestions: Maximum number of suggestions (default: 5)

    Returns:
        List of task suggestions with priority, reasoning, and confidence scores

    Example:
        >>> suggest_next_tasks(since_days=7)
        {
            "status": "success",
            "suggestion_count": 3,
            "suggestions": [
                {
                    "name": "Add comprehensive tests to prevent regressions",
                    "description": "Recent 4 bugfixes suggest missing test coverage...",
                    "priority": "high",
                    "reasoning": "4 bugfixes indicates gaps in test coverage",
                    "confidence": 0.85,
                    "related_commits": ["abc1234", "def5678"]
                }
            ]
        }

    Suggestion Rules:
        - Multiple bugfixes → Suggest adding tests
        - New features → Suggest updating documentation
        - High-impact changes → Suggest thorough testing
        - Refactoring → Suggest verifying all tests pass
        - Test additions → Suggest coverage review
        - Frequent changes to module → Suggest consistency review

    Use Cases:
        1. **Daily Planning**: Get AI-suggested next tasks for the day
        2. **Sprint Planning**: Identify overlooked tasks
        3. **Quality Improvement**: Proactive suggestions for tests/docs
        4. **Team Coordination**: Discover tasks based on team activity

    Notes:
        - Filters out tasks that already exist in task list
        - Uses pattern-based heuristics (no AI/LLM needed)
        - Confidence score indicates reliability (0.0-1.0)
    """
    try:
        from clauxton.analysis.task_suggester import TaskSuggester

        suggester = TaskSuggester(Path.cwd())
        suggestions = suggester.suggest_tasks(
            since_days=since_days,
            max_suggestions=max_suggestions,
        )

        return {
            "status": "success",
            "suggestion_count": len(suggestions),
            "suggestions": [s.to_dict() for s in suggestions],
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Task suggestion failed: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def extract_decisions_from_commits(
    since_days: int = 30,
    max_candidates: int = 10,
    min_confidence: float = 0.5,
) -> dict[str, Any]:
    """
    Extract technical decisions from commit history for Knowledge Base.

    This tool analyzes commits to identify technical decisions, architecture changes,
    and important design choices that should be documented.

    Args:
        since_days: Number of days to analyze (default: 30)
        max_candidates: Maximum number of candidates (default: 10)
        min_confidence: Minimum confidence threshold (default: 0.5)

    Returns:
        List of decision candidates with suggested KB entry data

    Example:
        >>> extract_decisions_from_commits(since_days=30)
        {
            "status": "success",
            "candidate_count": 3,
            "candidates": [
                {
                    "title": "Adopt FastAPI for REST API framework",
                    "category": "architecture",
                    "content": "**Commit Message:** feat: adopt FastAPI...",
                    "tags": ["fastapi", "api", "backend"],
                    "commit_sha": "abc1234",
                    "confidence": 0.85,
                    "reasoning": "Contains decision keywords; Changes dependencies"
                }
            ]
        }

    Detection Criteria:
        - Decision keywords (adopt, choose, decide, switch to, migrate to)
        - Dependency changes (package.json, requirements.txt, etc.)
        - Configuration changes (.env, config files)
        - Architecture Decision Records (ADR)
        - High-impact commits

    Categories:
        - architecture: Framework/tool/technology decisions
        - decision: General technical decisions
        - constraint: Limitations and requirements
        - convention: Code style and standards
        - pattern: Design patterns and approaches

    Use Cases:
        1. **Auto-Documentation**: Capture decisions from commits
        2. **Knowledge Building**: Build KB from existing work
        3. **Onboarding**: Help new team members understand decisions
        4. **Architecture Review**: Track architectural evolution

    Notes:
        - Filters out decisions already in Knowledge Base
        - Confidence score indicates reliability (0.0-1.0)
        - Higher confidence = more likely to be a real decision
        - Can auto-add high-confidence decisions with min_confidence
    """
    try:
        from clauxton.analysis.decision_extractor import DecisionExtractor

        extractor = DecisionExtractor(Path.cwd())
        candidates = extractor.extract_decisions(
            since_days=since_days,
            max_candidates=max_candidates,
        )

        # Filter by confidence
        filtered_candidates = [
            c for c in candidates if c.confidence >= min_confidence
        ]

        return {
            "status": "success",
            "candidate_count": len(filtered_candidates),
            "total_analyzed": len(candidates),
            "candidates": [c.to_dict() for c in filtered_candidates],
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Decision extraction failed: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def get_project_context(
    depth: str = "full",
    include_recent_activity: bool = True,
) -> dict[str, Any]:
    """
    Get comprehensive project context for Claude Code.

    Provides rich context about the project including Knowledge Base entries,
    tasks, recent activity, and project structure. This helps Claude Code
    understand the project state and make better recommendations.

    Args:
        depth: Context depth level
            - "minimal": Basic KB and task counts
            - "standard": Add recent entries and active tasks
            - "full": Complete context with recent activity (default)
        include_recent_activity: Include recent commit analysis (default: True)

    Returns:
        Dictionary with project context including:
        - kb_summary: Knowledge Base statistics and recent entries
        - task_summary: Task statistics and active tasks
        - recent_activity: Recent commits and patterns (if enabled)
        - project_state: Current project state indicators

    Use Cases:
        1. **Context Loading**: Help Claude Code understand project quickly
        2. **Onboarding**: Provide new team members with project overview
        3. **Decision Making**: Give Claude Code context for recommendations
        4. **Status Check**: Quick project health check

    Example:
        # Get full project context
        context = get_project_context()

        # Get minimal context for quick checks
        context = get_project_context(depth="minimal", include_recent_activity=False)

    Notes:
        - "full" depth may take longer but provides best context
        - Recent activity analysis requires Git repository
        - Useful at start of Claude Code sessions
    """
    try:
        project_root = Path.cwd()
        kb = KnowledgeBase(project_root)
        tm = TaskManager(project_root)

        context: dict[str, Any] = {
            "status": "success",
            "depth": depth,
            "timestamp": datetime.now().isoformat(),
        }

        # Knowledge Base summary
        all_entries = kb.list_all()
        kb_by_category: dict[str, list[KnowledgeBaseEntry]] = {}
        for entry in all_entries:
            category = entry.category
            if category not in kb_by_category:
                kb_by_category[category] = []
            kb_by_category[category].append(entry)

        context["kb_summary"] = {
            "total_entries": len(all_entries),
            "by_category": {
                cat: len(entries) for cat, entries in kb_by_category.items()
            },
        }

        if depth in ["standard", "full"]:
            # Add recent KB entries (last 5)
            recent_entries = sorted(
                all_entries,
                key=lambda e: e.updated_at,
                reverse=True,
            )[:5]
            context["kb_summary"]["recent_entries"] = [
                {
                    "id": e.id,
                    "title": e.title,
                    "category": e.category,
                    "tags": e.tags,
                    "updated_at": e.updated_at.isoformat(),
                }
                for e in recent_entries
            ]

        # Task summary
        all_tasks = tm.list_all()
        tasks_by_status: dict[str, list[Task]] = {}
        tasks_by_priority: dict[str, list[Task]] = {}
        for task in all_tasks:
            # By status
            status = task.status
            if status not in tasks_by_status:
                tasks_by_status[status] = []
            tasks_by_status[status].append(task)

            # By priority
            priority = task.priority
            if priority not in tasks_by_priority:
                tasks_by_priority[priority] = []
            tasks_by_priority[priority].append(task)

        context["task_summary"] = {
            "total_tasks": len(all_tasks),
            "by_status": {
                status: len(tasks) for status, tasks in tasks_by_status.items()
            },
            "by_priority": {
                priority: len(tasks) for priority, tasks in tasks_by_priority.items()
            },
        }

        if depth in ["standard", "full"]:
            # Add active tasks (in_progress and high priority pending)
            active_tasks = [t for t in all_tasks if t.status == "in_progress"]
            high_priority_pending = [
                t
                for t in all_tasks
                if t.status == "pending" and t.priority in ["critical", "high"]
            ]
            active_tasks.extend(high_priority_pending[:3])  # Add top 3

            context["task_summary"]["active_tasks"] = [
                {
                    "id": t.id,
                    "name": t.name,
                    "status": t.status,
                    "priority": t.priority,
                    "estimated_hours": t.estimated_hours,
                }
                for t in active_tasks[:5]  # Limit to 5
            ]

        # Recent activity (only for "full" depth)
        if depth == "full" and include_recent_activity:
            try:
                from clauxton.analysis.git_analyzer import GitAnalyzer

                git_analyzer = GitAnalyzer(project_root)
                recent_commits = git_analyzer.get_recent_commits(since_days=7)

                context["recent_activity"] = {
                    "commit_count_7days": len(recent_commits),
                    "recent_commits": [
                        {
                            "sha": commit.sha[:7],
                            "message": commit.message.split("\n")[0][:100],
                            "author": commit.author,
                            "date": commit.date.isoformat(),
                            "files_changed": len(commit.files),
                        }
                        for commit in recent_commits[:5]  # Last 5 commits
                    ],
                }
            except Exception as e:
                context["recent_activity"] = {
                    "error": f"Could not fetch recent activity: {str(e)}"
                }

        # Project state indicators
        in_progress_count = len(tasks_by_status.get("in_progress", []))
        blocked_count = len(tasks_by_status.get("blocked", []))
        critical_pending = len(
            [
                t
                for t in all_tasks
                if t.status == "pending" and t.priority == "critical"
            ]
        )

        context["project_state"] = {
            "has_active_work": in_progress_count > 0,
            "has_blockers": blocked_count > 0,
            "has_critical_tasks": critical_pending > 0,
            "kb_populated": len(all_entries) > 0,
            "tasks_managed": len(all_tasks) > 0,
        }

        return context

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get project context: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def generate_project_summary() -> dict[str, Any]:
    """
    Generate a human-readable project summary.

    Creates a comprehensive summary of the project suitable for documentation,
    reports, or quick overview. Includes Knowledge Base highlights, task status,
    recent activity, and key metrics.

    Returns:
        Dictionary with formatted project summary including:
        - summary_text: Markdown-formatted summary text
        - statistics: Key project metrics
        - highlights: Important items to note
        - recommendations: AI-generated recommendations

    Use Cases:
        1. **Documentation**: Generate project status reports
        2. **Onboarding**: Create overview for new team members
        3. **Standups**: Quick status summary for meetings
        4. **Reviews**: Monthly/weekly project reviews

    Example:
        summary = generate_project_summary()
        print(summary["summary_text"])

    Notes:
        - Output is Markdown-formatted for easy documentation
        - Includes actionable recommendations
        - Useful for generating README sections
    """
    try:
        # Get project context
        context_data: dict[str, Any] = get_project_context(
            depth="full", include_recent_activity=True
        )
        if context_data.get("status") != "success":
            return context_data  # Return error

        # Build summary text
        summary_lines = []
        summary_lines.append("# Project Summary\n")
        summary_lines.append(
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        )

        # Knowledge Base section
        kb_summary = context_data["kb_summary"]
        summary_lines.append("## Knowledge Base")
        summary_lines.append(
            f"- **Total Entries**: {kb_summary['total_entries']}"
        )
        if kb_summary.get("by_category"):
            summary_lines.append("- **By Category**:")
            for category, count in sorted(kb_summary["by_category"].items()):
                summary_lines.append(f"  - {category}: {count}")

        if kb_summary.get("recent_entries"):
            summary_lines.append("\n### Recent KB Entries")
            for entry in kb_summary["recent_entries"]:
                summary_lines.append(
                    f"- [{entry['category']}] **{entry['title']}** (`{entry['id']}`)"
                )

        # Task section
        summary_lines.append("\n## Tasks")
        task_summary = context_data["task_summary"]
        summary_lines.append(f"- **Total Tasks**: {task_summary['total_tasks']}")
        if task_summary.get("by_status"):
            summary_lines.append("- **By Status**:")
            for status, count in sorted(task_summary["by_status"].items()):
                summary_lines.append(f"  - {status}: {count}")

        if task_summary.get("active_tasks"):
            summary_lines.append("\n### Active Tasks")
            for task in task_summary["active_tasks"]:
                summary_lines.append(
                    f"- [{task['priority']}] **{task['name']}** "
                    f"(`{task['id']}`, {task['status']})"
                )

        # Recent activity section
        if context_data.get("recent_activity"):
            recent = context_data["recent_activity"]
            if "error" not in recent:
                summary_lines.append("\n## Recent Activity (Last 7 Days)")
                summary_lines.append(
                    f"- **Commits**: {recent['commit_count_7days']}"
                )
                if recent.get("recent_commits"):
                    summary_lines.append("\n### Recent Commits")
                    for commit in recent["recent_commits"]:
                        summary_lines.append(
                            f"- `{commit['sha']}` {commit['message']} "
                            f"({commit['author']}, {commit['files_changed']} files)"
                        )

        # Project state section
        summary_lines.append("\n## Project State")
        state = context_data["project_state"]
        status_indicators = []
        if state["has_active_work"]:
            status_indicators.append("✅ Active work in progress")
        if state["has_blockers"]:
            status_indicators.append("⚠️ Has blocked tasks")
        if state["has_critical_tasks"]:
            status_indicators.append("🔴 Has critical pending tasks")
        if state["kb_populated"]:
            status_indicators.append("📚 Knowledge Base populated")
        if state["tasks_managed"]:
            status_indicators.append("✓ Tasks being tracked")

        for indicator in status_indicators:
            summary_lines.append(f"- {indicator}")

        # Recommendations section
        summary_lines.append("\n## Recommendations")
        recommendations = []

        if not state["kb_populated"]:
            recommendations.append(
                "📝 Start documenting decisions in Knowledge Base"
            )
        if not state["tasks_managed"]:
            recommendations.append("📋 Add tasks to track work items")
        if state["has_blockers"]:
            recommendations.append("⚠️ Address blocked tasks to unblock workflow")
        if state["has_critical_tasks"]:
            recommendations.append(
                "🔴 Prioritize critical tasks in backlog"
            )
        if kb_summary["total_entries"] > 0 and task_summary["total_tasks"] == 0:
            recommendations.append(
                "💡 Consider creating tasks from KB entries"
            )
        if not recommendations:
            recommendations.append("✅ Project is in good shape!")

        for rec in recommendations:
            summary_lines.append(f"- {rec}")

        summary_text = "\n".join(summary_lines)

        # Statistics
        statistics = {
            "kb_entries": kb_summary["total_entries"],
            "total_tasks": task_summary["total_tasks"],
            "active_tasks": len(task_summary.get("active_tasks", [])),
            "recent_commits": context_data.get("recent_activity", {}).get(
                "commit_count_7days", 0
            ),
        }

        # Highlights (important items)
        highlights = []
        if state["has_blockers"]:
            highlights.append("Has blocked tasks requiring attention")
        if state["has_critical_tasks"]:
            highlights.append("Has critical pending tasks")
        if context_data.get("recent_activity", {}).get("commit_count_7days", 0) > 10:
            highlights.append("High development activity (10+ commits/week)")

        return {
            "status": "success",
            "summary_text": summary_text,
            "statistics": statistics,
            "highlights": highlights,
            "recommendations": recommendations,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate project summary: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def get_knowledge_graph() -> dict[str, Any]:
    """
    Get knowledge graph showing relationships between KB entries and tasks.

    Generates a graph representation of relationships between Knowledge Base
    entries, tasks, and their connections. Useful for visualizing project
    knowledge structure and dependencies.

    Returns:
        Dictionary with knowledge graph including:
        - nodes: List of nodes (KB entries, tasks)
        - edges: List of edges (relationships)
        - statistics: Graph statistics
        - clusters: Related groups of entries/tasks

    Use Cases:
        1. **Visualization**: Generate visual project maps
        2. **Discovery**: Find related knowledge and tasks
        3. **Analysis**: Understand project structure
        4. **Navigation**: Explore knowledge connections

    Example:
        graph = get_knowledge_graph()
        print(f"Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")

    Notes:
        - Relationships based on tags, dependencies, and categories
        - Can be visualized with graph libraries (networkx, D3.js)
        - Useful for identifying knowledge gaps
    """
    try:
        project_root = Path.cwd()
        kb = KnowledgeBase(project_root)
        tm = TaskManager(project_root)

        all_entries = kb.list_all()
        all_tasks = tm.list_all()

        nodes = []
        edges = []

        # Add KB entries as nodes
        for entry in all_entries:
            nodes.append(
                {
                    "id": entry.id,
                    "type": "kb_entry",
                    "label": entry.title,
                    "category": entry.category,
                    "tags": entry.tags,
                }
            )

        # Add tasks as nodes
        for task in all_tasks:
            nodes.append(
                {
                    "id": task.id,
                    "type": "task",
                    "label": task.name,
                    "status": task.status,
                    "priority": task.priority,
                }
            )

        # Add edges between KB entries (same tags)
        for i, entry1 in enumerate(all_entries):
            for entry2 in all_entries[i + 1 :]:
                # Connect entries with shared tags
                shared_tags = set(entry1.tags) & set(entry2.tags)
                if shared_tags:
                    edges.append(
                        {
                            "source": entry1.id,
                            "target": entry2.id,
                            "type": "shared_tags",
                            "weight": len(shared_tags),
                            "label": f"{len(shared_tags)} shared tags",
                        }
                    )

        # Add edges between tasks (dependencies)
        for task in all_tasks:
            if task.depends_on:
                for dep_id in task.depends_on:
                    edges.append(
                        {
                            "source": dep_id,
                            "target": task.id,
                            "type": "dependency",
                            "weight": 3,  # Higher weight for dependencies
                            "label": "depends on",
                        }
                    )

        # Add edges between KB entries and tasks (shared tags)
        for entry in all_entries:
            for task in all_tasks:
                # Check if task description mentions KB entry tags
                task_text = f"{task.name} {task.description or ''}".lower()
                matching_tags = [
                    tag for tag in entry.tags if tag.lower() in task_text
                ]
                if matching_tags:
                    edges.append(
                        {
                            "source": entry.id,
                            "target": task.id,
                            "type": "related_by_tags",
                            "weight": len(matching_tags),
                            "label": f"related ({len(matching_tags)} tags)",
                        }
                    )

        # Calculate clusters (groups of related nodes)
        # Simple clustering by category for KB entries and priority for tasks
        clusters: dict[str, dict[str, Any]] = {}
        for entry in all_entries:
            category = entry.category
            if category not in clusters:
                clusters[category] = {"type": "kb_category", "nodes": []}
            clusters[category]["nodes"].append(entry.id)

        for task in all_tasks:
            priority = task.priority
            cluster_key = f"task_{priority}"
            if cluster_key not in clusters:
                clusters[cluster_key] = {"type": "task_priority", "nodes": []}
            clusters[cluster_key]["nodes"].append(task.id)

        # Statistics
        kb_nodes = len([n for n in nodes if n["type"] == "kb_entry"])
        task_nodes = len([n for n in nodes if n["type"] == "task"])
        tag_edges = len([e for e in edges if e["type"] == "shared_tags"])
        dependency_edges = len([e for e in edges if e["type"] == "dependency"])
        related_edges = len([e for e in edges if e["type"] == "related_by_tags"])

        statistics = {
            "total_nodes": len(nodes),
            "kb_nodes": kb_nodes,
            "task_nodes": task_nodes,
            "total_edges": len(edges),
            "tag_relationships": tag_edges,
            "dependencies": dependency_edges,
            "cross_references": related_edges,
            "cluster_count": len(clusters),
        }

        return {
            "status": "success",
            "nodes": nodes,
            "edges": edges,
            "clusters": clusters,
            "statistics": statistics,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate knowledge graph: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def find_related_entries(
    entry_id: str,
    limit: int = 5,
    include_tasks: bool = True,
) -> dict[str, Any]:
    """
    Find KB entries and tasks related to a given entry.

    Discovers related entries based on tags, categories, and content similarity.
    Useful for exploring knowledge connections and finding relevant context.

    Args:
        entry_id: ID of the KB entry or task to find relations for
        limit: Maximum number of related items to return (default: 5)
        include_tasks: Include related tasks in results (default: True)

    Returns:
        Dictionary with related items including:
        - related_entries: List of related KB entries with similarity scores
        - related_tasks: List of related tasks (if include_tasks=True)
        - relationship_reasons: Why items are related

    Use Cases:
        1. **Context Discovery**: Find relevant context for a decision
        2. **Knowledge Navigation**: Explore related knowledge
        3. **Task Planning**: Find tasks related to KB entries
        4. **Documentation**: Build comprehensive documentation sections

    Example:
        # Find entries related to KB-20251020-001
        related = find_related_entries("KB-20251020-001", limit=5)

        # Find only KB entries (no tasks)
        related = find_related_entries("KB-20251020-001", include_tasks=False)

    Notes:
        - Similarity based on shared tags, category, and content
        - Higher scores indicate stronger relationships
        - Useful for building knowledge graphs
    """
    try:
        project_root = Path.cwd()
        kb = KnowledgeBase(project_root)
        tm = TaskManager(project_root)

        # Get the reference entry/task
        reference_entry = None
        reference_task = None
        is_kb_entry = entry_id.startswith("KB-")

        if is_kb_entry:
            reference_entry = kb.get(entry_id)
            if not reference_entry:
                return {
                    "status": "error",
                    "message": f"KB entry {entry_id} not found",
                }
        else:
            reference_task = tm.get(entry_id)
            if not reference_task:
                return {
                    "status": "error",
                    "message": f"Task {entry_id} not found",
                }

        related_entries = []
        related_tasks = []

        # Find related KB entries
        all_entries = kb.list_all()
        for entry in all_entries:
            if entry.id == entry_id:
                continue  # Skip self

            similarity_score = 0.0
            reasons = []

            if is_kb_entry and reference_entry:
                # Compare with reference KB entry
                # Same category
                if entry.category == reference_entry.category:
                    similarity_score += 0.3
                    reasons.append(f"same category ({entry.category})")

                # Shared tags
                shared_tags = set(entry.tags) & set(reference_entry.tags)
                if shared_tags:
                    tag_score = len(shared_tags) * 0.2
                    similarity_score += tag_score
                    reasons.append(
                        f"{len(shared_tags)} shared tags: {', '.join(shared_tags)}"
                    )

                # Content similarity (simple keyword matching)
                ref_keywords = set(
                    reference_entry.content.lower().split()[:50]
                )  # First 50 words
                entry_keywords = set(entry.content.lower().split()[:50])
                common_keywords = ref_keywords & entry_keywords
                if len(common_keywords) > 5:  # At least 5 common words
                    content_score = min(len(common_keywords) * 0.05, 0.4)
                    similarity_score += content_score
                    reasons.append(f"{len(common_keywords)} common keywords")

            elif reference_task:
                # Compare with reference task
                task_text = (
                    f"{reference_task.name} {reference_task.description or ''}"
                ).lower()

                # Tags in task text
                matching_tags = [
                    tag for tag in entry.tags if tag.lower() in task_text
                ]
                if matching_tags:
                    tag_score = len(matching_tags) * 0.3
                    similarity_score += tag_score
                    reasons.append(
                        f"tags match task: {', '.join(matching_tags)}"
                    )

                # Category mentioned in task
                if entry.category.lower() in task_text:
                    similarity_score += 0.2
                    reasons.append(f"category '{entry.category}' in task")

            if similarity_score > 0:
                related_entries.append(
                    {
                        "id": entry.id,
                        "title": entry.title,
                        "category": entry.category,
                        "tags": entry.tags,
                        "similarity_score": round(similarity_score, 2),
                        "reasons": reasons,
                    }
                )

        # Sort by similarity score
        def _get_score(entry: dict[str, Any]) -> float:
            score = entry.get("similarity_score", 0.0)
            return float(score) if score is not None else 0.0

        related_entries.sort(key=_get_score, reverse=True)
        related_entries = related_entries[:limit]

        # Find related tasks (if requested)
        if include_tasks:
            all_tasks = tm.list_all()
            for task in all_tasks:
                if task.id == entry_id:
                    continue  # Skip self

                similarity_score = 0.0
                reasons = []

                if is_kb_entry and reference_entry:
                    # Compare task with KB entry
                    task_text = f"{task.name} {task.description or ''}".lower()

                    # Tags in task
                    matching_tags = [
                        tag
                        for tag in reference_entry.tags
                        if tag.lower() in task_text
                    ]
                    if matching_tags:
                        tag_score = len(matching_tags) * 0.3
                        similarity_score += tag_score
                        reasons.append(
                            f"tags in task: {', '.join(matching_tags)}"
                        )

                    # Category in task
                    if reference_entry.category.lower() in task_text:
                        similarity_score += 0.2
                        reasons.append(f"category '{reference_entry.category}' in task")

                elif reference_task:
                    # Compare tasks
                    # Check dependencies
                    if task.id in reference_task.depends_on:
                        similarity_score += 0.5
                        reasons.append("is a dependency")
                    if reference_task.id in task.depends_on:
                        similarity_score += 0.5
                        reasons.append("depends on this task")

                    # Same priority
                    if task.priority == reference_task.priority:
                        similarity_score += 0.1
                        reasons.append(f"same priority ({task.priority})")

                    # Same status
                    if task.status == reference_task.status:
                        similarity_score += 0.1
                        reasons.append(f"same status ({task.status})")

                if similarity_score > 0:
                    related_tasks.append(
                        {
                            "id": task.id,
                            "name": task.name,
                            "status": task.status,
                            "priority": task.priority,
                            "similarity_score": round(similarity_score, 2),
                            "reasons": reasons,
                        }
                    )

            # Sort by similarity score
            def _get_task_score(task: dict[str, Any]) -> float:
                score = task.get("similarity_score", 0.0)
                return float(score) if score is not None else 0.0

            related_tasks.sort(key=_get_task_score, reverse=True)
            related_tasks = related_tasks[:limit]

        result = {
            "status": "success",
            "reference_id": entry_id,
            "reference_type": "kb_entry" if is_kb_entry else "task",
            "related_entries": related_entries,
        }

        if include_tasks:
            result["related_tasks"] = related_tasks

        return result

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to find related entries: {str(e)}",
            "error": str(e),
        }


@mcp.tool()
def watch_project_changes(
    enabled: bool, config: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Enable or disable real-time file monitoring.

    Args:
        enabled: True to enable monitoring, False to disable
        config: Optional configuration overrides

    Returns:
        Status and current configuration
    """
    try:
        monitor = _get_file_monitor()

        if enabled:
            if not monitor.is_running:
                # Update config if provided
                if config:
                    # Merge with existing config
                    monitor.config = MonitorConfig(**config)

                monitor.start()

                return {
                    "status": "enabled",
                    "message": "File monitoring started",
                    "config": monitor.config.model_dump(),
                }
            else:
                return {
                    "status": "already_enabled",
                    "message": "File monitoring already running",
                    "config": monitor.config.model_dump(),
                }
        else:
            if monitor.is_running:
                monitor.stop()

                return {
                    "status": "disabled",
                    "message": "File monitoring stopped",
                }
            else:
                return {
                    "status": "already_disabled",
                    "message": "File monitoring not running",
                }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@mcp.tool()
async def get_recent_changes(
    minutes: int = 10, include_patterns: bool = True
) -> dict[str, Any]:
    """
    Get recent file changes and detected patterns.

    Args:
        minutes: Time window in minutes (default: 10)
        include_patterns: Include detected patterns (default: True)

    Returns:
        Recent changes and activity summary
    """
    try:
        monitor = _get_file_monitor()

        # Get recent changes
        changes = monitor.get_recent_changes(minutes=minutes)

        if not changes:
            return {
                "status": "no_changes",
                "message": f"No changes in last {minutes} minutes",
                "changes": [],
                "patterns": [],
            }

        # Create activity summary
        processor = _get_event_processor()
        summary = await processor.create_activity_summary(changes, minutes)

        # Save activity
        await processor.save_activity(summary)

        # Build response
        response = {
            "status": "success",
            "time_window_minutes": minutes,
            "total_files_changed": summary.total_files_changed,
            "changes": [
                {
                    "path": str(c.path),
                    "change_type": c.change_type.value,
                    "timestamp": c.timestamp.isoformat(),
                    "src_path": str(c.src_path) if c.src_path else None,
                }
                for c in changes
            ],
        }

        if include_patterns and summary.patterns:
            response["patterns"] = [
                {
                    "pattern_type": p.pattern_type.value,
                    "files": [str(f) for f in p.files],
                    "confidence": p.confidence,
                    "description": p.description,
                }
                for p in summary.patterns
            ]

        if summary.most_active_directory:
            response["most_active_directory"] = str(summary.most_active_directory)

        return response

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
