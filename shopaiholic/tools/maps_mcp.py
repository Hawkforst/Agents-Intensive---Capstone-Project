"""Maps MCP toolset factory.

Returns a McpToolset backed by @modelcontextprotocol/server-google-maps
when GOOGLE_MAPS_API_KEY is set, or None when it isn't (Store Finder
will fall back to a stub message in that case).
"""

from __future__ import annotations

from shopaiholic.config import google_maps_api_key


def build_maps_toolset():
    """Build and return the Google Maps MCP toolset, or None if no API key."""
    key = google_maps_api_key()
    if not key:
        return None

    from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
    from mcp import StdioServerParameters

    return McpToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-google-maps"],
            env={"GOOGLE_MAPS_API_KEY": key},
        )
    )
