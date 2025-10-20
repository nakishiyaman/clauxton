# Week 2 Day 11 開始ガイド

## 現在の状態（2025-10-21）

### 完了済み
- ✅ Week 2 Day 1-2: YAML Bulk Import
- ✅ Week 2 Day 3: Undo/Rollback
- ✅ Week 2 Day 4: Confirmation Prompts
- ✅ Week 2 Day 5: Error Recovery + YAML Safety
- ✅ Week 2 Day 6: Enhanced Validation
- ✅ Week 2 Day 7: Logging Functionality
- ✅ Week 2 Day 8: KB Export Functionality
- ✅ Week 2 Day 9: Progress Display + Performance Optimization
- ✅ Week 2 Day 10: Backup Enhancement + Error Message Improvement

### 現在のメトリクス
- **テスト数**: 629 tests
- **カバレッジ**: 91%
- **最新コミット**: `38c3e24` (Week 2 Day 10 完了)
- **ブランチ**: main (origin/mainより7コミット先行)

---

## 次のタスク: Week 2 Day 11

### 機能: 設定可能な確認モード（Configurable Confirmation Mode）

#### 実装内容

**設定可能な確認モード (Configurable Confirmation Mode)**:
- `ConfirmationManager` class（新規作成）
- 3つの確認モード: "always" (100% HITL), "auto" (75% HITL), "never" (25% HITL)
- `.clauxton/config.yml` configuration file
- `clauxton config set/get/list` CLI commands
- MCP integration: 既存ツールへの統合

**3つの確認モード**:
1. **"always" mode (100% HITL)**: すべての書き込み操作で確認が必要
   - Use case: チーム開発、本番環境、厳格なワークフロー
   - Behavior: すべての`add`, `update`, `delete`, `import`操作で確認プロンプト

2. **"auto" mode (75% HITL, default)**: 閾値ベース確認
   - Use case: 多くの開発ワークフロー（バランス重視）
   - Behavior: 閾値超過時のみ確認（例: 10個以上のタスク一括作成）

3. **"never" mode (25% HITL)**: 確認プロンプトなし
   - Use case: 高速プロトタイピング、個人プロジェクト
   - Behavior: 確認なし（undo機能で復元可能）

#### テスト要件
- **Tests**: 7 tests (Confirmation Manager focused)
- 設定ファイル読み書きテスト
- モード切り替えテスト
- should_confirm ロジックテスト
- CLI commands テスト

---

## 新セッション開始コマンド

```bash
cd /home/kishiyama-n/workspace/projects/clauxton

# 1. 環境確認
git status
git log --oneline -5

# 2. テスト実行（現状確認）
source .venv/bin/activate
pytest tests/ -q

# 3. カバレッジ確認
pytest --cov=clauxton --cov-report=term | grep -E "(TOTAL|clauxton/)"
```

---

## 実装ファイル予定

### 新規作成ファイル
1. `clauxton/core/confirmation_manager.py` (NEW)
   - `ConfirmationManager` class
   - `get_mode()` method
   - `set_mode(mode)` method
   - `should_confirm(operation_type, operation_count)` method
   - `get_threshold(operation_type)` method
   - `set_threshold(operation_type, value)` method

2. `clauxton/cli/config.py` (NEW)
   - `config` command group
   - `clauxton config set <key> <value>` command
   - `clauxton config get <key>` command
   - `clauxton config list` command

### 修正するファイル
1. `clauxton/cli/main.py`
   - `config` command group を追加（import）

2. `clauxton/mcp/server.py` (Optional)
   - MCP tools に ConfirmationManager 統合（必要に応じて）

### 新規テストファイル
1. `tests/core/test_confirmation_manager.py` (NEW)
   - ConfirmationManager の全機能をテスト
   - モード切り替えテスト
   - should_confirm ロジックテスト

2. `tests/cli/test_config_commands.py` (NEW)
   - CLI config commands のテスト
   - set/get/list コマンドテスト

---

## 設計仕様

### ConfirmationManager Class

