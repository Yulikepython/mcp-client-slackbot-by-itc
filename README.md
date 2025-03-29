# MCP Simple Slackbot

A Slack bot using MCP servers.

## 必要条件

- Python 3.8 以上
- Node.js (MCP サーバー用)

## インストール

1. リポジトリをクローン:

```bash
git clone https://github.com/yourusername/mcp-client-slackbot.git
cd mcp-client-slackbot
```

2. 仮想環境を作成して有効化:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate  # Windows
```

3. パッケージをインストール:

```bash
# 基本的な依存関係のみをインストール
pip install -e .

# 開発用の依存関係も含めてインストール
pip install -e ".[dev]"
```

## 設定

1. `.env`ファイルを作成し、必要な環境変数を設定:

```env
# Slack API認証情報
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# OpenAI API認証情報
OPENAI_API_KEY=your-openai-api-key

# Google Workspace MCP Server設定
GOOGLE_WORKSPACE_SERVER_PATH=/path/to/your/server/index.js
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

2. 実行:

```bash
./run.sh
```

`run.sh`は以下の処理を行います：

1. 環境変数を`.env`ファイルから読み込み
2. `servers_config.json`を動的に生成
3. パッケージをインストール
4. アプリケーションを起動

## 依存関係の管理

このプロジェクトは`pyproject.toml`を使用して依存関係を管理しています。

### 依存関係の種類

1. **基本的な依存関係**

   - `pyproject.toml`の`dependencies`セクションで定義
   - アプリケーションの実行に必要な最小限のパッケージ
   - バージョンは`>=`で指定し、互換性のある最新バージョンを使用

2. **開発用の依存関係**
   - `pyproject.toml`の`[project.optional-dependencies]`セクションで定義
   - 開発、テスト、コード品質管理に必要なパッケージ
   - `pip install -e ".[dev]"`でインストール

### 依存関係の更新

1. 新しいパッケージの追加:

   ```bash
   # 基本的な依存関係の場合
   pip install new-package
   pip freeze | grep new-package >> requirements.txt
   # requirements.txtの内容をpyproject.tomlのdependenciesに追加

   # 開発用の依存関係の場合
   pip install new-dev-package
   pip freeze | grep new-dev-package >> requirements-dev.txt
   # requirements-dev.txtの内容をpyproject.tomlの[project.optional-dependencies].devに追加
   ```

2. 依存関係の更新:
   ```bash
   # すべての依存関係を最新バージョンに更新
   pip install --upgrade -e ".[dev]"
   ```

## MCP サーバーの追加

新しい MCP サーバーを追加するには、以下の手順に従います：

1. `scripts/generate_servers_config.py`を編集して、新しいサーバーの設定を追加:

```python
config = {
    "mcpServers": {
        "google-workspace": {
            "command": "node",
            "args": [os.getenv("GOOGLE_WORKSPACE_SERVER_PATH", "google-workspace-server/index.js")],
            "env": {
                "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
                "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN", "")
            },
            "encoding": "utf-8",
            "encoding_error_handler": "replace"
        },
        # 新しいサーバーの設定を追加
        "new-server": {
            "command": "node",  # または他のコマンド
            "args": [os.getenv("NEW_SERVER_PATH", "new-server/index.js")],
            "env": {
                "NEW_SERVER_API_KEY": os.getenv("NEW_SERVER_API_KEY", ""),
                # 他の環境変数
            },
            "encoding": "utf-8",
            "encoding_error_handler": "replace"
        }
    }
}
```

2. `.env`ファイルに必要な環境変数を追加:

```env
NEW_SERVER_PATH=/path/to/your/new/server/index.js
NEW_SERVER_API_KEY=your-api-key
```

3. アプリケーションを再起動:

```bash
./run.sh
```

## 開発

このプロジェクトは以下の開発ツールを使用しています：

- Ruff: コードリンティング
- Black: コードフォーマット
- isort: インポートの整理
- pytest: テスト実行

### コードのフォーマット

```bash
black .
isort .
```

### リンティング

```bash
ruff check .
```

### テストの実行

```bash
pytest
```

## ライセンス

MIT License
