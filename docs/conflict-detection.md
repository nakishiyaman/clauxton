# Conflict Detection

**Phase**: Phase 2 - Conflict Prevention
**Status**: Week 12 - In Progress
**Version**: 0.9.0 (unreleased)

---

## Overview

Clauxton's Conflict Detection feature identifies potential conflicts between tasks **before they occur**, helping you avoid merge conflicts and coordination issues.

### What is Conflict Detection?

Conflict Detection analyzes your tasks to find situations where:
- **File Overlap**: Multiple tasks edit the same files
- **Dependency Violations**: Task dependencies are not respected (future)
- **Resource Conflicts**: Tasks compete for the same resources (future)

### Why is it Important?

Without conflict detection:
- ❌ Merge conflicts discovered **after** work is done
- ❌ Wasted time resolving conflicts
- ❌ Manual coordination required

With conflict detection:
- ✅ Conflicts predicted **before** starting work
- ✅ Suggested safe execution order
- ✅ Automatic coordination recommendations

---

## Features

### 1. File Overlap Detection

Detects when multiple `in_progress` tasks attempt to edit the same files.

**Example**:
```
TASK-001 (in_progress): edits src/api/auth.py
TASK-002 (pending):     edits src/api/auth.py, src/models/user.py

Conflict: Both tasks edit src/api/auth.py
Risk: MEDIUM (67% overlap)
Recommendation: Complete TASK-001 before starting TASK-002
```

### 2. Risk Scoring

Automatically calculates conflict risk based on file overlap percentage.

**Risk Levels**:
- 🔴 **HIGH** (≥70% overlap): Significant conflict likely
- 🟡 **MEDIUM** (≥40% overlap): Moderate conflict possible
- 🟢 **LOW** (<40% overlap): Minor conflict unlikely

**Algorithm**:
```
risk_score = (overlapping_files_count) / (average_total_files)

Example:
  Task A: 2 files
  Task B: 1 file
  Overlap: 1 file
  Risk: 1 / ((2 + 1) / 2) = 1 / 1.5 = 0.67 → MEDIUM
```

### 3. Safe Order Recommendation

Recommends optimal task execution order to minimize conflicts.

Uses:
- **Topological sort** based on task dependencies
- **Conflict analysis** to prioritize low-conflict tasks

**Example**:
```
Input:  TASK-001, TASK-002, TASK-003
Output: TASK-001 → TASK-002 → TASK-003
Reason: Respects dependencies + minimizes file conflicts
```

### 4. File Conflict Checking

Checks which `in_progress` tasks are currently editing specific files.

**Example**:
```
Files: ["src/api/auth.py", "src/models/user.py"]
Result: ["TASK-001", "TASK-003"]
```

---

## Usage

### Python API

#### Initialize ConflictDetector

```python
from pathlib import Path
from clauxton.core import ConflictDetector, TaskManager

# Initialize TaskManager
tm = TaskManager(Path.cwd())

# Create ConflictDetector
detector = ConflictDetector(tm)
```

#### Detect Conflicts for a Task

```python
from clauxton.core import Task
from datetime import datetime

# Add tasks
task1 = Task(
    id="TASK-001",
    name="Refactor API authentication",
    description="Update auth.py to use JWT tokens",
    status="in_progress",
    priority="high",
    files_to_edit=["src/api/auth.py"],
    created_at=datetime.now(),
)

task2 = Task(
    id="TASK-002",
    name="Add OAuth support",
    description="Implement OAuth2 flow",
    status="pending",
    priority="medium",
    files_to_edit=["src/api/auth.py", "src/models/user.py"],
    created_at=datetime.now(),
)

tm.add(task1)
tm.add(task2)

# Detect conflicts for TASK-002
conflicts = detector.detect_conflicts("TASK-002")

for conflict in conflicts:
    print(f"⚠️ {conflict.risk_level.upper()} risk conflict detected:")
    print(f"  Task A: {conflict.task_a_id}")
    print(f"  Task B: {conflict.task_b_id}")
    print(f"  Files: {', '.join(conflict.overlapping_files)}")
    print(f"  Details: {conflict.details}")
    print(f"  Recommendation: {conflict.recommendation}")
```

