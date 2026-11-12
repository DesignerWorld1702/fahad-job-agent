import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "config/profile.json").read_text())
QUEUE = json.loads((ROOT / "data/application_queue.json").read_text()).get("queue", [])

enabled = os.getenv("AUTO_EMAIL_ENABLED", "false").lower() == "true"
sender = os.getenv("YAHOO_EMAIL", PROFILE["email"])
app_password = os.getenv("YAHOO_APP_PASSWORD")
max_score = int(os.getenv("AUTO_EMAIL_MIN_SCORE", "85"))

if not enabled:
    print("AUTO_EMAIL_ENABLED is false; email sending skipped safely.")
    raise SystemExit(0)
if not app_password:
    print("YAHOO_APP_PASSWORD is not configured; email sending skipped safely.")
    raise SystemExit(0)

cv_paths = {
    "graphic_designer_cv": ROOT / "cvs" / "graphic_designer_cv.pdf",
    "business_computer_cv": ROOT / "cvs" / "business_computer_cv.pdf",
}

sent = 0
skipped = 0

with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465, timeout=30) as smtp:
    smtp.login(sender, app_password)

    for item in QUEUE:
        if item.get("mode") != "EMAIL_READY" or (item.get("score") or 0) < max_score:
            continue

        recipients = item.get("emails", [])
        cv_path = cv_paths.get(item.get("cv"))
        if not recipients or not cv_path or not cv_path.exists():
            skipped += 1
            continue

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = recipients[0]
        msg["Subject"] = item.get("email_subject") or "Job Application – Fahad Asif"
        msg.set_content(item.get("email_body") or "")

        data = cv_path.read_bytes()
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=cv_path.name)
        smtp.send_message(msg)
        sent += 1

print(f"Yahoo email sender: sent={sent}, skipped={skipped}")
