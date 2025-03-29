import asyncio
import json
import logging
from typing import Dict, List

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from ..core.llm_client import LLMClient
from ..core.server import Server


class SlackMCPBot:
    """Manages the Slack bot integration with MCP servers."""

    def __init__(
        self,
        slack_bot_token: str,
        slack_app_token: str,
        servers: List[Server],
        llm_client: LLMClient,
    ) -> None:
        self.app = AsyncApp(token=slack_bot_token)
        # Create a socket mode handler with the app token
        self.socket_mode_handler = AsyncSocketModeHandler(
            self.app, slack_app_token)

        self.client = AsyncWebClient(token=slack_bot_token)
        self.servers = servers
        self.llm_client = llm_client
        self.conversations = {}  # Store conversation context per channel
        self.tools = []

        # Set up event handlers
        self.app.event("app_mention")(self.handle_mention)
        self.app.message()(self.handle_message)
        self.app.event("app_home_opened")(self.handle_home_opened)

    async def initialize_servers(self) -> None:
        """Initialize all MCP servers and discover tools."""
        for server in self.servers:
            try:
                await server.initialize()
                server_tools = await server.list_tools()
                self.tools.extend(server_tools)
                logging.info(
                    "Initialized server %s with %s tools",
                    server.mcp_server_name,
                    len(server_tools)
                )
            except Exception as e:
                logging.error(
                    "Failed to initialize server %s: %s",
                    server.mcp_server_name,
                    e
                )

    async def initialize_bot_info(self) -> None:
        """Get the bot's ID and other info."""
        try:
            auth_info = await self.client.auth_test()
            self.bot_id = auth_info["user_id"]
            logging.info("Bot initialized with ID: %s", self.bot_id)
        except Exception as e:
            logging.error("Failed to get bot info: %s", e)
            self.bot_id = None

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
        for tool in self.tools:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"- *{tool.name}*: {tool.description}",
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
            # Create system message with tool descriptions
            tools_text = "\n".join([tool.format_for_llm()
                                   for tool in self.tools])
            system_message = {
                "role": "system",
                "content": (
                    f"""You are a helpful assistant with access to the following tools:

                    {tools_text}
                    
                    When you need to use a tool, you MUST format your response exactly like this:
                    [TOOL] tool_name
                    {{"param1": "value1", "param2": "value2"}}

                    Make sure to include both the tool name AND the JSON arguments.
                    Never leave out the JSON arguments.

                    After receiving tool results, interpret them for the user in a helpful way.
                    """
                ),
            }

            # Add user message to history
            self.conversations[channel]["messages"].append(
                {"role": "user", "content": text}
            )

            # Set up messages for LLM
            messages = [system_message]

            # Add conversation history (last 5 messages)
            if "messages" in self.conversations[channel]:
                print('history', self.conversations[channel]["messages"][-5:])
                messages.extend(self.conversations[channel]["messages"][-5:])

            # Get LLM response
            response = await self.llm_client.get_response(messages)

            print('first response', response)

            # Process tool calls in the response
            if "[TOOL]" in response:
                response = await self._process_tool_call(response, channel)

            # Add assistant response to conversation history
            self.conversations[channel]["messages"].append(
                {"role": "assistant", "content": response}
            )

            # Send the response to the user
            await say(text=response, channel=channel, thread_ts=thread_ts)

        except Exception as e:
            error_message = f"I'm sorry, I encountered an error: {str(e)}"
            logging.error("Error processing message: %s", e, exc_info=True)
            await say(text=error_message, channel=channel, thread_ts=thread_ts)

    async def _process_tool_call(self, response: str, channel: str) -> str:
        """Process a tool call from the LLM response."""
        try:
            # Extract tool name and arguments
            tool_parts = response.split("[TOOL]")[1].strip().split("\n", 1)
            tool_name = tool_parts[0].strip()

            # Handle incomplete tool calls
            if len(tool_parts) < 2:
                return (
                    f"I tried to use the tool '{tool_name}', but the request "
                    f"was incomplete. Here's my response without the tool:"
                    f"\n\n{response.split('[TOOL]')[0]}"
                )

            # Parse JSON arguments
            try:
                args_text = tool_parts[1].strip()
                arguments = json.loads(args_text)
            except json.JSONDecodeError:
                return (
                    f"I tried to use the tool '{tool_name}', but the arguments "
                    f"were not properly formatted. Here's my response without "
                    f"the tool:\n\n{response.split('[TOOL]')[0]}"
                )

            # Find the appropriate server for this tool
            for server in self.servers:
                server_tools = [tool.name for tool in await server.list_tools()]
                if tool_name in server_tools:
                    # Execute the tool
                    tool_result = await server.execute_tool(tool_name, arguments)

                    # Add tool result to conversation history
                    tool_result_msg = f"Tool result for {tool_name}:\n{tool_result}"
                    self.conversations[channel]["messages"].append(
                        {"role": "system", "content": tool_result_msg}
                    )

                    try:
                        # Get interpretation from LLM
                        messages = [
                            {
                                "role": "system",
                                "content": (
                                    "You are a helpful assistant. You've just "
                                    "used a tool and received results. Interpret "
                                    "these results for the user in a clear, "
                                    "helpful way."
                                ),
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"I used the tool {tool_name} with arguments "
                                    f"{args_text} and got this result:\n\n"
                                    f"{tool_result}\n\n"
                                    f"Please interpret this result for me."
                                ),
                            },
                        ]

                        interpretation = await self.llm_client.get_response(messages)
                        return interpretation
                    except Exception as e:
                        logging.error(
                            "Error getting tool result interpretation: %s",
                            e,
                            exc_info=True,
                        )
                        # Fallback to basic formatting
                        if isinstance(tool_result, dict):
                            result_text = json.dumps(tool_result, indent=2)
                        else:
                            result_text = str(tool_result)
                        return (
                            f"I used the {tool_name} tool and got these results:"
                            f"\n\n```\n{result_text}\n```"
                        )

            # No server had the tool
            return (
                f"I tried to use the tool '{tool_name}', but it's not available. "
                f"Here's my response without the tool:\n\n{response.split('[TOOL]')[0]}"
            )

        except Exception as e:
            logging.error("Error executing tool: %s", e, exc_info=True)
            return (
                f"I tried to use a tool, but encountered an error: {str(e)}\n\n"
                f"Here's my response without the tool:\n\n{response.split('[TOOL]')[0]}"
            )

    async def start(self) -> None:
        """Start the Slack bot."""
        await self.initialize_servers()
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

        # Clean up servers
        for server in self.servers:
            try:
                await server.cleanup()
                logging.info("Server %s cleaned up", server.mcp_server_name)
            except Exception as e:
                logging.error(
                    "Error during cleanup of server %s: %s",
                    server.mcp_server_name, e
                )
