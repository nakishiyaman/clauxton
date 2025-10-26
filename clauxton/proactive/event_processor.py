"""Process file system events and detect patterns."""

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from clauxton.proactive.models import (
    ActivitySummary,
    ChangeType,
    DetectedPattern,
    FileChange,
    PatternType,
)
from clauxton.utils.yaml_utils import read_yaml, write_yaml


class EventProcessor:
    """Process file system events and detect patterns."""

    def __init__(self, project_root: Path):
        """Initialize event processor."""
        self.project_root = project_root
        self.clauxton_dir = project_root / ".clauxton"
        self.activity_file = self.clauxton_dir / "activity.yml"

    async def detect_patterns(
        self, changes: List[FileChange], confidence_threshold: float = 0.6
    ) -> List[DetectedPattern]:
        """
        Detect patterns in file changes.

        Args:
            changes: List of file changes
            confidence_threshold: Minimum confidence to return pattern

        Returns:
            List of detected patterns
        """
        if not changes:
            return []

        patterns: List[DetectedPattern] = []

        # Detect bulk edit (many modifications in short time)
        bulk_edit = self._detect_bulk_edit(changes)
        if bulk_edit and bulk_edit.confidence >= confidence_threshold:
            patterns.append(bulk_edit)

        # Detect new feature (new files created)
        new_feature = self._detect_new_feature(changes)
        if new_feature and new_feature.confidence >= confidence_threshold:
            patterns.append(new_feature)

        # Detect refactoring (files moved/renamed)
        refactoring = self._detect_refactoring(changes)
        if refactoring and refactoring.confidence >= confidence_threshold:
            patterns.append(refactoring)

        # Detect cleanup (files deleted)
        cleanup = self._detect_cleanup(changes)
        if cleanup and cleanup.confidence >= confidence_threshold:
            patterns.append(cleanup)

        # Detect configuration changes
        config_change = self._detect_configuration(changes)
        if config_change and config_change.confidence >= confidence_threshold:
            patterns.append(config_change)

        return patterns

    def _detect_bulk_edit(self, changes: List[FileChange]) -> Optional[DetectedPattern]:
        """Detect bulk editing pattern."""
        modified = [c for c in changes if c.change_type == ChangeType.MODIFIED]

        if len(modified) < 3:
            return None

        # Check time span (bulk edit = many files in short time)
        if modified:
            time_span = max(c.timestamp for c in modified) - min(
                c.timestamp for c in modified
            )
            if time_span > timedelta(minutes=5):
                return None

        # Calculate confidence based on number of files
        confidence = min(1.0, len(modified) / 10.0)

        return DetectedPattern(
            pattern_type=PatternType.BULK_EDIT,
            files=[c.path for c in modified],
            confidence=confidence,
            description=f"Bulk edit: {len(modified)} files modified",
        )

    def _detect_new_feature(self, changes: List[FileChange]) -> Optional[DetectedPattern]:
        """Detect new feature pattern (new files created)."""
        created = [c for c in changes if c.change_type == ChangeType.CREATED]

        if len(created) < 2:
            return None

        # Check if files are in same directory (likely related)
        directories = [c.path.parent for c in created]
        dir_counts = Counter(directories)
        most_common_dir, count = dir_counts.most_common(1)[0]

        if count < 2:
            return None

        # Calculate confidence
        confidence = min(1.0, count / 5.0)

        return DetectedPattern(
            pattern_type=PatternType.NEW_FEATURE,
            files=[c.path for c in created if c.path.parent == most_common_dir],
            confidence=confidence,
            description=f"New feature: {count} new files in {most_common_dir.name}/",
        )

    def _detect_refactoring(self, changes: List[FileChange]) -> Optional[DetectedPattern]:
        """Detect refactoring pattern (files moved/renamed)."""
        moved = [c for c in changes if c.change_type == ChangeType.MOVED]

        if len(moved) < 2:
            return None

        # Calculate confidence
        confidence = min(1.0, len(moved) / 5.0)

        return DetectedPattern(
            pattern_type=PatternType.REFACTORING,
            files=[c.path for c in moved],
            confidence=confidence,
            description=f"Refactoring: {len(moved)} files moved/renamed",
        )

    def _detect_cleanup(self, changes: List[FileChange]) -> Optional[DetectedPattern]:
        """Detect cleanup pattern (files deleted)."""
        deleted = [c for c in changes if c.change_type == ChangeType.DELETED]

        if len(deleted) < 2:
            return None

        # Calculate confidence
        confidence = min(1.0, len(deleted) / 5.0)

        return DetectedPattern(
            pattern_type=PatternType.CLEANUP,
            files=[c.path for c in deleted],
            confidence=confidence,
            description=f"Cleanup: {len(deleted)} files deleted",
        )

    def _detect_configuration(self, changes: List[FileChange]) -> Optional[DetectedPattern]:
        """Detect configuration changes."""
        config_extensions = {".yml", ".yaml", ".json", ".toml", ".ini", ".conf", ".config"}
        config_names = {"Dockerfile", "Makefile", ".env", ".gitignore"}

        config_changes = [
            c
            for c in changes
            if c.path.suffix in config_extensions or c.path.name in config_names
        ]

        if not config_changes:
            return None

        # Calculate confidence (config files are distinctive)
        confidence = 0.9

        return DetectedPattern(
            pattern_type=PatternType.CONFIGURATION,
            files=[c.path for c in config_changes],
            confidence=confidence,
            description=f"Configuration: {len(config_changes)} config files changed",
        )

    async def create_activity_summary(
        self, changes: List[FileChange], time_window_minutes: int
    ) -> ActivitySummary:
        """
        Create activity summary from changes.

        Args:
            changes: File changes
            time_window_minutes: Time window in minutes

        Returns:
            Activity summary
        """
        # Detect patterns
        patterns = await self.detect_patterns(changes)

        # Count total files
        total_files = len({c.path for c in changes})

        # Find most active directory
        most_active_dir = self._find_most_active_directory(changes)

        return ActivitySummary(
            time_window_minutes=time_window_minutes,
            changes=changes,
            patterns=patterns,
            total_files_changed=total_files,
            most_active_directory=most_active_dir,
        )

    def _find_most_active_directory(self, changes: List[FileChange]) -> Optional[Path]:
        """Find directory with most changes."""
        if not changes:
            return None

        dir_counts: Dict[Path, int] = defaultdict(int)

        for change in changes:
            dir_counts[change.path.parent] += 1

        if not dir_counts:
            return None

        most_active = max(dir_counts.items(), key=lambda x: x[1])
        return most_active[0]

    async def save_activity(self, summary: ActivitySummary) -> None:
        """Save activity summary to file."""
        # Load existing activities
        existing_data = {}
        if self.activity_file.exists():
            existing_data = read_yaml(self.activity_file) or {}

        # Add new activity
        activities = existing_data.get("activities", [])

        # Convert to dict
        summary_dict = summary.model_dump()

        # Convert Path objects to strings
        summary_dict["changes"] = [
            {
                "path": str(c.path),
                "change_type": c.change_type.value,
                "timestamp": c.timestamp.isoformat(),
                "src_path": str(c.src_path) if c.src_path else None,
            }
            for c in summary.changes
        ]

        summary_dict["patterns"] = [
            {
                "pattern_type": p.pattern_type.value,
                "files": [str(f) for f in p.files],
                "confidence": p.confidence,
                "description": p.description,
                "timestamp": p.timestamp.isoformat(),
            }
            for p in summary.patterns
        ]

        if summary.most_active_directory:
            summary_dict["most_active_directory"] = str(summary.most_active_directory)

        activities.append(summary_dict)

        # Keep only last 100 activities
        activities = activities[-100:]

        # Save
        data = {"activities": activities}
        write_yaml(self.activity_file, data)
