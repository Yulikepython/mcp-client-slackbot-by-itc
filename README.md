# MCP Simple Slackbot

Slack ボットを使用して MCP サーバーとツールを利用できるシンプルなアプリケーションです。

## 主な変更点（最新リリース）2025/03/30 時点

- **Agent ベースのアーキテクチャへの移行**

  - `openai-agents`パッケージを使用した新しいアーキテクチャ
  - より柔軟なツール管理と実行
  - 改善された会話コンテキスト管理

- **依存関係の改善**

  - `pyproject.toml`による依存関係管理
  - 開発用依存関係の分離
  - 最新のパッケージバージョンへの更新

- **設定管理の改善**
  - 動的な`servers_config.json`生成
  - 環境変数による設定管理
  - より柔軟なサーバー設定

## 機能

- Slack ボットとして機能
- MCP サーバーとの連携
- ツールの実行と結果の解釈
- スレッド対応の会話管理
- 多言語対応（日本語/英語）

## 必要条件

- Python 3.8 以上
- Node.js（Google Workspace MCP サーバー用）
- Slack API トークン
- OpenAI API キー

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

3. 依存関係をインストール:

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

pyproject.toml に必要なパッケージを追記してください。

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

- コードフォーマット: `black .`
- インポートの整理: `isort .`
- リント: `ruff check .`
- 型チェック: `pyright`

### 本番環境での実行

本番環境では、プロセスの永続化と自動再起動のために`systemd`サービスを使用することを推奨します。

1. サービスファイルの作成：

```bash
sudo nano /etc/systemd/system/mcp-slackbot.service
```

以下の内容を追加：

```ini
[Unit]
Description=MCP Slackbot Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/mcp-client-slackbot
Environment=PYTHONUNBUFFERED=1
ExecStart=/path/to/mcp-client-slackbot/run.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. サービスの有効化と起動：

```bash
# systemdの設定を再読み込み
sudo systemctl daemon-reload

# サービスを有効化（システム起動時に自動起動）
sudo systemctl enable mcp-slackbot

# サービスを起動
sudo systemctl start mcp-slackbot

# ステータスの確認
sudo systemctl status mcp-slackbot
```

3. ログの確認：

```bash
# リアルタイムでログを表示
sudo journalctl -u mcp-slackbot -f

# 最新のログを表示
sudo journalctl -u mcp-slackbot -n 100
```

4. サービスの管理：

```bash
# サービスの停止
sudo systemctl stop mcp-slackbot

# サービスの再起動
sudo systemctl restart mcp-slackbot
```

## 使用方法

- **DM**: ボットに直接メッセージを送信
- **チャンネルメンション**: チャンネルで`@MCP Assistant`とメンション
- **アプリホーム**: ボットのアプリホームタブで利用可能なツールを確認

## クレジット

このプロジェクトは[MCP Simple Chatbot](https://github.com/sooperset/mcp-client-slackbot)をベースにしています。

---

## ライセンス

MIT License
