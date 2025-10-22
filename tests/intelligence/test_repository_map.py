"""Tests for clauxton.intelligence.repository_map module."""

import pytest
from pathlib import Path
from clauxton.intelligence.repository_map import (
    RepositoryMap,
    RepositoryMapError,
    IndexResult,
    FileNode,
    Symbol,
)


class TestRepositoryMapInit:
    """Test RepositoryMap initialization."""

    def test_init_with_path_object(self, tmp_path):
        """Test initialization with Path object."""
        repo_map = RepositoryMap(tmp_path)
        assert repo_map.root_dir == tmp_path
        assert repo_map.map_dir == tmp_path / ".clauxton" / "map"
        assert repo_map.map_dir.exists()

    def test_init_with_string_path(self, tmp_path):
        """Test initialization with string path."""
        repo_map = RepositoryMap(str(tmp_path))
        assert repo_map.root_dir == tmp_path
        assert isinstance(repo_map.root_dir, Path)

    def test_init_creates_clauxton_directory(self, tmp_path):
        """Test that initialization creates .clauxton directory."""
        clauxton_dir = tmp_path / ".clauxton"
        assert not clauxton_dir.exists()

        RepositoryMap(tmp_path)

        assert clauxton_dir.exists()
        assert (clauxton_dir / "map").exists()

    def test_init_with_nonexistent_directory_raises_error(self, tmp_path):
        """Test that initializing with non-existent directory raises error."""
        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises(RepositoryMapError):
            RepositoryMap(nonexistent)

    def test_multiple_init_same_directory(self, tmp_path):
        """Test that multiple initializations on same directory work."""
        repo_map1 = RepositoryMap(tmp_path)
        repo_map2 = RepositoryMap(tmp_path)

        assert repo_map1.root_dir == repo_map2.root_dir
        assert repo_map1.map_dir == repo_map2.map_dir


class TestRepositoryMapLazyLoading:
    """Test lazy loading of index and symbols data."""

    def test_index_data_lazy_loading(self, tmp_path):
        """Test that index data is not loaded until accessed."""
        repo_map = RepositoryMap(tmp_path)

        # Initially None
        assert repo_map._index is None

        # Access triggers loading
        index = repo_map.index_data
        assert repo_map._index is not None
        assert isinstance(index, dict)

    def test_symbols_data_lazy_loading(self, tmp_path):
        """Test that symbols data is not loaded until accessed."""
        repo_map = RepositoryMap(tmp_path)

        # Initially None
        assert repo_map._symbols is None

        # Access triggers loading
        symbols = repo_map.symbols_data
        assert repo_map._symbols is not None
        assert isinstance(symbols, dict)

    def test_index_data_returns_default_when_no_file(self, tmp_path):
        """Test that index_data returns default structure when no file exists."""
        repo_map = RepositoryMap(tmp_path)
        index = repo_map.index_data

        assert index["version"] == "0.11.0"
        assert index["indexed_at"] is None
        assert index["root_path"] == str(tmp_path)
        assert index["files"] == []
        assert index["statistics"]["total_files"] == 0

    def test_symbols_data_returns_empty_when_no_file(self, tmp_path):
        """Test that symbols_data returns empty dict when no file exists."""
        repo_map = RepositoryMap(tmp_path)
        symbols = repo_map.symbols_data

        assert symbols == {}

    def test_clear_cache(self, tmp_path):
        """Test clearing cache."""
        repo_map = RepositoryMap(tmp_path)

        # Load data
        _ = repo_map.index_data
        _ = repo_map.symbols_data
        assert repo_map._index is not None
        assert repo_map._symbols is not None

        # Clear cache
        repo_map.clear_cache()
        assert repo_map._index is None
        assert repo_map._symbols is None


