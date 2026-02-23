from playwright.sync_api import sync_playwright
import time
import json
import logging

# The URL to DBSchenkers shipment tracking
URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"

logging.basicConfig(level=logging.INFO, force=True)
log = logging.getLogger(__name__)

class SchenkerClient:
    def __init__(self):
        clock_start = time.time()
        log.info("Starting SchenkerClient")
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )

        self.context = self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="sv-SE",
            timezone_id="Europe/Stockholm"
        )

        BLOCK_TYPES = {"image", "font", "media", "stylesheet", "other", "eventsource", "websocket"}
        def block_resources(route):
            if route.request.resource_type in BLOCK_TYPES:
                route.abort()
            else:
                route.continue_()

        clock_end = time.time()
        log.info("Browser setup: %.02f seconds" % (clock_end-clock_start))

        self.context.route("**/*", block_resources)


    def fetch_json(self, url:str, ref_id:str, time_out:int = 10_000, retries:int = 3) -> dict:
        """
        Opens a new page in the headless browser, enters the parcel ID and returns the JSON containing the information.
        It has a timeout of 10 seconds by default. If an error occurs, this function will return a dictionary in the form of
        {"error": "*the error*"}. This function handles exceptions for when the ID is not found and time outs.

        :param str url: The URL for the DBSchenker public webbsite
        :param str ref_id: The 10 digit parcel ID
        :param int time_out: Number of miliseconds to wait for the webbsite to load the page with shipment information
        :return: Returns the JSON in a python dictionary object response from the DBschenker API.
        """
        clock_start = time.time()
        log.info(f"Fetching JSON for {ref_id}. Time_out of {time_out/1000} seconds")

        # Attempt to fetch the JSON for each retry
        for attempt in range(retries):
            page = self.context.new_page()

            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """)

            try:
                page.goto(url, wait_until="domcontentloaded")

                # enter id and wait for the second response, either a 200 or 400
                # as the first 429 response is a captcha puzzle
                with page.expect_response(
                    lambda r: 
                    ("tracking-public/shipments?query" in r.url and r.status == 400) or 
                    ("tracking-public/shipments/land" in r.url and r.status == 200)
                    , timeout=time_out) as response_info:

                    page.fill("input#mat-input-0", ref_id)
                    page.keyboard.press("Enter")

                # Get the JSON response from either the 200 or 400 response
                response = response_info.value

                # If response is 400, id is not found, return error message
                if response.status == 400:
                    return {"error": response.json().get("message", "Shipment not found")}

                return response.json()
            
            except Exception as e:
                log.warning(f"Attempt {attempt+1} of {retries}:Failed to fetch Json: Shipment id {ref_id}. \n{e}")
                if attempt == retries-1:
                    log.warning(f"All atempts for shipment id {ref_id} failed, returning error dict from fetch_json.")
                    return {"error": f"{e}"}
            finally:
                page.close()
                clock_end = time.time()
                log.info("Json_fetch: %.02f seconds" % (clock_end-clock_start))

        return {"error" : f"Number of retries can not be 0: id {ref_id}"}

            

    def parse_json(self, source: dict) -> dict:
        """Takes the JSON dictionary object from the fetch_json() function 
        and sorts it, returning a dictionary object with the relevant parcel info. 
        If the form of the JSON from DBSchenker changes, this function needs changing.
        
        If this functions receives an error message, it simply passes it on"""

        if "error" in source: # If the json returns a dict with error, return the error
            log.warning("parse_json recieved an error as argument")
            return source
        else:
            try:
                data = {}
                data["receiver"] = source["location"]["consignee"]
                data["sender"] = source["location"]["shipper"]
                data["packageDetails"] = source["goods"]
                data["events"] = source["events"]
                for event in data["events"]:
                    del event["shellIconName"]
                return data
            
            except KeyError as e:
                return {"error": f"DBSchenker has likely changed their JSON response, code needs changing. Missing key: {e}"}
    
    def close(self):
        self.browser.close()
        self.p.stop()


##### TEST FOR DEBUG #####
if __name__ == "__main__":

    print("""
######################################
This is a short debug program for fetching shipment tracking data from DBSchenker. Select what to test.""")
    print("[1] Test with the id 1806256390, and print the json")
    print("[2] Test to run all 11 id's with a timout of 1.5 second to test timout exception handling")
    print("[3] type own id. Use it to try invalid id.")
    choice : str = input(": ")

    client = SchenkerClient() # start the client

    try:
        match choice:
            case "1":
                REF_ID = "1806256390"
                jsonnn = client.fetch_json(URL, REF_ID)
                parsed = client.parse_json(jsonnn)
                print(json.dumps(parsed, sort_keys=True, indent=4))

            case "2":
                # Test all the id's and stress test the time_out of the functions.
                id_list = ["1806203236",
                            "1806290829",
                            "1806273700",
                            "1806272330",
                            "1806271886",
                            "1806270433",
                            "1806268072",
                            "1806267579",
                            "1806264568",
                            "1806258974",
                            "1806256390"]
                for id in id_list:
                    raw = client.fetch_json(URL, id, 1_500)
                    if "error" in raw:
                        print(client.parse_json(raw))

            case "3":
                ref_id = input("Type the id: ")
                jsonnn = client.fetch_json(URL, ref_id)
                parsed = client.parse_json(jsonnn)
                print(json.dumps(parsed, sort_keys=True, indent=4))

            case default:
                print("No valid input, shutting down...")
    finally:
        client.close() 
            

