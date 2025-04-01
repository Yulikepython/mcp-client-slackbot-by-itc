#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# .envファイルから環境変数を読み込む
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Loading environment variables from .env file..."
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
else
    echo "Warning: .env file not found at $SCRIPT_DIR/.env"
    echo "Please create a .env file with the required environment variables"
    exit 1
fi

# 必要な環境変数が設定されているか確認
required_vars=(
    "SLACK_BOT_TOKEN"
    "SLACK_APP_TOKEN"
    "OPENAI_API_KEY"
    "GOOGLE_WORKSPACE_SERVER_PATH"
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
    "GOOGLE_REFRESH_TOKEN"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in .env file"
        exit 1
    fi
done

# servers_config.jsonを動的に生成
echo "Generating servers_config.json..."
cat > "$SCRIPT_DIR/mcp_simple_slackbot/servers_config.json" << EOF
{
  "mcpServers": {
    "google-workspace": {
      "command": "node",
      "args": [
        "${GOOGLE_WORKSPACE_SERVER_PATH}"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}",
        "GOOGLE_REFRESH_TOKEN": "${GOOGLE_REFRESH_TOKEN}"
      },
      "encoding": "utf-8",
      "encoding_error_handler": "replace"
    },
    "openai-vector-store": {
      "command": "node",
      "args": [
        "${OPENAI_VECTOR_STORE_PATH}"
      ],
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "OPENAI_VECTOR_STORE_ID": "${OPENAI_VECTOR_STORE_ID}",
        "SERVER_TOOL_NAME": "${SERVER_TOOL_NAME}",
        "SERVER_TOOL_DESCRIPTION": "${SERVER_TOOL_DESCRIPTION}"
      }
    }
  }
}
EOF

# Pythonの実行パスを設定（システムのPythonを使用）
PYTHON_PATH=${PYTHON_PATH:-$(which python3)}

# 必要なパッケージのインストール
echo "Installing required packages..."
$PYTHON_PATH -m pip install -e .

# スクリプトを実行
echo "Starting the application..."
cd "$SCRIPT_DIR"
$PYTHON_PATH -m mcp_simple_slackbot.main 
