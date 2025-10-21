# Clauxton MCP統合ガイド - Claude Code

**Version**: v0.9.0-beta
**Updated**: 2025-10-20

---

## 📋 目次

1. [前提条件](#前提条件)
2. [ステップ1: MCP設定ファイルの場所を確認](#ステップ1-mcp設定ファイルの場所を確認)
3. [ステップ2: MCP設定を追加](#ステップ2-mcp設定を追加)
4. [ステップ3: Claude Codeを再起動](#ステップ3-claude-codeを再起動)
5. [ステップ4: 動作確認](#ステップ4-動作確認)
6. [トラブルシューティング](#トラブルシューティング)
7. [利用可能なツール一覧](#利用可能なツール一覧)

---

## 前提条件

### 必須環境

- ✅ Claude Code がインストール済み
- ✅ Python 3.11+ がインストール済み
- ✅ Clauxton v0.9.0-beta がインストール済み

### Clauxton インストール確認

```bash
# 開発版を使用する場合
cd /home/kishiyama-n/workspace/projects/clauxton
source .venv/bin/activate
clauxton --version
# 出力: clauxton, version 0.9.0-beta

# または, PyPI版を使用する場合(将来)
pip install clauxton==0.9.0-beta
```

---

## ステップ1: MCP設定ファイルの場所を確認

Claude CodeのMCP設定ファイルは環境によって異なります: 

### Linux/WSL

```bash
# 設定ファイルの場所
~/.config/claude-code/mcp-servers.json

# ディレクトリ作成(存在しない場合)
mkdir -p ~/.config/claude-code
```

### macOS

```bash
# 設定ファイルの場所
~/Library/Application Support/Claude/mcp-servers.json

# ディレクトリ作成(存在しない場合)
mkdir -p ~/Library/Application\ Support/Claude
```

### Windows

```powershell
# 設定ファイルの場所
%APPDATA%\Claude\mcp-servers.json

# 実際のパス(例)
C:\Users\YourName\AppData\Roaming\Claude\mcp-servers.json
```

---

## ステップ2: MCP設定を追加

### 方法A: 開発版を使用(現在の環境)

**重要**: 現在のclauxton開発ディレクトリを使用する場合

`~/.config/claude-code/mcp-servers.json` に以下を追加: 

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "/home/kishiyama-n/workspace/projects/clauxton"
      }
    }
  }
}
```

**ポイント**:
- `command`: 仮想環境のPythonを直接指定
- `PYTHONPATH`: clauxtonパッケージの場所を指定
- `cwd`: `${workspaceFolder}` はClaude Codeが開いているプロジェクトのルートディレクトリ

### 方法B: システムインストール版を使用(将来)

PyPIからインストールした場合: 

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "python3",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

### 既存のMCPサーバーがある場合

既に他のMCPサーバーを使用している場合は, `clauxton`を追加: 

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "clauxton": {
      "command": "/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "/home/kishiyama-n/workspace/projects/clauxton"
      }
    }
  }
}
```

---

## ステップ3: Claude Codeを再起動

### VSCode版 Claude Code

1. VSCodeを完全に終了
2. VSCodeを再起動
3. Claude Code拡張機能が自動的にMCPサーバーを起動

### CLI版 Claude Code

```bash
# プロセスを完全に終了
pkill -9 claude-code

# 再起動
claude-code
```

---

## ステップ4: 動作確認

### 4.1 プロジェクトでClauxtonを初期化

```bash
# テストプロジェクトで初期化
cd /path/to/test-project
clauxton init
```

### 4.2 Claude Codeで確認

Claude Codeを開き, 以下のような質問をしてみてください: 

#### 確認1: Knowledge Base検索

```
User: "clauxtonでFastAPIに関する情報を検索して"
```

**期待される動作**:
- Claude Codeが `kb_search` ツールを呼び出す
- 結果が表示される(まだエントリーがない場合は空)

#### 確認2: タスク一覧

```
User: "現在のタスクを一覧表示して"
```

**期待される動作**:
- Claude Codeが `task_list` ツールを呼び出す
- タスク一覧が表示される

#### 確認3: ツールが利用可能か確認

```
User: "利用可能なclauxtonツールを教えて"
```

**期待される応答**:
```
以下のClauxtonツールが利用可能です: 

Knowledge Base (6ツール):
- kb_search: 情報を検索
- kb_add: 情報を追加
- kb_list: 一覧表示
...

Task Management (6ツール):
- task_add: タスク追加
- task_list: タスク一覧
...

Conflict Detection (3ツール):
- detect_conflicts: 競合検出
- recommend_safe_order: 最適順序
- check_file_conflicts: ファイル競合確認
```

---

## トラブルシューティング

### 問題1: MCPサーバーが起動しない

**症状**: Claude Codeでツールが表示されない

**確認方法**:
```bash
# 手動でMCPサーバーを起動してエラーを確認
cd /path/to/test-project
source /home/kishiyama-n/workspace/projects/clauxton/.venv/bin/activate
python -m clauxton.mcp.server
```

**よくある原因**:
1. **Pythonパスが間違っている**
   - `command` のパスを確認
   - `which python` の出力と一致させる

2. **PYTHONPATHが設定されていない**
   - 開発版を使う場合は `env.PYTHONPATH` が必須

3. **cwdが正しくない**
   - `${workspaceFolder}` が展開されているか確認

**解決方法**:
```json
{
  "mcpServers": {
    "clauxton": {
      "command": "/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "/home/kishiyama-n/workspace/projects/clauxton"
      }
    }
  }
}
```

### 問題2: ツールは表示されるが実行できない

**症状**: ツール呼び出し時にエラー

**確認方法**:
```bash
# プロジェクトが初期化されているか確認
cd /path/to/your-project
ls -la .clauxton/

# 初期化されていない場合
clauxton init
```

**よくある原因**:
1. **Clauxtonが初期化されていない**
   - プロジェクトで `clauxton init` を実行

2. **パーミッションエラー**
   - `.clauxton/` のパーミッションを確認
   - `chmod 700 .clauxton`

### 問題3: "Task not found"エラー

**症状**: タスク操作時にエラー

**確認方法**:
```bash
# タスクが存在するか確認
clauxton task list

# タスクIDの形式を確認
# 正: TASK-001, TASK-002, ...
# 誤: task-1, Task1, ...
```

### 問題4: MCPサーバーのログを確認したい

**ログの場所**(環境による):

Linux/WSL:
```bash
~/.local/state/claude-code/logs/
```

macOS:
```bash
~/Library/Logs/Claude/
```

**ログ確認**:
```bash
# 最新のログを確認
tail -f ~/.local/state/claude-code/logs/mcp-server-clauxton.log
```

---

## 利用可能なツール一覧

### Knowledge Base Tools (6)

#### `kb_search`
```json
{
  "query": "FastAPI",
  "category": "architecture",  // optional
  "limit": 10                   // optional
}
```
**説明**: TF-IDF relevance searchで情報を検索

#### `kb_add`
```json
{
  "title": "FastAPIを使用",
  "category": "architecture",
  "content": "バックエンドはFastAPIで構築...",
  "tags": ["backend", "api"]
}
```
**説明**: Knowledge Baseに新しいエントリーを追加

#### `kb_list`
```json
{
  "category": "architecture"  // optional
}
```
**説明**: すべてのエントリーを一覧表示

#### `kb_get`
```json
{
  "entry_id": "KB-20251020-001"
}
```
**説明**: 特定のエントリーを取得

#### `kb_update`
```json
{
  "entry_id": "KB-20251020-001",
  "title": "新しいタイトル",      // optional
  "content": "新しい内容",        // optional
  "category": "decision",         // optional
  "tags": ["updated"]             // optional
}
```
**説明**: エントリーを更新

#### `kb_delete`
```json
{
  "entry_id": "KB-20251020-001"
}
```
**説明**: エントリーを削除

---

### Task Management Tools (6)

#### `task_add`
```json
{
  "name": "認証機能追加",
  "description": "JWT認証を実装",       // optional
  "priority": "high",                   // optional: critical, high, medium, low
  "depends_on": ["TASK-001"],          // optional
  "files": ["src/api/auth.py"],        // optional
  "kb_refs": ["KB-20251020-001"],      // optional
  "estimate": 4.0                       // optional: hours
}
```
**説明**: 新しいタスクを追加(自動依存関係推論あり)

#### `task_list`
```json
{
  "status": "pending",     // optional: pending, in_progress, completed, blocked
  "priority": "high"       // optional: critical, high, medium, low
}
```
**説明**: タスク一覧を取得(フィルタ可能)

#### `task_get`
```json
{
  "task_id": "TASK-001"
}
```
**説明**: 特定のタスク詳細を取得

#### `task_update`
```json
{
  "task_id": "TASK-001",
  "status": "in_progress",   // optional
  "priority": "critical",    // optional
  "name": "新しい名前"       // optional
}
```
**説明**: タスクを更新

#### `task_next`
```json
{}
```
**説明**: AI推奨の次タスクを取得

#### `task_delete`
```json
{
  "task_id": "TASK-001"
}
```
**説明**: タスクを削除

---

### Conflict Detection Tools (3) - 🆕 v0.9.0-beta

#### `detect_conflicts`
```json
{
  "task_id": "TASK-002"
}
```
**説明**: タスクの競合を検出(リスクレベル付き)

**出力例**:
```json
{
  "task_id": "TASK-002",
  "task_name": "認証機能追加",
  "files": ["src/api/auth.py", "src/models/user.py"],
  "conflicts": [
    {
      "with_task_id": "TASK-003",
      "with_task_name": "データベース接続",
      "risk_level": "HIGH",
      "overlap_percentage": 75.0,
      "conflicting_files": ["src/models/user.py"]
    }
  ]
}
```

#### `recommend_safe_order`
```json
{
  "task_ids": ["TASK-001", "TASK-002", "TASK-003"]
}
```
**説明**: 競合を最小化する最適な実行順序を推奨

**出力例**:
```json
{
  "recommended_order": [
    {
      "position": 1,
      "task_id": "TASK-001",
      "task_name": "FastAPI setup",
      "reason": "No dependencies, no conflicts"
    },
    {
      "position": 2,
      "task_id": "TASK-003",
      "task_name": "Database connection",
      "reason": "Complete before TASK-002 to avoid file conflicts"
    },
    {
      "position": 3,
      "task_id": "TASK-002",
      "task_name": "Authentication",
      "reason": "Depends on TASK-003 completion"
    }
  ]
}
```

#### `check_file_conflicts`
```json
{
  "files": ["src/models/user.py", "src/api/auth.py"]
}
```
**説明**: 特定ファイルを編集中のタスクを確認

**出力例**:
```json
{
  "files_in_use": [
    {
      "file_path": "src/models/user.py",
      "in_use": true,
      "tasks": [
        {
          "task_id": "TASK-002",
          "task_name": "認証機能追加",
          "status": "in_progress"
        }
      ]
    },
    {
      "file_path": "src/api/auth.py",
      "in_use": false,
      "tasks": []
    }
  ]
}
```

---

## 実践例: Claude Codeでの使用

### シナリオ1: プロジェクト開始時

```
User: "このプロジェクトでFastAPIを使う理由を記録して"

Claude Code: kb_add ツールを使用
{
  "title": "FastAPIを採用",
  "category": "architecture",
  "content": "非同期処理, OpenAPI自動生成, 高性能",
  "tags": ["backend", "fastapi"]
}

User: "3つのタスクを追加: 認証, データベース, API"

Claude Code: task_add を3回呼び出し
TASK-001: 認証機能
TASK-002: データベース接続
TASK-003: API実装

User: "競合はある?"

Claude Code: recommend_safe_order 呼び出し
推奨順序: TASK-002 → TASK-001 → TASK-003
```

### シナリオ2: タスク開始前のチェック

```
User: "次に何をすべき?"

Claude Code: task_next 呼び出し
推奨: TASK-002(データベース接続)

User: "TASK-002は安全?"

Claude Code: detect_conflicts("TASK-002") 呼び出し
結果: 競合なし, 開始可能

User: "開始する"

Claude Code: task_update("TASK-002", status="in_progress")
更新完了
```

### シナリオ3: ファイル編集前の確認

```
User: "user.pyを編集したい"

Claude Code: check_file_conflicts(["src/models/user.py"])
結果: TASK-001が編集中

User: "誰が使ってる?"

Claude Code: task_get("TASK-001")
詳細表示: 認証機能タスク, in_progress

User: "別のファイルで作業する"

Claude Code: 了解, 他のタスクを推奨
```

---

## 設定ファイルテンプレート

### 完全版(開発環境用)

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "/home/kishiyama-n/workspace/projects/clauxton/.venv/bin/python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "/home/kishiyama-n/workspace/projects/clauxton",
        "CLAUXTON_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### シンプル版(PyPI版用· 将来)

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "python3",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

---

## 次のステップ

1. ✅ MCP統合完了
2. プロジェクトで `clauxton init` 実行
3. Claude Codeで情報を追加· 検索
4. タスク管理を開始
5. Conflict Detectionを活用

---

## サポート

- **ドキュメント**: `docs/` ディレクトリ(420KB+)
- **GitHub Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Quick Start**: `docs/quick-start.md`
- **Troubleshooting**: `docs/troubleshooting.md`

---

**Clauxton v0.9.0-beta MCP Integration** ✅

*最終更新: 2025-10-20*
*ステータス: Production Ready*
