import json
from pathlib import Path
from urllib.parse import quote
import re

def explicit_whatsapp_application_invitation(text):
    """True only when the hiring post invites applicants to use WhatsApp."""
    text = re.sub(r"\s+", " ", (text or "").lower())
    invitation_patterns = [
        r"whatsapp\s+(?:your\s+)?(?:cv|resume|application)",
        r"whatsapp\s+(?:contact|number|no\.?)",
        r"whatsapp\s*[:\-]\s*\+?\d[\d\s().-]{7,}",
        r"(?:send|share|submit)\s+(?:your\s+)?(?:cv|resume|application)\s+(?:on|via|through|to)\s+whatsapp",
        r"(?:apply|application)\s+(?:via|through|on|by)\s+whatsapp",
        r"whatsapp\s+(?:us|me|hr|the\s+hr|to\s+apply|for\s+application)",
        r"contact\s+(?:us|hr|the\s+hr)\s+(?:on|via|through)\s+whatsapp",
        r"(?:call|message|text)\s+(?:us|hr|the\s+hr)\s+(?:on|via|through)\s+whatsapp",
        r"for\s+(?:job\s+)?(?:details|application)\s+(?:contact|whatsapp)\s+(?:us|hr)",
    ]
    return any(re.search(pattern, text) for pattern in invitation_patterns)

ROOT = Path(__file__).resolve().parents[1]
jobs = json.loads((ROOT / "data/jobs.json").read_text()).get("jobs", [])
apps = json.loads((ROOT / "data/applications.json").read_text()) if (ROOT / "data/applications.json").exists() else []

by_url = {a.get("url"): a for a in apps}
queue = []

for job in jobs:
    app = by_url.get(job.get("url"), {})
    emails = app.get("emails", [])
    phones = app.get("phones", [])
    url = job.get("url", "")
    description = (job.get("description") or "").lower()
    search_context = (job.get("query") or "").lower()
    source = job.get("source") or ""
    region = "pakistan" if "pakistan" in search_context else "international"

    combined_post_text = (job.get("title") or "") + " " + (job.get("description") or "")
    has_whatsapp_signal = any(
        marker in combined_post_text.lower()
        for marker in ("whatsapp", "wa.me", "whatsapp.com")
    )
    whatsapp_opt_in = explicit_whatsapp_application_invitation(combined_post_text)
    explicit_email_invite = bool(re.search(
        r"(?:send|email|submit|share)\s+(?:your\s+)?(?:cv|resume|application)|"
        r"(?:apply|application)\s+(?:by|via|through|to)\s+email|"
        r"email\s+(?:your\s+)?(?:cv|resume|application)|"
        r"send\s+(?:your\s+)?application\s+to\s+[a-z0-9._%+-]+@",
        combined_post_text, re.I
    ))
    # A publicly published hiring/recruitment address is an actionable application
    # route even when the post does not contain the words "apply by email".
    hiring_email = any(
        re.search(r"(?:career|recruit|hr|hiring|jobs?|talent|apply)", str(e).lower())
        and not re.search(r"(?:noreply|no-reply|donotreply|example\\.com)", str(e).lower())
        for e in emails
    )
    email_application_invited = explicit_email_invite or hiring_email
    social_source = any(site in source.lower() for site in ("facebook", "instagram"))
    social_dm_invited = social_source and bool(re.search(
        r"(?:send|share|submit)\s+(?:your\s+)?(?:cv|resume|portfolio|application)\s+(?:via|through|in|by)\s+(?:instagram\s+)?dm|"
        r"apply\s+(?:via|through|in)\s+(?:instagram\s+)?dm|"
        r"(?:message|dm)\s+(?:us|the\s+page|our\s+page|hr)",
        combined_post_text, re.I
    ))

    if emails and phones and has_whatsapp_signal and whatsapp_opt_in:
        mode = "EMAIL_AND_WHATSAPP_READY"
        priority = "automatic when Yahoo SMTP and WhatsApp Cloud API are configured"
        action = "Send the tailored application by email and WhatsApp when both channels are configured."
    elif emails:
        mode = "EMAIL_READY"
        priority = "automatic only when the employer explicitly invites email applications and Yahoo SMTP is configured"
        action = "Email the tailored CV only when the employer explicitly invites email applications."
    elif phones and has_whatsapp_signal and whatsapp_opt_in:
        mode = "WHATSAPP_READY"
        priority = "automatic when WhatsApp Cloud API is configured"
        action = "Send through the configured WhatsApp Business/Cloud API using an approved message template."
    elif phones:
        mode = "PHONE_ACTION"
        priority = "manual"
        action = "Call the listed number using the prepared application details."
    elif social_dm_invited:
        mode = "SOCIAL_DM_REVIEW"
        priority = "manual"
        action = "The post invites a social-media DM. Review the original post and send the application manually; the agent does not send social DMs."
    elif url:
        mode = "WEB_APPLICATION"
        priority = "automatic where the public form is supported; manual for protected or unknown steps"
        action = "The agent opens the public application page, fills known fields and uploads the selected CV; it stops for CAPTCHA, login, 2FA or unknown required answers."
    else:
        mode = "REVIEW"
        priority = "manual"
        action = "Review listing and decide whether to pursue it."

    queue.append({
        # Keep the raw source headline for traceability, but use the cleaned role
        # title in outbound messages and the user-facing application queue.
        "title": app.get("title") or job.get("title"),
        "source_title": job.get("title"),
        "region": region,
        "source": source,
        "url": url,
        "score": job.get("match_score"),
        "cv": job.get("cv"),
        "mode": mode,
        "whatsapp_ready": bool(phones and has_whatsapp_signal and whatsapp_opt_in),
        "whatsapp_opt_in": whatsapp_opt_in,
        "social_dm_invited": social_dm_invited,
        "priority": priority,
        "action": action,
        "emails": emails,
        "phones": phones,
        "email_application_invited": email_application_invited,
        "email_subject": app.get("email_subject"),
        "email_body": app.get("email_body"),
        "whatsapp_message": app.get("whatsapp_message"),
        "portfolio_url": app.get("portfolio_url"),
        "cv_url": app.get("cv_url"),
        "whatsapp_template_variables": [
            job.get("title") or "",
            app.get("portfolio_url") or "",
            app.get("cv_url") or ""
        ],
        # Never expose a WhatsApp contact link unless the employer explicitly
        # invited applications through WhatsApp in the published post.
        "whatsapp_links": (
            [
                "https://wa.me/" + "".join(ch for ch in p if ch.isdigit()) + "?text=" + quote(app.get("whatsapp_message", ""))
                for p in phones
            ] if whatsapp_opt_in else []
        )
    })

queue.sort(key=lambda x: (x["score"] or 0), reverse=True)
(ROOT / "data/application_queue.json").write_text(
    json.dumps({"queue": queue[:150]}, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Built application queue with {len(queue)} records.")