class TestIndexResult:
    """Test IndexResult class."""

    def test_index_result_creation(self):
        """Test creating IndexResult."""
        result = IndexResult(
            files_indexed=10,
            symbols_found=50,
            duration_seconds=1.5
        )

        assert result.files_indexed == 10
        assert result.symbols_found == 50
        assert result.duration_seconds == 1.5
        assert result.errors == []

    def test_index_result_with_errors(self):
        """Test IndexResult with errors."""
        errors = ["Error 1", "Error 2"]
        result = IndexResult(
            files_indexed=5,
            symbols_found=20,
            duration_seconds=0.5,
            errors=errors
        )

        assert result.errors == errors

    def test_index_result_repr(self):
        """Test IndexResult string representation."""
        result = IndexResult(10, 50, 1.5)
        repr_str = repr(result)

        assert "10" in repr_str
        assert "50" in repr_str
        assert "1.5" in repr_str or "1.50" in repr_str


class TestFileNode:
    """Test FileNode class."""

    def test_file_node_creation(self, tmp_path):
        """Test creating FileNode."""
        from datetime import datetime

        file_path = tmp_path / "test.py"
        node = FileNode(
            path=file_path,
            relative_path="test.py",
            file_type="source",
            language="python",
            size_bytes=1024,
            line_count=50,
            last_modified=datetime.now()
        )

        assert node.path == file_path
        assert node.relative_path == "test.py"
        assert node.file_type == "source"
        assert node.language == "python"

    def test_file_node_to_dict(self, tmp_path):
        """Test FileNode.to_dict()."""
        from datetime import datetime

        file_path = tmp_path / "test.py"
        now = datetime.now()

        node = FileNode(
            path=file_path,
            relative_path="test.py",
            file_type="source",
            language="python",
            size_bytes=1024,
            line_count=50,
            last_modified=now
        )

        d = node.to_dict()

        assert d["path"] == str(file_path)
        assert d["relative_path"] == "test.py"
        assert d["file_type"] == "source"
        assert d["language"] == "python"
        assert d["size_bytes"] == 1024
        assert d["line_count"] == 50
        assert isinstance(d["last_modified"], str)


class TestSymbol:
    """Test Symbol class."""

    def test_symbol_creation(self):
        """Test creating Symbol."""
        symbol = Symbol(
            name="my_function",
            type="function",
            file_path="/path/to/file.py",
            line_start=10,
            line_end=20,
            docstring="Does something",
            signature="def my_function(x: int) -> str"
        )

        assert symbol.name == "my_function"
        assert symbol.type == "function"
        assert symbol.file_path == "/path/to/file.py"
        assert symbol.line_start == 10
        assert symbol.line_end == 20

    def test_symbol_to_dict(self):
        """Test Symbol.to_dict()."""
        symbol = Symbol(
            name="MyClass",
            type="class",
            file_path="/path/to/file.py",
            line_start=5,
            line_end=15
        )

        d = symbol.to_dict()

        assert d["name"] == "MyClass"
        assert d["type"] == "class"
        assert d["file_path"] == "/path/to/file.py"
        assert d["line_start"] == 5
        assert d["line_end"] == 15

    def test_symbol_repr(self):
        """Test Symbol string representation."""
        symbol = Symbol(
            name="test_func",
            type="function",
            file_path="test.py",
            line_start=1,
            line_end=5
        )

        repr_str = repr(symbol)
        assert "test_func" in repr_str
        assert "function" in repr_str
        assert "test.py" in repr_str


class TestRepositoryMapIndex:
    """Test RepositoryMap.index() method."""

    def test_index_returns_index_result(self, tmp_path):
        """Test that index() returns IndexResult."""
        repo_map = RepositoryMap(tmp_path)
        result = repo_map.index()

        assert isinstance(result, IndexResult)

    def test_index_placeholder_implementation(self, tmp_path):
        """Test placeholder index implementation."""
        repo_map = RepositoryMap(tmp_path)
        result = repo_map.index()

        # Placeholder returns zeros
        assert result.files_indexed == 0
        assert result.symbols_found == 0
        assert len(result.errors) > 0  # Has "not implemented" error


class TestRepositoryMapSearch:
    """Test RepositoryMap.search() method."""

    def test_search_returns_list(self, tmp_path):
        """Test that search() returns a list."""
        repo_map = RepositoryMap(tmp_path)
        results = repo_map.search("test")

        assert isinstance(results, list)

    def test_search_placeholder_implementation(self, tmp_path):
        """Test placeholder search implementation."""
        repo_map = RepositoryMap(tmp_path)
        results = repo_map.search("anything")

        # Placeholder returns empty list
        assert results == []
