"""
Project context awareness for intelligent, context-aware suggestions.

This module provides rich contextual information about the current project state,
including git branch, active files, recent commits, and time-based context.
"""

import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


class ProjectContext(BaseModel):
    """Rich project context for intelligent suggestions."""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    current_branch: Optional[str] = Field(
        None, description="Current git branch name"
    )
    active_files: List[str] = Field(
        default_factory=list, description="Recently modified files"
    )
    recent_commits: List[Dict[str, str]] = Field(
        default_factory=list, description="Recent commit information"
    )
    current_task: Optional[str] = Field(
        None, description="Current task ID from task manager"
    )
    time_context: str = Field(
        "unknown", description="Time context: morning, afternoon, evening, night"
    )
    work_session_start: Optional[datetime] = Field(
        None, description="When current work session started"
    )
    last_activity: Optional[datetime] = Field(
        None, description="Last detected activity"
    )
    is_feature_branch: bool = Field(
        False, description="Whether current branch is a feature branch"
    )
    is_git_repo: bool = Field(True, description="Whether project is a git repository")

    # Week 3: Session analysis
    session_duration_minutes: Optional[int] = Field(
        None, description="Current session duration in minutes"
    )
    focus_score: Optional[float] = Field(
        None, description="Focus score (0.0-1.0), based on file switch frequency"
    )
    breaks_detected: int = Field(
        0, description="Number of breaks detected in current session"
    )

    # Week 3: Prediction
    predicted_next_action: Optional[Dict[str, Any]] = Field(
        None, description="Predicted next action based on patterns"
    )

    # Week 3: Enhanced git stats
    uncommitted_changes: int = Field(
        0, description="Number of uncommitted changes"
    )
    diff_stats: Optional[Dict[str, int]] = Field(
        None, description="Git diff statistics (additions, deletions, files_changed)"
    )


