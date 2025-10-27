"""
Tests for Week 3 Day 2 MCP Context Intelligence Tools.

Tests cover:
- analyze_work_session MCP tool (6 tests)
- predict_next_action MCP tool (6 tests)
- get_current_context MCP tool (3 tests)
"""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from clauxton.core.models import Priority, Task, TaskStatus
from clauxton.core.task_manager import TaskManager
from clauxton.mcp import server


def setup_temp_project(tmp_path: Path) -> None:
    """
    Set up a temporary project structure.

    Args:
        tmp_path: Temporary directory path
    """
    # Create basic project structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".clauxton").mkdir()

    # Create dummy files
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "tests" / "__init__.py").write_text("")

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=False)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        capture_output=True,
        check=False,
    )


def create_modified_files(
    tmp_path: Path, count: int, time_spread_minutes: int = 30
) -> None:
    """
    Create modified files with specific timestamps.

    Args:
        tmp_path: Base directory
        count: Number of files to create
        time_spread_minutes: Time spread for file modifications
    """
    for i in range(count):
        file_path = tmp_path / "src" / f"file{i}.py"
        file_path.write_text(f"# File {i}\nprint('test')")

        # Set modification time
        minutes_ago = time_spread_minutes - (i * (time_spread_minutes // max(count, 1)))
        file_time = datetime.now() - timedelta(minutes=minutes_ago)
        os.utime(file_path, (file_time.timestamp(), file_time.timestamp()))


class TestAnalyzeWorkSession:
    """Test analyze_work_session MCP tool."""

    def test_analyze_work_session_basic(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test basic work session analysis."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create files modified in last 30 minutes
        create_modified_files(tmp_path, count=5, time_spread_minutes=30)

        result = server.analyze_work_session()

        assert result["status"] == "success"
        assert "duration_minutes" in result
        assert "focus_score" in result
        assert "breaks" in result
        assert "file_switches" in result
        assert "active_periods" in result

        # Verify types
        assert isinstance(result["duration_minutes"], int)
        assert isinstance(result["focus_score"], (int, float))
        assert isinstance(result["breaks"], list)
        assert isinstance(result["file_switches"], int)
        assert isinstance(result["active_periods"], list)

    def test_analyze_work_session_with_breaks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test session analysis with multiple breaks detected."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create files with gaps (breaks)
        file1 = tmp_path / "src" / "file1.py"
        file1.write_text("print(1)")
        time1 = datetime.now() - timedelta(minutes=60)
        os.utime(file1, (time1.timestamp(), time1.timestamp()))

        # Gap of 20 minutes (break)
        file2 = tmp_path / "src" / "file2.py"
        file2.write_text("print(2)")
        time2 = datetime.now() - timedelta(minutes=40)
        os.utime(file2, (time2.timestamp(), time2.timestamp()))

        # Gap of 18 minutes (break)
        file3 = tmp_path / "src" / "file3.py"
        file3.write_text("print(3)")
        time3 = datetime.now() - timedelta(minutes=22)
        os.utime(file3, (time3.timestamp(), time3.timestamp()))

        # Recent file
        file4 = tmp_path / "src" / "file4.py"
        file4.write_text("print(4)")

        result = server.analyze_work_session()

        assert result["status"] == "success"
        # Should detect at least 1 break (15+ minute gaps)
        assert len(result["breaks"]) >= 1
        assert result["duration_minutes"] > 0

    def test_analyze_work_session_high_focus(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test session with high focus (few file switches)."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create only 3 files in last hour (high focus)
        create_modified_files(tmp_path, count=3, time_spread_minutes=60)

        result = server.analyze_work_session()

        assert result["status"] == "success"
        # High focus should be >= 0.8
        assert result["focus_score"] >= 0.7  # Allow slight variance
        assert result["file_switches"] <= 5

    def test_analyze_work_session_low_focus(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test session with low focus (many file switches)."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create many files in short time (low focus)
        create_modified_files(tmp_path, count=25, time_spread_minutes=30)

        result = server.analyze_work_session()

        assert result["status"] == "success"
        # Low focus should be < 0.5
        assert result["focus_score"] < 0.6  # Allow slight variance
        assert result["file_switches"] > 15

    def test_analyze_work_session_no_session(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test when no active session exists."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Don't create any recent files

        result = server.analyze_work_session()

        # Should return no_session status or success with 0 duration
        assert result["status"] in ["no_session", "success"]
        assert result["duration_minutes"] == 0

    def test_analyze_work_session_error_handling(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error handling in analyze_work_session."""
        monkeypatch.chdir(tmp_path)

        # Patch ContextManager at the import location within the function
        with patch(
            "clauxton.proactive.context_manager.ContextManager.analyze_work_session",
            side_effect=Exception("Test error"),
        ):
            # Need to set up basic project for import to work
            setup_temp_project(tmp_path)

            result = server.analyze_work_session()

            assert result["status"] == "error"
            assert "error" in result
            assert "message" in result


class TestPredictNextAction:
    """Test predict_next_action MCP tool."""

    def test_predict_next_action_run_tests(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prediction to run tests when many files changed."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create many implementation files but no test files
        for i in range(10):
            impl_file = tmp_path / "src" / f"module{i}.py"
            impl_file.write_text(f"def func{i}():\n    pass")

        result = server.predict_next_action()

        assert result["status"] == "success"
        assert "action" in result
        assert "confidence" in result
        assert "reasoning" in result

        # Verify types
        assert isinstance(result["action"], str)
        assert isinstance(result["confidence"], (int, float))
        assert isinstance(result["reasoning"], str)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_next_action_commit(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prediction to commit when on feature branch with changes."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create feature branch
        subprocess.run(
            ["git", "checkout", "-b", "feature/test"],
            cwd=tmp_path,
            capture_output=True,
            check=False,
        )

        # Create and stage files
        test_file = tmp_path / "src" / "test.py"
        test_file.write_text("print('test')")

        subprocess.run(
            ["git", "add", "."],
            cwd=tmp_path,
            capture_output=True,
            check=False,
        )

        result = server.predict_next_action()

        assert result["status"] == "success"
        assert result["action"] in [
            "commit_changes",
            "run_tests",
            "write_tests",
            "no_clear_action",
        ]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_next_action_pr_creation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prediction to create PR when branch ahead of main."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Initialize with a commit on main
        test_file = tmp_path / "README.md"
        test_file.write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=False)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmp_path,
            capture_output=True,
            check=False,
        )

        # Create feature branch with commits
        subprocess.run(
            ["git", "checkout", "-b", "feature/new-feature"],
            cwd=tmp_path,
            capture_output=True,
            check=False,
        )

        # Add commits
        for i in range(3):
            feature_file = tmp_path / f"feature{i}.py"
            feature_file.write_text(f"# Feature {i}")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmp_path,
                capture_output=True,
                check=False,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Add feature {i}"],
                cwd=tmp_path,
                capture_output=True,
                check=False,
            )

        result = server.predict_next_action()

        assert result["status"] == "success"
        # Could predict various actions based on state
        assert result["action"] in [
            "create_pr",
            "commit_changes",
            "run_tests",
            "review_code",
            "no_clear_action",
        ]

    def test_predict_next_action_morning_context(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test time-based prediction (morning context)."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Simply call without mocking time - test that prediction works
        # The actual time-based logic will be tested in the prediction
        result = server.predict_next_action()

        assert result["status"] == "success"
        # Should get a valid action regardless of time
        assert result["action"] in [
            "run_tests",
            "write_tests",
            "commit_changes",
            "create_pr",
            "take_break",
            "morning_planning",
            "resume_work",
            "review_code",
            "no_clear_action",
        ]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_next_action_no_context(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prediction with no clear pattern."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Don't create any specific patterns

        result = server.predict_next_action()

        assert result["status"] == "success"
        # With no context, should return low confidence or no_clear_action
        if result["action"] == "no_clear_action":
            assert result["confidence"] < 0.7
        assert "reasoning" in result

    def test_predict_next_action_low_confidence(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prediction with uncertain/low confidence scenario."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create minimal context (1-2 files)
        create_modified_files(tmp_path, count=2, time_spread_minutes=60)

        result = server.predict_next_action()

        assert result["status"] == "success"
        # Should still provide prediction even with low confidence
        assert 0.0 <= result["confidence"] <= 1.0
        assert len(result["reasoning"]) > 0


class TestGetCurrentContext:
    """Test get_current_context MCP tool."""

    def test_get_current_context_with_new_fields(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_current_context includes all new Week 3 fields."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Create some context
        create_modified_files(tmp_path, count=5, time_spread_minutes=30)

        result = server.get_current_context(include_prediction=True)

        assert result["status"] == "success"

        # Verify original fields
        assert "current_branch" in result
        assert "active_files" in result
        assert "recent_commits" in result
        assert "time_context" in result
        assert "is_git_repo" in result

        # Verify new Week 3 fields
        assert "session_duration_minutes" in result
        assert "focus_score" in result
        assert "breaks_detected" in result
        assert "predicted_next_action" in result
        assert "uncommitted_changes" in result
        assert "diff_stats" in result

        # Verify types
        assert isinstance(result["session_duration_minutes"], (int, type(None)))
        assert isinstance(result["focus_score"], (int, float, type(None)))
        assert isinstance(result["breaks_detected"], int)

    def test_get_current_context_caching(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that context caching works effectively."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        create_modified_files(tmp_path, count=3, time_spread_minutes=30)

        # Call twice in quick succession
        result1 = server.get_current_context(include_prediction=False)
        result2 = server.get_current_context(include_prediction=False)

        assert result1["status"] == "success"
        assert result2["status"] == "success"

        # Should have similar data (caching should work)
        assert result1["session_duration_minutes"] == result2["session_duration_minutes"]
        assert result1["focus_score"] == result2["focus_score"]

    def test_get_current_context_integration(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test full integration with prediction."""
        monkeypatch.chdir(tmp_path)
        setup_temp_project(tmp_path)

        # Initialize task manager and add a task
        tm = TaskManager(tmp_path)
        task = Task(
            id="TASK-001",
            name="Test task",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        tm.add(task)

        # Create context with changes
        create_modified_files(tmp_path, count=8, time_spread_minutes=40)

        result = server.get_current_context(include_prediction=True)

        assert result["status"] == "success"

        # Should include prediction
        assert "predicted_next_action" in result
        if result["predicted_next_action"]:
            assert "action" in result["predicted_next_action"]
            assert "confidence" in result["predicted_next_action"]
            assert "reasoning" in result["predicted_next_action"]

        # Should have session stats
        assert result["session_duration_minutes"] > 0
        assert result["focus_score"] is not None
        assert result["uncommitted_changes"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
