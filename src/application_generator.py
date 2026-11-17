import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "config/profile.json").read_text())
JOBS = json.loads((ROOT / "data/jobs.json").read_text()).get("jobs", []) if (ROOT / "data/jobs.json").exists() else []

PORTFOLIO = PROFILE["behance"]
CV_LINKS = {
    "graphic_designer_cv": "https://github.com/DesignerWorld1702/fahad-job-agent/raw/refs/heads/main/cvs/graphic_designer_cv.pdf",
    "business_computer_cv": "https://github.com/DesignerWorld1702/fahad-job-agent/raw/refs/heads/main/cvs/business_computer_cv.pdf",
}

def contact_method(text):
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"(?:\+?92|0)\s?3\d{2}[-\s]?\d{3}[-\s]?\d{4}", text)
    return list(dict.fromkeys(emails)), list(dict.fromkeys(phones))

def make_record(job):
    body = job.get("description", "")
    emails, phones = contact_method(body)
    cv = job.get("cv")
    name = job.get("title", "the advertised role")

    if cv == "graphic_designer_cv":
        intro = (
            "I am a Graphic Designer with 4+ years of experience in branding, "
            "social media, packaging, print, marketing collateral and AI-assisted design."
        )
    else:
        intro = (
            "I am a business and computer-focused professional with a B.Com background "
            "and experience in sales coordination, production planning, reporting, records "
            "management and digital marketing support."
        )

    short_cover = (
        f"Dear Hiring Team,\n\n"
        f"I am writing to apply for the {name} position. {intro} "
        "I would welcome the opportunity to contribute to your team and discuss my suitability for the role."
    )

    email_body = f"""{short_cover}

Portfolio: {PORTFOLIO}
CV: {CV_LINKS.get(cv, "")}

Phone: {PROFILE["phone"]}
Email: {PROFILE["email"]}

Kind regards,
Fahad Asif"""

    whatsapp_message = (
        f"Hello, I’m Fahad Asif. I’m interested in the {name} position. "
        f"I have relevant professional experience and would be grateful for the opportunity to be considered. "
        f"Portfolio: {PORTFOLIO} "
        f"CV: {CV_LINKS.get(cv, '')} "
        f"Thank you."
    )

    return {
        "title": name,
        "url": job.get("url"),
        "score": job.get("match_score"),
        "cv": cv,
        "emails": emails,
        "phones": phones,
        "email_subject": f"Application – {name} – Fahad Asif",
        "email_body": email_body,
        "cover_letter": short_cover,
        "portfolio_url": PORTFOLIO,
        "cv_url": CV_LINKS.get(cv, ""),
        "whatsapp_message": whatsapp_message,
    }

(Path(ROOT / "data")).mkdir(exist_ok=True)
(Path(ROOT / "data/applications.json")).write_text(
    json.dumps([make_record(j) for j in JOBS], indent=2, ensure_ascii=False)
)
print(f"Prepared {len(JOBS)} application records.")
