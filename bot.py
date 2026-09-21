import os
import time
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

print("Create response:", response.status_code)
print("Create body:", response.text)

response.raise_for_status()

creation_id = response.json()["id"]
print("Media container created:", creation_id)

# 2. Give Instagram time to process the image
print("Waiting for Instagram to process media...")
time.sleep(10)

# 3. Check media container status
status_url = f"https://graph.instagram.com/{creation_id}"

status_response = requests.get(
    status_url,
    params={
        "fields": "status_code",
        "access_token": ACCESS_TOKEN,
    },
)

print("Status response:", status_response.status_code)
print("Status body:", status_response.text)

# 4. Publish the media
publish_url = f"https://graph.instagram.com/{IG_USER_ID}/media_publish"

publish_response = requests.post(
    publish_url,
    data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN,
    },
)

print("Publish response:", publish_response.status_code)
print("Publish body:", publish_response.text)

publish_response.raise_for_status()

print("Instagram post published successfully!")