```python
# clauxton/core/confirmation_manager.py
from pathlib import Path
from typing import Literal, Dict

ConfirmationMode = Literal["always", "auto", "never"]

class ConfirmationManager:
    """
    Manage confirmation levels for operations.

    Supports 3 modes:
    - "always": Confirm all write operations (100% HITL)
    - "auto": Confirm based on thresholds (75% HITL, default)
    - "never": No confirmation prompts (25% HITL)

    Example:
        >>> cm = ConfirmationManager(Path(".clauxton/config.yml"))
        >>> cm.set_mode("always")
        >>> cm.should_confirm("task_import", 5)
        True
    """

    def __init__(self, config_path: Path):
        """
        Initialize ConfirmationManager.

        Args:
            config_path: Path to config file (e.g., .clauxton/config.yml)
        """
        pass

    def get_mode(self) -> ConfirmationMode:
        """
        Get current confirmation mode.

        Returns:
            Current mode: "always", "auto", or "never"

        Example:
            >>> cm.get_mode()
            'auto'
        """
        pass

    def set_mode(self, mode: ConfirmationMode) -> None:
        """
        Set confirmation mode.

        Args:
            mode: New mode ("always", "auto", or "never")

        Raises:
            ValidationError: If mode is invalid

        Example:
            >>> cm.set_mode("always")
        """
        pass

    def should_confirm(
        self,
        operation_type: str,
        operation_count: int = 1
    ) -> bool:
        """
        Check if confirmation is needed for an operation.

        Args:
            operation_type: Type of operation (e.g., "task_import", "task_delete")
            operation_count: Number of items affected (default: 1)

        Returns:
            True if confirmation is needed, False otherwise

        Logic:
            - "always" mode: Always return True
            - "never" mode: Always return False
            - "auto" mode: Return True if operation_count >= threshold

        Example:
            >>> cm.set_mode("auto")
            >>> cm.should_confirm("task_import", 5)
            False  # Below default threshold (10)
            >>> cm.should_confirm("task_import", 15)
            True   # Above threshold
        """
        pass

    def get_threshold(self, operation_type: str) -> int:
        """
        Get threshold for an operation type.

        Args:
            operation_type: Type of operation

        Returns:
            Threshold value (default: 10 if not configured)

        Example:
            >>> cm.get_threshold("task_import")
            10
        """
        pass

    def set_threshold(self, operation_type: str, value: int) -> None:
        """
        Set threshold for an operation type.

        Args:
            operation_type: Type of operation
            value: New threshold value (must be >= 1)

        Raises:
            ValidationError: If value < 1

        Example:
            >>> cm.set_threshold("task_import", 5)
        """
        pass
```

### Configuration File Format

```yaml
# .clauxton/config.yml
version: "1.0"
confirmation_mode: auto  # always | auto | never

confirmation_thresholds:
  task_import: 10      # Confirm if importing >= 10 tasks
  task_delete: 5       # Confirm if deleting >= 5 tasks
  kb_delete: 3         # Confirm if deleting >= 3 KB entries
  kb_import: 5         # Confirm if importing >= 5 KB entries
```

### CLI Commands

```bash
# Set confirmation mode
clauxton config set confirmation_mode always
clauxton config set confirmation_mode auto
clauxton config set confirmation_mode never

# Get confirmation mode
clauxton config get confirmation_mode
# Output: always

# Set threshold
clauxton config set task_import_threshold 20
clauxton config get task_import_threshold
# Output: 20

# List all configuration
clauxton config list
# Output:
# confirmation_mode: auto
# task_import_threshold: 10
# task_delete_threshold: 5
# kb_delete_threshold: 3
# kb_import_threshold: 5
```

### CLI Implementation

```python
# clauxton/cli/config.py
import click
from pathlib import Path
from clauxton.core.confirmation_manager import ConfirmationManager

@click.group()
def config():
    """Manage Clauxton configuration."""
    pass

@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """
    Set configuration value.

    Example:
        clauxton config set confirmation_mode always
        clauxton config set task_import_threshold 20
    """
    pass

@config.command()
@click.argument("key")
def get(key: str):
    """
    Get configuration value.

    Example:
        clauxton config get confirmation_mode
    """
    pass

@config.command()
def list():
    """
    List all configuration values.

    Example:
        clauxton config list
    """
    pass
```

---

## テスト設計

### Core Tests (4 tests) - tests/core/test_confirmation_manager.py

```python
def test_confirmation_manager_init():
    """Test ConfirmationManager initialization creates config if missing."""

def test_get_set_mode():
    """Test getting and setting confirmation mode."""

def test_should_confirm_always_mode():
    """Test should_confirm returns True for all operations in 'always' mode."""

def test_should_confirm_auto_mode():
    """Test should_confirm respects thresholds in 'auto' mode."""

def test_should_confirm_never_mode():
    """Test should_confirm returns False for all operations in 'never' mode."""

def test_get_set_threshold():
    """Test getting and setting thresholds."""

def test_invalid_mode():
    """Test setting invalid mode raises ValidationError."""
```

