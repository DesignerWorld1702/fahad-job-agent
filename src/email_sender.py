import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "config/profile.json").read_text())
QUEUE = json.loads((ROOT / "data/application_queue.json").read_text()).get("queue", [])

enabled = os.getenv("AUTO_EMAIL_ENABLED", "false").lower() == "true"
test_mode = os.getenv("EMAIL_TEST_MODE", "false").lower() == "true"
test_recipient = os.getenv("EMAIL_TEST_RECIPIENT", "").strip()
sender = os.getenv("YAHOO_EMAIL", PROFILE["email"]).strip()
app_password = os.getenv("YAHOO_APP_PASSWORD", "").strip()
max_score = int(os.getenv("AUTO_EMAIL_MIN_SCORE", "85"))

STATUS_PATH = ROOT / "data" / "sent_applications.json"
if STATUS_PATH.exists():
    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
else:
    status = {"sent": []}

sent_keys = {
    x.get("key") for x in status.get("sent", [])
    if isinstance(x, dict) and x.get("key")
}

def save_status():
    STATUS_PATH.write_text(
        json.dumps(status, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

if not enabled:
    print("AUTO_EMAIL_ENABLED is false; email sending skipped safely.")
    raise SystemExit(0)
if not sender or not app_password:
    print("Yahoo sender credentials are not configured; email sending skipped safely.")
    raise SystemExit(0)

cv_paths = {
    "graphic_designer_cv": ROOT / "cvs" / "graphic_designer_cv.pdf",
    "business_computer_cv": ROOT / "cvs" / "business_computer_cv.pdf",
}

eligible = [
    item for item in QUEUE
    if (item.get("score") or 0) >= max_score
    and cv_paths.get(item.get("cv")) is not None
    and cv_paths[item.get("cv")].exists()
]

if test_mode:
    if not test_recipient:
        print("EMAIL_TEST_RECIPIENT is missing; test email skipped safely.")
        raise SystemExit(0)
    if not eligible:
        print("No eligible job with an available CV; test email skipped.")
        raise SystemExit(0)
    item = eligible[0]
    recipient = test_recipient
    key = f"email_test|{item.get('url','')}|{recipient.lower()}"
    if key in sent_keys:
        print("This exact email test was already recorded; skipping duplicate.")
        raise SystemExit(0)
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = "[TEST] " + (item.get("email_subject") or "Job Application – Fahad Asif")
    body = (
        "This is a test email from Fahad's Job Agent. It is sent only to the configured test recipient, "
        "not to the employer. The attached PDF is the CV selected for the sample job below.\n\n"
        f"Sample job: {item.get('title','')}\n"
        f"Job listing: {item.get('url','')}\n\n"
        + (item.get("email_body") or "")
    )
    msg.set_content(body)
    cv_path = cv_paths[item.get("cv")]
    msg.add_attachment(cv_path.read_bytes(), maintype="application", subtype="pdf", filename=cv_path.name)
    with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465, timeout=30) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)
    status["sent"].append({
        "key": key, "channel": "email_test", "recipient": recipient,
        "url": item.get("url"), "title": item.get("title"),
        "score": item.get("score"), "cv": item.get("cv")
    })
    save_status()
    print(f"Yahoo TEST email accepted by SMTP for {recipient}; one message sent with CV attachment.")
    raise SystemExit(0)

sent = 0
skipped = 0
with smtplib.SMTP_SSL("smtp.mail.yahoo.com", 465, timeout=30) as smtp:
    smtp.login(sender, app_password)
    for item in QUEUE:
        if item.get("mode") not in ("EMAIL_READY", "EMAIL_AND_WHATSAPP_READY") or (item.get("score") or 0) < max_score:
            continue
        recipients = item.get("emails", [])
        cv_path = cv_paths.get(item.get("cv"))
        if not recipients or not cv_path or not cv_path.exists():
            skipped += 1
            continue
        recipient = recipients[0].strip().lower()
        key = f"email|{item.get('url','')}|{recipient}"
        if key in sent_keys:
            skipped += 1
            continue
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = item.get("email_subject") or "Job Application – Fahad Asif"
        msg.set_content(item.get("email_body") or "")
        msg.add_attachment(cv_path.read_bytes(), maintype="application", subtype="pdf", filename=cv_path.name)
        smtp.send_message(msg)
        status["sent"].append({
            "key": key, "channel": "email", "recipient": recipient,
            "url": item.get("url"), "title": item.get("title"), "score": item.get("score")
        })
        sent_keys.add(key)
        save_status()
        sent += 1

print(f"Yahoo email sender: sent={sent}, skipped={skipped}")
