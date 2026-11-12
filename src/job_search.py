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
    for role in roles[:16]:
        qs.append(f'"{role}" Pakistan')
        qs.append(f'site:pk.indeed.com "{role}" Pakistan')
        qs.append(f'site:rozee.pk "{role}" Pakistan')
        qs.append(f'site:glassdoor.com/Job "{role}" Pakistan')
    for role in roles[:12]:
        qs.append(f'"{role}" ("visa sponsorship" OR relocation OR "overseas applicants")')
    qs += [
        # Pakistan job boards and social/direct-employer sources
        'site:mustakbil.com "graphic designer" Pakistan',
        'site:brightspyre.com "graphic designer" Pakistan',
        'site:careerjoin.com "graphic designer" Pakistan',
        'site:glassdoor.com/Job "graphic designer" Pakistan',
        'site:glassdoor.com/Job "sales coordinator" Pakistan',
        'site:glassdoor.com/Job "computer operator" Pakistan',
        '"graphic designer" Pakistan WhatsApp vacancy',
        '"graphic designer" Pakistan email vacancy',
        '"graphic designer" Pakistan Facebook hiring',
        '"graphic designer" Pakistan Instagram hiring',
        '"graphic designer" Pakistan LinkedIn hiring',
        '"graphic designer" Lahore "60,000"',
        '"graphic designer" Lahore "60000"',
        '"graphic designer" Pakistan "60,000"',
        '"graphic designer" Pakistan "70,000"',
        '"graphic designer" Pakistan "80,000"',
        '"graphic designer" Pakistan "100,000"',
        '"computer operator" Pakistan WhatsApp job',
        '"data entry" Pakistan WhatsApp job',
        '"business coordinator" Pakistan email job',
        '"sales coordinator" Pakistan "60,000"',

        # Google-indexed company career sites: national Pakistani employers
        'site:careers.systemsltd.com graphic designer Pakistan',
        'site:systemsltd.com careers graphic designer Pakistan',
        'site:netsoltech.com careers graphic designer Pakistan',
        'site:arbisoft.com careers graphic designer Pakistan',
        'site:careers.jazz.com.pk graphic designer',
        'site:jazz.com.pk careers graphic designer',
        'site:ptcl.com.pk careers graphic designer',
        'site:engro.com careers graphic designer Pakistan',
        'site:packages.com.pk careers graphic designer Pakistan',
        'site:careers.hbl.com graphic designer Pakistan',
        'site:ubldigital.com careers graphic designer Pakistan',
        'site:meezanbank.com careers marketing coordinator Pakistan',
        'site:daraz.pk careers graphic designer Pakistan',
        'site:foodpanda.pk careers graphic designer Pakistan',

        # Google-indexed company career sites: multinational employers
        'site:careers.unilever.com graphic designer Pakistan',
        'site:jobs.nestle.com graphic designer Pakistan',
        'site:pepsicojobs.com graphic designer Pakistan',
        'site:careers.coca-colacompany.com graphic designer Pakistan',
        'site:careers.pandg.com graphic designer Pakistan',
        'site:jobs.dhl.com graphic designer Pakistan',
        'site:careers.emiratesgroupcareers.com graphic designer UAE',
        'site:careers.ibm.com graphic designer Pakistan',
        'site:careers.microsoft.com graphic designer Pakistan',
        'site:careers.adobe.com graphic designer',
        'site:careers.unilever.com marketing coordinator Pakistan',
        'site:jobs.nestle.com marketing coordinator Pakistan',

        # International employers and ATS career platforms indexed by Google
        'site:jobs.lever.co "graphic designer" Pakistan',
        'site:boards.greenhouse.io "graphic designer" Pakistan',
        'site:myworkdayjobs.com "graphic designer" Pakistan',
        'site:smartrecruiters.com "graphic designer" Pakistan',
        'site:jobs.ashbyhq.com "graphic designer" Pakistan',
        'site:icims.com "graphic designer" Pakistan',
        'site:jobs.lever.co "graphic designer" UAE',
        'site:boards.greenhouse.io "graphic designer" UAE',
        'site:myworkdayjobs.com "graphic designer" UAE',
        'site:jobs.lever.co "graphic designer" Saudi Arabia',
        'site:boards.greenhouse.io "graphic designer" Saudi Arabia',
        'site:myworkdayjobs.com "graphic designer" Saudi Arabia',
        'site:jobs.lever.co "graphic designer" UK',
        'site:boards.greenhouse.io "graphic designer" UK',
        'site:myworkdayjobs.com "graphic designer" UK',

        # Google web-search discovery for employer career pages and direct applications
        '"graphic designer" Pakistan "careers" "apply"',
        '"graphic designer" Pakistan "career" "apply now"',
        '"graphic designer" Pakistan "jobs" "apply now" -indeed -rozee',
        '"business coordinator" Pakistan "careers" "apply"',
        '"sales coordinator" Pakistan "careers" "apply"',
        '"computer operator" Pakistan "careers" "apply"',
        '"graphic designer" UAE "visa sponsorship" "apply"',
        '"graphic designer" Saudi Arabia "visa sponsorship" "apply"',
        '"graphic designer" UK "visa sponsorship" "apply"',
        '"graphic designer" Germany "relocation" "apply"',
        '"graphic designer" Netherlands "relocation" "apply"',
        '"graphic designer" Australia "relocation" "apply"',
        '"graphic designer" Canada "relocation" "apply"'
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

    # Reject career content and clearly closed/expired vacancies.
    bad_phrases=[
        "how a ", "how to ", "salary guide", "career advice", "course",
        "training", "tips for", "interview questions", "resume tips",
        "job search", "jobs in ", "jobs near ", "job openings in ",
        "find jobs", "search jobs", "browse jobs",
        "expired", "position filled", "no longer accepting",
        "applications closed", "job expired", "vacancy closed"
    ]
    if any(x in title for x in bad_phrases):
        return False

    # Salary itself is NOT a reason to reject a listing. A salary page is rejected
    # only when it is clearly a salary-only article/page.
    if any(x in title for x in ["monthly salaries", "yearly salaries", "salary comparison", "salary report"]):
        return False

    # Reject pages that are clearly aggregators/listicles rather than one vacancy.
    if re.search(r'\b\d+\+\s+(?:urgent\s+)?(?:graphic|creative|design|sales|data|computer|office|admin|business)?\s*jobs?\b', title):
        return False

    role_terms=[r.lower() for r in PREF["graphic_roles"]+PREF["business_roles"]]
    role_hit=any(r in title for r in role_terms) or any(x in title for x in [
        "data entry","computer operator","office assistant","administrative assistant"
    ])
    hiring_signal=any(x in title for x in [
        "hiring","vacancy","vacancies","job","career","apply","recruiting",
        "opening","position","required","needed","walk in","walk-in"
    ])
    return role_hit and hiring_signal

def salary_boost(row):
    text=(row["title"]+" "+row["description"]).lower().replace(",","")
    amounts=[]
    # PKR amounts such as 60,000, 60000, 60k, 80k.
    for m in re.finditer(r'(?:(?:rs.?|pkr)\s*)?(\d{2,3})(?:000|\s*k)\b', text):
        try:
            n=int(m.group(1))
            if n < 1000:
                n*=1000
            amounts.append(n)
        except ValueError:
            pass
    if re.search(r'(?:rs\.?|pkr)\s*60(?:000|\s*k)\b', text):
        amounts.append(60000)
    return 5 if any(n >= PREF.get("salary_priority",{}).get("preferred_minimum",60000) for n in amounts) else 0

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
                score=min(100,score+salary_boost(row))
                if score >= PREF["min_match_score"]:
                    row.update({"match_score":score,"cv":cv,"query":q})
                    jobs.append(row)
            time.sleep(0.2)
        except Exception as e:
            print("Search failed:",q,e)
    jobs.sort(key=lambda x:(x["match_score"],x["published"]),reverse=True)
    out=ROOT/"data"
    out.mkdir(exist_ok=True)
    payload={
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "recent_window_days":RECENT_DAYS,
        "salary_preference_pkr":PREF.get("salary_priority",{}).get("preferred_minimum",60000),
        "company_size_policy":PREF.get("company_size_policy"),
        "jobs":jobs[:100]
    }
    (out/"jobs.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False))
    print(f"Collected {len(jobs)} recent matched listings from the last {RECENT_DAYS} days.")

if __name__=="__main__":
    main()
