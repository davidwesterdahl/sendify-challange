from test_schenker import fetch_html, html_to_dict
from configparser import ConfigParser
import json

config = ConfigParser()
config.read("testtestconfig.cfg")
URL = config.get("WEBBSITE", "url")

print("Welcome to the debug menu!\nPlease put in the 10 digit ID of your parcel.\nType -1 for a standard debug id\nThe process is slow...\n")
run_program = True
while run_program:
    object_id = input("Object ID: ")

    if object_id == "-1":
        object_id = "1806272330"

    elif object_id == "x":
        run_program = False

    if not int(object_id) > 1_000_000_000 and int(object_id) < 9_999_999_999:
        print("Must be an id 10 digits long")


    else:
        html = fetch_html(URL, object_id)
        dict_obj = html_to_dict(html)
        print(json.dumps(dict_obj, indent=4, sort_keys=True))


