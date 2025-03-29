import logging
import asyncio
import shutil
import os

from contextlib import AsyncExitStack
from typing import Any, Dict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class Server:
    """Manages MCP server connections and tool execution."""

    def __init__(self, mcp_server_name: str, mcp_server_config: dict):
        self.mcp_server_name: str = mcp_server_name
        self.mcp_server_config: Dict[str, Any] = mcp_server_config
        self.stdio_context: Any | None = None
        self.session: ClientSession | None = None
        self._cleanup_lock: asyncio.Lock = asyncio.Lock()
        self.exit_stack: AsyncExitStack = AsyncExitStack()

    async def initialize(self):
        """Initialize the server connection."""
        command = (
            shutil.which("npx")
            if self.mcp_server_config["command"] == "npx"
            else self.mcp_server_config["command"]
        )
        if command is None:
            raise ValueError(
                "The command must be a valid string and cannot be None.")

        server_params = StdioServerParameters(
            command=command,
            args=self.mcp_server_config["args"],
            env={**os.environ, **self.mcp_server_config["env"]}
            if self.mcp_server_config.get("env")
            else None,
        )
        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.session = session
        except Exception as e:
            logging.error(
                "Error initializing server %s: %s",
                self.mcp_server_name, e
            )
            await self.cleanup()
            raise

    async def cleanup(self):
        try:
            # Implementation of cleanup
            pass
        except Exception as e:
            logging.error(
                "Error during cleanup of server %s: %s",
                self.mcp_server_name, e
            )

    async def execute_tool(self, e, attempt, retries, delay):
        try:
            # Implementation of execute_tool
            pass
        except Exception as e:
            logging.warning(
                "Error executing tool: %s. Attempt %d of %d.",
                e, attempt, retries
            )
            if attempt < retries:
                logging.info("Retrying in %f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                logging.error("Max retries reached. Failing.")
                raise
