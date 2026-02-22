from mcp.server.fastmcp import FastMCP
from schenkers_api import SchenkerClient
import logging
import asyncio
import atexit


URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"
mcp = FastMCP("Schenker Tracking Server")
client = None


# Functions for handling shutdown of the MCP server
def shutdown() -> None:
    global client
    if client is not None:
        logging.info("Closing browser...")
        client.close()
    else:
        logging.info("Client already closed")
atexit.register(shutdown)


@mcp.tool()
async def track_shipment(tracking_number: str) -> dict:
    """
    Fetch tracking information for a DB Schenker shipment.
    """
    def fetch():
        asyncio.set_event_loop(asyncio.new_event_loop()) 
        global client
        if client is None:
            client = SchenkerClient()
        raw = client.fetch_json(URL, tracking_number)
        return client.parse_json(raw)

    return await asyncio.to_thread(fetch)


if __name__ == "__main__":
    logging.info("starting client. Press CTRL+C to exit the server.")
    mcp.run(transport="stdio")


