"""
Repository Map for automatic codebase indexing.

This module provides automatic understanding of codebase structure through:
- File structure indexing (respects .gitignore)
- Symbol extraction (functions, classes, methods)
- Dependency graph building
- Semantic search over code

Example:
    >>> from clauxton.intelligence import RepositoryMap
    >>> repo_map = RepositoryMap(".")
    >>> result = repo_map.index()
    >>> print(f"Indexed {result.files_indexed} files")
    >>> symbols = repo_map.search("authentication")
"""

from pathlib import Path
from typing import List, Dict, Optional, Literal, Callable
from datetime import datetime
import json
import logging

from clauxton.core.models import ClauxtonError

logger = logging.getLogger(__name__)


class RepositoryMapError(ClauxtonError):
    """Base error for repository map operations."""
    pass


class IndexResult:
    """Result of indexing operation."""

    def __init__(
        self,
        files_indexed: int,
        symbols_found: int,
        duration_seconds: float,
        errors: Optional[List[str]] = None
    ):
        """
        Initialize index result.

        Args:
            files_indexed: Number of files successfully indexed
            symbols_found: Number of symbols extracted
            duration_seconds: Time taken for indexing
            errors: List of error messages (if any)
        """
        self.files_indexed = files_indexed
        self.symbols_found = symbols_found
        self.duration_seconds = duration_seconds
        self.errors = errors or []

    def __repr__(self) -> str:
        return (
            f"IndexResult(files={self.files_indexed}, "
            f"symbols={self.symbols_found}, "
            f"duration={self.duration_seconds:.2f}s)"
        )


class FileNode:
    """Represents a file in the repository."""

    def __init__(
        self,
        path: Path,
        relative_path: str,
        file_type: str,
        language: Optional[str],
        size_bytes: int,
        line_count: int,
        last_modified: datetime,
    ):
        """Initialize file node."""
        self.path = path
        self.relative_path = relative_path
        self.file_type = file_type
        self.language = language
        self.size_bytes = size_bytes
        self.line_count = line_count
        self.last_modified = last_modified

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "relative_path": self.relative_path,
            "file_type": self.file_type,
            "language": self.language,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
            "last_modified": self.last_modified.isoformat(),
        }


class Symbol:
    """Represents a code symbol (function, class, etc.)."""

    def __init__(
        self,
        name: str,
        type: str,
        file_path: str,
        line_start: int,
        line_end: int,
        docstring: Optional[str] = None,
        signature: Optional[str] = None,
    ):
        """Initialize symbol."""
        self.name = name
        self.type = type
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.docstring = docstring
        self.signature = signature

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "docstring": self.docstring,
            "signature": self.signature,
        }

    def __repr__(self) -> str:
        return f"Symbol({self.name}, {self.type}, {self.file_path}:{self.line_start})"


class RepositoryMap:
    """
    Indexes and queries codebase structure.

    This class provides automatic codebase understanding through file indexing
    and symbol extraction. It creates a searchable map of your code.

    Usage:
        >>> repo_map = RepositoryMap(Path("."))
        >>> result = repo_map.index()
        >>> print(f"Found {result.symbols_found} symbols")
        >>>
        >>> # Search for symbols
        >>> results = repo_map.search("create_user")
        >>> for symbol in results:
        ...     print(f"{symbol.name} at {symbol.file_path}:{symbol.line_start}")

    Attributes:
        root_dir: Project root directory
        map_dir: Directory where index data is stored (.clauxton/map/)
    """

    def __init__(self, root_dir: Path | str):
        """
        Initialize repository map at root_dir.

        Args:
            root_dir: Project root directory (Path or str)

        Raises:
            RepositoryMapError: If root_dir doesn't exist
        """
        self.root_dir = Path(root_dir) if isinstance(root_dir, str) else root_dir

        if not self.root_dir.exists():
            raise RepositoryMapError(f"Root directory does not exist: {self.root_dir}")

        # Ensure .clauxton directory exists
        clauxton_dir = self.root_dir / ".clauxton"
        clauxton_dir.mkdir(parents=True, exist_ok=True)

        # Map data directory
        self.map_dir = clauxton_dir / "map"
        self.map_dir.mkdir(parents=True, exist_ok=True)

        # Lazy-loaded data
        self._index: Optional[Dict] = None
        self._symbols: Optional[Dict] = None

        logger.debug(f"RepositoryMap initialized at {self.root_dir}")

    def index(
        self,
        incremental: bool = False,
        progress_callback: Optional[Callable[[int, Optional[int], str], None]] = None
    ) -> IndexResult:
        """
        Index the codebase.

        Scans all files in the repository, extracts symbols from source files,
        and builds an index for fast searching.

        Args:
            incremental: If True, only index changed files (not implemented yet)
            progress_callback: Optional callback (current, total, status) -> None

        Returns:
            IndexResult with statistics

        Note:
            This is a placeholder implementation. Full implementation in Task 3.
        """
        logger.info("Index method called (placeholder)")

        if incremental:
            logger.warning("Incremental indexing not yet implemented")

        # Placeholder return
        return IndexResult(
            files_indexed=0,
            symbols_found=0,
            duration_seconds=0.0,
            errors=["Not implemented yet - Task 3"]
        )

    def search(
        self,
        query: str,
        search_type: Literal["semantic", "exact", "fuzzy"] = "exact",
        limit: int = 20
    ) -> List[Symbol]:
        """
        Search codebase for symbols.

        Args:
            query: Search query (symbol name or pattern)
            search_type: Search algorithm to use
                - "exact": Exact substring match (default)
                - "fuzzy": Fuzzy matching (typo-tolerant)
                - "semantic": TF-IDF semantic search (not implemented)
            limit: Maximum number of results to return

        Returns:
            List of matching symbols, ranked by relevance

        Note:
            This is a placeholder implementation. Full implementation in Task 5.
        """
        logger.info(f"Search called for '{query}' (placeholder)")

        # Placeholder return
        return []

    @property
    def index_data(self) -> Dict:
        """
        Lazy load index data from disk.

        Returns:
            Index data dictionary with file information
        """
        if self._index is None:
            index_file = self.map_dir / "index.json"
            if index_file.exists():
                logger.debug(f"Loading index from {index_file}")
                with open(index_file) as f:
                    self._index = json.load(f)
            else:
                logger.debug("No index file found, returning empty index")
                self._index = {
                    "version": "0.11.0",
                    "indexed_at": None,
                    "root_path": str(self.root_dir),
                    "files": [],
                    "statistics": {
                        "total_files": 0,
                        "by_type": {},
                        "by_language": {},
                    }
                }
        return self._index

    @property
    def symbols_data(self) -> Dict:
        """
        Lazy load symbols data from disk.

        Returns:
            Symbols data dictionary mapping file paths to symbol lists
        """
        if self._symbols is None:
            symbols_file = self.map_dir / "symbols.json"
            if symbols_file.exists():
                logger.debug(f"Loading symbols from {symbols_file}")
                with open(symbols_file) as f:
                    self._symbols = json.load(f)
            else:
                logger.debug("No symbols file found, returning empty dict")
                self._symbols = {}
        return self._symbols

    def clear_cache(self) -> None:
        """Clear in-memory cache, forcing reload from disk."""
        self._index = None
        self._symbols = None
        logger.debug("Cache cleared")
