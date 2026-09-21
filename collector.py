import json
import re
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from sources import SOURCES


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 Chrome/140 Safari/537.36"
    )
}


KEYWORDS = [
    "efootball",
    "announcement",
    "update",
    "maintenance",
    "event",
    "campaign",
    "live update",
    "player condition",
    "gameplay",
    "version",
    "world finals",
    "world festival",
    "collaboration",
    "issue",
    "coins",
]


def extract_date(soup, title):
    text = soup.get_text(" ", strip=True)

    patterns = [
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
    ]

    # Check metadata first
    for tag in soup.find_all(["meta", "time"]):
        values = [
            tag.get("datetime", ""),
            tag.get("content", ""),
            tag.get_text(" ", strip=True),
        ]

        for value in values:
            for pattern in patterns:
                match = re.search(pattern, value, re.IGNORECASE)
                if match:
                    return match.group(0)

    # Then inspect title/page text
    for source in [title, text[:5000]]:
        for pattern in patterns:
            match = re.search(pattern, source, re.IGNORECASE)
            if match:
                return match.group(0)

    return None


def collect_source(source_id, source):
    url = source["url"]

    print(f"\n[{source_id}] {source['name']}")
    print(f"URL: {url}")

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
        )

        print(f"HTTP: {response.status_code}")

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        results = []

        for link in soup.find_all("a", href=True):

            title = link.get_text(" ", strip=True)

            if not title:
                continue

            href = urljoin(url, link["href"])

            lower_title = title.lower()

            if not any(
                keyword in lower_title
                for keyword in KEYWORDS
            ):
                continue

            # Ignore obvious navigation links
            if len(title) < 8:
                continue

            item = {
                "title": title,
                "url": href,
                "source": source["name"],
                "tier": source["tier"],
            }

            article_date = extract_date(
                soup,
                title
            )

            if article_date:
                item["date"] = article_date

            results.append(item)

        return results

    except Exception as e:
        print(f"ERROR: {e}")
        return []


def main():

    all_news = []

    for source_id, source in SOURCES.items():

        items = collect_source(
            source_id,
            source
        )

        all_news.extend(items)

    # Remove exact duplicate URLs
    unique = {}
    for item in all_news:
        unique[item["url"]] = item

    all_news = list(unique.values())

    with open(
        "news.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            all_news,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print(f"Saved {len(all_news)} raw news items to news.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
