import json
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

from selector import select_news
from caption import clean_title


W, H = 1080, 1920
FPS = 30
DURATION = 8
OUT_DIR = "reels"

os.makedirs(OUT_DIR, exist_ok=True)


def font(size, bold=False):
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word

        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def make_frame(item, frame):
    img = Image.new("RGB", (W, H), (10, 12, 18))
    draw = ImageDraw.Draw(img)

    progress = frame / (FPS * DURATION)

    # Header
    draw.text(
        (70, 100),
        "eFootWire",
        font=font(72, True),
        fill=(255, 255, 255),
    )

    draw.text(
        (74, 190),
        "eFOOTBALL NEWS",
        font=font(32),
        fill=(170, 175, 185),
    )

    draw.line(
        (70, 270, 1010, 270),
        fill=(255, 255, 255),
        width=3,
    )

    title = clean_title(item["title"])

    # Remove leading "Announcements"
    if title.lower().startswith("announcements"):
        title = title[len("announcements"):].strip()

    # Category
    category = "OFFICIAL UPDATE"

    if "potw" in title.lower():
        category = "POTW UPDATE"
    elif "player condition" in title.lower():
        category = "PLAYER CONDITION"
    elif "maintenance" in title.lower():
        category = "MAINTENANCE"
    elif "campaign" in title.lower():
        category = "CAMPAIGN"

    draw.text(
        (70, 390),
        category,
        font=font(30, True),
        fill=(190, 195, 205),
    )

    # Headline
    headline_font = font(72, True)
    lines = wrap(draw, title, headline_font, 900)

    y = 500

    for line in lines[:5]:
        draw.text(
            (70, y),
            line,
            font=headline_font,
            fill=(255, 255, 255),
        )
        y += 100

    # Source box
    box_y = 1120

    draw.rounded_rectangle(
        (70, box_y, 1010, box_y + 210),
        radius=25,
        outline=(255, 255, 255),
        width=3,
    )

    draw.text(
        (105, box_y + 35),
        "SOURCE",
        font=font(27),
        fill=(160, 165, 175),
    )

    draw.text(
        (105, box_y + 85),
        item["source"],
        font=font(38, True),
        fill=(255, 255, 255),
    )

    draw.text(
        (105, box_y + 140),
        "Official details available in caption",
        font=font(25),
        fill=(160, 165, 175),
    )

    # Bottom CTA
    draw.line(
        (70, 1600, 1010, 1600),
        fill=(255, 255, 255),
        width=3,
    )

    draw.text(
        (70, 1680),
        "FOLLOW",
        font=font(28),
        fill=(160, 165, 175),
    )

    draw.text(
        (70, 1730),
        "@efootwire",
        font=font(58, True),
        fill=(255, 255, 255),
    )

    draw.text(
        (70, 1825),
        "Fast. Simple. Updated.",
        font=font(30),
        fill=(170, 175, 185),
    )

    return img


def create_reel(item, index):
    with tempfile.TemporaryDirectory() as tmp:

        for frame in range(FPS * DURATION):
            img = make_frame(item, frame)
            img.save(
                os.path.join(tmp, f"frame_{frame:05d}.jpg"),
                quality=92,
            )

        output = os.path.join(
            OUT_DIR,
            f"efootwire_reel_{index}.mp4"
        )

        subprocess.run([
            "ffmpeg",
            "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(tmp, "frame_%05d.jpg"),
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "48000",
            "-shortest",
            "-movflags", "+faststart",
            "-preset", "veryfast",
            output,
        ], check=True)

        return output


def main():
    with open("news.json", "r", encoding="utf-8") as f:
        news = json.load(f)

    selected = select_news(news)

    if not selected:
        print("No fresh news available.")
        return

    print()
    print("=" * 60)
    print("eFootWire REEL GENERATOR")
    print("=" * 60)

    for i, item in enumerate(selected, 1):
        output = create_reel(item, i)
        print(f"Created: {output}")

    print("=" * 60)


if __name__ == "__main__":
    main()
