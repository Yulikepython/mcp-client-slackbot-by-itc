from typing import Dict, Any
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from agents import gen_trace_id, trace


class MCPServer:
    """Manages MCP server."""

    def __init__(self, mcp_server_name: str, mcp_server_config: dict):
        self.mcp_server_name: str = mcp_server_name
        self.mcp_server_config: Dict[str, Any] = mcp_server_config

    async def initialize_and_return_server_stdio(self) -> MCPServerStdio:
        """Initialize the MCP server.
        return the server instance.
        """
        # MCPServerStdioParams のインスタンスを作成
        mcp_params: MCPServerStdioParams = MCPServerStdioParams(
            command=self.mcp_server_config['command'],
            args=self.mcp_server_config.get('args', []),
            env=self.mcp_server_config.get('env', {}),
            encoding=self.mcp_server_config.get('encoding', 'utf-8'),
            encoding_error_handler=self.mcp_server_config.get(
                'encoding_error_handler', 'strict')
        )

        # MCPServerStdioのインスタンスを作成
        mcp_server_stdio = MCPServerStdio(
            params=mcp_params,
            cache_tools_list=True,
            name=self.mcp_server_name
        )

        # サーバーを接続
        await mcp_server_stdio.connect()

        trace_id = gen_trace_id()
        with trace(
            workflow_name="MCP CLIENT SLACKBOT",
            trace_id=trace_id
        ):
            print(
                f"View trace: https://platform.openai.com/traces/{trace_id}\n")
            return mcp_server_stdio
