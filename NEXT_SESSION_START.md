# Week 2 Day 10 開始ガイド

## 現在の状態（2025-10-21）

### 完了済み
- ✅ Week 2 Day 6: Enhanced Validation
- ✅ Week 2 Day 7: Logging Functionality
- ✅ Week 2 Day 8: KB Export Functionality
- ✅ Week 2 Day 9: Progress Display + Performance Optimization

### 現在のメトリクス
- **テスト数**: 607 tests
- **カバレッジ**: 92%
- **最新コミット**: `66482e7` (Week 2 Day 9 完了)
- **ブランチ**: main (origin/mainより5コミット先行)

---

## 次のタスク: Week 2 Day 10

### 機能: バックアップ強化 + エラーメッセージ改善

#### 実装内容

**バックアップ強化 (Backup Enhancement)**:
- `BackupManager` class（新規作成）
- Timestamped backups: `filename_YYYYMMDD_HHMMSS.yml`
- Multiple generations: 最新10世代を保持
- `.clauxton/backups/` directory
- 自動クリーンアップ（古いバックアップ削除）

**エラーメッセージ改善 (Error Message Improvement)**:
- Detailed error messages with context
- Suggested fixes for common errors
- Help links to documentation
- Examples in error messages

#### テスト要件
- **Tests**: 15 tests (Backup focused)
- バックアップ作成テスト
- 世代管理テスト（10世代制限）
- 古いバックアップ削除テスト
- エラーメッセージ改善テスト

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
1. `clauxton/utils/backup_manager.py` (NEW)
   - `BackupManager` class
   - `create_backup(file_path, max_generations=10)` method
   - `cleanup_old_backups(file_path, max_generations)` method
   - `list_backups(file_path)` method
   - `restore_backup(backup_path)` method

### 修正するファイル
1. `clauxton/utils/yaml_utils.py`
   - `write_yaml()` に BackupManager 統合
   - バックアップ作成を自動化

2. `clauxton/core/models.py`
   - エラーメッセージ改善（ValidationError, NotFoundError等）
   - 具体的な修正提案を追加

### 新規テストファイル
1. `tests/utils/test_backup_manager.py` (NEW)
   - BackupManager の全機能をテスト
   - 世代管理テスト
   - クリーンアップテスト

---

## 参考情報

### 現在のバックアップ実装

現在、`yaml_utils.py` にはシンプルなバックアップ機能があります：

```python
# clauxton/utils/yaml_utils.py (現状)
def write_yaml(file_path: Path, data: Dict[str, Any]) -> None:
    """Write data to YAML file with atomic write and backup."""
    # Create backup if file exists
    if file_path.exists():
        backup_path = file_path.with_suffix(".yml.bak")
        shutil.copy2(file_path, backup_path)

    # Atomic write logic...
```

**問題点**:
- 1世代しか保持されない（`.bak` のみ）
- タイムスタンプなし
- 古いバックアップが上書きされる

### 新しいバックアップ設計

```python
# clauxton/utils/backup_manager.py (新設計)
from pathlib import Path
from typing import List
from datetime import datetime

class BackupManager:
    """
    Manages timestamped backups with generation limit.

    Example:
        >>> bm = BackupManager()
        >>> bm.create_backup(Path("tasks.yml"), max_generations=10)
        Path(".clauxton/backups/tasks_20251021_143052.yml")
    """

    def __init__(self, backup_dir: Path):
        """Initialize BackupManager."""
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        file_path: Path,
        max_generations: int = 10
    ) -> Path:
        """
        Create timestamped backup and cleanup old generations.

        Args:
            file_path: File to backup
            max_generations: Max backups to keep (default: 10)

        Returns:
            Path to created backup file
        """
        pass

    def cleanup_old_backups(
        self,
        file_path: Path,
        max_generations: int = 10
    ) -> List[Path]:
        """
        Remove old backups beyond max_generations.

        Args:
            file_path: Original file path
            max_generations: Max backups to keep

        Returns:
            List of deleted backup paths
        """
        pass

    def list_backups(self, file_path: Path) -> List[Path]:
        """
        List all backups for a file, sorted by timestamp (newest first).

        Args:
            file_path: Original file path

        Returns:
            List of backup paths
        """
        pass

    def restore_backup(self, backup_path: Path, target_path: Path) -> None:
        """
        Restore a backup to target path.

        Args:
            backup_path: Backup file to restore
            target_path: Destination path
        """
        pass
```