**Output**:
```
⚠️ MEDIUM risk conflict detected:
  Task A: TASK-002
  Task B: TASK-001
  Files: src/api/auth.py
  Details: Both tasks edit: src/api/auth.py. Task TASK-002 has 2 file(s), Task TASK-001 has 1 file(s).
  Recommendation: Complete TASK-002 before starting TASK-001, or coordinate changes in src/api/auth.py.
```

#### Recommend Safe Execution Order

```python
# Get recommended order for multiple tasks
order = detector.recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])

print("Recommended execution order:")
print(" → ".join(order))
```

**Output**:
```
Recommended execution order:
TASK-001 → TASK-002 → TASK-003
```

#### Check File Conflicts

```python
# Check which tasks are editing specific files
files = ["src/api/auth.py", "src/models/user.py"]
conflicting_tasks = detector.check_file_conflicts(files)

if conflicting_tasks:
    print(f"⚠️ Files in use by: {', '.join(conflicting_tasks)}")
else:
    print("✅ No conflicts - files are available")
```

**Output**:
```
⚠️ Files in use by: TASK-001, TASK-003
```

---

## MCP Tools

Clauxton provides MCP (Model Context Protocol) tools for conflict detection, allowing Claude Code to check conflicts directly.

### Available Tools

#### 1. detect_conflicts

Detect potential conflicts for a specific task.

**Signature**:
```python
detect_conflicts(task_id: str) -> dict[str, Any]
```

**Parameters**:
- `task_id` (string, required): Task ID to check (e.g., "TASK-001")

**Returns**:
```json
{
  "task_id": "TASK-002",
  "conflict_count": 1,
  "conflicts": [
    {
      "task_a_id": "TASK-002",
      "task_b_id": "TASK-001",
      "conflict_type": "file_overlap",
      "risk_level": "medium",
      "risk_score": 0.67,
      "overlapping_files": ["src/api/auth.py"],
      "details": "Both tasks edit: src/api/auth.py. ...",
      "recommendation": "Complete TASK-002 before starting TASK-001, ..."
    }
  ]
}
```

**Example (Claude Code)**:
```
User: Check if TASK-002 has any conflicts

Claude: Let me check for conflicts in TASK-002.

[Uses detect_conflicts("TASK-002")]

I found 1 conflict:
- TASK-002 conflicts with TASK-001 (MEDIUM risk, 0.67 score)
- Both tasks edit src/api/auth.py
- Recommendation: Complete TASK-002 before starting TASK-001
```

#### 2. recommend_safe_order

Recommend safe execution order for multiple tasks.

**Signature**:
```python
recommend_safe_order(task_ids: List[str]) -> dict[str, Any]
```

**Parameters**:
- `task_ids` (array of strings, required): List of task IDs to order

**Returns**:
```json
{
  "task_count": 3,
  "recommended_order": ["TASK-001", "TASK-002", "TASK-003"],
  "message": "Execute tasks in the order shown to minimize conflicts"
}
```

**Example (Claude Code)**:
```
User: What's the best order to execute TASK-001, TASK-002, and TASK-003?

Claude: Let me analyze the optimal execution order.

[Uses recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])]

Recommended execution order:
1. TASK-001 (no dependencies, no conflicts)
2. TASK-002 (depends on TASK-001)
3. TASK-003 (depends on TASK-002)

This order minimizes conflicts and respects all task dependencies.
```

#### 3. check_file_conflicts

Check which tasks are currently editing specific files.

**Signature**:
```python
check_file_conflicts(files: List[str]) -> dict[str, Any]
```

**Parameters**:
- `files` (array of strings, required): List of file paths to check

**Returns**:
```json
{
  "file_count": 2,
  "files": ["src/api/auth.py", "src/models/user.py"],
  "conflicting_tasks": ["TASK-001", "TASK-003"],
  "message": "2 in_progress task(s) are editing these files"
}
```

