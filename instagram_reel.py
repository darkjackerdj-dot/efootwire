import json
import os
import sys
import time

import requests


ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
USER_ID = os.environ["INSTAGRAM_USER_ID"]

GRAPH_URL = "https://graph.instagram.com"


def load_posted():
    if not os.path.exists("posted.json"):
        return []

    try:
        with open("posted.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_posted(posted):
    with open("posted.json", "w", encoding="utf-8") as f:
        json.dump(
            posted,
            f,
            indent=2,
            ensure_ascii=False,
        )


def get_selected_news():
    with open("news.json", "r", encoding="utf-8") as f:
        news = json.load(f)

    from selector import select_news

    return select_news(news)


def create_container(video_url, caption):
    url = f"{GRAPH_URL}/{USER_ID}/media"

    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    }

    response = requests.post(
        url,
        params=params,
        timeout=60,
    )

    print("Container response:", response.text)

    response.raise_for_status()

    data = response.json()

    if "id" not in data:
        raise RuntimeError(
            f"Instagram did not return a container ID: {data}"
        )

    return data["id"]


def check_container(container_id):
    url = f"{GRAPH_URL}/{container_id}"

    params = {
        "fields": "status_code,status",
        "access_token": ACCESS_TOKEN,
    }

    response = requests.get(
        url,
        params=params,
        timeout=60,
    )

    print("Container status:", response.text)

    response.raise_for_status()

    return response.json()


def publish_container(container_id):
    url = f"{GRAPH_URL}/{USER_ID}/media_publish"

    params = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }

    response = requests.post(
        url,
        params=params,
        timeout=60,
    )

    print("Publish response:", response.text)

    response.raise_for_status()

    return response.json()


def main():

    selected = get_selected_news()

    if not selected:
        print("No fresh news. Nothing to publish.")
        return

    posted = load_posted()

    posted_urls = {
        item.get("url")
        for item in posted
    }

    for index, item in enumerate(selected, 1):

        url = item["url"]

        if url in posted_urls:
            print("Already posted:", url)
            continue

        reel_file = f"reels/efootwire_reel_{index}.mp4"

        if not os.path.exists(reel_file):
            print("Missing Reel:", reel_file)
            continue

        print()
        print("=" * 60)
        print("READY TO PUBLISH")
        print(item["title"])
        print("=" * 60)

        print()
        print("IMPORTANT:")
        print("Instagram needs a publicly accessible video URL.")
        print("Local file:", reel_file)
        print()
        print("Publisher stopped safely before creating an Instagram container.")
        print("No Instagram post was created.")

        # Intentionally disabled until the public video hosting
        # method is configured.
        sys.exit(0)


if __name__ == "__main__":
    main()
