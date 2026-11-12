import json, re, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
PREF=json.loads((ROOT/"config/job_preferences.json").read_text())
PROFILE=json.loads((ROOT/"config/profile.json").read_text())
from job_matcher import score_job

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
    countries=PREF["countries"]
    # Pakistan and international searches; include contact-method terms to catch social/ad style listings.
    for role in roles[:12]:
        qs.append(f'"{role}" Pakistan (email OR WhatsApp OR apply)')
        qs.append(f'site:pk.indeed.com "{role}" Pakistan')
        qs.append(f'site:rozee.pk "{role}" Pakistan')
    for role in roles[:10]:
        qs.append(f'"{role}" ("visa sponsorship" OR relocation OR "overseas applicants")')
    qs += [
        '"site:mustakbil.com" graphic designer Pakistan',
        '"site:brightspyre.com" graphic designer Pakistan',
        '"site:careerjoin.com" graphic designer Pakistan',
        '"graphic designer" Pakistan WhatsApp vacancy',
        '"graphic designer" Pakistan email vacancy',
        '"computer operator Pakistan WhatsApp job',
        '"data entry Pakistan WhatsApp job',
        '"business coordinator Pakistan email job'
    ]
    return qs

def main():
    seen=set()
    jobs=[]
    for q in build_queries():
        try:
            for row in parse_rss(google_news_rss(q)):
                key=row["url"] or row["title"]
                if key in seen: continue
                seen.add(key)
                score,cv=score_job(row["title"],row["description"])
                if score >= PREF["min_match_score"]:
                    row.update({"match_score":score,"cv":cv,"query":q})
                    jobs.append(row)
            time.sleep(0.2)
        except Exception as e:
            print("Search failed:",q,e)
    jobs.sort(key=lambda x:(x["match_score"],x["published"]),reverse=True)
    out=ROOT/"data"; out.mkdir(exist_ok=True)
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"jobs":jobs[:150]}
    (out/"jobs.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    print(f"Collected {len(jobs)} matched listings.")

if __name__=="__main__":
    main()