**Example (Claude Code)**:
```
User: Is src/api/auth.py safe to edit?

Claude: Let me check if anyone is currently editing that file.

[Uses check_file_conflicts(["src/api/auth.py"])]

⚠️ src/api/auth.py is currently being edited by:
- TASK-001 (in_progress)

You should coordinate with TASK-001 or wait until it's completed.
```

### MCP Tool Usage Patterns

#### Pattern 1: Pre-Start Conflict Check

Before starting a new task, check for conflicts:

```
User: I want to start TASK-005

Claude:
[Uses detect_conflicts("TASK-005")]

✅ TASK-005 has no conflicts with active tasks.
It's safe to start working on it.

[User can proceed with task]
```

#### Pattern 2: Batch Task Planning

When planning multiple tasks:

```
User: I have TASK-001, TASK-002, TASK-003. What order should I do them?

Claude:
[Uses recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])]

Recommended order:
1. TASK-001 (no conflicts, no deps)
2. TASK-002 (depends on TASK-001)
3. TASK-003 (depends on TASK-002)

This minimizes conflicts and respects dependencies.
```

#### Pattern 3: File Availability Check

Before editing a file:

```
User: Can I edit src/api/auth.py?

Claude:
[Uses check_file_conflicts(["src/api/auth.py"])]

⚠️ Warning: src/api/auth.py is being edited by TASK-001 (in_progress).

Recommendations:
- Wait for TASK-001 to complete, or
- Coordinate changes with the TASK-001 owner
```

### Integration with Claude Code

MCP tools work seamlessly in Claude Code:

1. **Automatic Tool Selection**: Claude Code automatically selects the appropriate conflict tool based on your question
2. **Natural Language**: Just ask in plain English (e.g., "Are there any conflicts?")
3. **Contextual Recommendations**: Claude Code uses conflict data to provide actionable advice

**Example Conversation**:
```
User: I'm about to start TASK-007. Anything I should know?

Claude:
[Automatically uses detect_conflicts("TASK-007")]

⚠️ TASK-007 has 1 high-risk conflict:
- Conflicts with TASK-005 (both edit src/models/user.py)
- Risk: 0.85 (HIGH)

Recommendation:
1. Complete TASK-005 first (currently in_progress)
2. Or, coordinate changes in src/models/user.py to avoid overlap

Would you like me to check the recommended execution order for all pending tasks?
```

See [MCP Server documentation](mcp-server.md) for complete MCP setup instructions.

---

## CLI Commands

> **Status**: ✅ Available in v0.9.0 (Week 12 Day 5)

Clauxton provides three CLI commands for conflict detection:

### 1. conflict detect

Detect conflicts for a specific task.

**Syntax**:
```bash
clauxton conflict detect TASK_ID [--verbose]
```

**Examples**:
```bash
# Basic conflict detection
$ clauxton conflict detect TASK-002

Conflict Detection Report
Task: TASK-002 - Add OAuth support
Files: 2 file(s)

⚠ 1 conflict(s) detected

Conflict 1:
  Task: TASK-001 - Refactor JWT authentication
  Risk: MEDIUM (67%)
  Files: 1 overlapping
  → Complete TASK-002 before starting TASK-001, or coordinate changes

# Verbose output (shows file details)
$ clauxton conflict detect TASK-002 --verbose

Conflict Detection Report
Task: TASK-002 - Add OAuth support
Files: 2 file(s)

⚠ 1 conflict(s) detected

Conflict 1:
  Task: TASK-001 - Refactor JWT authentication
  Risk: MEDIUM (67%)
  Files: 1 overlapping
  Overlapping files:
    - src/api/auth.py
  Details: Both tasks edit: src/api/auth.py. Potential merge conflict.
  → Complete TASK-002 before starting TASK-001, or coordinate changes
```

**Options**:
- `--verbose`, `-v`: Show detailed conflict information (overlapping files, details)

**Exit Codes**:
- `0`: Success (conflicts detected or not)
- `1`: Error (task not found, etc.)

### 2. conflict order

Recommend safe execution order for tasks.

