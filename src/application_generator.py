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
    phones = re.findall(
        r"(?<!\w)(?:\+\d{1,3}|00\d{1,3})[\s().-]?(?:\d[\s().-]?){7,14}(?!\w)|"
        r"(?<!\w)(?:\+?92|0)\s?3\d{2}[-\s]?\d{3}[-\s]?\d{4}(?!\w)",
        text
    )
    normalized = []
    for phone in phones:
        digits = re.sub(r"\D", "", phone)
        if 10 <= len(digits) <= 15 and digits not in normalized:
            normalized.append(digits)
    return list(dict.fromkeys(emails)), normalized

def clean_role_title(raw_title):
    """Extract a concise role name; never reuse a pasted hiring-ad headline."""
    raw = re.sub(r"\\s+", " ", str(raw_title or "")).strip()
    configured = []
    prefs_path = ROOT / "config" / "job_preferences.json"
    if prefs_path.exists():
        prefs = json.loads(prefs_path.read_text(encoding="utf-8"))
        configured = prefs.get("graphic_roles", []) + prefs.get("business_roles", [])
    # Prefer a known role phrase that actually appears in the source headline.
    for role in sorted(configured, key=len, reverse=True):
        if re.search(r"(?<![A-Za-z])" + re.escape(role) + r"(?![A-Za-z])", raw, re.I):
            return role
    # Catch reasonable role titles not yet in the preference list, including
    # titles embedded after generic social-media announcement wording.
    patterns = [
        r"([A-Z][A-Za-z/&(),'-]*(?:\\s+[A-Z][A-Za-z/&(),'-]*){0,5}\\s+(?:Coordinator|Designer|Assistant|Executive|Operator|Clerk|Controller|Specialist|Officer|Administrator|Analyst))",
        r"([A-Z][A-Za-z/&(),'-]*(?:\\s+[A-Z][A-Za-z/&(),'-]*){0,5}\\s+Manager)"
    ]
    for pattern in patterns:
        match = re.search(pattern, raw)
        if match:
            candidate = match.group(1).strip(" -–—:|")
            if 2 <= len(candidate.split()) <= 7:
                return candidate
    raw = re.sub(r"^(?:application\\s*[–-]\\s*)?", "", raw, flags=re.I)
    raw = re.sub(r"[🚨🔶🔹📢📣✨⭐️]+", " ", raw)
    raw = re.split(r"\\b(?:requirements|qualification|qualifications|responsibilities|we are pleased|we are hiring|send your cv)\\b", raw, maxsplit=1, flags=re.I)[0]
    raw = re.sub(r"\\s+", " ", raw).strip(" -–—:|.")
    return raw[:80] if raw else "the advertised position"

def make_record(job):
    body = job.get("description", "")
    emails, phones = contact_method(body)
    cv = job.get("cv")
    name = clean_role_title(job.get("title", ""))

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
        f"I am pleased to apply for the {name} position. {intro} "
        "In my recent roles, I have worked with teams, handled day-to-day deadlines, "
        "and delivered practical work aligned with business and brand requirements. "
        "I am dependable, quick to learn, and comfortable adapting to new tools and workflows. "
        "I would value the opportunity to bring my experience to your organisation.\n\n"
        "My CV is attached for your review. I would be glad to discuss the role and "
        "how my background could support your team.\n\n"
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
        f"{name} opportunity. {intro} I’m keen to contribute, learn your team’s "
        "requirements and discuss how my experience matches this role. I’ve attached "
        "my CV for your review. Thank you for considering my application."
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
