import asyncio
import logging

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from agents import Agent, Runner


class SlackAgentBot:
    """Manages the Slack bot integration with MCP servers."""

    def __init__(
        self,
        slack_bot_token: str,
        slack_app_token: str,
        agent: Agent,
    ) -> None:
        self.app = AsyncApp(token=slack_bot_token)
        # Create a socket mode handler with the app token
        self.socket_mode_handler = AsyncSocketModeHandler(
            self.app, slack_app_token)

        self.client = AsyncWebClient(token=slack_bot_token)
        self.conversations = {}  # Store conversation context per channel
        self.agent = agent

        self.tools: tuple[str, str] = []

        self.bot_id = None
        # Set up event handlers
        self.app.event("app_mention")(self.handle_mention)
        self.app.message()(self.handle_message)
        self.app.event("app_home_opened")(self.handle_home_opened)

    async def initialize_bot_info(self) -> None:
        """Get the bot's ID and other info."""
        try:
            auth_info = await self.client.auth_test()
            self.bot_id = auth_info["user_id"]
            logging.info("Bot initialized with ID: %s", self.bot_id)
        except Exception as e:
            logging.error("Failed to get bot info: %s", e)
            self.bot_id = None

        # MCPツールの追加
        all_tools = await self.agent.get_all_tools()
        for tool in all_tools:
            self.tools.append((tool.name, tool.description))

    async def handle_mention(self, event, say):
        """Handle mentions of the bot in channels."""
        await self._process_message(event, say)

    async def handle_message(self, message, say):
        """Handle direct messages to the bot."""
        # Only process direct messages
        if message.get("channel_type") == "im" and not message.get("subtype"):
            await self._process_message(message, say)

    async def handle_home_opened(self, event, client):
        """Handle when a user opens the App Home tab."""
        user_id = event["user"]

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Welcome to MCP Assistant!"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "I'm an AI assistant with access to tools and resources "
                        "through the Model Context Protocol."
                    ),
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Available Tools:*"},
            },
        ]

        # Add tools
        for name, description in self.tools:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"- *{name}*: {description}",
                    },
                }
            )

        # Add usage section
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        "*How to Use:*\n• Send me a direct message\n"
                        "• Mention me in a channel with @MCP Assistant"
                    ),
                },
            }
        )

        try:
            await client.views_publish(
                user_id=user_id, view={"type": "home", "blocks": blocks}
            )
        except Exception as e:
            logging.error("Error publishing home view: %s", e)

    async def _process_message(self, event, say):
        """Process incoming messages and generate responses."""
        channel = event["channel"]
        user_id = event.get("user")

        # Skip messages from the bot itself
        if user_id == getattr(self, "bot_id", None):
            return

        # Get text and remove bot mention if present
        text = event.get("text", "")
        if hasattr(self, "bot_id") and self.bot_id:
            text = text.replace(f"<@{self.bot_id}>", "").strip()

        thread_ts = event.get("thread_ts", event.get("ts"))

        # Get or create conversation context
        if channel not in self.conversations:
            self.conversations[channel] = {"messages": []}

        try:

            # Get LLM response
            response = await Runner.run(self.agent, text)

            await say(text=response.final_output, channel=channel, thread_ts=thread_ts)

        except Exception as e:
            error_message = f"I'm sorry, I encountered an error: {str(e)}"
            logging.error("Error processing message: %s", e, exc_info=True)
            await say(text=error_message, channel=channel, thread_ts=thread_ts)

    async def start(self) -> None:
        """Start the Slack bot."""
        await self.initialize_bot_info()
        # Start the socket mode handler
        logging.info("Starting Slack bot...")
        asyncio.create_task(self.socket_mode_handler.start_async())
        logging.info("Slack bot started and waiting for messages")

    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if hasattr(self, "socket_mode_handler"):
                await self.socket_mode_handler.close_async()
            logging.info("Slack socket mode handler closed")
        except Exception as e:
            logging.error("Error closing socket mode handler: %s", e)
