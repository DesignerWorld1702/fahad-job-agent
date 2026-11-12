import json
from pathlib import Path
from urllib.parse import quote

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

    if emails:
        mode = "EMAIL_READY"
        priority = "automatic when Yahoo SMTP is configured"
        action = "Send tailored email with selected CV after email-sending secrets are configured."
    elif "whatsapp" in description and phones:
        mode = "WHATSAPP_READY"
        priority = "one-click"
        action = "Open WhatsApp with the prepared message; user presses Send unless an approved WhatsApp Business integration is configured."
    elif phones:
        mode = "PHONE_ACTION"
        priority = "manual"
        action = "Call the listed number using the prepared application details."
    elif url:
        mode = "WEB_APPLICATION"
        priority = "manual/protected as required"
        action = "Open the listing/application URL. If login, CAPTCHA or 2FA appears, complete that step manually."
    else:
        mode = "REVIEW"
        priority = "manual"
        action = "Review listing and decide whether to pursue it."

    queue.append({
        "title": job.get("title"),
        "source": job.get("source"),
        "url": url,
        "score": job.get("match_score"),
        "cv": job.get("cv"),
        "mode": mode,
        "priority": priority,
        "action": action,
        "emails": emails,
        "phones": phones,
        "email_subject": app.get("email_subject"),
        "email_body": app.get("email_body"),
        "whatsapp_message": app.get("whatsapp_message"),
        "whatsapp_links": [
            "https://wa.me/" + "".join(ch for ch in p if ch.isdigit()) + "?text=" + quote(app.get("whatsapp_message", ""))
            for p in phones
        ]
    })

queue.sort(key=lambda x: (x["score"] or 0), reverse=True)
(ROOT / "data/application_queue.json").write_text(
    json.dumps({"queue": queue[:150]}, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Built application queue with {len(queue)} records.")
