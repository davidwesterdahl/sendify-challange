from mcp.server.fastmcp import FastMCP
from schenkers_api import SchenkerClient
import logging
import asyncio

URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"
mcp = FastMCP("Schenker Tracking Server")
client = None

@mcp.tool()
async def track_shipment(tracking_number: str) -> dict:
    """
    Fetch tracking information for a DB Schenker shipment.
    """
    def fetch():
        asyncio.set_event_loop(asyncio.new_event_loop()) 
        global client
        if client==None:
            client = SchenkerClient()
        raw = client.fetch_json(URL, tracking_number)
        return client.parse_json(raw)

    return await asyncio.to_thread(fetch)


if __name__ == "__main__":
    logging.info("starting client")
    mcp.run(transport="stdio")
    #print("shutting down")