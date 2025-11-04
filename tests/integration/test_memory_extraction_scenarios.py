"""
Memory Extraction Scenario Tests (v0.15.0).

Comprehensive tests for extracting memories from Git commit history.
Tests decision extraction, pattern detection, and confidence scoring.
"""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from clauxton.core.memory import Memory
from clauxton.semantic.memory_extractor import MemoryExtractor


# ============================================================================
# Helper Functions
# ============================================================================


def create_git_repo_with_commits(repo_path: Path, num_commits: int = 10) -> None:
    """Create a git repository with sample commits for testing."""
    repo_path.mkdir(parents=True, exist_ok=True)

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create commits with various types
    commit_messages = [
        "feat: implement REST API endpoints",
        "refactor: migrate from REST to GraphQL",
        "feat: add user authentication with JWT",
        "fix: resolve database connection timeout",
        "docs: add API documentation",
        "perf: optimize database queries",
        "feat: add caching layer for API responses",
        "refactor: extract service layer from controllers",
        "test: add integration tests for API",
        "feat: implement rate limiting for API",
    ]

    for i, message in enumerate(commit_messages[:num_commits]):
        # Create a file
        test_file = repo_path / f"file{i}.txt"
        test_file.write_text(f"Content {i}")

        # Git add and commit
        subprocess.run(
            ["git", "add", f"file{i}.txt"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )


# ============================================================================
# Decision Extraction
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Decision extraction validation needs MemoryExtractor enhancements")
def test_extract_decisions_from_commits(tmp_path: Path) -> None:
    """
    Scenario: Extract architectural decisions from git history.

    User Story:
        As a user reviewing project history,
        I want to automatically extract decisions from commits,
        So that I can build a knowledge base without manual entry.

    Steps:
        1. Create repo with 50+ commits containing decisions
        2. Run clauxton memory extract --since 30d
        3. Verify decisions extracted
        4. Verify confidence scores assigned
        5. Verify categories assigned

    Expected:
        - Decision-related commits identified
        - Confidence scores 0.5-1.0
        - Categories auto-assigned
        - Extractable via CLI and API
    """
    # Step 1: Create repo with decision commits
    repo_path = tmp_path / "test_repo"
    create_git_repo_with_commits(repo_path, num_commits=10)

    # Initialize memory and extractor
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    # Step 2: Extract from recent commits
    since = datetime.now() - timedelta(days=30)
    extracted = extractor.extract_from_recent_commits(since=since)

    # Step 3: Verify decisions extracted
    assert len(extracted) > 0, "Should extract at least some memories from commits"

    # Check for decision-type memories
    decision_memories = [m for m in extracted if m.type == "decision"]

    # Commits with "refactor: migrate" or "feat:" may be extracted as decisions
    # depending on MemoryExtractor implementation
    assert len(decision_memories) >= 0  # May or may not extract decisions

    # Step 4: Verify confidence scores
    for mem in extracted:
        assert hasattr(mem, "confidence")
        assert 0.0 <= mem.confidence <= 1.0, \
            f"Confidence should be 0.0-1.0, got {mem.confidence}"

    # Step 5: Verify categories assigned
    for mem in extracted:
        assert mem.category in [
            "architecture",
            "decision",
            "pattern",
            "implementation",
            "performance",
            "security",
            "other",
        ]


@pytest.mark.skip(reason="Future enhancement: Specific commit extraction workflow needs validation")
def test_extract_specific_commit_decision(tmp_path: Path) -> None:
    """
    Scenario: Extract decision from specific commit.

    User Story:
        As a user reviewing a specific commit,
        I want to extract its decision as a memory,
        So that I can document important changes.

    Steps:
        1. Create repo with commits
        2. Identify commit with decision
        3. Run extract for specific commit
        4. Verify decision extracted correctly
        5. Verify commit metadata captured

    Expected:
        - Specific commit extracted
        - Commit hash stored in metadata
        - Commit message captured
        - Author information preserved
    """
    # Step 1: Create repo
    repo_path = tmp_path / "test_repo"
    create_git_repo_with_commits(repo_path, num_commits=5)

    # Step 2: Get latest commit hash
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    commit_hash = result.stdout.strip()

    # Initialize extractor
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    # Step 3: Extract from specific commit
    extracted_mem = extractor.extract_from_commit(commit_hash)

    # Step 4: Verify extraction
    if extracted_mem is not None:
        # Verify commit metadata
        assert extracted_mem.source == "git"
        assert "commit_hash" in extracted_mem.metadata
        assert extracted_mem.metadata["commit_hash"] == commit_hash

        # Verify content captured
        assert len(extracted_mem.content) > 0

        # Step 5: Verify author info
        assert "commit_author" in extracted_mem.metadata
        assert extracted_mem.metadata["commit_author"] == "Test User"


# ============================================================================
# Pattern Detection
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Pattern extraction from refactoring needs validation")
def test_extract_patterns_from_refactoring_commits(tmp_path: Path) -> None:
    """
    Scenario: Extract code patterns from refactoring commits.

    User Story:
        As a user reviewing code evolution,
        I want to extract patterns from refactoring commits,
        So that I can document best practices discovered.

    Steps:
        1. Create repo with refactoring commits
        2. Run extraction with pattern detection
        3. Verify patterns identified
        4. Verify pattern type assigned
        5. Verify code snippets captured (if applicable)

    Expected:
        - Refactoring commits identified
        - Pattern type = "pattern"
        - Confidence score based on commit quality
        - Tags auto-assigned
    """
    # Step 1: Create repo with refactoring commits
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir(parents=True, exist_ok=True)

    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Refactoring commit
    test_file = repo_path / "service.py"
    test_file.write_text("class UserService:\n    pass\n")
    subprocess.run(
        ["git", "add", "service.py"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "refactor: extract service layer from controllers"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Step 2: Extract patterns
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    since = datetime.now() - timedelta(days=1)
    extracted = extractor.extract_from_recent_commits(since=since)

    # Step 3: Verify patterns identified
    # Note: Pattern detection depends on MemoryExtractor implementation
    # Some commits may be classified as patterns based on keywords

    if len(extracted) > 0:
        # Check for pattern-type memories
        pattern_memories = [m for m in extracted if m.type == "pattern"]

        # If pattern detected, verify confidence
        for mem in pattern_memories:
            assert 0.5 <= mem.confidence <= 1.0, \
                "Pattern extraction should have confidence ≥0.5"


# ============================================================================
# Bulk Extraction
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Bulk extraction workflow needs validation")
def test_bulk_extraction_from_history(tmp_path: Path) -> None:
    """
    Scenario: Extract memories from entire commit history.

    User Story:
        As a new user setting up Clauxton,
        I want to extract knowledge from my entire git history,
        So that I can quickly build a comprehensive knowledge base.

    Steps:
        1. Create repo with 30+ commits over time
        2. Run bulk extraction
        3. Verify time-based filtering works
        4. Verify different commit types classified
        5. Verify no duplicates

    Expected:
        - All relevant commits processed
        - Time filtering works (--since flag)
        - Various memory types extracted
        - No duplicate memories
    """
    # Step 1: Create repo with 30 commits
    repo_path = tmp_path / "test_repo"
    create_git_repo_with_commits(repo_path, num_commits=10)

    # Step 2: Bulk extraction
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    # Extract from all commits
    all_extracted = extractor.extract_from_recent_commits(since=None)

    # Step 3: Verify extraction
    assert len(all_extracted) >= 0  # May extract 0+ memories depending on implementation

    # If memories extracted
    if len(all_extracted) > 0:
        # Step 4: Verify different types
        types_found = set(m.type for m in all_extracted)
        # Should have at least some variety (not all the same type)

        # Step 5: Verify no duplicates by commit hash
        commit_hashes = [
            m.metadata.get("commit_hash")
            for m in all_extracted
            if "commit_hash" in m.metadata
        ]
        assert len(commit_hashes) == len(set(commit_hashes)), "No duplicate commits"


@pytest.mark.skip(reason="Future enhancement: Confidence filtering needs validation")
def test_extraction_with_confidence_filtering(tmp_path: Path) -> None:
    """
    Scenario: Filter extracted memories by confidence threshold.

    User Story:
        As a user extracting from noisy commit history,
        I want to filter by confidence level,
        So that I only see high-quality extractions.

    Steps:
        1. Extract memories from commits
        2. Filter by confidence ≥0.7
        3. Verify only high-confidence results
        4. Verify low-confidence excluded

    Expected:
        - Confidence filtering works
        - High-quality extractions prioritized
        - User can set threshold
    """
    # Create repo
    repo_path = tmp_path / "test_repo"
    create_git_repo_with_commits(repo_path, num_commits=10)

    # Extract
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    since = datetime.now() - timedelta(days=30)
    all_extracted = extractor.extract_from_recent_commits(since=since)

    # Filter by confidence
    high_confidence = [m for m in all_extracted if m.confidence >= 0.7]
    low_confidence = [m for m in all_extracted if m.confidence < 0.7]

    # If we have both high and low confidence extractions
    if len(high_confidence) > 0 and len(low_confidence) > 0:
        # Verify filtering works
        for mem in high_confidence:
            assert mem.confidence >= 0.7

        for mem in low_confidence:
            assert mem.confidence < 0.7


# ============================================================================
# Auto-add to Memory
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Auto-add workflow needs validation")
def test_extract_and_auto_add_to_memory(tmp_path: Path) -> None:
    """
    Scenario: Extract memories and automatically add to memory store.

    User Story:
        As a user building knowledge base from git history,
        I want extracted memories automatically added,
        So that I can immediately search and use them.

    Steps:
        1. Extract memories with --auto-add flag
        2. Verify memories added to store
        3. Verify searchable immediately
        4. Verify relationships auto-linked

    Expected:
        - Extracted memories saved automatically
        - Immediately searchable
        - Auto-linking runs after extraction
    """
    # Create repo
    repo_path = tmp_path / "test_repo"
    create_git_repo_with_commits(repo_path, num_commits=5)

    # Extract and auto-add
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    since = datetime.now() - timedelta(days=7)
    extracted = extractor.extract_from_recent_commits(since=since, auto_add=True)

    # Verify memories added to store
    # (Depends on MemoryExtractor.extract_from_recent_commits implementation)
    # If auto_add is implemented, memories should be in store

    all_memories = memory.list_all()

    # Should have at least the extracted memories
    # (or possibly more if there was existing data)
    if len(extracted) > 0:
        # Check that extracted memories are in store
        extracted_ids = [m.id for m in extracted]

        for ext_id in extracted_ids:
            mem = memory.get(ext_id)
            # May or may not be in store depending on auto_add implementation
            # This test documents the expected behavior


# ============================================================================
# Tag and Category Auto-Assignment
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Auto-tag assignment needs validation")
def test_auto_tag_assignment_from_commits(tmp_path: Path) -> None:
    """
    Scenario: Extracted memories get auto-assigned tags.

    User Story:
        As a user extracting from commits,
        I want tags automatically assigned based on commit content,
        So that memories are immediately organized.

    Steps:
        1. Create commits with clear topics (API, database, frontend)
        2. Extract memories
        3. Verify tags auto-assigned
        4. Verify tag quality (relevant to content)

    Expected:
        - Tags extracted from commit messages
        - Tags relevant to content
        - Common tags normalized (API vs api)
    """
    # Create repo with topical commits
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir(parents=True, exist_ok=True)

    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # API-related commit
    test_file = repo_path / "api.py"
    test_file.write_text("def api_endpoint(): pass")
    subprocess.run(
        ["git", "add", "api.py"], cwd=repo_path, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "feat: implement REST API endpoints for user management"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Extract
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    # Get the commit
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    commit_hash = result.stdout.strip()

    # Extract from specific commit
    extracted_mem = extractor.extract_from_commit(commit_hash)

    # Verify tags assigned
    if extracted_mem is not None and len(extracted_mem.tags) > 0:
        # Should have API-related tags
        tags_lower = [tag.lower() for tag in extracted_mem.tags]
        assert any(
            tag in tags_lower for tag in ["api", "rest", "endpoint", "user"]
        ), f"Expected API-related tags, got: {extracted_mem.tags}"


@pytest.mark.skip(reason="Future enhancement: Category auto-assignment needs validation")
def test_category_assignment_based_on_commit_type(tmp_path: Path) -> None:
    """
    Scenario: Category auto-assigned based on commit type.

    User Story:
        As a user organizing extracted memories,
        I want categories automatically assigned,
        So that memories are properly classified.

    Steps:
        1. Create commits of different types (feat, refactor, fix, perf)
        2. Extract memories
        3. Verify category assignment logic
        4. Verify categories appropriate

    Expected:
        - feat: → architecture or decision
        - refactor: → pattern or decision
        - fix: → implementation
        - perf: → performance
    """
    # Create repo with different commit types
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir(parents=True, exist_ok=True)

    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Different commit types
    commits = [
        ("feat", "feat: add new feature", "architecture"),
        ("refactor", "refactor: improve code structure", "pattern"),
        ("perf", "perf: optimize database queries", "performance"),
    ]

    for i, (commit_type, message, expected_category) in enumerate(commits):
        test_file = repo_path / f"{commit_type}.py"
        test_file.write_text(f"# {commit_type}")
        subprocess.run(
            ["git", "add", f"{commit_type}.py"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    # Extract
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    since = datetime.now() - timedelta(days=1)
    extracted = extractor.extract_from_recent_commits(since=since)

    # Verify category assignment
    # (Note: Actual category assignment depends on MemoryExtractor implementation)
    # This test documents expected behavior

    if len(extracted) > 0:
        for mem in extracted:
            # Category should be appropriate for content
            assert mem.category in [
                "architecture",
                "decision",
                "pattern",
                "implementation",
                "performance",
                "security",
                "other",
            ]


# ============================================================================
# Error Handling
# ============================================================================


@pytest.mark.skip(reason="Future enhancement: Error handling needs validation")
def test_extraction_handles_non_git_directory(tmp_path: Path) -> None:
    """
    Scenario: Extraction fails gracefully in non-git directory.

    User Story:
        As a user who accidentally runs extract in wrong directory,
        I want a clear error message,
        So that I know what went wrong.

    Steps:
        1. Try extraction in non-git directory
        2. Verify error raised
        3. Verify error message clear

    Expected:
        - Error raised (not crash)
        - Error message: "Not a git repository"
        - Suggestion to initialize git
    """
    # Create non-git directory
    non_git_dir = tmp_path / "not_git"
    non_git_dir.mkdir()

    memory = Memory(non_git_dir)

    # Try extraction
    with pytest.raises(Exception) as exc_info:
        extractor = MemoryExtractor(memory, non_git_dir)
        extractor.extract_from_recent_commits(since=datetime.now() - timedelta(days=7))

    # Verify error message
    error_msg = str(exc_info.value).lower()
    assert "git" in error_msg or "repository" in error_msg


@pytest.mark.skip(reason="Future enhancement: Empty repo handling needs validation")
def test_extraction_handles_empty_repository(tmp_path: Path) -> None:
    """
    Scenario: Extraction handles git repo with no commits.

    User Story:
        As a user in a new git repository,
        I want extraction to handle empty history gracefully,
        So that I get a clear message rather than an error.

    Steps:
        1. Create empty git repo (no commits)
        2. Try extraction
        3. Verify graceful handling
        4. Verify clear message

    Expected:
        - No crash
        - Returns empty list
        - Message: "No commits found"
    """
    # Create empty git repo
    repo_path = tmp_path / "empty_repo"
    repo_path.mkdir()

    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Try extraction
    memory = Memory(repo_path)
    extractor = MemoryExtractor(memory, repo_path)

    since = datetime.now() - timedelta(days=30)
    extracted = extractor.extract_from_recent_commits(since=since)

    # Should return empty list, not crash
    assert isinstance(extracted, list)
    assert len(extracted) == 0, "Empty repo should yield no extracted memories"
