"""
Tests for CLI Conflict Detection Commands.

Tests cover:
- conflict detect command
- conflict order command
- conflict check command
- Error handling
- Output formatting
"""

from datetime import datetime
from pathlib import Path

from click.testing import CliRunner

from clauxton.cli.main import cli
from clauxton.core.models import Task
from clauxton.core.task_manager import TaskManager


def test_conflict_detect_no_conflicts(tmp_path: Path) -> None:
    """Test conflict detect command with no conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create task
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Test task",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict detect
        result = runner.invoke(cli, ["conflict", "detect", "TASK-001"])
        assert result.exit_code == 0
        assert "No conflicts detected" in result.output
        assert "safe to start" in result.output


def test_conflict_detect_with_conflicts(tmp_path: Path) -> None:
    """Test conflict detect command with conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Add OAuth",
            status="pending",
            files_to_edit=["src/api/auth.py", "src/models/user.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict detect
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002"])
        assert result.exit_code == 0
        assert "conflict(s) detected" in result.output
        assert "TASK-001" in result.output
        assert "Refactor auth" in result.output


def test_conflict_detect_verbose(tmp_path: Path) -> None:
    """Test conflict detect command with verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Add OAuth",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict detect with verbose
        result = runner.invoke(cli, ["conflict", "detect", "TASK-002", "--verbose"])
        assert result.exit_code == 0
        assert "Overlapping files:" in result.output
        assert "src/api/auth.py" in result.output
        assert "Details:" in result.output


def test_conflict_detect_task_not_found(tmp_path: Path) -> None:
    """Test conflict detect command with non-existent task."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Run conflict detect with non-existent task
        result = runner.invoke(cli, ["conflict", "detect", "TASK-999"])
        assert result.exit_code == 1
        assert "Error:" in result.output


def test_conflict_order_basic(tmp_path: Path) -> None:
    """Test conflict order command."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        for i in range(1, 4):
            task = Task(
                id=f"TASK-{i:03d}",
                name=f"Task {i}",
                status="pending",
                files_to_edit=[f"src/file{i}.py"],
                created_at=now,
            )
            tm.add(task)

        # Run conflict order
        result = runner.invoke(
            cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
        )
        assert result.exit_code == 0
        assert "Task Execution Order" in result.output
        assert "Recommended Order:" in result.output
        assert "TASK-001" in result.output
        assert "TASK-002" in result.output
        assert "TASK-003" in result.output


def test_conflict_order_with_dependencies(tmp_path: Path) -> None:
    """Test conflict order command with dependencies."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks with dependencies
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Task 1",
            status="pending",
            depends_on=[],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Task 2",
            status="pending",
            depends_on=["TASK-001"],
            created_at=now,
        )
        task3 = Task(
            id="TASK-003",
            name="Task 3",
            status="pending",
            depends_on=["TASK-002"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)
        tm.add(task3)

        # Run conflict order
        result = runner.invoke(
            cli, ["conflict", "order", "TASK-001", "TASK-002", "TASK-003"]
        )
        assert result.exit_code == 0
        assert "respects dependencies" in result.output


def test_conflict_order_with_details(tmp_path: Path) -> None:
    """Test conflict order command with details flag."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task = Task(
            id="TASK-001",
            name="High priority task",
            status="pending",
            priority="high",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        tm.add(task)

        # Run conflict order with details
        result = runner.invoke(cli, ["conflict", "order", "TASK-001", "--details"])
        assert result.exit_code == 0
        assert "Priority:" in result.output
        assert "Files:" in result.output


def test_conflict_order_task_not_found(tmp_path: Path) -> None:
    """Test conflict order command with non-existent task."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Run conflict order with non-existent task
        result = runner.invoke(cli, ["conflict", "order", "TASK-999"])
        assert result.exit_code == 1
        assert "Error:" in result.output


def test_conflict_check_no_conflicts(tmp_path: Path) -> None:
    """Test conflict check command with no conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create task (not in_progress)
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Test task",
            status="pending",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict check
        result = runner.invoke(cli, ["conflict", "check", "src/api/auth.py"])
        assert result.exit_code == 0
        assert "available for editing" in result.output


def test_conflict_check_with_conflicts(tmp_path: Path) -> None:
    """Test conflict check command with conflicts."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create in_progress task
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict check
        result = runner.invoke(cli, ["conflict", "check", "src/api/auth.py"])
        assert result.exit_code == 0
        assert "task(s) editing these files" in result.output
        assert "TASK-001" in result.output
        assert "Refactor auth" in result.output


def test_conflict_check_multiple_files(tmp_path: Path) -> None:
    """Test conflict check command with multiple files."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create tasks
        tm = TaskManager(Path.cwd())
        now = datetime.now()

        task1 = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=now,
        )
        task2 = Task(
            id="TASK-002",
            name="Update model",
            status="in_progress",
            files_to_edit=["src/models/user.py"],
            created_at=now,
        )
        tm.add(task1)
        tm.add(task2)

        # Run conflict check with multiple files
        result = runner.invoke(
            cli, ["conflict", "check", "src/api/auth.py", "src/models/user.py"]
        )
        assert result.exit_code == 0
        assert "TASK-001" in result.output
        assert "TASK-002" in result.output


def test_conflict_check_verbose(tmp_path: Path) -> None:
    """Test conflict check command with verbose output."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize
        result = runner.invoke(cli, ["init"])
        assert result.exit_code == 0

        # Create in_progress task
        tm = TaskManager(Path.cwd())
        task = Task(
            id="TASK-001",
            name="Refactor auth",
            status="in_progress",
            files_to_edit=["src/api/auth.py"],
            created_at=datetime.now(),
        )
        tm.add(task)

        # Run conflict check with verbose
        result = runner.invoke(
            cli, ["conflict", "check", "src/api/auth.py", "--verbose"]
        )
        assert result.exit_code == 0
        assert "File Status:" in result.output
        assert "locked by:" in result.output


def test_conflict_help_commands(tmp_path: Path) -> None:
    """Test help output for conflict commands."""
    runner = CliRunner()

    # Test conflict group help
    result = runner.invoke(cli, ["conflict", "--help"])
    assert result.exit_code == 0
    assert "Conflict detection commands" in result.output
    assert "detect" in result.output
    assert "order" in result.output
    assert "check" in result.output

    # Test detect help
    result = runner.invoke(cli, ["conflict", "detect", "--help"])
    assert result.exit_code == 0
    assert "Detect conflicts for a specific task" in result.output

    # Test order help
    result = runner.invoke(cli, ["conflict", "order", "--help"])
    assert result.exit_code == 0
    assert "Recommend safe execution order" in result.output

    # Test check help
    result = runner.invoke(cli, ["conflict", "check", "--help"])
    assert result.exit_code == 0
    assert "Check which tasks are currently editing" in result.output
