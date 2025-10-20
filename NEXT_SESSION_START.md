# Week 2 Day 9 開始ガイド

## 現在の状態（2025-10-21）

### 完了済み
- ✅ Week 2 Day 6: Enhanced Validation
- ✅ Week 2 Day 7: Logging Functionality
- ✅ Week 2 Day 8: KB Export Functionality

### 現在のメトリクス
- **テスト数**: 599 tests
- **カバレッジ**: 91%
- **最新コミット**: `61f90fd` (Week 2 Day 8 完了)
- **ブランチ**: main (origin/mainより4コミット先行)

---

## 次のタスク: Week 2 Day 9

### 機能: 進捗表示 + パフォーマンス最適化

#### 実装内容

**進捗表示 (Progress Display)**:
- Progress callback mechanism
- Progress reporting（every 5 tasks）
- Percentage calculation
- `task_import_yaml` に進捗コールバック追加

**パフォーマンス最適化 (Performance Optimization)**:
- `TaskManager._batch_add()` - 一括書き込み
- Single file operation（100個 5秒 → 0.2秒目標）
- Memory-efficient processing
- 既存の `task_import_yaml` を最適化

#### テスト要件
- **Tests**: 5 tests (Performance focused)
- パフォーマンステスト（100タスク一括追加）
- 進捗コールバックテスト
- メモリ効率テスト

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

### 修正するファイル
1. `clauxton/core/task_manager.py`
   - `_batch_add()` メソッド追加
   - `add_many()` メソッド追加（進捗コールバック付き）

2. `clauxton/mcp/server.py`
   - `task_import_yaml()` に進捗コールバック統合

### 新規テストファイル
1. `tests/core/test_performance.py` (新規作成)
   - 大量タスク追加のパフォーマンステスト
   - 進捗コールバック動作テスト

---

## 参考情報

### 現在の task_import_yaml の場所
- **File**: `clauxton/core/task_manager.py:400-500` (推定)
- **MCP Tool**: `clauxton/mcp/server.py:450-550` (推定)

### 進捗コールバックの設計案

```python
from typing import Callable, Optional

ProgressCallback = Callable[[int, int], None]  # (current, total)

def add_many(
    self,
    tasks: List[Task],
    progress_callback: Optional[ProgressCallback] = None
) -> List[str]:
    """
    Add multiple tasks with optional progress reporting.

    Args:
        tasks: List of tasks to add
        progress_callback: Optional callback(current, total)

    Returns:
        List of created task IDs
    """
    task_ids = []
    for i, task in enumerate(tasks, 1):
        task_id = self._batch_add(task)
        task_ids.append(task_id)

        if progress_callback and i % 5 == 0:
            progress_callback(i, len(tasks))

    return task_ids
```

### パフォーマンス目標
- **Before**: 100タスク追加 → 5秒
- **After**: 100タスク追加 → 0.2秒（25倍高速化）
- **方法**: 個別write → 1回のbatch write

---

## 品質チェックリスト

実装後に必ず実行：
- [ ] `mypy clauxton/core/task_manager.py clauxton/mcp/server.py`
- [ ] `ruff check clauxton/ tests/`
- [ ] `pytest tests/ -q`
- [ ] `pytest --cov=clauxton --cov-report=term`
- [ ] カバレッジが90%以上維持されていること
- [ ] 全テストがパスすること

---

## 推奨開始フロー

1. **環境確認** (2分)
   ```bash
   git status
   pytest tests/ -q
   ```

2. **設計レビュー** (5分)
   - `task_manager.py` の現状確認
   - 進捗コールバックの設計確認

3. **実装** (1.5時間)
   - `_batch_add()` 実装
   - 進捗コールバック追加
   - MCP tool統合

4. **テスト作成** (1時間)
   - パフォーマンステスト
   - 進捗コールバックテスト

5. **品質チェック** (30分)
   - mypy, ruff, pytest
   - カバレッジ確認

6. **コミット** (15分)
   - git commit with comprehensive message

---

## 注意事項

### 既存機能への影響
- `task_import_yaml` は既に実装済み（Week 1 Day 1-2）
- 既存テストを壊さないように注意
- 後方互換性を保つ

### テスト観点
- 大量タスク（100個）の追加性能
- 進捗コールバックが正しく呼ばれるか
- メモリ効率（大量データでメモリリークなし）
- エラー時のロールバック動作

---

## 参考リンク

- Roadmap: `docs/design/REVISED_ROADMAP_v0.10.0.md:214-226`
- TaskManager: `clauxton/core/task_manager.py`
- MCP Server: `clauxton/mcp/server.py`
- 既存テスト: `tests/core/test_task_manager.py`

---

**準備完了！新セッションでこのファイルを参照して Week 2 Day 9 を開始してください。**
