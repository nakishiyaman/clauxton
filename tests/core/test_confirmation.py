"""
Tests for confirmation prompts functionality.
"""

import pytest
from pathlib import Path
from clauxton.core.task_manager import TaskManager


class TestConfirmationPrompts:
    """Test confirmation prompts for bulk operations."""

    def test_confirmation_triggered_above_threshold(self, tmp_path):
        """Test that confirmation is required when task count exceeds threshold."""
        tm = TaskManager(tmp_path)

        # Create YAML with 10 tasks (default threshold)
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
          - name: "Task 3"
            priority: medium
          - name: "Task 4"
            priority: medium
          - name: "Task 5"
            priority: medium
          - name: "Task 6"
            priority: low
          - name: "Task 7"
            priority: low
          - name: "Task 8"
            priority: low
          - name: "Task 9"
            priority: low
          - name: "Task 10"
            priority: low
        """

        result = tm.import_yaml(yaml_content)

        # Should require confirmation
        assert result["status"] == "confirmation_required"
        assert result["confirmation_required"] is True
        assert "preview" in result
        assert result["tasks_to_create"] == 10
        assert result["imported"] == 0  # Nothing imported yet

    def test_skip_confirmation_parameter(self, tmp_path):
        """Test that skip_confirmation parameter bypasses confirmation."""
        tm = TaskManager(tmp_path)

        # Create YAML with 10 tasks
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
          - name: "Task 3"
            priority: medium
          - name: "Task 4"
            priority: medium
          - name: "Task 5"
            priority: medium
          - name: "Task 6"
            priority: low
          - name: "Task 7"
            priority: low
          - name: "Task 8"
            priority: low
          - name: "Task 9"
            priority: low
          - name: "Task 10"
            priority: low
        """

        result = tm.import_yaml(yaml_content, skip_confirmation=True)

        # Should directly import without confirmation
        assert result["status"] == "success"
        assert result["imported"] == 10
        assert len(result["task_ids"]) == 10

    def test_below_threshold_no_confirmation(self, tmp_path):
        """Test that tasks below threshold don't require confirmation."""
        tm = TaskManager(tmp_path)

        # Create YAML with 5 tasks (below default threshold of 10)
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
          - name: "Task 3"
            priority: medium
          - name: "Task 4"
            priority: medium
          - name: "Task 5"
            priority: low
        """

        result = tm.import_yaml(yaml_content)

        # Should directly import without confirmation
        assert result["status"] == "success"
        assert result["imported"] == 5
        assert "confirmation_required" not in result

    def test_custom_threshold(self, tmp_path):
        """Test custom confirmation threshold."""
        tm = TaskManager(tmp_path)

        # Create YAML with 5 tasks
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
          - name: "Task 3"
            priority: medium
          - name: "Task 4"
            priority: medium
          - name: "Task 5"
            priority: low
        """

        # Set threshold to 5 - should trigger confirmation
        result = tm.import_yaml(yaml_content, confirmation_threshold=5)

        assert result["status"] == "confirmation_required"
        assert result["confirmation_required"] is True
        assert result["tasks_to_create"] == 5

        # Set threshold to 6 - should not trigger confirmation
        result2 = tm.import_yaml(yaml_content, confirmation_threshold=6)

        assert result2["status"] == "success"
        assert result2["imported"] == 5

    def test_preview_accuracy(self, tmp_path):
        """Test that preview contains accurate information."""
        tm = TaskManager(tmp_path)

        # Create YAML with diverse tasks
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: critical
            estimated_hours: 5
          - name: "Task 2"
            priority: high
            estimated_hours: 3
          - name: "Task 3"
            priority: high
            estimated_hours: 2
          - name: "Task 4"
            priority: medium
            estimated_hours: 4
          - name: "Task 5"
            priority: medium
            estimated_hours: 1
          - name: "Task 6"
            priority: low
            estimated_hours: 2
          - name: "Task 7"
            priority: low
          - name: "Task 8"
            priority: low
          - name: "Task 9"
            priority: low
          - name: "Task 10"
            priority: low
        """

        result = tm.import_yaml(yaml_content)

        assert result["status"] == "confirmation_required"

        preview = result["preview"]
        assert preview["task_count"] == 10
        assert preview["total_estimated_hours"] == 17  # 5+3+2+4+1+2 = 17
        assert preview["by_priority"]["critical"] == 1
        assert preview["by_priority"]["high"] == 2
        assert preview["by_priority"]["medium"] == 2
        assert preview["by_priority"]["low"] == 5
        assert preview["by_status"]["pending"] == 10
        assert len(preview["tasks_summary"]) == 5  # First 5 tasks

        # Verify first task in summary
        assert preview["tasks_summary"][0]["name"] == "Task 1"
        assert preview["tasks_summary"][0]["priority"] == "critical"
        assert preview["tasks_summary"][0]["estimated_hours"] == 5

    def test_dry_run_no_confirmation(self, tmp_path):
        """Test that dry_run mode doesn't trigger confirmation."""
        tm = TaskManager(tmp_path)

        # Create YAML with 10 tasks
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: high
          - name: "Task 3"
            priority: medium
          - name: "Task 4"
            priority: medium
          - name: "Task 5"
            priority: medium
          - name: "Task 6"
            priority: low
          - name: "Task 7"
            priority: low
          - name: "Task 8"
            priority: low
          - name: "Task 9"
            priority: low
          - name: "Task 10"
            priority: low
        """

        result = tm.import_yaml(yaml_content, dry_run=True)

        # Dry run should not trigger confirmation
        assert result["status"] == "success"
        assert result["imported"] == 0  # Nothing imported in dry run
        assert "confirmation_required" not in result