### バックアップファイル命名規則

```
Original file: .clauxton/tasks.yml

Backups:
  .clauxton/backups/tasks_20251021_143052.yml  (newest)
  .clauxton/backups/tasks_20251021_142030.yml
  .clauxton/backups/tasks_20251021_141015.yml
  ...
  .clauxton/backups/tasks_20251020_153000.yml  (10th generation)

Deleted (older than 10 generations):
  .clauxton/backups/tasks_20251020_152000.yml  (removed)
  .clauxton/backups/tasks_20251020_151000.yml  (removed)
```

### エラーメッセージ改善例

**Before (現状)**:
```
NotFoundError: Task with ID 'TASK-999' not found.
```

**After (改善後)**:
```
NotFoundError: Task with ID 'TASK-999' not found.

Suggestion: Check if the task ID is correct.
  - List all tasks: clauxton task list
  - Search tasks: clauxton task list | grep TASK

Available task IDs: TASK-001, TASK-002, TASK-003

Documentation: https://docs.clauxton.com/troubleshooting#task-not-found
```

---

## 品質チェックリスト

実装後に必ず実行：
- [ ] `mypy clauxton/utils/backup_manager.py clauxton/utils/yaml_utils.py`
- [ ] `ruff check clauxton/ tests/`
- [ ] `pytest tests/ -q`
- [ ] `pytest --cov=clauxton --cov-report=term`
- [ ] カバレッジが92%以上維持されていること
- [ ] 全テストがパスすること

---

## 推奨開始フロー

1. **環境確認** (2分)
   ```bash
   git status
   pytest tests/ -q
   ```

2. **設計レビュー** (10分)
   - BackupManager のインターフェース設計
   - 既存の yaml_utils.py との統合方法

3. **実装** (2時間)
   - `BackupManager` class 実装
   - `yaml_utils.py` 統合
   - エラーメッセージ改善

4. **テスト作成** (1.5時間)
   - BackupManager テスト
   - 統合テスト

5. **品質チェック** (30分)
   - mypy, ruff, pytest
   - カバレッジ確認

6. **コミット** (15分)
   - git commit with comprehensive message

---

## 注意事項

### 既存機能への影響
- `yaml_utils.py` は既存の多くの場所で使用されている
- 後方互換性を保つ
- 既存の `.yml.bak` ファイルは残す（互換性のため）

### テスト観点
- タイムスタンプが正しいフォーマットか
- 10世代制限が正しく動作するか
- 古いバックアップが正しく削除されるか
- バックアップディレクトリが自動作成されるか
- ファイルパーミッションが正しいか（600）

### パフォーマンス考慮
- バックアップ作成は高速であるべき（< 100ms）
- クリーンアップは効率的であるべき
- ファイル数が多くても問題ないこと

---

## 参考リンク

- Roadmap: `docs/design/REVISED_ROADMAP_v0.10.0.md:227-244`
- yaml_utils: `clauxton/utils/yaml_utils.py`
- 既存テスト: `tests/utils/test_yaml_utils.py`

---

## 期待される成果

### 機能
- ✅ BackupManager class（タイムスタンプ付きバックアップ）
- ✅ 10世代管理（自動クリーンアップ）
- ✅ yaml_utils.py 統合（自動バックアップ）
- ✅ 改善されたエラーメッセージ

### テスト
- ✅ 15 新規テスト（backup_manager.py）
- ✅ 既存テスト全てパス
- ✅ 92%+ カバレッジ維持

### ドキュメント
- ✅ CHANGELOG.md 更新
- ✅ docs/backup-guide.md 作成（推奨）

---

**準備完了！新セッションでこのファイルを参照して Week 2 Day 10 を開始してください。**
