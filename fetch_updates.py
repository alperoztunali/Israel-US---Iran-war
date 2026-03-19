import os
import json
import hashlib
import time
from datetime import datetime, timezone
import feedparser
import anthropic

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
    "missile", "drone", "strike", "military", "attack", "casualties",
    "sanction", "nuclear", "strait of hormuz", "red sea", "lebanon",
    "hezbollah", "syria", "iraq", "yemen", "regional", "tensions",
    "persian gulf", "idf", "revolution guard",
]

ENTRIES_FILE = "entries.json"
SEEN_FILE = "seen_ids.json"

SYSTEM_PROMPT = """You are a strict military intelligence data extractor.
Extract ONLY factual data. No analysis, no opinion, no commentary.
Rules:
- Use EXACT wording from source for the excerpt field.
- If multiple distinct events exist, return multiple objects.
- source: use the provided source name exactly
- category: ONE of: Airstrike, Statement, Casualties, Movement, Missile/Drone, Naval, Diplomatic, Other
- date: ISO 8601 format YYYY-MM-DDTHH:MM
- location: city/region/country or Unknown
- headline: max 12 words, factual only
- relevance: true if related to Iran/regional tensions/Middle East military activity

Return ONLY a JSON array, no markdown, no explanation:
[{"source":"...","date":"...","category":"...","location":"...","excerpt":"...","headline":"...","relevance":true}]
"""

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
                    "summary": summary[:800],
                    "link": link,
                    "published": pub,
                })
        return items
    except Exception as e:
        print(f"Failed to fetch {source['name']}: {e}")
        return []

def extract_with_claude(items, client):
    if not items:
        return []
    batch_text = ""
    for i, item in enumerate(items):
        batch_text += f"\n--- ITEM {i+1} | SOURCE: {item['source']} | DATE: {item['published']} ---\n"
        batch_text += f"HEADLINE: {item['title']}\n"
        batch_text += f"BODY: {item['summary']}\n"
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": batch_text}],
        )
        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        return [e for e in parsed if e.get("relevance", True)]
    except Exception as e:
        print(f"Claude extraction error: {e}")
        return []

def run():
    print(f"IRAN TRACKER - RUN AT {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=api_key)
    entries = load_json(ENTRIES_FILE, [])
    seen_ids = set(load_json(SEEN_FILE, []))
    new_items_total = []
    for source in SOURCES:
        print(f"Fetching {source['name']}...")
        items = fetch_feed(source)
        new_items = [i for i in items if entry_id(i["link"], i["title"]) not in seen_ids]
        print(f"  {len(new_items)} new items")
        new_items_total.extend(new_items)
        for i in new_items:
            seen_ids.add(entry_id(i["link"], i["title"]))
        time.sleep(1)
    if not new_items_total:
        print("No new relevant items this run.")
        save_json(SEEN_FILE, list(seen_ids))
        return
    print(f"Sending {len(new_items_total)} items to Claude...")
    extracted = []
    for i in range(0, len(new_items_total), 10):
        batch = new_items_total[i:i+10]
        result = extract_with_claude(batch, client)
        extracted.extend(result)
        time.sleep(2)
    timestamped = []
    for idx, e in enumerate(extracted):
        e["id"] = hashlib.md5(f"{e.get('date','')}{e.get('headline','')}{idx}".encode()).hexdigest()[:12]
        e["addedAt"] = datetime.now(timezone.utc).isoformat()
        timestamped.append(e)
    all_entries = timestamped + entries
    all_entries = all_entries[:500]
    save_json(ENTRIES_FILE, all_entries)
    save_json(SEEN_FILE, list(seen_ids))
    print(f"Done. {len(timestamped)} new entries added. Total: {len(all_entries)}")

if __name__ == "__main__":
    run()
