#!/usr/bin/env python3
import json
import os
from pathlib import Path


def generate_servers_config():
    """Generate servers_config.json from environment variables."""
    config = {
        "mcpServers": {
            "google-workspace": {
                "command": "node",
                "args": [
                    os.getenv("GOOGLE_WORKSPACE_SERVER_PATH",
                              "google-workspace-server/index.js")
                ],
                "env": {
                    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
                    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
                    "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN", "")
                },
                "encoding": "utf-8",
                "encoding_error_handler": "replace"
            }
        }
    }

    # 設定ファイルのパスを取得
    config_path = Path("mcp_simple_slackbot/servers_config.json")

    # ディレクトリが存在しない場合は作成
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # 設定ファイルを書き込み
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"Generated {config_path}")


if __name__ == "__main__":
    generate_servers_config()
