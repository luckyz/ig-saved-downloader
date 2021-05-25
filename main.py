import json
import time
from instagram_private_api import Client, ClientCompatPatch
from pathlib import Path
import os

# Credentials #################################################################
USERNAME = ""
PASSWORD = ""
###############################################################################
URL_FILE = "urls.txt"
IMG_FOLDER = "img"

# Bootstrap code
cookies = None
try:
  with open("cookies.pkl", "rb") as read_cookies:
    cookies = read_cookies.read()
except:
  pass

if cookies is None:
  print("Not using cookies")
  api = Client(USERNAME, PASSWORD, auto_patch=True)
else:
  print("Using cookies")
  api = Client(USERNAME, PASSWORD, cookie=cookies, auto_patch=True)

cookies = api.cookie_jar.dump()
with open("cookies.pkl", "wb") as save_cookies:
    save_cookies.write(cookies)


photo_urls = []

def parse_results(results):
  for result in results["items"]:
    try:
      carousel_imgs = result["media"]["carousel_media"]
      # print("have carousel media")
      for img in carousel_imgs:
        photo_urls.append(img["images"]["standard_resolution"]["url"])
    except KeyError as e:
      # print("dont have it")
      photo_urls.append(result["media"]["images"]["standard_resolution"]["url"])

results = api.saved_feed()
# print(json.dumps(results["items"]))
parse_results(results)
next_max_id = results.get("next_max_id")

print("Sleeping for 1.5 seconds, next max id is: " + str(next_max_id))
time.sleep(1.5)

while next_max_id:
  results = api.saved_feed(max_id=next_max_id)
  parse_results(results)
  next_max_id = results.get("next_max_id")

  with open(URL_FILE, "a") as myfile:
    for url in photo_urls:
      myfile.write(url + "\n")
  photo_urls = []

  print("Sleeping for 1.5 seconds, next max id is: " + str(next_max_id))
  time.sleep(1.5)

BASE_DIR = Path(__file__).resolve().parent
FULL_URL_PATH = os.path.join(BASE_DIR, URL_FILE)

# create images folder
if not os.path.exists(IMG_FOLDER):
    os.mkdir(IMG_FOLDER)

os.chdir(IMG_FOLDER)

stream = os.popen("wget -i {}".format(FULL_URL_PATH))
output = stream.read()
print(output)

print("All images has been succesfully downloaded!")
