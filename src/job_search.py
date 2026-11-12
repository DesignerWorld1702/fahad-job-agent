import json, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT=Path(__file__).resolve().parents[1]
PREF=json.loads((ROOT/"config/job_preferences.json").read_text())
from job_matcher import score_job

RECENT_DAYS=20

def google_news_rss(query):
    url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":query,"hl":"en-PK","gl":"PK","ceid":"PK:en"})
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return r.read()

def parse_rss(data):
    root=ET.fromstring(data)
    rows=[]
    for item in root.findall(".//item"):
        rows.append({
            "title":item.findtext("title","").strip(),
            "url":item.findtext("link","").strip(),
            "published":item.findtext("pubDate","").strip(),
            "description":re.sub("<[^>]+>"," ",item.findtext("description","")).strip(),
            "source":(item.find("source").text if item.find("source") is not None else "Google News")
        })
    return rows

def build_queries():
    qs=[]
    roles=PREF["graphic_roles"]+PREF["business_roles"]
    # Google News date filters are intentionally broad; recent_enough() is the
    # authoritative local 20-day cutoff so the workflow stays maintainable.
    for role in roles[:12]:
        qs.append(f'"{role}" Pakistan')
        qs.append(f'site:pk.indeed.com "{role}" Pakistan')
        qs.append(f'site:rozee.pk "{role}" Pakistan')
        qs.append(f'site:glassdoor.com/Job "{role}" Pakistan')
    for role in roles[:10]:
        qs.append(f'"{role}" ("visa sponsorship" OR relocation OR "overseas applicants")')
    qs += [
        'site:mustakbil.com "graphic designer" Pakistan',
        'site:brightspyre.com "graphic designer" Pakistan',
        'site:careerjoin.com "graphic designer" Pakistan',
        'site:glassdoor.com/Job "graphic designer" Pakistan',
        'site:glassdoor.com/Job "sales coordinator" Pakistan',
        'site:glassdoor.com/Job "computer operator" Pakistan',
        '"graphic designer" Pakistan WhatsApp vacancy',
        '"graphic designer" Pakistan email vacancy',
        '"computer operator" Pakistan WhatsApp job',
        '"data entry" Pakistan WhatsApp job',
        '"business coordinator" Pakistan email job'
    ]
    return qs

def recent_enough(published):
    if not published:
        return True
    try:
        from email.utils import parsedate_to_datetime
        dt=parsedate_to_datetime(published)
        if dt.tzinfo is None:
            dt=dt.replace(tzinfo=timezone.utc)
        return dt >= datetime.now(timezone.utc)-timedelta(days=RECENT_DAYS)
    except Exception:
        return True

def looks_like_job(row):
    title=(row["title"]+" "+row["description"]).lower()

    # Reject salary pages, generic search/result pages and career-content pages.
    bad_phrases=[
        "how a ", "how to ", "salary guide", "career advice", "course",
        "training", "tips for", "interview questions", "resume tips",
        "salary", "salaries", "yearly salaries", "monthly salaries",
        "job search", "jobs in ", "jobs near ", "job openings in ",
        "find jobs", "search jobs", "browse jobs", "25+ jobs", "50+ jobs",
        "75+ jobs", "100+ jobs", "300+ jobs", "500+ jobs",
        "expired", "closed", "position filled", "no longer accepting",
        "applications closed", "job expired", "vacancy closed"
    ]
    if any(x in title for x in bad_phrases):
        return False

    # Reject pages that are clearly aggregators/listicles rather than one vacancy.
    if re.search(r'\b\d+\+\s+(?:urgent\s+)?(?:graphic|creative|design|sales|data|computer|office|admin|business)?\s*jobs?\b', title):
        return False

    role_terms=PREF["graphic_roles"]+PREF["business_roles"]
    return any(r.lower() in title for r in role_terms) or any(x in title for x in [
        "data entry","computer operator","office assistant","administrative assistant"
    ])

def main():
    seen=set()
    jobs=[]
    for q in build_queries():
        try:
            for row in parse_rss(google_news_rss(q)):
                key=row["url"] or row["title"]
                if key in seen or not recent_enough(row["published"]) or not looks_like_job(row):
                    continue
                seen.add(key)
                score,cv=score_job(row["title"],row["description"])
                if score >= PREF["min_match_score"]:
                    row.update({"match_score":score,"cv":cv,"query":q})
                    jobs.append(row)
            time.sleep(0.2)
        except Exception as e:
            print("Search failed:",q,e)
    jobs.sort(key=lambda x:(x["match_score"],x["published"]),reverse=True)
    out=ROOT/"data"
    out.mkdir(exist_ok=True)
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"recent_window_days":RECENT_DAYS,"jobs":jobs[:100]}
    (out/"jobs.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    print(f"Collected {len(jobs)} recent matched listings from the last {RECENT_DAYS} days.")

if __name__=="__main__":
    main()
