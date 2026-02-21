from playwright.sync_api import sync_playwright
import time
import json
import logging

URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"
REF_ID = "1806256390"
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


    def fetch_json(self, url:str, ref_id:str, time_out:int = 20_000) -> dict:
        """
        Opens a new page in the headless browser, enters the parcel ID and returns the JSON containing the information.
        It has a timeout of 20 seconds by default

        :param str url: The URL for the DBSchenker public webbsite
        :param str ref_id: The 10 digit parcel ID
        :param int time_out: Number of miliseconds to wait for the webbsite to load the page with shipment information
        :return: Returns the JSON in a python dictionary object response from the DBschenker API.
        """
        clock_start = time.time()
        log.info(f"Fetching JSON for {ref_id}. Time_out of {time_out/1000} seconds")
        

        page = self.context.new_page()

        #page.on("request", lambda request: print(">>", request.method, request.url))
        #page.on("response", lambda response: print("<<", response.status, response.url))

        data = {}

        # Function to fetch only the necessary data
        def response_test(r):
            if r.status == 200:
                if "tracking-public/shipments?query" in r.url:
                    #print("The first one:", r.url)
                    data["first"] = r.json()

                if "tracking-public/shipments/land" in r.url:
                    #print("The second one:", r.url)
                    data["second"] = r.json()

        page.on("response", response_test)

        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        page.goto(url, wait_until="domcontentloaded")
        page.fill("input#mat-input-0", ref_id)
        page.keyboard.press("Enter")
        page.wait_for_selector("es-event-list", timeout=time_out)
        page.close()

        clock_end = time.time()
        log.info("Json_fetch: %.02f seconds" % (clock_end-clock_start))

        return data

    def parse_json(self, source:dict) -> dict:
        """Takes the JSON dictionary object from the fetch_json() function 
        and sorts it, returning a dictionary object with the relevant parcel info. 
        If the form of the JSON from DBSchenker changes, this function needs changing."""
        clock_start = time.time()
        data = {}

        data["receiver"] = source["second"]["location"]["consignee"]
        data["sender"] = source["second"]["location"]["shipper"]
        data["packageDetails"] = source["second"]["goods"]
        data["events"] = source["second"]["events"]
        for event in data["events"]:
            del event["shellIconName"]
        
        clock_end = time.time()
        print("Json_parse: %.02f seconds" % (clock_end-clock_start))
        
        return data


##### TEST FOR DEBUG #####
if __name__ == "__main__":
    client = SchenkerClient()
    jsonnn = client.fetch_json(URL, REF_ID)
    parsed = client.parse_json(jsonnn)
    #print(json.dumps(parsed, sort_keys=True, indent=4))
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
        client.fetch_json(URL, id)
