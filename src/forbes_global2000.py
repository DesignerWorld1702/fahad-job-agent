import json, re, urllib.request
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
URL = "https://www.forbes.com/lists/global2000/"
STATE_PATH = DATA / "forbes_state.json"
TARGETS_PATH = DATA / "forbes_targets.json"

def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent":"Mozilla/5.0 (compatible; FahadJobAgent/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def parse(html):
    found = {}
    # Forbes company profile links are a useful stable fallback even if the page's
    # client-side JSON changes.
    for m in re.finditer(r'https?://(?:www\.)?forbes\.com/companies/([a-z0-9-]+)[^"<> ]*', html, re.I):
        slug = m.group(1).lower()
        found.setdefault(slug.replace("-", " ").title(), f"https://www.forbes.com/companies/{slug}/")
    # Do not scrape generic JSON "name" fields: they include people,
    # page labels and placeholders (e.g. "Andrea Murphy", "city", "country").
    # Only actual Forbes company-profile URLs are accepted as targets.
    invalid_slugs = {"city", "country", "global-2000", "global2000", "forbes"}
    found = {name: url for name, url in found.items()
             if name.lower().replace(" ", "-") not in invalid_slugs
             and url.startswith("https://www.forbes.com/companies/")}
    rows = [{"rank": i+1, "company": n, "forbes_url": u} for i,(n,u) in enumerate(found.items())]
    return rows

def main():
    try:
        html = fetch()
        rows = parse(html)
        if len(rows) < 50:
            raise RuntimeError(f"Forbes page parsing produced only {len(rows)} companies")
    except Exception as e:
        print("Forbes sync failed:", e)
        if TARGETS_PATH.exists():
            print("Keeping the last successful Forbes target list.")
        else:
            print("No cached Forbes list is available; continuing without Forbes targets.")
        return

    now = datetime.now(timezone.utc)
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    cycle_start = datetime.fromisoformat(state["cycle_start"]) if state.get("cycle_start") else now
    elapsed_days = max(0, (now - cycle_start).days)
    cycle_number = elapsed_days // 10
    index = cycle_number % len(rows)
    format_index = cycle_number % 3

    active = rows[index]
    state.update({
        "cycle": cycle_number + 1,
        "format_index": format_index,
        "active_company_index": index,
        "active_company": active["company"],
        "active_forbes_url": active["forbes_url"],
        "cycle_start": cycle_start.isoformat(),
        "source_url": URL,
        "synced_at": now.isoformat(),
        "companies_count": len(rows),
        "application_rule": "Each Forbes company is the active target for 10 days; after the full list is traversed, the application-format cycle rotates."
    })
    TARGETS_PATH.write_text(
        json.dumps({"source_url":URL,"synced_at":now.isoformat(),"companies":rows}, indent=2, ensure_ascii=False)
    )
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"Forbes Global 2000 sync: {len(rows)} companies. Active target: {active['company']} (index {index}). Format cycle: {format_index+1}.")

if __name__ == "__main__":
    main()
