import os
import json
import time
import requests

GRAPH_VERSION = "v24.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
INSTAGRAM_USER_ID = os.environ["INSTAGRAM_USER_ID"]
REPOSITORY = os.environ["GITHUB_REPOSITORY"]

POSTED_FILE = "posted.json"
NEWS_FILE = "news.json"


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


posted = load_json(POSTED_FILE, [])
news = load_json(NEWS_FILE, [])

if not news:
    print("No news found.")
    raise SystemExit(0)

# Find first news item that has not already been posted
selected = None

for item in news:
    key = item.get("url") or item.get("title")

    if key and key not in posted:
        selected = item
        break

if not selected:
    print("No new news to publish.")
    raise SystemExit(0)

title = selected.get("title", "eFootball News")
source_url = selected.get("url", "")

# Match generated Reel with selected news item
index = news.index(selected) + 1

video_url = (
    f"https://{REPOSITORY.split('/')[0]}.github.io/"
    f"{REPOSITORY.split('/')[1]}/reels/efootwire_reel_{index}.mp4"
)

caption = (
    f"⚽ {title}\n\n"
    f"🔎 Source: {source_url}\n\n"
    f"Follow @efootwire for eFootball news & updates.\n\n"
    f"#eFootball #eFootball2026 #KONAMI #PES #eFootWire"
)

print("Selected news:")
print(title)
print()
print("Video URL:")
print(video_url)


# ---------------------------------------------------------
# 1. Create Instagram Reel container
# ---------------------------------------------------------

create_url = f"{GRAPH_URL}/{INSTAGRAM_USER_ID}/media"

create_data = {
    "media_type": "REELS",
    "video_url": video_url,
    "caption": caption,
    "access_token": ACCESS_TOKEN,
}

response = requests.post(create_url, data=create_data, timeout=60)

print("Container response:", response.text)

if response.status_code != 200:
    raise SystemExit("Failed to create Instagram media container.")

container = response.json()
container_id = container.get("id")

if not container_id:
    raise SystemExit("Instagram did not return a container ID.")

print("Container ID:", container_id)


# ---------------------------------------------------------
# 2. Wait for Instagram to process the video
# ---------------------------------------------------------

status_url = f"{GRAPH_URL}/{container_id}"

for attempt in range(20):
    time.sleep(15)

    status_response = requests.get(
        status_url,
        params={
            "fields": "status_code,status",
            "access_token": ACCESS_TOKEN,
        },
        timeout=60,
    )

    print("Processing:", status_response.text)

    if status_response.status_code != 200:
        raise SystemExit("Failed to check container status.")

    status_data = status_response.json()
    status_code = status_data.get("status_code")

    if status_code == "FINISHED":
        break

    if status_code in ("ERROR", "EXPIRED"):
        raise SystemExit(f"Instagram processing failed: {status_data}")

else:
    raise SystemExit("Instagram video processing timed out.")


# ---------------------------------------------------------
# 3. Publish Reel
# ---------------------------------------------------------

publish_url = f"{GRAPH_URL}/{INSTAGRAM_USER_ID}/media_publish"

publish_response = requests.post(
    publish_url,
    data={
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    },
    timeout=60,
)

print("Publish response:", publish_response.text)

if publish_response.status_code != 200:
    raise SystemExit("Failed to publish Reel.")

publish_data = publish_response.json()
media_id = publish_data.get("id")

if not media_id:
    raise SystemExit("Instagram did not return a published media ID.")


# ---------------------------------------------------------
# 4. Save posted news
# ---------------------------------------------------------

key = selected.get("url") or selected.get("title")

posted.append(key)
save_json(POSTED_FILE, posted)

print()
print("======================================")
print("✅ INSTAGRAM REEL PUBLISHED")
print("Media ID:", media_id)
print("News:", title)
print("======================================")
