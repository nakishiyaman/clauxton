"""
Tests for error recovery functionality.
"""

from clauxton.core.task_manager import TaskManager


class TestErrorRecoveryRollback:
    """Test rollback error recovery strategy (default)."""

    def test_rollback_on_validation_error(self, tmp_path):
        """Test that rollback reverts all changes on validation error."""
        tm = TaskManager(tmp_path)

        # YAML with one valid task and one invalid task (missing name)
        yaml_content = """
        tasks:
          - name: "Valid Task"
            priority: high
          - priority: medium
            # Missing required 'name' field
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        # Should return error status, no tasks imported
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["task_ids"]) == 0
        assert len(result["errors"]) > 0
        assert "name" in result["errors"][0].lower() or "required" in result["errors"][0].lower()

        # Verify no tasks were created
        tasks = tm.list_all()
        assert len(tasks) == 0

    def test_rollback_default_strategy(self, tmp_path):
        """Test that rollback is the default error recovery strategy."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: invalid_priority  # Invalid priority
        """

        # Don't specify on_error, should default to rollback
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(tm.list_all()) == 0

    def test_rollback_multiple_errors(self, tmp_path):
        """Test rollback with multiple validation errors."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Valid Task"
            priority: high
          - priority: medium
            # Missing name
          - name: "Another Task"
            priority: invalid
            # Invalid priority
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) >= 2  # At least 2 errors
        assert len(tm.list_all()) == 0


class TestErrorRecoverySkip:
    """Test skip error recovery strategy."""

    def test_skip_invalid_tasks(self, tmp_path):
        """Test that skip strategy skips invalid tasks and continues."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: medium
            # Missing name - should be skipped
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        # Should return partial status
        assert result["status"] == "partial"
        assert result["imported"] == 2  # Only 2 valid tasks
        assert len(result["task_ids"]) == 2
        assert len(result["errors"]) == 1  # 1 error logged
        assert len(result["skipped"]) == 1  # 1 task skipped
        assert "unnamed" in result["skipped"][0]

        # Verify only valid tasks were created
        tasks = tm.list_all()
        assert len(tasks) == 2
        assert tasks[0].name == "Task 1"
        assert tasks[1].name == "Task 3"

    def test_skip_multiple_invalid_tasks(self, tmp_path):
        """Test skip with multiple invalid tasks."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: invalid
            # Invalid priority
          - priority: medium
            # Missing name
          - name: "Task 4"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        assert result["status"] == "partial"
        assert result["imported"] == 2  # Task 1 and Task 4
        assert len(result["errors"]) == 2
        assert len(result["skipped"]) == 2

        tasks = tm.list_all()
        assert len(tasks) == 2
        assert tasks[0].name == "Task 1"
        assert tasks[1].name == "Task 4"

    def test_skip_all_invalid(self, tmp_path):
        """Test skip when all tasks are invalid."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - priority: high
            # Missing name
          - name: "Task 2"
            priority: invalid
            # Invalid priority
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        # All tasks failed, return error
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) == 2
        assert len(result["skipped"]) == 2
        assert len(tm.list_all()) == 0

    def test_skip_with_success(self, tmp_path):
        """Test skip strategy with all valid tasks (success case)."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        # All tasks valid, should be success
        assert result["status"] == "success"
        assert result["imported"] == 2
        assert len(result["errors"]) == 0
        assert "skipped" not in result or len(result["skipped"]) == 0


class TestErrorRecoveryAbort:
    """Test abort error recovery strategy."""

    def test_abort_on_first_error(self, tmp_path):
        """Test that abort stops immediately on first error."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: medium
            # Missing name - should abort here
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="abort")

        # Should return error immediately
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["task_ids"]) == 0
        assert len(result["errors"]) == 1  # Only 1 error (aborted)

        # No tasks created
        tasks = tm.list_all()
        assert len(tasks) == 0

    def test_abort_with_multiple_potential_errors(self, tmp_path):
        """Test abort stops at first error, not processing subsequent errors."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: invalid
            # First error - should abort
          - priority: medium
            # Second error - not processed
        """

        result = tm.import_yaml(yaml_content, on_error="abort")

        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(result["errors"]) == 1  # Only first error
        assert len(tm.list_all()) == 0

    def test_abort_with_valid_tasks_before_error(self, tmp_path):
        """Test abort doesn't commit valid tasks processed before error."""
        tm = TaskManager(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
          - priority: low
            # Error on third task
        """

        result = tm.import_yaml(yaml_content, on_error="abort")

        # Abort strategy: No tasks committed
        assert result["status"] == "error"
        assert result["imported"] == 0
        assert len(tm.list_all()) == 0


class TestErrorRecoveryWithUndo:
    """Test error recovery integration with undo functionality."""

    def test_rollback_no_undo_history(self, tmp_path):
        """Test that rollback doesn't create undo history (no changes made)."""
        from clauxton.core.operation_history import OperationHistory

        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: invalid
        """

        result = tm.import_yaml(yaml_content, on_error="rollback")

        assert result["status"] == "error"

        # No operation recorded (rollback means no changes)
        operations = history.list_operations()
        assert len(operations) == 0

    def test_skip_creates_undo_history(self, tmp_path):
        """Test that skip strategy creates undo history for successful imports."""
        from clauxton.core.operation_history import OperationHistory

        tm = TaskManager(tmp_path)
        history = OperationHistory(tmp_path)

        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - priority: invalid
            # Skipped
          - name: "Task 3"
            priority: low
        """

        result = tm.import_yaml(yaml_content, on_error="skip")

        assert result["status"] == "partial"
        assert result["imported"] == 2

        # Operation recorded for 2 successfully imported tasks
        operations = history.list_operations()
        assert len(operations) == 1
        assert operations[0].operation_type == "task_import"
        assert operations[0].operation_data["task_ids"] == result["task_ids"]
