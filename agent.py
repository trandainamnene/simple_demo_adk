"""Root agent definition plus MCP integration."""

import os
import warnings

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

try:  # Optional but convenient to load .env when running `python agent.py`.
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - best effort convenience only.
    load_dotenv = None  # type: ignore[assignment]

if load_dotenv:
    load_dotenv()


# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}


def _build_mcp_toolsets() -> list[McpToolset]:
    """Create MCP toolsets (if creds are available)."""
    tools: list[McpToolset] = []
    exa_api_key = os.getenv("EXA_API_KEY")

    if not exa_api_key:
        warnings.warn(
            "EXA_API_KEY is not set. Skipping the Exa MCP toolset. "
            "Set the value in your environment or .env file to enable MCP.",
            stacklevel=1,
        )
        return tools

    tools.append(
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "exa-mcp-server"],
                    env={"EXA_API_KEY": exa_api_key},
                ),
                timeout=30,
            ),
            tool_name_prefix="exa",
        )
    )
    return tools


root_agent = Agent(
    model="gemini-2.0-flash",
    name="root_agent",
    description="Tells the current time in a specified city.",
    instruction=(
        "You are a helpful assistant that tells the current time in cities. "
        "Prefer the 'get_current_time' tool, but you can also call MCP tools "
        "when you need web context."
    ),
    tools=[get_current_time, *_build_mcp_toolsets()],

)