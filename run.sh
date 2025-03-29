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
    }
  }
}
EOF

# Pythonの実行パスを設定（システムのPythonを使用）
PYTHON_PATH=${PYTHON_PATH:-$(which python3)}

# 必要なパッケージのインストール
echo "Installing required packages..."
$PYTHON_PATH -m pip install -r mcp_simple_slackbot/requirements.txt

# Install the package in development mode
echo "Installing the package in development mode..."
$PYTHON_PATH -m pip install -e .

# スクリプトを実行
echo "Starting the application..."
cd "$SCRIPT_DIR"
$PYTHON_PATH mcp_simple_slackbot/main.py 
