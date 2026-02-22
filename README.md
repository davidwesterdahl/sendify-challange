# Sendify challange
## David Westerdahl

Since the API sends a CAPTCHA puzzle to solve, I had to take a different route. This project uses the playwright browser in headless mode to enter the schenker webbsite, enter the id and retrieves the JSON file with all shipment info that the frontend of their webbsite gets./

The public DB Schenker tracking UI performs bot detection by checking navigator.webdriver. The implementation mitigates this by masking the property before page scripts execute

#### Code structure

This project consists of two python files, one for fetching data from schenker, and one for setting up the MCP server, with following functions:

|**mcp_server.py**| |
|-|-|
|**track_shipment**(_tracking number: <span style="color:blue"> str</span>_)|The @mcp.tool() used by the ai agent. The tracking number is issued by the user.

|**schenkers_api.py**||
|-|-|
|**SchenkerClient**| The object containing the playwright chromium browser used to fetch the data from schenkers webbsite. It starts a chromium browser when first created.Also contains the following methods:
|**fetch_json**(*url: <span style="color:blue"> str</span>, ref_id: <span style="color:blue"> str</span>, time_out: <span style="color:blue"> int</span>, retries: <span style="color:blue"> int</span>*)| Sets up a chromium page, goes to the *url* and types in the *ref_id* and waits for maximum *time_out* miliseconds for the page to load a maximum of *retries* times. If it times out all retries, returns a dictionary object with an error message.
|**parse_json**(*source: <span style="color:blue"> dict</span>*)|Parses the raw json fetched from the webbsite. Not much is changed, but it makes sure that all the information is right. If fetch_json returned an error, this will simply send the message forward to the ai agent.