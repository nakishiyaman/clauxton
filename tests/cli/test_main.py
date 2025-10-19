"""
Tests for CLI commands.

Tests cover:
- init command
- kb add/get/list/search commands
- Error handling
- Invalid inputs
"""

from pathlib import Path

import pytest
from click.testing import CliRunner

from clauxton.cli.main import cli


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create temporary project directory."""
    return tmp_path


# ============================================================================
# init command tests
# ============================================================================


def test_init_creates_clauxton_dir(runner: CliRunner, temp_project: Path) -> None:
    """Test that init command creates .clauxton directory."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert ".clauxton" in result.output
        assert Path(".clauxton").exists()
        assert Path(".clauxton/knowledge-base.yml").exists()


def test_init_creates_gitignore(runner: CliRunner, temp_project: Path) -> None:
    """Test that init command creates .gitignore."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        gitignore = Path(".clauxton/.gitignore")
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "*.bak" in content


def test_init_fails_if_already_initialized(runner: CliRunner, temp_project: Path) -> None:
    """Test that init command fails if .clauxton already exists."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # First init should succeed
        result1 = runner.invoke(cli, ["init"])
        assert result1.exit_code == 0

        # Second init should fail
        result2 = runner.invoke(cli, ["init"])
        assert result2.exit_code != 0
        assert "already exists" in result2.output


def test_init_force_overwrites_existing(runner: CliRunner, temp_project: Path) -> None:
    """Test that init --force overwrites existing .clauxton."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # First init
        result1 = runner.invoke(cli, ["init"])
        assert result1.exit_code == 0

        # Force init should succeed
        result2 = runner.invoke(cli, ["init", "--force"])
        assert result2.exit_code == 0
        assert "Initialized" in result2.output


# ============================================================================
# kb add command tests
# ============================================================================


def test_kb_add_creates_entry(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb add command creates entry."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize first
        runner.invoke(cli, ["init"])

        # Add entry
        result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content\ntest,entry\n",
        )

        assert result.exit_code == 0
        assert "Added entry" in result.output
        assert "KB-" in result.output


def test_kb_add_fails_without_init(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb add fails if not initialized."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content\n\n",
        )

        assert result.exit_code != 0
        assert ".clauxton/ not found" in result.output


# ============================================================================
# kb get command tests
# ============================================================================


def test_kb_get_retrieves_entry(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb get retrieves existing entry."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entry
        runner.invoke(cli, ["init"])
        add_result = runner.invoke(
            cli,
            ["kb", "add"],
            input="Test Entry\narchitecture\nTest content\n\n",
        )

        # Extract entry ID from output
        entry_id = None
        for line in add_result.output.split("\n"):
            if "KB-" in line:
                # Extract KB-YYYYMMDD-NNN pattern
                import re

                match = re.search(r"KB-\d{8}-\d{3}", line)
                if match:
                    entry_id = match.group(0)
                    break

        assert entry_id is not None

        # Get entry
        result = runner.invoke(cli, ["kb", "get", entry_id])

        assert result.exit_code == 0
        assert "Test Entry" in result.output
        assert "architecture" in result.output
        assert "Test content" in result.output


def test_kb_get_fails_for_nonexistent(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb get fails for non-existent entry."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "get", "KB-20251019-999"])

        assert result.exit_code != 0
        assert "Error" in result.output


# ============================================================================
# kb list command tests
# ============================================================================


def test_kb_list_shows_all_entries(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb list shows all entries."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entries
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 1\narchitecture\nContent 1\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 2\ndecision\nContent 2\n\n",
        )

        # List all
        result = runner.invoke(cli, ["kb", "list"])

        assert result.exit_code == 0
        assert "Entry 1" in result.output
        assert "Entry 2" in result.output
        assert "(2)" in result.output  # Should show count


def test_kb_list_filters_by_category(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb list filters by category."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entries
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 1\narchitecture\nContent 1\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Entry 2\ndecision\nContent 2\n\n",
        )

        # List only architecture
        result = runner.invoke(cli, ["kb", "list", "--category", "architecture"])

        assert result.exit_code == 0
        assert "Entry 1" in result.output
        assert "Entry 2" not in result.output


def test_kb_list_empty_shows_help(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb list shows help message when empty."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "list"])

        assert result.exit_code == 0
        assert "No entries found" in result.output
        assert "clauxton kb add" in result.output


# ============================================================================
# kb search command tests
# ============================================================================


def test_kb_search_finds_entries(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb search finds matching entries."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entry
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="Use FastAPI\narchitecture\nAll APIs use FastAPI framework.\n\n",
        )

        # Search
        result = runner.invoke(cli, ["kb", "search", "FastAPI"])

        assert result.exit_code == 0
        assert "Use FastAPI" in result.output
        assert "FastAPI" in result.output


def test_kb_search_no_results(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb search handles no results."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        runner.invoke(cli, ["init"])

        result = runner.invoke(cli, ["kb", "search", "nonexistent"])

        assert result.exit_code == 0
        assert "No results found" in result.output


def test_kb_search_with_category_filter(runner: CliRunner, temp_project: Path) -> None:
    """Test that kb search filters by category."""
    with runner.isolated_filesystem(temp_dir=temp_project):
        # Initialize and add entries
        runner.invoke(cli, ["init"])
        runner.invoke(
            cli,
            ["kb", "add"],
            input="API Design\narchitecture\nAPI uses REST.\n\n",
        )
        runner.invoke(
            cli,
            ["kb", "add"],
            input="API Decision\ndecision\nChoose REST over GraphQL.\n\n",
        )

        # Search with category filter
        result = runner.invoke(
            cli, ["kb", "search", "API", "--category", "architecture"]
        )

        assert result.exit_code == 0
        assert "API Design" in result.output
        assert "API Decision" not in result.output


# ============================================================================
# Version command tests
# ============================================================================


def test_version_command(runner: CliRunner) -> None:
    """Test that --version shows version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


# ============================================================================
# Help command tests
# ============================================================================


def test_help_command(runner: CliRunner) -> None:
    """Test that --help shows help."""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Clauxton" in result.output
    assert "Knowledge Base" in result.output


def test_kb_help_command(runner: CliRunner) -> None:
    """Test that kb --help shows KB commands."""
    result = runner.invoke(cli, ["kb", "--help"])

    assert result.exit_code == 0
    assert "add" in result.output
    assert "get" in result.output
    assert "list" in result.output
    assert "search" in result.output