**Syntax**:
```bash
clauxton conflict order TASK_ID... [--details]
```

**Examples**:
```bash
# Basic order recommendation
$ clauxton conflict order TASK-001 TASK-002 TASK-003

Task Execution Order
Tasks: 3 task(s)

Order respects dependencies and minimizes conflicts

Recommended Order:
1. TASK-001 - Refactor authentication
2. TASK-002 - Add OAuth support
3. TASK-003 - Update user model

💡 Execute tasks in this order to minimize conflicts

# With details (shows priority, files, dependencies)
$ clauxton conflict order TASK-001 TASK-002 TASK-003 --details

Task Execution Order
Tasks: 3 task(s)

Order respects dependencies and minimizes conflicts

Recommended Order:
1. TASK-001 - Refactor authentication
   Priority: HIGH
   Files: 2 file(s)

2. TASK-002 - Add OAuth support
   Priority: MEDIUM
   Files: 3 file(s)
   Depends on: TASK-001

3. TASK-003 - Update user model
   Priority: LOW
   Files: 1 file(s)
   Depends on: TASK-002

💡 Execute tasks in this order to minimize conflicts
```

**Options**:
- `--details`, `-d`: Show task details (priority, file count, dependencies)

**Exit Codes**:
- `0`: Success
- `1`: Error (task not found, etc.)

### 3. conflict check

Check which tasks are currently editing specific files.

**Syntax**:
```bash
clauxton conflict check FILE... [--verbose]
```

**Examples**:
```bash
# Basic file check
$ clauxton conflict check src/api/auth.py

File Availability Check
Files: 1 file(s)

⚠ 1 task(s) editing these files

Conflicting Tasks:
  TASK-001 - Refactor authentication
  Status: in_progress
  Editing: 1 of your file(s)

💡 Coordinate with task owners or wait until tasks complete

# Multiple files
$ clauxton conflict check src/api/auth.py src/models/user.py

File Availability Check
Files: 2 file(s)

⚠ 2 task(s) editing these files

Conflicting Tasks:
  TASK-001 - Refactor authentication
  Status: in_progress
  Editing: 1 of your file(s)

  TASK-003 - Update user model
  Status: in_progress
  Editing: 1 of your file(s)

💡 Coordinate with task owners or wait until tasks complete

# Verbose output (shows file-by-file status)
$ clauxton conflict check src/api/auth.py src/models/user.py --verbose

File Availability Check
Files: 2 file(s)

⚠ 2 task(s) editing these files

Conflicting Tasks:
  TASK-001 - Refactor authentication
  Status: in_progress
  Editing: 1 of your file(s)
    - src/api/auth.py

  TASK-003 - Update user model
  Status: in_progress
  Editing: 1 of your file(s)
    - src/models/user.py

File Status:
  ✗ src/api/auth.py (locked by: TASK-001)
  ✗ src/models/user.py (locked by: TASK-003)

💡 Coordinate with task owners or wait until tasks complete

# No conflicts
$ clauxton conflict check src/api/posts.py

File Availability Check
Files: 1 file(s)

✓ All 1 file(s) available for editing
```

**Options**:
- `--verbose`, `-v`: Show detailed file status and which tasks are editing each file

**Exit Codes**:
- `0`: Success (conflicts found or not)
- `1`: Error

### Common Workflows

#### Pre-Start Workflow
Before starting work on a task:
```bash
# 1. Check if task has conflicts
$ clauxton conflict detect TASK-005

✓ No conflicts detected
This task is safe to start working on.

# 2. Start the task
$ clauxton task update TASK-005 --status in_progress
```

#### Sprint Planning Workflow
Plan execution order for multiple tasks:
```bash
# 1. List pending tasks
$ clauxton task list --status pending

# 2. Get recommended order
$ clauxton conflict order TASK-010 TASK-011 TASK-012 --details

# 3. Execute tasks in recommended order
$ clauxton task update TASK-010 --status in_progress
```

