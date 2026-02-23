from mcp.server.fastmcp import FastMCP
from schenker_client import SchenkerClient
import logging
import asyncio

URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"
mcp = FastMCP("Schenker Tracking Server")
client = None

logging.basicConfig(level=logging.INFO, force=True)
log = logging.getLogger(__name__)

@mcp.tool()
async def track_shipment(tracking_number: str) -> dict:
    """
    Fetch tracking information for a DB Schenker shipment.
    Returns sender, receiver, package details and tracking history.
    Returns an error message if tracking number is invalid, not found or 
    in case of request time out.
    
    This client has a time out of 10 seconds for each request made to the
    DBSchenker tracking website, and retries 3 times if timed out.

    :param str tracking_number: The tracking number for the shipment.
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
    log.info("starting MCP client for DBSchenker shipment tracking.")
    mcp.run(transport="stdio")


