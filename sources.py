SOURCES = {
    "konami": {
        "name": "KONAMI eFootball",
        "url": "https://www.konami.com/efootball/en/",
        "tier": "official",
    },

    "efhub": {
        "name": "eFootballHub",
        "url": "https://efootballhub.net/",
        "tier": "established",
    },

    "pesmaster": {
        "name": "PES Master",
        "url": "https://www.pesmaster.com/news/",
        "tier": "established",
    },

    "pesoccerworld": {
        "name": "PeSoccerWorld",
        "url": "https://www.pesoccerworld.com/noticias-efootball2026.html?lang=en",
        "tier": "additional",
    },
}


if __name__ == "__main__":
    print("eFootWire Sources")
    print("=" * 40)

    for source_id, source in SOURCES.items():
        print(f"{source_id}: {source['name']} [{source['tier']}]")
        print(f"  {source['url']}")
