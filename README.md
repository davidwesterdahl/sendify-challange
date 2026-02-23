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

Next, download this project and open the sendify-challange-master folder. If you are on mac open the run.command, or on windows the run.bat. A new console window will open and run the necessary commands to set up the enviroment, as well as run the schenker_client.py for debugging purposes. This will prompt you with different choices on what to test, to see that it functions properly.

**Mac security warning**
When opening `run.command` for the first time, Mac may show a security warning. 
Right-click the file in Finder and select **Open**, then confirm in the dialog. 
After that you can double-click it as normal.

**Windows security warning**
When opening `run.bat` for the first time, Windows SmartScreen may show a warning.
Click **More info** and then **Run anyway** to proceed.

If for some reason the run files does not work, simply open the sendify-challange-master folder in terminal and run the following commands

```bsh
uv sync
uv run playwright install chromium
run src/schenker_client.py
```

Next we want to connect the MCP server to your AI desktop agent. Full instructions are on how to setup a local MCP server are [here](https://modelcontextprotocol.io/docs/develop/connect-local-servers). 

This MCP server has been tested and works with Claude. To connect the MCP server go to **Settings → Developer** in Claude and add a new MCP server:

```json
{
  "mcpServers": {
    "schenker": {
      "command": "uv",
      "args": ["run", "/ABSOLUTE/PATH/TO/sendify-challange-master/src/mcp_server.py"]
    }
  }
}
```

Replace the path with your actual path to `mcp_server.py`, for example:
- **Mac/Linux:** `/Users/yourname/code_projects/sendify-challange-master/src/mcp_server.py`
- **Windows:** `C:\\Users\\yourname\\code_projects\\sendify-challange-master\\src\\mcp_server.py`

Make sure that the foldername `sendify-challange-master` is correct.

Restart Claude and the `track_shipment` tool will be available.