#### File Coordination Workflow
Check if files are available before editing:
```bash
# 1. Check file availability
$ clauxton conflict check src/api/auth.py src/models/user.py

⚠ 1 task(s) editing these files
  TASK-008 (in_progress)

# 2. Decide: wait, coordinate, or work on different files
$ clauxton conflict check src/api/posts.py

✓ All files available for editing

# 3. Safe to edit available files
```

---

## Algorithm Details

### Risk Scoring Algorithm

The risk score is calculated based on the **percentage of overlapping files** relative to the average number of files being edited by both tasks.

**Formula**:
```
risk_score = min(1.0, overlapping_files_count / average_total_files)

where:
  overlapping_files_count = |files_to_edit_A ∩ files_to_edit_B|
  average_total_files = (|files_to_edit_A| + |files_to_edit_B|) / 2
```

**Risk Level Classification**:
```
if risk_score >= 0.7:
    risk_level = "high"
elif risk_score >= 0.4:
    risk_level = "medium"
else:
    risk_level = "low"
```

**Examples**:

| Task A Files | Task B Files | Overlap | Avg Total | Risk Score | Risk Level |
|--------------|--------------|---------|-----------|------------|------------|
| 1 | 1 | 1 | 1.0 | 1.00 | HIGH |
| 2 | 1 | 1 | 1.5 | 0.67 | MEDIUM |
| 4 | 2 | 1 | 3.0 | 0.33 | LOW |
| 3 | 3 | 0 | 3.0 | 0.00 | LOW |

**Why This Algorithm?**

- **Simple**: Easy to understand and explain
- **Intuitive**: Higher overlap % = higher risk
- **Fair**: Accounts for different task sizes
- **Fast**: O(n) where n = number of files

**Future Improvements**:
- Line-level overlap detection (AST parsing)
- Historical conflict data (machine learning)
- Weighted files (critical files get higher scores)

### Safe Order Recommendation Algorithm

Uses a combination of **topological sort** (for dependencies) and **conflict minimization** (for file overlap).

**Steps**:
1. **Topological Sort**: Respect task dependencies (DAG)
2. **Conflict Analysis**: Among tasks ready to execute, prioritize those with fewer conflicts
3. **Greedy Selection**: Execute tasks with lowest conflict potential first

**Pseudocode**:
```python
def recommend_safe_order(task_ids):
    ordered = []
    remaining = set(task_ids)

    while remaining:
        # Find tasks with no unmet dependencies
        ready = [tid for tid in remaining if all_deps_met(tid)]

        if not ready:
            # Circular dependency detected (should not happen with DAG validation)
            ordered.extend(sorted(remaining))  # Fallback
            break

        # Sort ready tasks by conflict potential (fewest conflicts first)
        ready_sorted = sort_by_conflict_potential(ready)

        # Add first ready task
        ordered.append(ready_sorted[0])
        remaining.remove(ready_sorted[0])

    return ordered
```

**Complexity**:
- **Time**: O(V² + E) where V = tasks, E = dependencies
- **Space**: O(V)

---

## Conflict Types

### Current: File Overlap

**Definition**: Two or more tasks edit the same file(s).

**Detection**: String matching on `Task.files_to_edit` field.

**Scope**: File-level only (not line-level).

**Example**:
```
TASK-001: edits src/api/auth.py (lines unknown)
TASK-002: edits src/api/auth.py (lines unknown)
→ Conflict detected (file-level)
```

### Future: Dependency Violation (Week 12 Day 2-3)

**Definition**: Task B depends on Task A, but Task A is blocked or not started.

**Example**:
```
TASK-002: depends on TASK-001
TASK-001: status = "blocked"
→ Dependency violation (TASK-002 cannot proceed)
```

### Future: Line-Level Overlap (Phase 3)

**Definition**: Two tasks edit overlapping lines in the same file.

**Example**:
```
TASK-001: edits src/api/auth.py, lines 50-100
TASK-002: edits src/api/auth.py, lines 80-120
→ High-risk conflict (lines 80-100 overlap)
```

---

## Performance

### Benchmarks (Week 12 Day 1)