### CLI Tests (3 tests) - tests/cli/test_config_commands.py

```python
def test_config_set_mode():
    """Test 'clauxton config set confirmation_mode' command."""

def test_config_get_mode():
    """Test 'clauxton config get confirmation_mode' command."""

def test_config_list():
    """Test 'clauxton config list' command."""

def test_config_set_threshold():
    """Test 'clauxton config set task_import_threshold' command."""
```

---

## デフォルト設定

```python
DEFAULT_CONFIG = {
    "version": "1.0",
    "confirmation_mode": "auto",  # Default to balanced mode
    "confirmation_thresholds": {
        "task_import": 10,
        "task_delete": 5,
        "kb_delete": 3,
        "kb_import": 5,
    }
}
```

---

## MCP統合（Optional）

既存のMCPツールに`ConfirmationManager`を統合する場合：

```python
# clauxton/mcp/server.py

# Example: task_import_yaml tool integration
@server.call_tool()
async def task_import_yaml(
    yaml_content: str,
    skip_confirmation: bool = False,
    on_error: str = "rollback"
) -> Dict[str, Any]:
    """Import tasks from YAML with configurable confirmation."""

    # Check if confirmation is needed
    cm = ConfirmationManager(Path(".clauxton/config.yml"))
    tasks_count = len(parsed_tasks)

    if not skip_confirmation and cm.should_confirm("task_import", tasks_count):
        return {
            "status": "confirmation_required",
            "message": f"Confirmation needed for {tasks_count} tasks",
            "preview": {...}
        }

    # Proceed with import
    # ...
```

**Note**: MCP統合はDay 11のスコープ外としても良い（Day 12-13で統合テスト時に実装）。

---

## 品質チェックリスト

実装後に必ず実行：
- [ ] `mypy clauxton/core/confirmation_manager.py clauxton/cli/config.py`
- [ ] `ruff check clauxton/ tests/`
- [ ] `pytest tests/ -q`
- [ ] `pytest --cov=clauxton --cov-report=term`
- [ ] カバレッジが91%以上維持されていること
- [ ] 全テストがパスすること（636+ tests expected）

---

## 推奨開始フロー

1. **環境確認** (2分)
   ```bash
   git status
   pytest tests/ -q
   ```

2. **設計レビュー** (10分)
   - ConfirmationManager のインターフェース設計
   - config.yml のスキーマ設計

3. **実装** (4時間)
   - `ConfirmationManager` class 実装
   - `clauxton/cli/config.py` 実装
   - config.yml 読み書き機能

4. **テスト作成** (2時間)
   - Core tests (4 tests)
   - CLI tests (3 tests)

5. **品質チェック** (30分)
   - mypy, ruff, pytest
   - カバレッジ確認

6. **コミット** (15分)
   - git commit with comprehensive message

---

## 注意事項

### 既存機能への影響
- 既存のconfirmation_threshold機能と統合
- `task_import_yaml()` の `skip_confirmation` パラメータとの互換性維持
- 後方互換性を保つ（既存の動作を破壊しない）

### テスト観点
- 設定ファイルが存在しない場合（初回実行）
- 設定ファイルが破損している場合
- 無効なモード/閾値が設定された場合
- 複数の操作タイプでの動作確認
- CLI出力フォーマット

### パフォーマンス考慮
- 設定ファイル読み込みはキャッシュ（頻繁な読み込みを避ける）
- should_confirm() は高速であるべき（< 1ms）

---

## 参考リンク

- Roadmap: `docs/design/REVISED_ROADMAP_v0.10.0.md:246-266`
- 既存の confirmation 実装: `tests/core/test_confirmation.py`
- CLAUDE.md: Human-in-the-Loop philosophy

---

## 期待される成果

### 機能
- ✅ ConfirmationManager class（モード管理）
- ✅ .clauxton/config.yml（設定ファイル）
- ✅ clauxton config CLI commands（set/get/list）
- ✅ 3つの確認モード（always/auto/never）

### テスト
- ✅ 7 新規テスト（confirmation_manager + config CLI）
- ✅ 既存テスト全てパス
- ✅ 91%+ カバレッジ維持

### ドキュメント
- ✅ CHANGELOG.md 更新
- ✅ docs/human-in-the-loop-guide.md 作成（推奨）

---

**準備完了！新セッションでこのファイルを参照して Week 2 Day 11 を開始してください。**
