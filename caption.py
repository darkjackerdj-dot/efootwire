import json
import re


def clean_title(title):
    # Remove leading dates
    title = re.sub(
        r"^\s*\d{2}/\d{2}/\d{4}\s*",
        "",
        title
    )

    # Remove common KONAMI suffix
    title = re.sub(
        r"\s+KONAMI\s*-\s*\d{1,2}\s+\w+\s+\d{4}\s*$",
        "",
        title,
        flags=re.IGNORECASE
    )

    title = re.sub(
        r"\s+KONAMI\s*$",
        "",
        title,
        flags=re.IGNORECASE
    )

    return title.strip()


def extract_period(title):
    match = re.search(
        r"(\d{1,2}/\d{2}/\d{4})\s*[–-]\s*(\d{1,2}/\d{2}/\d{4})",
        title
    )

    if match:
        return f"{match.group(1)} – {match.group(2)}"

    match = re.search(
        r"(\d{2}/\d{2}/\d{4})\s*[–-]\s*(\d{2}/\d{2}/\d{4})",
        title
    )

    if match:
        return f"{match.group(1)} – {match.group(2)}"

    return None


def make_headline(title):
    clean = clean_title(title)

    lower = clean.lower()

    if "potw" in lower:
        return "🎯 POTW Availability Announced"

    if "player condition" in lower:
        return "🎮 Player Condition Update"

    if "maintenance" in lower:
        return "🛠️ Maintenance Update"

    if "live update" in lower:
        return "🔄 Live Update Notice"

    if "price change" in lower:
        return "💰 eFootball Coins Price Update"

    if "campaign" in lower:
        return "🔥 New Campaign Announced"

    if "world finals" in lower:
        return "🏆 eFootball World Finals Update"

    if "world festival" in lower:
        return "🌍 eFootball World Festival Update"

    return f"⚡ {clean}"


def make_body(title):
    clean = clean_title(title)
    lower = clean.lower()

    if "potw" in lower:
        return (
            "KONAMI has announced the upcoming POTW "
            "availability period in eFootball."
        )

    if "player condition" in lower:
        return (
            "KONAMI has published the upcoming "
            "Player Condition schedule for eFootball."
        )

    if "maintenance" in lower:
        return (
            "KONAMI has announced an upcoming "
            "maintenance period for eFootball."
        )

    if "live update" in lower:
        return (
            "KONAMI has published an update regarding "
            "the latest eFootball Live Update."
        )

    return (
        "KONAMI has published a new update regarding "
        "eFootball."
    )


def make_caption(item):

    title = item["title"]
    source = item["source"]
    url = item["url"]

    headline = make_headline(title)
    body = make_body(title)
    period = extract_period(title)

    caption = "⚡ eFootWire UPDATE\n\n"
    caption += f"{headline}\n\n"

    if period:
        caption += f"📅 {period}\n\n"

    caption += f"{body}\n\n"

    caption += f"📌 Source: {source}\n"
    caption += f"🔗 Official details:\n{url}\n\n"

    caption += (
        "Follow @efootwire for the latest "
        "eFootball updates.\n\n"
    )

    caption += (
        "#eFootball #eFootball2026 "
        "#eFootballNews #eFootballUpdate #KONAMI"
    )

    if "potw" in title.lower():
        caption += " #POTW"

    return caption


def main():

    with open("news.json", "r", encoding="utf-8") as f:
        news = json.load(f)

    from selector import select_news

    selected = select_news(news)

    if not selected:
        print("No fresh news found.")
        return

    for i, item in enumerate(selected, 1):

        print()
        print("=" * 70)
        print(f"eFootWire CLEAN CAPTION {i}")
        print("=" * 70)

        print(make_caption(item))


if __name__ == "__main__":
    main()
