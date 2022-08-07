from instagrapi import Client
import os
from getpass import getpass
import subprocess
import time

INSTAGRAM_USER = ""
INSTAGRAM_PASSWORD = ""
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = "cookies.json"
SETTINGS_DIR = os.path.join(BASE_DIR, SETTINGS_FILE)
MEDIA_FOLDER = "media"
MEDIA_DIR = os.path.join(BASE_DIR, MEDIA_FOLDER)

new_folders = []
downloaded_media = {}

cl = Client()

def use_cookies(messages=True):
    if messages:
        print("\n[+] Instagram Saved Downloader started...")

    if os.path.exists(SETTINGS_DIR):
        cl.load_settings(SETTINGS_DIR)
        cl.login(INSTAGRAM_USER, INSTAGRAM_PASSWORD)
        cookies = True
    else:
        print("-> Enter your credentials")
        os.environ["INSTAGRAM_USER"] = input("Username: ")
        os.environ["INSTAGRAM_PASSWORD"] = getpass()
        cl.login(os.getenv("INSTAGRAM_USER"), os.getenv("INSTAGRAM_PASSWORD"))
        cl.dump_settings(SETTINGS_DIR)
        cookies = False
    
    if messages:
        if cookies:
            print("- Using cookies")
        else:
            print("- Not using cookies")

def runcmd(cmd, verbose = False, *args, **kwargs):
    process = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True
    )

    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    pass

def get_media_type(resource):
    MEDIA_TYPES = {
        1: "photo",
        2: "video",
        8: "album",
    }
    return MEDIA_TYPES[resource]

def get_extension(media_type):
    return ".png" if media_type == "photo" else ".mp4"

def handle_folders(username, messages=False):
    new_path = os.path.join(MEDIA_DIR, username)
    if os.path.exists(MEDIA_DIR):
        if messages:
            print("- Media folder found\n")
        folders_list = os.listdir(MEDIA_DIR)
        if not username in folders_list:
            os.mkdir(new_path)
            print(f"- Folder created: [ {username} ]")
            new_folders.append(username)

    else:
        os.mkdir(MEDIA_DIR)
        os.mkdir(new_path)

    os.chdir(new_path)
    try:
        downloaded_media[username] += 1
    except:
        downloaded_media[username] = 1

def download_media(media):
    media_type = get_media_type(media.media_type)
    if media_type == "album":
        cl.album_download(media.pk)
    elif media_type == "photo":
        cl.photo_download(media.pk)
    elif media_type == "video":
        cl.video_download(media.pk)

def show_statistics():
    def remove_chars(var):
        return str(var).replace("[", "").replace("]", "").replace("'", "")

    print(f"\n- {len(new_folders)} new folders: {remove_chars(new_folders)}")

    keys = [key for key in downloaded_media.keys()]
    values = sum([value for value in downloaded_media.values()])
    print(f"- {values} files has been downloaded from: {remove_chars(keys)}")

def main():
    use_cookies()

    collection = cl.collection_medias("All Posts", 0)
    username = collection[0].user.username

    print(f"\n- {len(collection)} posts found")

    handle_folders(username, True)
    download_media(collection[0])
    cl.media_unsave(collection[0].id)

    collection.pop(0)

    count = 0

    for index, media in enumerate(collection):
        username = media.user.username
        handle_folders(username)
        download_media(media)
        cl.media_unsave(media.id)

        count += 1
        if count == 21:
            print(f"\nWaiting 5 minutes to prevent a ban\n")
            time.sleep(60 * 5) # wait 5 minutes

    show_statistics()


if "__main__" == __name__:
    main()
