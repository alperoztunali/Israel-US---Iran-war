import json
import hashlib
import time
from datetime import datetime, timezone
import feedparser

SOURCES = [
    {"name": "CENTCOM", "url": "https://www.centcom.mil/RSS/"},
    {"name": "IDF", "url": "https://www.idf.il/en/rss/"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "PressTV", "url": "https://www.presstv.ir/rss.xml"},
    {"name": "Tasnim News", "url": "https://www.tasnimnews.com/en/rss/feed/0/8/0"},
    {"name": "Gulf News", "url": "https://gulfnews.com/rss/world"},
    {"name": "Arab News", "url": "https://www.arabnews.com/rss.xml"},
    {"name": "CGTN Europe", "url": "https://www.cgtn.com/subscribe/rss/section/europe.do"},
    {"name": "WAM UAE", "url": "https://wam.ae/en/feeds/rss"},
]

KEYWORDS = [
    "iran", "irgc", "israel", "houthi", "gaza", "centcom", "airstrike",
    "missile", "drone", "dron", "rocket", "ballistic", "intercept",
    "strike", "military", "attack", "casualties", "killed", "wounded",
    "sanction", "nuclear", "strait of hormuz", "red sea", "lebanon",
    "hezbollah", "syria", "iraq", "yemen", "tensions", "persian gulf",
    "idf", "revolution guard", "uae", "united arab emirates", "dubai",
    "abu dhabi", "ksa", "saudi arabia", "riyadh", "oman", "muscat",
    "kuwait", "bahrain", "manama", "qatar", "doha", "jerusalem",
    "tel aviv", "haifa", "baghdad", "damascus", "beirut", "sanaa",
    "tehran", "natanz", "isfahan", "hypersonic", "cruise missile",
    "air defense", "iron dome", "patriot", "warplane", "fighter jet",
]

CATEGORY_KEYWORDS = {
    "Airstrike": ["airstrike", "air strike", "bombing", "bomb", "warplane", "jet", "f-35", "f35", "fighter"],
    "Missile/Drone": ["missile", "drone", "dron", "rocket", "ballistic", "cruise", "uav", "projectile", "hypersonic", "intercept"],
    "Casualties": ["killed", "dead", "wounded", "casualties", "deaths", "injured", "fatalities", "martyred"],
    "Naval": ["naval", "warship", "destroyer", "carrier", "fleet", "vessel", "ship", "tanker", "frigate"],
    "Movement": ["deployed", "troops", "forces", "convoy", "mobilized", "advancing", "withdrawal", "reinforcement"],
    "Diplomatic": ["ceasefire", "talks", "negotiate", "sanctions", "diplomat", "agreement", "deal", "summit", "envoy"],
    "Statement": ["statement", "announced", "declared", "warned", "said", "called", "urged", "confirmed"],
}

ENTRIES_FILE = "entries.json"
SEEN_FILE = "seen_ids.json"


def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def entry_id(url, title):
    return hashlib.md5(f"{url}{title}".encode()).hexdigest()


def is_relevant(title, summary):
    text = (title + " " + summary).lower()
    return any(k in text for k in KEYWORDS)


def guess_category(title, summary):
    text = (title + " " + summary).lower()
    for category, keys in CATEGORY_KEYWORDS.items():
        if any(k in text for k in keys):
            return category
    return "Other"


def guess_location(title, summary):
    text = (title + " " + summary).lower()
    locations = [
        "tehran", "iran", "israel", "gaza", "lebanon", "syria", "iraq",
        "yemen", "saudi arabia", "jordan", "egypt", "qatar", "doha",
        "dubai", "abu dhabi", "uae", "united arab emirates",
        "strait of hormuz", "red sea", "persian gulf", "beirut",
        "damascus", "baghdad", "sanaa", "riyadh", "jerusalem",
        "tel aviv", "haifa", "natanz", "isfahan", "oman", "muscat",
        "bahrain", "manama", "kuwait", "kuwait city",
    ]
    for loc in locations:
        if loc in text:
            return loc.title()
    return "Unknown"


def clean_summary(summary):
    import re
    clean = re.sub(r"<[^>]+>", "", summary)
    clean = clean.strip()
    return clean[:300]


def fetch_feed(source):
    try:
        feed = feedparser.parse(source["url"])
        items = []
        for entry in feed.entries[:20]:
            title = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "")
            link = getattr(entry, "link", "")
            pub = getattr(entry, "published", "") or getattr(entry, "updated", "")
            if is_relevant(title, summary):
                items.append({
                    "source": source["name"],
                    "title": title,
                    "summary": clean_summary(summary),
                    "link": link,
                    "published": pub,
                })
        return items
    except Exception as e:
        print(f"Failed to fetch {source['name']}: {e}")
        return []


def parse_date(pub_string):
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(pub_string)
        return dt.strftime("%Y-%m-%dT%H:%M")
    except Exception:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")


def run():
    print(f"IRAN TRACKER - RUN AT {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    entries = load_json(ENTRIES_FILE, [])
    seen_ids = set(load_json(SEEN_FILE, []))

    new_entries = []

    for source in SOURCES:
        print(f"Fetching {source['name']}...")
        items = fetch_feed(source)
        count = 0
        for item in items:
            eid = entry_id(item["link"], item["title"])
            if eid in seen_ids:
                continue
            seen_ids.add(eid)
            entry = {
                "id": eid[:12],
                "source": item["source"],
                "date": parse_date(item["published"]),
                "headline": item["title"][:100],
                "excerpt": item["summary"],
                "category": guess_category(item["title"], item["summary"]),
                "location": guess_location(item["title"], item["summary"]),
                "addedAt": datetime.now(timezone.utc).isoformat(),
                "link": item["link"],
            }
            new_entries.append(entry)
            count += 1
        print(f"  {count} new entries")
        time.sleep(1)

    if not new_entries:
        print("No new items this run.")
        save_json(SEEN_FILE, list(seen_ids))
        return

    all_entries = new_entries + entries
    all_entries = all_entries[:500]

    save_json(ENTRIES_FILE, all_entries)
    save_json(SEEN_FILE, list(seen_ids))
    print(f"Done. {len(new_entries)} new entries added. Total: {len(all_entries)}")


if __name__ == "__main__":
    run()
