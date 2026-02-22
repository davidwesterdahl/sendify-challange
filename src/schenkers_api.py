from playwright.sync_api import sync_playwright
import time
import json
import logging

URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"
logging.basicConfig(level=logging.INFO, force=True)
log = logging.getLogger(__name__)

class SchenkerClient:
    def __init__(self):
        clock_start = time.time()
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


        BLOCK_TYPES = {"image", "font", "media"}
        def block_resources(route):
            if route.request.resource_type in BLOCK_TYPES:
                route.abort()
            else:
                route.continue_()

        clock_end = time.time()
        log.info("Browser setup: %.02f seconds" % (clock_end-clock_start))

        self.context.route("**/*", block_resources)


    def fetch_json(self, url:str, ref_id:str, time_out:int = 20_000, retries:int = 3) -> dict:
        """
        Opens a new page in the headless browser, enters the parcel ID and returns the JSON containing the information.
        It has a timeout of 20 seconds by default. If an error occurs, this function will return a dictionary in the form of
        {"error": "*the error*"}. This function handles exceptions for when the ID is not found and time outs.

        :param str url: The URL for the DBSchenker public webbsite
        :param str ref_id: The 10 digit parcel ID
        :param int time_out: Number of miliseconds to wait for the webbsite to load the page with shipment information
        :return: Returns the JSON in a python dictionary object response from the DBschenker API.
        """
        clock_start = time.time()
        log.info(f"Fetching JSON for {ref_id}. Time_out of {time_out/1000} seconds")
        
        for attempt in range(retries):
            page = self.context.new_page()

            # test for seeing which requests and responses are sent
            #page.on("request", lambda request: print(">>", request.method, request.url))
            #page.on("response", lambda response: print("<<", response.status, response.url))

            self.data = {} # holding the json for the shipment, if it is found
            self.message = {} # holding error message if shipment id is not found

            # Function to fetch only the necessary data
            def gather_json(r):
                if r.status == 400: # set message if id not found
                    if "tracking-public/shipments?query" in r.url:
                        #print("The first one:", r.url)
                        try:
                            self.message = r.json()
                        except Exception:
                            log.warning(f"400 message for {ref_id} not found") 

                if r.status == 200: # set json if id found
                    if "tracking-public/shipments/land" in r.url:
                        #print("The second one:", r.url)
                        try:
                            self.data = r.json()
                        except Exception:
                            log.warning(f"Could not retrieve json for: {ref_id}")

            page.on("response", gather_json)

            page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """)

        
            try:
                page.goto(url, wait_until="domcontentloaded")

                # enter id and wait for the second response, either a 200 or 400
                # as the first 429 is a captcha puzzle
                with page.expect_response(
                    lambda r: "tracking-public/shipments?query" in r.url
                    and r.status != 429
                    ):
                    page.fill("input#mat-input-0", ref_id)
                    page.keyboard.press("Enter")

                # if the id is wrong, the page will not load, and we get a json response
                if self.message:
                    return {"error": self.message["message"]}
                
               #page.wait_for_selector("es-tracking-public", timeout=time_out)
                page.wait_for_selector("es-event-list", timeout=time_out)

                if page.query_selector("es-shipment-not-found"):
                    log.warning(f"shipment {ref_id} not found")
                    return {"error": f"shipment {ref_id} not found by DBschenker webbsite"}
                return self.data
            except Exception as e:
                log.warning(f"Attempt {attempt+1} of {retries}:Failed to fetch Json: Shipment id {ref_id}. \n{e}")
                if attempt == retries-1:
                    log.warning(f"All atempts for shipment id {ref_id} failed, returning error dict from fetch_json.")
                    return {"error": f"{e}"}
                #     raise
            finally:
                page.close()
                clock_end = time.time()
                log.info("Json_fetch: %.02f seconds" % (clock_end-clock_start))

        return {"error" : f"No retries attempted for {ref_id}"}

            

    def parse_json(self, source: dict) -> dict:
        """Takes the JSON dictionary object from the fetch_json() function 
        and sorts it, returning a dictionary object with the relevant parcel info. 
        If the form of the JSON from DBSchenker changes, this function needs changing.
        
        If this functions receives a None value, it retuns a dictionary with an error message"""

        data = {}

        if "error" in source: # If the json returns a dict with error, return the error
            log.warning("parse_json did not receive a dictionary object")
            return source
        else:
            data["receiver"] = source["location"]["consignee"]
            data["sender"] = source["location"]["shipper"]
            data["packageDetails"] = source["goods"]
            data["events"] = source["events"]
            for event in data["events"]:
                del event["shellIconName"]
 
        return data
    
    def close(self):
        self.browser.close()
        self.p.stop()


##### TEST FOR DEBUG #####
if __name__ == "__main__":

    print("This is the debug. Choose what to test.")
    print("[1] Test with the id 1806256390, and print the json")
    print("[2] Test to run all 11 id's with a timout of 1 second to test timout exception handling")
    print("[3] type own id")
    choice : str = input(": ")

    client = SchenkerClient() # start the client
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
                raw = client.fetch_json(URL, id, 1_000)
                if raw is None:
                    print(client.parse_json(raw))

        case "3":
            ref_id = input("Type the id: ")
            jsonnn = client.fetch_json(URL, ref_id)
            parsed = client.parse_json(jsonnn)
            print(json.dumps(parsed, sort_keys=True, indent=4))

        

