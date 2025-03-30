import json
import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv


class Configuration:
    """
    Manages configuration and environment variables for the MCP Slackbot.

    Attributes:
        slack_bot_token (str): The Slack bot token.
        slack_app_token (str): The Slack app token.
        openai_api_key (str): The OpenAI API key.
        groq_api_key (str): The Groq API key.

    @todo: if use OpenAI Agents, no feature needed for other LLM models.
    """

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_app_token = os.getenv("SLACK_APP_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4o")

    def load_env(self) -> None:
        """Load environment variables from .env file."""
        env_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            logging.info("Loaded environment variables from %s", env_path)
        else:
            logging.warning(
                "Environment file not found at %s. Ensure the .env file exists and is accessible.",
                env_path
            )

    @staticmethod
    def load_config(file_path: str) -> Dict[str, Any]:
        """Load server configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file.

        Returns:
            Dict containing server configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            JSONDecodeError: If configuration file is invalid JSON.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def llm_api_key(self) -> str:
        """Get the appropriate LLM API key based on the model.

        Returns:
            The API key as a string.

        Raises:
            ValueError: If no API key is found for the selected model.
        """
        if "gpt" in self.llm_model.lower() and self.openai_api_key:
            return self.openai_api_key
        elif "llama" in self.llm_model.lower() and self.groq_api_key:
            return self.groq_api_key
        elif "claude" in self.llm_model.lower() and self.anthropic_api_key:
            return self.anthropic_api_key

        # Fallback to any available key
        if self.openai_api_key:
            return self.openai_api_key
        elif self.groq_api_key:
            return self.groq_api_key
        elif self.anthropic_api_key:
            return self.anthropic_api_key

        raise ValueError("No API key found for any LLM provider")
