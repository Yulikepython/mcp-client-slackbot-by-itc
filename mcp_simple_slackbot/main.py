import asyncio
import logging
from typing import List
from agents.mcp import MCPServerStdio
from mcp_simple_slackbot.core.mcp_servers import MCPServer
from mcp_simple_slackbot.core.openai_agent import setup_agent
from mcp_simple_slackbot.config.configuration import Configuration
from mcp_simple_slackbot.slack.agent_bot import SlackAgentBot


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SERVER_CONFIG_PATH = "mcp_simple_slackbot/servers_config.json"
SERVER_CONFIG_KEY_MCP_SERVERS = "mcpServers"


async def initialize_servers(server_config: dict) -> List[MCPServerStdio]:
    """Initialize MCP servers asynchronously."""
    servers = []
    for mcp_server_name, srv_config in server_config[SERVER_CONFIG_KEY_MCP_SERVERS].items():
        server = MCPServer(mcp_server_name, srv_config)
        server_stdio = await server.initialize_and_return_server_stdio()
        servers.append(server_stdio)
    return servers


async def main() -> None:
    """Initialize and run the Slack bot."""

    # Load configuration
    config = Configuration()

    if not config.slack_bot_token or not config.slack_app_token:
        raise ValueError(
            "SLACK_BOT_TOKEN and SLACK_APP_TOKEN must be set in environment variables"
        )

    # Load server configuration
    server_config = config.load_config(SERVER_CONFIG_PATH)
    mcp_servers = await initialize_servers(server_config)

    agent = setup_agent(
        config.openai_api_key,
        mcp_servers,
        "You are a helpful assistant that can help with tasks related to the MCP servers and tools. You can use the tools to get information about the MCP servers and tools. You should reply in a friendly and helpful manner with the language that the user speaks."
    )

    slack_agent_bot = SlackAgentBot(
        config.slack_bot_token,
        config.slack_app_token,
        agent
    )

    try:
        await slack_agent_bot.start()
        # Keep the main task alive until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error("Error: %s", e)
    finally:
        await slack_agent_bot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
