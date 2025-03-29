import datetime
from typing import List
from agents import Agent, set_default_openai_key
from agents.tool import function_tool
from agents.mcp import MCPServerStdio


@function_tool
def get_today():
    """Get the current date in Japanese."""
    jst = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(jst).strftime("%Y年%m月%d日")


def setup_agent(openai_api_key: str, mcp_servers: List[MCPServerStdio], instruction: str) -> Agent:
    """Setup the OpenAI agent."""
    set_default_openai_key(openai_api_key)
    return Agent(
        name="Slackbot Agent",
        instructions=instruction,
        tools=[get_today],
        mcp_servers=mcp_servers
    )