class ContextManager:
    """Manage and provide project context."""

    def __init__(self, project_root: Path):
        """
        Initialize context manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self._cache: Dict[str, Any] = {}
        self._cache_timeout = timedelta(seconds=30)  # Cache for 30 seconds

    def get_current_context(self) -> ProjectContext:
        """
        Get comprehensive project context.

        Returns:
            ProjectContext with all available information
        """
        # Check cache
        cache_key = "current_context"
        if cache_key in self._cache:
            cached_data = self._cache[cache_key]
            cached_context: ProjectContext = cached_data[0]
            cached_time: datetime = cached_data[1]
            if datetime.now() - cached_time < self._cache_timeout:
                return cached_context

        # Build fresh context
        context = ProjectContext(
            current_branch=self._get_current_branch(),
            active_files=self.detect_active_files(minutes=30),
            recent_commits=self._get_recent_commits(limit=5),
            current_task=self._infer_current_task(),
            time_context=self.get_time_context(),
            work_session_start=self._estimate_session_start(),
            last_activity=datetime.now(),
            is_feature_branch=self._is_feature_branch(),
            is_git_repo=self._is_git_repository(),
        )

        # Cache the result
        self._cache[cache_key] = (context, datetime.now())

        return context

    def detect_active_files(self, minutes: int = 30) -> List[str]:
        """
        Detect recently modified files.

        Args:
            minutes: Time window in minutes (default: 30)

        Returns:
            List of file paths relative to project root
        """
        active_files: List[str] = []

        try:
            # Use find to get recently modified files
            # Search only common source directories to avoid scanning everything
            search_dirs = [".", "src", "lib", "clauxton", "tests"]

            for search_dir in search_dirs:
                dir_path = self.project_root / search_dir
                if not dir_path.exists():
                    continue

                # Find files modified in the last N minutes
                result = subprocess.run(
                    [
                        "find",
                        str(dir_path),
                        "-type",
                        "f",
                        "-mmin",
                        f"-{minutes}",
                        "-not",
                        "-path",
                        "*/.git/*",
                        "-not",
                        "-path",
                        "*/__pycache__/*",
                        "-not",
                        "-path",
                        "*/.clauxton/*",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    files = result.stdout.strip().split("\n")
                    for file_path in files:
                        if file_path:
                            try:
                                rel_path = Path(file_path).relative_to(self.project_root)
                                active_files.append(str(rel_path))
                            except ValueError:
                                pass  # Skip files outside project root

        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout detecting active files in {search_dir}")
        except FileNotFoundError:
            logger.debug("find command not available")
        except Exception as e:
            logger.error(f"Error detecting active files: {e}")

        return sorted(list(set(active_files)))  # Deduplicate and sort

    def get_branch_context(self) -> Dict[str, Any]:
        """
        Get git branch information.

        Returns:
            Dictionary with branch details
        """
        return {
            "current_branch": self._get_current_branch(),
            "is_feature_branch": self._is_feature_branch(),
            "is_main_branch": self._is_main_branch(),
            "is_git_repo": self._is_git_repository(),
        }

    def get_time_context(self) -> str:
        """
        Get time-based context.

        Returns:
            "morning", "afternoon", "evening", or "night"
        """
        hour = datetime.now().hour

        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"

    def infer_current_task(self) -> Optional[str]:
        """
        Infer what user is working on based on context.

        Returns:
            Task ID or description, if detectable
        """
        return self._infer_current_task()

    def _get_current_branch(self) -> Optional[str]:
        """
        Get current git branch name.

        Returns:
            Branch name or None if not in git repo
        """
        if not self._is_git_repository():
            return None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting git branch")
        except FileNotFoundError:
            logger.debug("git command not available")
        except Exception as e:
            logger.error(f"Error getting git branch: {e}")

        return None

    def _is_git_repository(self) -> bool:
        """
        Check if project is a git repository.

        Returns:
            True if git repository, False otherwise
        """
        git_dir = self.project_root / ".git"
        return git_dir.exists()

    def _is_feature_branch(self) -> bool:
        """
        Check if current branch is a feature branch.

        Returns:
            True if branch name suggests feature branch
        """
        branch = self._get_current_branch()
        if not branch:
            return False

        # Common feature branch prefixes
        feature_prefixes = ["feature/", "feat/", "fix/", "bugfix/", "hotfix/"]
        return any(branch.startswith(prefix) for prefix in feature_prefixes)

    def _is_main_branch(self) -> bool:
        """
        Check if current branch is main/master branch.

        Returns:
            True if main or master branch
        """
        branch = self._get_current_branch()
        return branch in ["main", "master"] if branch else False

    def _get_recent_commits(self, limit: int = 5) -> List[Dict[str, str]]:
        """
        Get recent git commits.

        Args:
            limit: Maximum number of commits to retrieve

        Returns:
            List of commit dictionaries
        """
        if not self._is_git_repository():
            return []

        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"-{limit}",
                    "--pretty=format:%H|%an|%ae|%s|%ai",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3,
            )

            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split("|")
                        if len(parts) >= 5:
                            commits.append(
                                {
                                    "hash": parts[0][:8],  # Short hash
                                    "author_name": parts[1],
                                    "author_email": parts[2],
                                    "message": parts[3],
                                    "date": parts[4],
                                }
                            )
                return commits
        except subprocess.TimeoutExpired:
            logger.warning("Timeout getting git commits")
        except FileNotFoundError:
            logger.debug("git command not available")
        except Exception as e:
            logger.error(f"Error getting git commits: {e}")

        return []

    def _infer_current_task(self) -> Optional[str]:
        """
        Infer current task from branch name or recent commits.

        Returns:
            Task ID or None
        """
        branch = self._get_current_branch()
        if not branch:
            return None

        # Try to extract task ID from branch name
        # Common patterns: feature/TASK-123, fix/TASK-456
        import re

        task_pattern = r"TASK-\d+"
        match = re.search(task_pattern, branch)
        if match:
            return match.group(0)

        # Check recent commit messages
        commits = self._get_recent_commits(limit=3)
        for commit in commits:
            match = re.search(task_pattern, commit["message"])
            if match:
                return match.group(0)

        return None

    def _estimate_session_start(self) -> Optional[datetime]:
        """
        Estimate when current work session started.

        Returns:
            Estimated session start time
        """
        active_files = self.detect_active_files(minutes=120)  # Check last 2 hours

        if not active_files:
            return None

        # Try to get oldest modification time from active files
        try:
            oldest_time = None
            for file_path in active_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    mtime = datetime.fromtimestamp(full_path.stat().st_mtime)
                    if oldest_time is None or mtime < oldest_time:
                        oldest_time = mtime

            return oldest_time
        except Exception:
            return None

    def clear_cache(self) -> None:
        """Clear the context cache."""
        self._cache.clear()
