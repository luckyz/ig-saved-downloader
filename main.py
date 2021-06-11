#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime
from instagram_private_api import Client
from pathlib import Path
import os
import re

# Credentials #################################################################
USERNAME = ""
PASSWORD = ""
###############################################################################
URL_FILE = "urls.txt"
MEDIA_FOLDER = "media"

BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = os.path.join(BASE_DIR, MEDIA_FOLDER)
URL_DIR = os.path.join(BASE_DIR, URL_FILE)


def use_cookies():
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

	return api


def create_media_folder(media_folder):
	if os.path.exists(media_folder):
		os.system("rm -rf %s" % media_folder)
		print("Deleting media folder")
	os.mkdir(media_folder)
	print("Media folder created")


def current_page(page_count):
	page_count += 1
	print(f"\nCurrent page: #{page_count}")

	return page_count


def select_user(username):
	user_dir = os.path.join(MEDIA_DIR, username)
	if not os.path.exists(user_dir):
		os.mkdir(user_dir)
	os.chdir(user_dir)


def parse_results(results, page_data):
	def detect_media_type(url):
		match = re.findall("jpg|mp4", url)
		return match[0]

	for result in results["items"]:
		user = result["media"]["user"]["username"]
		id = result["media"]["id"]

		if user not in page_data.keys():
			page_data[user] = []

		try:
			carousel_imgs = result["media"]["carousel_media"]
			# have carousel media
			for img in carousel_imgs:
				url = img["images"]["standard_resolution"]["url"]

		except KeyError as e:
			# dont have it
			url = result["media"]["images"]["standard_resolution"]["url"]

		finally:
			ext = detect_media_type(url)
			page_data[user].append((url, id, ext))

	return page_data


def accumulate(page_data, stats):
	for user in page_data.keys():
		count = len(page_data[user])
		if user in stats:
			stats[user] += count
		else:
			stats[user] = count

	return stats


def show_statistics(stats):
	print("\n=== Total media files downloaded by user ===".upper())
	for user in stats:
		print(f"  - {user}: {stats[user]}")


def download_media(datalist):
	for user in datalist:
		select_user(user)

		print("Downloading media from user [ {} ]".format(user))
		for number, urls in enumerate(datalist[user]):
			url = urls[0]
			id = urls[1]
			ext = urls[2]

			now = datetime.utcnow()

			if ext == "jpg" or ext == "png":
				type = "IMG"
			else:
				type == "VID"

			os.system(f"wget -q -c '{url}' -O '{type}_{id}.{ext}'")


def main():
	data = {}
	stats = {}
	page_count = 0

	create_media_folder(MEDIA_DIR)

	instagram = use_cookies()
	results = instagram.saved_feed()

	data = parse_results(results, data)
	next_max_id = results.get("next_max_id")
	stats = accumulate(data, stats)
	download_media(data)
	page_count = current_page(page_count)
	time.sleep(1.5)

	while next_max_id:
		results = instagram.saved_feed(max_id=next_max_id)
		response = parse_results(results, data)
		next_max_id = results.get("next_max_id")
		stats = accumulate(response, stats)
		download_media(data)

		page_count = current_page(page_count)
		time.sleep(1.5)
		data = {}

	show_statistics(stats)

	print("\nAll images has been succesfully downloaded!")


if __name__ == "__main__":
	main()
