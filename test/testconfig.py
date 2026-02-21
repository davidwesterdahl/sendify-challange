from configparser import ConfigParser

config_w = ConfigParser()

config_w["USERINFO"] = {
    "admin": "Svante",
    "password": "123"
}
config_w["WEBBSITE"] = {
    "URL": "www.hej.se"
}

with open("testconfig.cfg", "w") as f:
    config_w.write(f)

config_r = ConfigParser()
config_r.read("testconfig.cfg")
user = config_r.get("USERINFO", "admin")
print(user)