| Operation | Tasks | Files | Time | Status |
|-----------|-------|-------|------|--------|
| detect_conflicts | 5 | 10 | ~5ms | ✅ |
| recommend_safe_order | 3 | 6 | ~3ms | ✅ |
| check_file_conflicts | 2 files | 5 tasks | ~2ms | ✅ |

**Performance Targets** (from requirements.md):
- Conflict detection: <2s for 5 parallel tasks ✅ (achieved: ~5ms, **400x faster**)
- Safe order: <100ms for 50 tasks (pending verification)

### Scalability

**Current Implementation**:
- Conflict detection: O(n) where n = number of in_progress tasks
- Safe order: O(V² + E) where V = tasks, E = dependencies
- File conflict check: O(n × m) where n = tasks, m = files

**Recommended Limits**:
- ✅ <50 tasks: Excellent performance (<50ms)
- ⚠️ 50-200 tasks: Acceptable performance (<200ms)
- ❌ >200 tasks: Consider optimization (caching, indexing)

---

## Troubleshooting

### No Conflicts Detected (Expected Conflicts)

**Symptom**: `detect_conflicts()` returns empty list, but you expect conflicts.

**Possible Causes**:
1. **Both tasks are not in_progress**: Only in_progress tasks are checked
   - **Solution**: Update task status to `in_progress`
2. **Different file paths**: File paths must match exactly
   - **Solution**: Use consistent paths (e.g., `src/api/auth.py` not `./src/api/auth.py`)
3. **Empty files_to_edit**: Tasks with no files cannot conflict
   - **Solution**: Add files to `Task.files_to_edit` field

**Debug**:
```python
task = tm.get("TASK-001")
print(f"Status: {task.status}")
print(f"Files: {task.files_to_edit}")
```

### False Positives (Unexpected Conflicts)

**Symptom**: Conflict detected, but tasks don't actually conflict.

**Possible Causes**:
1. **File-level detection only**: Tasks may edit different parts of the file
   - **Mitigation**: Coordinate manually or wait for line-level detection (Phase 3)
2. **Case-sensitive paths**: `src/Api/auth.py` ≠ `src/api/auth.py`
   - **Solution**: Use consistent casing

### Performance Issues (Slow Conflict Detection)

**Symptom**: Conflict detection takes >1 second.

**Possible Causes**:
1. **Too many tasks**: >200 tasks in_progress
   - **Solution**: Complete or archive old tasks
2. **Large files_to_edit lists**: >100 files per task
   - **Solution**: Break task into smaller sub-tasks

**Debug**:
```python
import time
start = time.perf_counter()
conflicts = detector.detect_conflicts("TASK-001")
elapsed = (time.perf_counter() - start) * 1000  # ms
print(f"Detection time: {elapsed:.2f}ms")
```

---

## Best Practices

### 1. Always Specify files_to_edit

```python
# ✅ Good
task = Task(
    id="TASK-001",
    files_to_edit=["src/api/auth.py", "src/models/user.py"]
)

# ❌ Bad (no files = no conflict detection)
task = Task(id="TASK-001", files_to_edit=[])
```

### 2. Use Consistent File Paths

```python
# ✅ Good (consistent)
files_to_edit=["src/api/auth.py"]

# ❌ Bad (inconsistent)
files_to_edit=["./src/api/auth.py"]  # Relative path
files_to_edit=["src/Api/auth.py"]    # Different casing
```

### 3. Check Conflicts Before Starting Tasks

```python
# Before starting TASK-002
conflicts = detector.detect_conflicts("TASK-002")

if conflicts:
    print("⚠️ Conflicts detected - coordinate with team")
    for c in conflicts:
        print(f"  - {c.task_b_id}: {c.details}")
else:
    # Safe to start
    tm.update("TASK-002", {"status": "in_progress"})
```

### 4. Use Safe Order Recommendation

```python
# Get all pending tasks
pending_tasks = tm.list_tasks(status="pending")
task_ids = [t.id for t in pending_tasks]

# Get recommended order
order = detector.recommend_safe_order(task_ids)

# Execute in recommended order
for task_id in order:
    print(f"Next: {task_id}")
    # Start task...
```

