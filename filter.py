
import json
import re
from urllib.parse import urlsplit, urlunsplit


BLOCKED_PHRASES = [
    "compare players",
    "featured players",
    "squad builder",
    "shortlist",
    "searches",
    "new players",
    "player review",
]

BLOCKED_EXACT_TITLES = {
    "efootball™",
    "efootball",
    "let's play efootball™",
    "let's play efootball",
    "online pvp setup for efootball™",
    "online pvp setup for efootball",
    "special player list",
}

NEWS_KEYWORDS = [
    "announcement",
    "update",
    "maintenance",
    "event",
    "campaign",
    "live update",
    "player condition",
    "coins",
    "price",
    "pack",
    "epic",
    "showtime",
    "legend",
    "world festival",
    "world finals",
    "gameplay",
    "version",
    "season",
    "collaboration",
    "naruto",
    "issue",
    "unavailable players",
    "player models",
    "ranking rewards",
]

ARTICLE_PATHS = [
    "/topic/news/",
    "/articles/",
    "/noticiaspes/",
    "/news/",
    "/blog/",
]


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def clean_url(url):
    parts = urlsplit(url)

    # Remove tracking query parameters
    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path.rstrip("/"),
        "",
        ""
    ))


def is_blocked_title(title):
    normalized = normalize(title)

    if normalized in BLOCKED_EXACT_TITLES:
        return True

    return any(
        phrase in normalized
        for phrase in BLOCKED_PHRASES
    )


def looks_like_article(url):
    url_lower = url.lower()

    return any(
        path in url_lower
        for path in ARTICLE_PATHS
    )


def is_news(title, url):
    normalized = normalize(title)

    if any(keyword in normalized for keyword in NEWS_KEYWORDS):
        return True

    # Article URLs can still be useful even if the title
    # doesn't contain one of our keywords.
    return looks_like_article(url)


def load_posted():
    try:
        with open("posted.json", "r", encoding="utf-8") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()


def filter_news(items):
    posted = load_posted()

    filtered = []
    seen_urls = set()

    for item in items:
        title = item.get("title", "").strip()
        raw_url = item.get("url", "").strip()

        if not title or not raw_url:
            continue

        url = clean_url(raw_url)

        if is_blocked_title(title):
            continue

        if not is_news(title, url):
            continue

        # Same URL = same story
        if url in seen_urls:
            continue

        # Already published = skip
        if url in posted:
            continue

        seen_urls.add(url)

        clean_item = dict(item)
        clean_item["url"] = url

        filtered.append(clean_item)

    return filtered


def print_news(items):
    print("\n" + "=" * 60)
    print("eFootWire CLEAN NEWS")
    print("=" * 60)

    for index, item in enumerate(items, 1):
        print(f"\n{index}. {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   Tier:   {item['tier']}")
        print(f"   URL:    {item['url']}")

    print("\n" + "=" * 60)
    print(f"CLEAN NEWS COUNT: {len(items)}")
    print("=" * 60)


if __name__ == "__main__":
    with open("news.json", "r", encoding="utf-8") as f:
        all_news = json.load(f)

    filtered = filter_news(all_news)
    print_news(filtered)
