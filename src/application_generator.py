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
        f"Dear Hiring Team,\\n\\n"
        f"I am pleased to apply for the {name} position. {intro} "
        "In my recent roles, I have worked with teams, handled day-to-day deadlines, "
        "and delivered practical work aligned with business and brand requirements. "
        "I am dependable, quick to learn, and comfortable adapting to new tools and workflows. "
        "I would value the opportunity to bring my experience to your organisation.\\n\\n"
        "My CV is attached for your review. I would be glad to discuss the role and "
        "how my background could support your team.\\n\\n"
        f"Portfolio: {PORTFOLIO}"
    )

    email_body = f"""{short_cover}

Thank you for your time and consideration.

Kind regards,
Fahad Asif
{PROFILE["phone"]}
{PROFILE["email"]}"""

    whatsapp_message = (
        f"Hello! My name is Fahad Asif, and I’m contacting you regarding the "
        f"{name} opportunity. I have 4+ years of experience in graphic design, "
        "branding, social media creatives and packaging, along with experience in "
        "coordination, reporting and office support. I’m keen to contribute, learn "
        "your team’s requirements and discuss how my experience matches this role. "
        "I’ve attached my CV for your review. Thank you for considering my application."
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
