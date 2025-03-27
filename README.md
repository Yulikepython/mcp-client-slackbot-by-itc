# MCP Simple Slackbot

MCP（Model Context Protocol）を使用して外部ツールの機能を拡張するシンプルな Slack ボットです。

## 機能

- **AI アシスタント**: LLM の機能を使用してチャンネルや DM でメッセージに応答
- **MCP 統合**: SQLite データベースや Web フェッチなどの MCP ツールに完全アクセス
- **マルチ LLM サポート**: OpenAI、Groq、Anthropic のモデルに対応
- **アプリホームタブ**: 利用可能なツールと使用方法の情報を表示

## セットアップ

### 1. リポジトリのクローンと初期設定

```bash
# リポジトリをクローン
git clone https://github.com/Yulikepython/mcp-client-slackbot-by-itc.git
cd mcp-client-slackbot

# 実行権限の付与
chmod +x run.sh
```

### 2. Slack アプリの作成

1. [api.slack.com/apps](https://api.slack.com/apps)にアクセスし、「Create New App」をクリック
2. 「From an app manifest」を選択し、ワークスペースを選択
3. `mcp_simple_slackbot/manifest.yaml`の内容をマニフェストエディタにコピー
4. アプリを作成し、ワークスペースにインストール
5. 「Basic Information」セクションで「App-Level Tokens」までスクロール
6. 「Generate Token and Scopes」をクリックし：
   - 名前を「mcp-assistant」などと入力
   - `connections:write`スコープを追加
   - 「Generate」をクリック
7. 以下のトークンをメモ：
   - Bot Token (`xoxb-...`) - 「OAuth & Permissions」にあります
   - App Token (`xapp-...`) - 先ほど生成したもの

### 3. 環境変数の設定

`.env`ファイルを作成し、以下の内容を設定：

```
# Slack API認証情報
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token

# LLM API認証情報
OPENAI_API_KEY=sk-your-openai-key
# または GROQ_API_KEY または ANTHROPIC_API_KEY

# LLM設定
LLM_MODEL=gpt-4-turbo

# Google Workspace MCP Server設定
GOOGLE_WORKSPACE_SERVER_PATH=/path/to/your/server/index.js
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

## 実行方法

### 開発環境での実行

```bash
./run.sh
```

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

## アーキテクチャ

ボットは以下の構造で設計されています：

1. **SlackMCPBot**: Slack イベントとメッセージ処理を管理するコアクラス
2. **LLMClient**: LLM API（OpenAI、Groq、Anthropic）との通信を処理
3. **Server**: MCP サーバーとの通信を管理
4. **Tool**: MCP サーバーから利用可能なツールを表現

メッセージ受信時の処理フロー：

1. メッセージと利用可能なツールを LLM に送信
2. LLM の応答にツール呼び出しが含まれる場合、ツールを実行
3. 結果を LLM に返して解釈
4. 最終的な応答をユーザーに送信

## クレジット

このプロジェクトは[MCP Simple Chatbot](https://github.com/sooperset/mcp-client-slackbot)をベースにしています。

## ライセンス

MIT License
