import json
import os
import re
import textwrap

from PIL import Image, ImageDraw, ImageFont

from selector import select_news
from caption import clean_title


WIDTH = 1080
HEIGHT = 1080

OUTPUT_DIR = "generated"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]

    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def draw_wrapped(draw, text, font, x, y, max_width, spacing=12):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word

        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    for line in lines:
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255),
        )

        box = draw.textbbox((x, y), line, font=font)
        y = box[3] + spacing

    return y


def create_image(item, index):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (12, 14, 20),
    )

    draw = ImageDraw.Draw(image)

    # Header
    logo_font = get_font(54, True)
    small_font = get_font(28, False)
    headline_font = get_font(62, True)
    body_font = get_font(32, False)

    draw.text(
        (70, 55),
        "eFootWire",
        font=logo_font,
        fill=(255, 255, 255),
    )

    draw.text(
        (72, 125),
        "eFOOTBALL NEWS",
        font=small_font,
        fill=(180, 185, 195),
    )

    # Divider
    draw.rectangle(
        (70, 175, 1010, 178),
        fill=(255, 255, 255),
    )

    title = clean_title(item["title"])

    # Remove leading announcement wording
    title = re.sub(
        r"^Announcements\s*",
        "",
        title,
        flags=re.IGNORECASE,
    )

    # Headline
    y = 245

    y = draw_wrapped(
        draw,
        title,
        headline_font,
        70,
        y,
        900,
        spacing=18,
    )

    # Source
    source_y = 650

    draw.text(
        (70, source_y),
        "SOURCE",
        font=small_font,
        fill=(160, 165, 175),
    )

    draw.text(
        (70, source_y + 42),
        item["source"],
        font=body_font,
        fill=(255, 255, 255),
    )

    # Date
    draw.text(
        (70, 770),
        "LATEST UPDATE",
        font=small_font,
        fill=(160, 165, 175),
    )

    draw.text(
        (70, 812),
        "eFootball • Official Update",
        font=body_font,
        fill=(255, 255, 255),
    )

    # Footer
    draw.rectangle(
        (70, 945, 1010, 948),
        fill=(255, 255, 255),
    )

    draw.text(
        (70, 970),
        "@efootwire",
        font=small_font,
        fill=(255, 255, 255),
    )

    filename = os.path.join(
        OUTPUT_DIR,
        f"efootwire_{index}.jpg",
    )

    image.save(
        filename,
        "JPEG",
        quality=95,
    )

    return filename


def main():

    with open("news.json", "r", encoding="utf-8") as f:
        news = json.load(f)

    selected = select_news(news)

    if not selected:
        print("No fresh news available.")
        return

    print()
    print("=" * 60)
    print("eFootWire IMAGE GENERATOR")
    print("=" * 60)

    for i, item in enumerate(selected, 1):

        filename = create_image(
            item,
            i,
        )

        print(f"Created: {filename}")

    print("=" * 60)


if __name__ == "__main__":
    main()