---

## API Reference

### ConflictDetector

```python
class ConflictDetector:
    def __init__(self, task_manager: TaskManager) -> None: ...

    def detect_conflicts(self, task_id: str) -> List[ConflictReport]: ...

    def recommend_safe_order(self, task_ids: List[str]) -> List[str]: ...

    def check_file_conflicts(self, files: List[str]) -> List[str]: ...
```

### ConflictReport

```python
class ConflictReport(BaseModel):
    task_a_id: str              # First task ID
    task_b_id: str              # Second task ID
    conflict_type: Literal["file_overlap", "dependency_violation"]
    risk_level: Literal["low", "medium", "high"]
    risk_score: float           # 0.0-1.0
    overlapping_files: List[str]
    details: str                # Human-readable description
    recommendation: str         # Suggested action
```

---

## Performance Tuning

### Performance Characteristics

Based on comprehensive benchmarking (Week 12 Day 3-4):

| Operation | Scale | Typical Time | Max Time |
|-----------|-------|--------------|----------|
| detect_conflicts | 50 tasks | ~5-10ms | <100ms |
| recommend_safe_order | 50 tasks | ~50-100ms | <200ms |
| check_file_conflicts | 100 files | ~30-50ms | <100ms |

All operations perform well within target constraints (sub-second response times).

### Optimization Tips

#### 1. Reduce Task Count in `in_progress`

**Problem**: `detect_conflicts` must check every `in_progress` task
```python
# Slower: 20 tasks in_progress
detector.detect_conflicts("TASK-050")  # Checks 20 tasks

# Faster: 5 tasks in_progress
detector.detect_conflicts("TASK-050")  # Checks 5 tasks
```

**Solution**: Complete or block tasks regularly
```python
# Complete finished tasks
tm.update("TASK-001", {"status": "completed"})

# Block tasks waiting on dependencies
tm.update("TASK-005", {"status": "blocked"})
```

#### 2. Minimize Files Per Task

**Problem**: Risk scoring is O(n × m) where n, m are file counts

**Example**:
```python
# Slower: 20 files per task
task = Task(
    files_to_edit=["src/file1.py", "src/file2.py", ..., "src/file20.py"]
)

# Faster: 3-5 files per task (split into sub-tasks)
task1 = Task(files_to_edit=["src/file1.py", "src/file2.py"])
task2 = Task(files_to_edit=["src/file3.py", "src/file4.py"])
```

**Best Practice**: Keep tasks focused (5-10 files max)

#### 3. Batch Operations

**Problem**: Multiple separate API calls increase overhead

**Example**:
```python
# Slower: Separate calls
for task_id in ["TASK-001", "TASK-002", "TASK-003"]:
    detect_conflicts(task_id)

# Faster: Use recommend_safe_order (one call)
recommend_safe_order(["TASK-001", "TASK-002", "TASK-003"])
```

#### 4. Cache Detection Results

**Problem**: Repeated conflict detection for same task

**Solution**: Cache results until task status changes
```python
from functools import lru_cache

# Cache decorator (invalidate on update)
@lru_cache(maxsize=128)
def detect_conflicts_cached(task_id: str, status_hash: int):
    return detector.detect_conflicts(task_id)

# Use with status hash for cache invalidation
task = tm.get("TASK-001")
status_hash = hash(task.status + str(task.files_to_edit))
conflicts = detect_conflicts_cached("TASK-001", status_hash)
```

### Performance Benchmarks

Based on integration tests (tests/integration/test_conflict_e2e.py):

#### Scenario 1: 50 Tasks, 10 in_progress
- **Operation**: detect_conflicts("TASK-025")
- **Result**: ~5-10ms
- **Files per task**: 2-3
- **Verdict**: ✅ Excellent

#### Scenario 2: 50 Tasks, Topological Sort
- **Operation**: recommend_safe_order(50 task IDs)
- **Result**: ~50-100ms
- **Dependencies**: Chain of 5 dependency levels
- **Verdict**: ✅ Good

