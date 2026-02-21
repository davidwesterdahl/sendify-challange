from playwright.sync_api import sync_playwright
import json
from bs4 import BeautifulSoup

URL = "https://www.dbschenker.com/app/tracking-public/?uiMode=details-se"
REF_ID = "1806256390"

# start the headless browser
p = sync_playwright().start()
browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

context = browser.new_context(
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


def fetch_data(url:str, ref_id) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="sv-SE",
            timezone_id="Europe/Stockholm"
        )

        page = context.new_page()

        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        page.goto(url, wait_until="networkidle")

        page.fill("input#mat-input-0", ref_id)
        page.keyboard.press("Enter")

        page.wait_for_selector("es-event-list", timeout=20_000)

        #latest_status_raw = page.locator("es-latest-status").inner_text()
        event_list_raw = page.locator("es-event-list").inner_text()
        shipment_info_raw = page.locator("es-shipment-information").inner_text()
        shipment_info_html = page.locator("es-shipment-information").inner_html()

        #print(latest_status_raw)

        main_info = {} # This is the dict that will contain all the info

        # Divide the events into dictionary items in a list
        event_list = event_list_raw.split("\n")
        event_list.pop(0)
        events = []
        for i in range(int(len(event_list)/3)):
            new_dict = {}
            new_dict["description"] = event_list[i*3]
            new_dict["time"] = event_list[i*3 + 1]
            new_dict["location"] = event_list[i*3 + 2]
            events.append(new_dict)
        main_info["events"] = events

        # Divide the shipment info
        shipment_info_list = shipment_info_raw.split("\n")
        main_info["sender"] = {
            "adress": shipment_info_list[8]
        }
        main_info["receiver"] = {
            "adress": shipment_info_list[10]
        }
        main_info["package_details"] = {
            "id": shipment_info_list[2],
            "weight": shipment_info_list[4],
            "stt-number": shipment_info_list[12],
            "product": shipment_info_list[14]
        }

        print("--------------DEBUG--------------------")
        print(json.dumps(main_info, sort_keys=True, indent=4))
        print("---------------------------------------")
        print("\n\n\n\n\n")


        soup = BeautifulSoup(shipment_info_html, "html.parser")
        
        print(soup.find("div", {"class": "col-8 col-sm-6 col-lg-10"}))
    
        browser.close()
        return main_info
    
def fetch_html(url:str, ref_id:str, time_out:int = 20_000) -> str:
    """
    Opens a new page in the headless browser, enters the parcel ID and returns the HTML containing the information.
    It has a timeout of 20 seconds by default

    :param str url: The URL for the DBSchenker public webbsite
    :param str ref_id: The 10 digit parcel ID
    :param int time_out: Number of miliseconds to wait for the webbsite to load the page with shipment information
    :return: Returns the HTML string for the es-tracking-details-se container.
    """
    

    page = context.new_page()

    "______________________TEST TEST TEST_________________"
    #page.on("request", lambda request: print(">>", request.method, request.url))
    #page.on("response", lambda response: print("<<", response.status, response.url))
    def response_test(r):
        if r.status == 200:
            if "tracking-public/shipments?query" in r.url:
                print("The first one:", r.json())

            if "tracking-public/shipments/land" in r.url:
                print("The second one:", r.url)

                
    page.on("response", response_test)
    "______________________TEST TEST TEST_________________"

    page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """)

    page.goto(url, wait_until="domcontentloaded")
    page.fill("input#mat-input-0", ref_id)
    page.keyboard.press("Enter")

    page.wait_for_selector("es-event-list", timeout=time_out)
    html = page.locator("es-tracking-details-se").inner_html()
    page.close()

    return html

def html_to_dict(html:str) -> dict:
    """Returns a dictionary object containing the parcel information
    
    :param str html: The html string from the DBschenker webbsite showing the parcel information
    :return: A dictionary object containing the relevant parcel information"""

    soup = BeautifulSoup(html, "html.parser")

    data = {}

    rows = soup.select("div.row.mb-8")
    for row in rows:
        key = row.find("div", {"class": "col-12"}).get_text(strip=True)
        value = row.find("div", {"class": "col-8"}).get_text(strip=True)
        data[key] = value
    
    event_soup = soup.find_all("div", {"class": "event-info"})
    event_list = []
    for event in event_soup:
        comment = event.find("div",{"class": "title"}).get_text()
        date = event.find("div",{"class": "date"}).get_text()
        location = event.find("div",{"class": "location"}).get_text()
        event_list.append({
            "comment": comment, 
            "date": date, 
            "location": location
            })
    data["events"] = event_list

    return data

def fetch_json(url:str, ref_id:str, time_out:int = 20_000) -> dict:
    """
    Opens a new page in the headless browser, enters the parcel ID and returns the JSON containing the information.
    It has a timeout of 20 seconds by default

    :param str url: The URL for the DBSchenker public webbsite
    :param str ref_id: The 10 digit parcel ID
    :param int time_out: Number of miliseconds to wait for the webbsite to load the page with shipment information
    :return: Returns the JSON in a python dictionary object response from the DBschenker API.
    """
    

    page = context.new_page()

    #page.on("request", lambda request: print(">>", request.method, request.url))
    #page.on("response", lambda response: print("<<", response.status, response.url))

    data = {}

    def response_test(r):
        if r.status == 200:
            if "tracking-public/shipments?query" in r.url:
                print("The first one:", r.url)
                data["first"] = r.json()

            if "tracking-public/shipments/land" in r.url:
                print("The second one:", r.url)
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

    return data

def parse_json(source:dict) -> dict:
    """Takes the JSON dictionary object from the fetch_json() function 
    and sorts it, returning a dictionary object with the relevant parcel info. 
    If the form of the JSON from DBSchenker changes, this function needs changing."""

    data = {}

    data["receiver"] = source["second"]["location"]["consignee"]
    data["sender"] = source["second"]["location"]["shipper"]
    data["packageDetails"] = source["second"]["goods"]
    data["events"] = source["second"]["events"]
    for event in data["events"]:
        del event["shellIconName"]
    

    return data

print(json.dumps(parse_json(fetch_json(URL, REF_ID)), sort_keys=True, indent=4))
#print(html_to_dict(fetch_html(URL, REF_ID)))
