import json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PROFILE=json.loads((ROOT/"config/profile.json").read_text())
JOBS=json.loads((ROOT/"data/jobs.json").read_text()).get("jobs",[]) if (ROOT/"data/jobs.json").exists() else []

def contact_method(text):
    emails=re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}",text)
    phones=re.findall(r"(?:\\+?92|0)\\s?3\\d{2}[-\\s]?\\d{3}[-\\s]?\\d{4}",text)
    return emails,phones

def make_record(job):
    body=job.get("description","")
    emails,phones=contact_method(body)
    cv=job.get("cv")
    name=job.get("title","the advertised role")
    if cv=="graphic_designer_cv":
        intro="I am a Graphic Designer with 4+ years of experience across branding, social media, packaging, print, marketing collateral and AI-assisted creative work."
    else:
        intro="I am a business and computer-focused professional with a B.Com background and experience in sales coordination, production planning, reporting, records management and digital marketing support."
    email_subject=f"Application – {name} – Fahad Asif"
    email_body=f"""Dear Hiring Team,

{intro}

I am writing to apply for {name}. Please find my CV attached for your consideration. I would welcome the opportunity to discuss how my experience can support your team.

Portfolio: {PROFILE['behance']}
Phone: {PROFILE['phone']}
Email: {PROFILE['email']}

Kind regards,
Fahad Asif"""
    whatsapp=f"Hello, I am Fahad Asif. I would like to apply for the {name} position. I have relevant professional experience and can share my CV and portfolio here. Thank you."
    return {
        "title":name,"url":job.get("url"),"score":job.get("match_score"),
        "cv":cv,"emails":emails,"phones":phones,
        "email_subject":email_subject,"email_body":email_body,"whatsapp_message":whatsapp
    }

(Path(ROOT/"data")).mkdir(exist_ok=True)
(Path(ROOT/"data/applications.json")).write_text(json.dumps([make_record(j) for j in JOBS],indent=2,ensure_ascii=False))
print(f"Prepared {len(JOBS)} application records.")
