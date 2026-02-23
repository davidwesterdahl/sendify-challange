# Sendify challange shipment tracker MCP server 
## David Westerdahl

Since the API on the website sends a CAPTCHA puzzle to solve, I had to take a different route. This project uses the playwright browser in headless mode to go to the schenker website, enter the id and retrieves the JSON file with all shipment info that the frontend of their website gets.

## Code structure

This project consists of two python files, one for fetching data from DBSchenker, and one for setting up the MCP server, with following functions:

|**mcp_server.py**| |
|-|-|
|**track_shipment**(_tracking number: str_)|The @mcp.tool() used by the ai agent. The tracking number is issued by the user.

|**schenker_client.py**| |
|-|-|
|**SchenkerClient**| The object containing the playwright chromium browser used to fetch the data from schenkers website. It starts a chromium browser when first created. Also contains the following methods:
|**fetch_json**(*url: str, ref_id: str, time_out: int, retries: int*)| Sets up a chromium page, goes to the *url* and types in the *ref_id* and waits for maximum *time_out* miliseconds for the page to load a maximum of *retries* times. If it times out all retries, returns a dictionary object with an error message.
|**parse_json**(*source: dict*)|Parses the raw json fetched from the webbsite. Not much is changed, but it makes sure that all the information is right. If fetch_json returned an error, this will simply send the message forward to the ai agent.

## Installation

You need to have python installed, download it [here](https://www.python.org/downloads/)

This project uses the uv package manager for python. Instructions on how to install it is [here](https://docs.astral.sh/uv/getting-started/installation/). If you have homebrew simply type ```brew install uv``` in the terminal. UV is needed for the next step.

Next, download this project and open the sendify-challange-master folder. If you are on mac open the `run.command`, or on windows the `run.bat`. A new console window will open and run the necessary commands to set up the enviroment, as well as run the schenker_client.py for debugging purposes. This will prompt you with different choices on what to test, to see that it functions properly.

Mac and windows might not open the run files for security reasons. If so, then simply open the sendify-challange-master folder in terminal and run the following commands:

```bsh
uv sync
uv run playwright install chromium
run src/schenker_client.py
```

Next we want to connect the MCP server to your AI desktop agent. Full instructions on how to setup a MCP server are [here](https://modelcontextprotocol.io/docs/develop/connect-local-servers). 

This MCP server has been tested and works with Claude. To connect the MCP server go to **Settings → Developer** in Claude and add a new MCP server in the config file via the **Edit config** button:

```json
{
  "mcpServers": {
    "schenker": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/sendify-challange-master/src",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

If you have multiple MCP servers in there, make sure the new `"schenker"` is added in the `"mcpServers"` key, after a comma. The name `"schenker"` can be changed to anything you like.

Replace the path with your actual path to `mcp_server.py`, for example:
- **Mac/Linux:** `/Users/yourname/sendify-challange-master/src/mcp_server.py`
- **Windows:** `C:\\Users\\yourname\\sendify-challange-master\\src\\mcp_server.py`

Make sure that the foldername `sendify-challange-master` is correct.

Restart Claude and the `track_shipment` tool will be available. Ask claude to track a shipment id `1806264568` with the schenker mcp and it should be working.
