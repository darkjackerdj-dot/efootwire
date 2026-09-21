import json
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

MAX_RESULTS = 5
MAX_AGE_DAYS = 3

BLOCKED_PHRASES = [
    "efootball™",
    "let's play efootball",
    "online pvp setup",
    "special player list",
    "new players",
    "player review",
    "compare players",
    "featured players",
    "squad builder",
    "shortlist",
    "search players",
    "kit creator weekly",
    "youtube short",
    "top 10",
    "ballon d'or",
]

BLOCKED_WORDS = [
    "rumor",
    "rumour",
    "leak",
    "leaked",
    "unconfirmed",
]


def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc.lower()}{parsed.path.rstrip('/')}"


def is_official(url):
    host = urlparse(url).netloc.lower()
    return "konami.com" in host or "e-football.konami.net" in host


def extract_date(title):
    patterns = [
        (r"\b(\d{2}/\d{2}/\d{4})\b", "%d/%m/%Y"),
        (r"\b(\d{4}-\d{2}-\d{2})\b", "%Y-%m-%d"),
        (r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b", "%d %B %Y"),
        (r"\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b", "%d %b %Y"),
    ]

    for pattern, fmt in patterns:
        match = re.search(pattern, title, re.IGNORECASE)

        if not match:
            continue

        try:
            if "%B" in fmt or "%b" in fmt:
                value = " ".join(match.groups())
            else:
                value = match.group(1)

            return datetime.strptime(value, fmt)
        except ValueError:
            pass

    return None


def is_blocked(title):
    text = title.lower()

    if any(x in text for x in BLOCKED_PHRASES):
        return True

    if any(x in text for x in BLOCKED_WORDS):
        return True

    return False


def score(item):
    title = item.get("title", "")
    title_lower = title.lower()

    article_date = extract_date(title)

    # Automatic posting requires an explicit publication date.
    if article_date is None:
        return -1

    # If the title contains a date, enforce freshness.
    if article_date:
        age = datetime.now() - article_date

        if age < timedelta(days=0):
            age = timedelta(days=0)

        if age > timedelta(days=MAX_AGE_DAYS):
            return -1

    value = 100

    if is_official(item.get("url", "")):
        value += 50

    important = [
        "announcement",
        "maintenance",
        "live update",
        "player condition",
        "price change",
        "campaign",
        "world festival",
        "world finals",
        "gameplay",
        "version",
        "collaboration",
        "event",
        "issue",
        "unavailable",
        "suspension",
    ]

    for word in important:
        if word in title_lower:
            value += 15

    if article_date:
        age = datetime.now() - article_date

        if age <= timedelta(days=1):
            value += 30
        elif age <= timedelta(days=2):
            value += 20
        else:
            value += 10

    return value


def select_news(news):
    selected = []
    seen = set()

    for item in news:

        title = item.get("title", "").strip()

        if not title:
            continue

        if is_blocked(title):
            continue

        raw_url = item.get("url", "")

        if not raw_url:
            continue

        url = normalize_url(raw_url)

        if url in seen:
            continue

        seen.add(url)

        item_score = score(item)

        if item_score < 0:
            continue

        result = dict(item)
        result["url"] = url
        result["score"] = item_score

        if is_official(url):
            result["source"] = "KONAMI eFootball"
            result["tier"] = "official"

        selected.append(result)

    selected.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return selected[:MAX_RESULTS]


def main():

    with open("news.json", "r", encoding="utf-8") as f:
        news = json.load(f)

    selected = select_news(news)

    print()
    print("=" * 70)
    print("eFootWire FRESH NEWS QUEUE")
    print("=" * 70)

    for i, item in enumerate(selected, 1):
        print()
        print(f"{i}. [{item['score']}] {item['title']}")
        print(f"   Source : {item['source']}")
        print(f"   URL    : {item['url']}")

    print()
    print("=" * 70)
    print(f"READY TO POST: {len(selected)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
