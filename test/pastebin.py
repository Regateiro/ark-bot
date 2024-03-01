import configparser
import requests
import json

config = configparser.ConfigParser()
config.read("/home/regateiro/.config/ark-bot/config.ini")


params = {
    "api_dev_key": config['Pastebin']['ApiKey'],
    "api_paste_code": None,
    "api_paste_private": 1,
    "api_paste_name": None,
    "api_paste_expire_date": "10M",
    "api_paste_format": "ini",
    "api_option": "paste"
}

# Read configuration files
with open(config['Ark']['GameUserSettingsIni'], encoding="utf-8") as f:
    data = f.read()

# Create the pastebin
params["api_paste_name"] = "GameUserSettings.ini"
params["api_paste_code"] = data
gus_ini_url = requests.post("https://pastebin.com/api/api_post.php", data=params)


# Read configuration files
with open(config['Ark']['GameIni'], encoding="utf-8") as f:
    data = f.read()

# Create the pastebin
params["api_paste_name"] = "Game.ini"
params["api_paste_code"] = data
game_ini_url = requests.post("https://pastebin.com/api/api_post.php", data=params)

print(gus_ini_url.text)
print(game_ini_url.text)