#### Scenario 3: 100 Files, 20 in_progress Tasks
- **Operation**: check_file_conflicts(100 files)
- **Result**: ~30-50ms
- **Files per task**: 5
- **Verdict**: ✅ Excellent

### Scaling Guidelines

| Tasks | Files/Task | in_progress | Expected Time |
|-------|------------|-------------|---------------|
| 10 | 5 | 2-3 | <5ms |
| 50 | 5 | 10 | <20ms |
| 100 | 10 | 20 | <100ms |
| 500 | 10 | 50 | <500ms |

**Rule of Thumb**: Keep `in_progress * files_per_task < 500` for sub-100ms response times.

### Troubleshooting Slow Performance

#### Symptom: detect_conflicts takes >100ms

**Diagnosis**:
```python
# Count in_progress tasks
in_progress = tm.list_all(status="in_progress")
print(f"In progress: {len(in_progress)}")

# Check files per task
for task in in_progress:
    print(f"{task.id}: {len(task.files_to_edit)} files")
```

**Solutions**:
1. Complete finished tasks: `tm.update(task_id, {"status": "completed"})`
2. Split large tasks into smaller sub-tasks
3. Use `blocked` status for waiting tasks

#### Symptom: recommend_safe_order takes >200ms

**Diagnosis**:
```python
# Check dependency graph complexity
tasks = [tm.get(tid) for tid in task_ids]
avg_deps = sum(len(t.depends_on) for t in tasks) / len(tasks)
print(f"Avg dependencies: {avg_deps}")
```

**Solutions**:
1. Simplify dependency graph (avoid unnecessary dependencies)
2. Process tasks in smaller batches
3. Consider parallel execution for independent tasks

---

## Limitations

### Current Limitations (Week 12 Day 1)

1. **File-level detection only**: Cannot detect line-level conflicts
   - **Impact**: May report conflicts when editing different parts of same file
   - **Workaround**: Manual coordination
   - **Future**: Line-level detection with AST parsing (Phase 3)

2. **Static analysis only**: No Git integration
   - **Impact**: Relies on `Task.files_to_edit` field accuracy
   - **Workaround**: Keep `files_to_edit` up-to-date
   - **Future**: Git integration for drift detection (Week 13)

3. **No historical data**: Cannot learn from past conflicts
   - **Impact**: Risk scoring doesn't improve over time
   - **Workaround**: Manual risk assessment
   - **Future**: Event logging + ML (Phase 3)

4. **No LLM-based prediction**: Cannot infer file dependencies
   - **Impact**: Must manually specify `files_to_edit`
   - **Workaround**: Use file patterns (e.g., `src/api/**/*.py`)
   - **Future**: Conflict Detector Subagent with LLM (Phase 3)

---

## Roadmap

### Week 12 (Current)
- ✅ Day 1: ConflictDetector core + file overlap detection
- ✅ Day 2: MCP tools for conflict detection
- ✅ Day 3-4: Integration tests + performance benchmarks + MCP enhancements
- ✅ Day 5: CLI commands for conflict detection
- ⏳ Day 6-7: Tests, documentation, polish

### Week 13 (Next)
- Drift Detection (expected vs actual files edited)
- Event Logging (conflict detection events)
- Git integration

### Week 14
- Lifecycle Hooks (pre-commit conflict checks)
- Automatic conflict prevention

### Phase 3 (Future)
- Line-level conflict detection (AST parsing)
- Conflict Detector Subagent (LLM-powered)
- Machine learning-based risk prediction
- Team collaboration features

---

## Related Documentation

- [Task Management Guide](task-management-guide.md) - Task creation and management
- [Architecture](architecture.md) - System architecture (coming soon: ConflictDetector)
- [Requirements](requirements.md) - FR-CONFLICT-001, NFR-PERF-004
- [Phase 2 Plan](PHASE_2_PLAN.md) - Complete Phase 2 roadmap

---

**Last Updated**: 2025-10-20
**Version**: Week 12 Day 5 (CLI Commands implementation)
**Status**: In Progress (Final polish in Day 6-7)
