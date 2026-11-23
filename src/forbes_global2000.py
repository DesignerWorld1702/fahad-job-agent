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
    # Also collect common JSON company-name fields when present.
    for m in re.finditer(r'"(?:organizationName|companyName|company_name|name)"\s*:\s*"([^"]{2,120})"', html):
        name = re.sub(r'\\u[0-9a-fA-F]{4}', ' ', m.group(1)).strip()
        if 2 <= len(name) <= 120 and not any(x in name.lower() for x in ("global 2000","forbes")):
            found.setdefault(name, "")
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
            return
        raise

    now = datetime.now(timezone.utc)
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {
        "cycle": 1, "format_index": 0, "last_company_index": -1, "last_applied_at": {}
    }
    # A company is eligible again after 10 days. The list is traversed in order;
    # after the last company, the next pass increments the application-format cycle.
    last_index = int(state.get("last_company_index", -1))
    eligible = []
    cooldown = state.setdefault("last_applied_at", {})
    for idx, row in enumerate(rows):
        last = cooldown.get(row["company"])
        if not last or now - datetime.fromisoformat(last) >= timedelta(days=10):
            eligible.append((idx, row))
    if eligible:
        idx, active = eligible[0]
        state["last_company_index"] = idx
        state["active_company"] = active["company"]
        state["active_forbes_url"] = active["forbes_url"]
    state["source_url"] = URL
    state["synced_at"] = now.isoformat()
    state["companies_count"] = len(rows)
    TARGETS_PATH.write_text(json.dumps({"source_url":URL,"synced_at":now.isoformat(),"companies":rows}, indent=2, ensure_ascii=False))
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
    print(f"Forbes Global 2000 sync: {len(rows)} companies. Active target: {state.get('active_company','none')}. Format cycle: {state.get('format_index',0)+1}")

if __name__ == "__main__":
    main()
