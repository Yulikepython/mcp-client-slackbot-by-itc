import datetime
from typing import List
from agents import Agent, set_default_openai_key, ModelSettings
from agents.tool import function_tool
from agents.mcp import MCPServerStdio

from mcp_simple_slackbot.config.configuration import Configuration


@function_tool
def get_now():
    """Get now in Japan.

    Returns:
        str: The current time in Japan.
    """
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return "The current time in Japan is " + datetime.datetime.now(jst).isoformat()


def setup_agent(mcp_servers: List[MCPServerStdio], instruction: str) -> Agent:
    """Setup the OpenAI agent."""

    config = Configuration()
    set_default_openai_key(config.openai_api_key)
    return Agent(
        name="Slackbot Agent",
        model=config.llm_model,
        instructions=instruction,
        tools=[get_now],
        mcp_servers=mcp_servers,
        model_settings=ModelSettings(
            temperature=0.4,
            parallel_tool_calls=True
        ),
    )
