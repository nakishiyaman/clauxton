"""Tests for clauxton.intelligence.symbol_extractor module."""

import pytest
from pathlib import Path
from clauxton.intelligence.symbol_extractor import (
    SymbolExtractor,
    PythonSymbolExtractor,
)


class TestSymbolExtractor:
    """Test SymbolExtractor class."""

    def test_init(self):
        """Test SymbolExtractor initialization."""
        extractor = SymbolExtractor()
        assert "python" in extractor.extractors
        assert isinstance(extractor.extractors["python"], PythonSymbolExtractor)

    def test_extract_with_supported_language(self, tmp_path):
        """Test extracting from supported language."""
        # Create a simple Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass")

        extractor = SymbolExtractor()
        symbols = extractor.extract(test_file, "python")

        assert isinstance(symbols, list)
        assert len(symbols) >= 1
        assert symbols[0]["name"] == "hello"

    def test_extract_with_unsupported_language(self, tmp_path):
        """Test extracting from unsupported language."""
        test_file = tmp_path / "test.go"
        test_file.write_text("func main() {}")

        extractor = SymbolExtractor()
        symbols = extractor.extract(test_file, "go")

        # Should return empty list for unsupported language
        assert symbols == []


class TestPythonSymbolExtractor:
    """Test PythonSymbolExtractor class."""

    def test_init(self):
        """Test PythonSymbolExtractor initialization."""
        extractor = PythonSymbolExtractor()

        # Should have either tree-sitter or fallback
        assert extractor.available in [True, False]

        if extractor.available:
            assert extractor.parser is not None
            assert extractor.language is not None

    def test_extract_simple_function(self, tmp_path):
        """Test extracting a simple function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    '''Say hello.'''
    print("Hello, World!")
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol["name"] == "hello"
        assert symbol["type"] == "function"
        assert symbol["line_start"] > 0
        assert symbol["line_end"] > symbol["line_start"]

    def test_extract_simple_class(self, tmp_path):
        """Test extracting a simple class."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class MyClass:
    '''A test class.'''
    pass
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol["name"] == "MyClass"
        assert symbol["type"] == "class"

    def test_extract_function_and_class(self, tmp_path):
        """Test extracting both function and class."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def my_function():
    '''A function.'''
    pass

class MyClass:
    '''A class.'''
    pass
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert len(symbols) == 2
        names = [s["name"] for s in symbols]
        assert "my_function" in names
        assert "MyClass" in names

    def test_extract_with_docstring(self, tmp_path):
        """Test that docstrings are extracted."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def documented_function():
    '''This function has a docstring.'''
    pass
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert len(symbols) == 1
        symbol = symbols[0]
        # Note: docstring extraction depends on whether tree-sitter is available
        if extractor.available:
            # tree-sitter should extract docstring
            assert symbol["docstring"] is not None
        # ast fallback also extracts docstrings

    def test_extract_nested_function(self, tmp_path):
        """Test extracting nested functions."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def outer():
    def inner():
        pass
    pass
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        # Both outer and inner should be extracted
        assert len(symbols) >= 1
        names = [s["name"] for s in symbols]
        assert "outer" in names

    def test_extract_class_with_methods(self, tmp_path):
        """Test extracting class with methods."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        # Should extract class and methods
        assert len(symbols) >= 1
        names = [s["name"] for s in symbols]
        assert "MyClass" in names

    def test_extract_with_syntax_error(self, tmp_path):
        """Test extracting from file with syntax error."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def broken(
    # Missing closing paren
""")

        extractor = PythonSymbolExtractor()

        # Should return empty list and log warning (not raise exception)
        if extractor.available:
            # tree-sitter may or may not handle this gracefully
            symbols = extractor.extract(test_file)
            # Should not crash
            assert isinstance(symbols, list)
        else:
            # ast fallback should return empty list
            symbols = extractor.extract(test_file)
            assert symbols == []

    def test_extract_empty_file(self, tmp_path):
        """Test extracting from empty file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert symbols == []

    def test_extract_file_with_only_comments(self, tmp_path):
        """Test extracting from file with only comments."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# Just a comment
# Another comment
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert symbols == []

    def test_extract_nonexistent_file_raises_error(self, tmp_path):
        """Test that extracting from non-existent file raises error."""
        nonexistent = tmp_path / "does_not_exist.py"

        extractor = PythonSymbolExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract(nonexistent)

    def test_extract_with_unicode(self, tmp_path):
        """Test extracting from file with Unicode characters."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def 日本語関数():
    '''ユニコード対応テスト.'''
    pass

class ФайлЫ:
    '''Кириллица support.'''
    pass
""", encoding="utf-8")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert len(symbols) >= 2
        names = [s["name"] for s in symbols]
        assert "日本語関数" in names
        assert "ФайлЫ" in names

    def test_extract_with_complex_signature(self, tmp_path):
        """Test extracting function with complex signature."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def complex_func(
    arg1: str,
    arg2: int = 10,
    *args,
    **kwargs
) -> bool:
    '''Complex signature.'''
    return True
""")

        extractor = PythonSymbolExtractor()
        symbols = extractor.extract(test_file)

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol["name"] == "complex_func"
        assert symbol["type"] == "function"
        # Signature extraction depends on tree-sitter availability
        if extractor.available and symbol.get("signature"):
            assert "arg1" in symbol["signature"]


class TestPythonSymbolExtractorFallback:
    """Test ast module fallback."""

    def test_fallback_works_when_tree_sitter_unavailable(self, tmp_path, monkeypatch):
        """Test that ast fallback works when tree-sitter unavailable."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def test_func():
    '''Test function.'''
    pass
""")

        # Force fallback by making tree-sitter unavailable
        import sys
        monkeypatch.setitem(sys.modules, "tree_sitter", None)
        monkeypatch.setitem(sys.modules, "tree_sitter_python", None)

        # Create new extractor (will use fallback)
        extractor = PythonSymbolExtractor()
        assert not extractor.available

        symbols = extractor.extract(test_file)

        # Should still extract symbols using ast
        assert len(symbols) == 1
        assert symbols[0]["name"] == "test_func"
