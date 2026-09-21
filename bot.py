import os
import requests

ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
IG_USER_ID = os.environ["INSTAGRAM_USER_ID"]

IMAGE_URL = "https://picsum.photos/1080/1080"

caption = """⚽ eFootWire Test Post

eFootball News & Updates
Fast. Simple. Updated.

#eFootball #eFootballNews #eFootWire
"""

# 1. Create Instagram media container
create_url = f"https://graph.instagram.com/{IG_USER_ID}/media"

response = requests.post(
    create_url,
    data={
        "image_url": IMAGE_URL,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    },
)

response.raise_for_status()
creation_id = response.json()["id"]

print("Media container created:", creation_id)

# 2. Publish the media
publish_url = f"https://graph.instagram.com/{IG_USER_ID}/media_publish"

response = requests.post(
    publish_url,
    data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    },
)

response.raise_for_status()

print("Instagram post published successfully!")
print(response.json())
