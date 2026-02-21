from mcp.server.fastmcp import FastMCP
from schenkers_api import SchenkerClient
import logging


mcp = FastMCP("Schenker Tracking Server")
client = None

@mcp.tool()
def track_shipment(tracking_number: str) -> dict:
    """
    Fetch tracking information for a DB Schenker shipment.
    """
    global client
    if client==None:
        client = SchenkerClient()
    raw = client.fetch_json(tracking_number)
    parsed = client.parse_json(raw)

    return parsed


if __name__ == "__main__":
    logging.info("starting client")
    mcp.run(transport="stdio")
    #print("shutting down")