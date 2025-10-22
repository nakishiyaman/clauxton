"""
Symbol extraction from source files using tree-sitter.

This module extracts code symbols (functions, classes, methods) from source files
using tree-sitter for accurate AST parsing, with fallback to Python's built-in
ast module if tree-sitter is unavailable.

Example:
    >>> from clauxton.intelligence import PythonSymbolExtractor
    >>> extractor = PythonSymbolExtractor()
    >>> symbols = extractor.extract(Path("myfile.py"))
    >>> for symbol in symbols:
    ...     print(f"{symbol['name']} ({symbol['type']})")
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SymbolExtractor:
    """
    Multi-language symbol extractor.

    Dispatches to language-specific extractors based on file extension.
    Currently supports Python, with JavaScript/TypeScript planned for v0.11.1.
    """

    def __init__(self):
        """Initialize symbol extractor with language-specific extractors."""
        self.extractors: Dict[str, "PythonSymbolExtractor"] = {
            "python": PythonSymbolExtractor(),
            # v0.11.1: Add JS/TS extractors
            # "javascript": JavaScriptSymbolExtractor(),
            # "typescript": TypeScriptSymbolExtractor(),
        }
        logger.debug(f"SymbolExtractor initialized with {len(self.extractors)} languages")

    def extract(self, file_path: Path, language: str) -> List[Dict]:
        """
        Extract symbols from a file.

        Args:
            file_path: Path to source file
            language: Programming language ("python", "javascript", etc.)

        Returns:
            List of symbol dictionaries with keys:
                - name: Symbol name
                - type: Symbol type ("function", "class", etc.)
                - file_path: Path to file
                - line_start: Starting line number
                - line_end: Ending line number
                - docstring: Optional docstring
                - signature: Optional function signature
        """
        extractor = self.extractors.get(language)
        if not extractor:
            logger.debug(f"No extractor available for language: {language}")
            return []

        try:
            return extractor.extract(file_path)
        except Exception as e:
            logger.warning(f"Failed to extract symbols from {file_path}: {e}")
            return []


class PythonSymbolExtractor:
    """
    Extract symbols from Python files.

    Uses tree-sitter for accurate parsing when available, with automatic
    fallback to Python's built-in ast module if tree-sitter is not installed.
    """

    def __init__(self):
        """
        Initialize Python symbol extractor.

        Attempts to load tree-sitter. If unavailable, uses ast module as fallback.
        """
        self.available = False
        self.parser = None
        self.language = None

        try:
            from tree_sitter import Language, Parser
            import tree_sitter_python as tspython

            self.language = Language(tspython.language())
            self.parser = Parser(self.language)
            self.available = True
            logger.info("tree-sitter initialized successfully")
        except ImportError as e:
            logger.warning(
                f"tree-sitter not available ({e}), will use ast module fallback"
            )

    def extract(self, file_path: Path) -> List[Dict]:
        """
        Extract symbols from Python file.

        Args:
            file_path: Path to Python source file

        Returns:
            List of extracted symbols

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.available:
            return self._extract_with_tree_sitter(file_path)
        else:
            return self._extract_with_ast(file_path)

    def _extract_with_tree_sitter(self, file_path: Path) -> List[Dict]:
        """
        Extract symbols using tree-sitter.

        Args:
            file_path: Path to Python file

        Returns:
            List of symbols
        """
        logger.debug(f"Extracting symbols from {file_path} with tree-sitter")

        with open(file_path, "rb") as f:
            source_code = f.read()

        tree = self.parser.parse(source_code)
        symbols: List[Dict] = []

        self._walk_tree(tree.root_node, symbols, str(file_path))

        logger.debug(f"Extracted {len(symbols)} symbols from {file_path}")
        return symbols

    def _walk_tree(self, node, symbols: List[Dict], file_path: str) -> None:
        """
        Recursively walk AST and extract symbols.

        Args:
            node: tree-sitter Node
            symbols: List to append symbols to
            file_path: Path to file being parsed
        """
        if node.type == "function_definition":
            # Extract function
            name_node = node.child_by_field_name("name")
            if name_node:
                symbol = {
                    "name": name_node.text.decode(),
                    "type": "function",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "docstring": self._extract_docstring(node),
                    "signature": self._extract_signature(node),
                }
                symbols.append(symbol)

        elif node.type == "class_definition":
            # Extract class
            name_node = node.child_by_field_name("name")
            if name_node:
                symbol = {
                    "name": name_node.text.decode(),
                    "type": "class",
                    "file_path": file_path,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "docstring": self._extract_docstring(node),
                }
                symbols.append(symbol)

        # Recurse into children
        for child in node.children:
            self._walk_tree(child, symbols, file_path)

    def _extract_docstring(self, node) -> Optional[str]:
        """
        Extract docstring from function or class node.

        Args:
            node: tree-sitter Node (function_definition or class_definition)

        Returns:
            Docstring content or None
        """
        # Look for expression_statement with string as first child of body
        for child in node.children:
            if child.type == "block":
                for stmt in child.children:
                    if stmt.type == "expression_statement":
                        for expr_child in stmt.children:
                            if expr_child.type == "string":
                                # Remove quotes
                                text = expr_child.text.decode()
                                return text.strip('"""\'\'\'')
                        break
                break
        return None

    def _extract_signature(self, node) -> Optional[str]:
        """
        Extract function signature.

        Args:
            node: tree-sitter Node (function_definition)

        Returns:
            Function signature string or None
        """
        try:
            # Get everything before the colon
            text = node.text.decode()
            signature = text.split(":")[0].strip()
            return signature
        except Exception:
            return None

    def _extract_with_ast(self, file_path: Path) -> List[Dict]:
        """
        Fallback extraction using Python's built-in ast module.

        Args:
            file_path: Path to Python file

        Returns:
            List of symbols
        """
        logger.debug(f"Extracting symbols from {file_path} with ast module")

        import ast

        with open(file_path, encoding="utf-8") as f:
            try:
                source_code = f.read()
                tree = ast.parse(source_code, filename=str(file_path))
            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")
                return []

        symbols: List[Dict] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                symbols.append({
                    "name": node.name,
                    "type": "function",
                    "file_path": str(file_path),
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                    "docstring": ast.get_docstring(node),
                    "signature": None,  # Not available from ast
                })
            elif isinstance(node, ast.ClassDef):
                symbols.append({
                    "name": node.name,
                    "type": "class",
                    "file_path": str(file_path),
                    "line_start": node.lineno,
                    "line_end": node.end_lineno or node.lineno,
                    "docstring": ast.get_docstring(node),
                })

        logger.debug(f"Extracted {len(symbols)} symbols from {file_path}")
        return symbols
