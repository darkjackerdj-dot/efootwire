import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse


SOURCE_SCORE = {
    "official": 100,
    "established": 70,
    "additional": 40,
}

HIGH_VALUE_KEYWORDS = [
    "announcement",
    "maintenance",
    "live update",
    "player condition",
    "price change",
    "campaign",
    "world festival",
    "world finals",
    "version",
    "gameplay",
    "event",
    "collaboration",
]

LOW_VALUE_KEYWORDS = [
    "player review",
    "top 10",
    "rankings",
    "kit creator weekly",
    "youtube",
]

RUMOUR_KEYWORDS = [
    "rumor",
    "rumour",
    "leak",
    "leaked",
    "unconfirmed",
]


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def get_date_from_title(title):
    patterns = [
        r"(\d{2})/(\d{2})/(\d{4})",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"sep(?:tember)?\.?\s+(\d{1,2}),?\s+(\d{4})?",
    ]

    title = normalize(title)

    for pattern in patterns:
        match = re.search(pattern, title)

        if not match:
            continue

        try:
            groups = match.groups()

            if "/" in pattern:
                day, month, year = groups
                return datetime(int(year), int(month), int(day))

            if "-" in pattern:
                year, month, day = groups
                return datetime(int(year), int(month), int(day))

            # September 21, 2026
            month = 9
            day = int(groups[0])
            year = int(groups[1]) if groups[1] else datetime.now().year

            return datetime(year, month, day)

        except ValueError:
            pass

    return None


def score_item(item):
    title = normalize(item.get("title", ""))
    source = item.get("tier", "additional")

    score = SOURCE_SCORE.get(source, 30)

    # High-value topics
    for keyword in HIGH_VALUE_KEYWORDS:
        if keyword in title:
            score += 20

    # Lower-value content
    for keyword in LOW_VALUE_KEYWORDS:
        if keyword in title:
            score -= 25

    # Rumours should not become normal confirmed news
    for keyword in RUMOUR_KEYWORDS:
        if keyword in title:
            score -= 60

    # Freshness
    article_date = get_date_from_title(title)

    if article_date:
        age = datetime.now() - article_date

        if age <= timedelta(days=1):
            score += 30
        elif age <= timedelta(days=3):
            score += 15
        elif age > timedelta(days=7):
            score -= 50

    return score


def rank_news(items):
    ranked = []

    for item in items:
        score = score_item(item)

        item = dict(item)
        item["score"] = score

        # Only keep reasonable candidates
        if score >= 70:
            ranked.append(item)

    ranked.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return ranked


def print_ranked(items):
    print("\n" + "=" * 60)
    print("eFootWire PRIORITY NEWS")
    print("=" * 60)

    for index, item in enumerate(items, 1):
        print(f"\n{index}. [{item['score']}] {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   Tier:   {item['tier']}")
        print(f"   URL:    {item['url']}")

    print("\n" + "=" * 60)
    print(f"ELIGIBLE NEWS: {len(items)}")
    print("=" * 60)


if __name__ == "__main__":
    with open("news.json", "r", encoding="utf-8") as f:
        news = json.load(f)

    ranked = rank_news(news)
    print_ranked(ranked)
