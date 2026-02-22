# Sendify challange shipment tracker MCP server 
## David Westerdahl

Since the API on the website sends a CAPTCHA puzzle to solve, I had to take a different route. This project uses the playwright browser in headless mode to go to the schenker webbsite, enter the id and retrieves the JSON file with all shipment info that the frontend of their website gets.

## Code structure

This project consists of two python files, one for fetching data from schenker, and one for setting up the MCP server, with following functions:

|**mcp_server.py**| |
|-|-|
|**track_shipment**(_tracking number: str_)|The @mcp.tool() used by the ai agent. The tracking number is issued by the user.

|**schenkers_api.py**| |
|-|-|
|**SchenkerClient**| The object containing the playwright chromium browser used to fetch the data from schenkers webbsite. It starts a chromium browser when first created. Also contains the following methods:
|**fetch_json**(*url: str, ref_id: str, time_out: int, retries: int*)| Sets up a chromium page, goes to the *url* and types in the *ref_id* and waits for maximum *time_out* miliseconds for the page to load a maximum of *retries* times. If it times out all retries, returns a dictionary object with an error message.
|**parse_json**(*source: dict*)|Parses the raw json fetched from the webbsite. Not much is changed, but it makes sure that all the information is right. If fetch_json returned an error, this will simply send the message forward to the ai agent.

## Installation

You need to have python installed, download it [here](https://www.python.org/downloads/)

This project uses the uv package manager for python. Instructions on how to install it is [here](https://docs.astral.sh/uv/getting-started/installation/). If you have homebrew simply type ```brew install uv``` in the terminal. 

Next download this project and open the sendify-challange-master folder. If you are on mac open the run.command, or on windows the run.bat. A new console window will open and run `uv sync` as well as run the schenker_api.py for debugging purposes. This will prompt you with different choices on what to test, to see that it functions properly.

Next we want to configure the MCP.
