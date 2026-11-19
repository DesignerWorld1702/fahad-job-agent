import json
import os
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = json.loads((ROOT / "data/application_queue.json").read_text()).get("queue", [])

enabled = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
token = os.getenv("WHATSAPP_TOKEN", "").strip()
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
waba_id = os.getenv("WHATSAPP_WABA_ID", "").strip()
api_version = os.getenv("WHATSAPP_API_VERSION", "v24.0").strip()
template_name = os.getenv("WHATSAPP_APPLICATION_TEMPLATE_NAME", "").strip()
template_language = os.getenv("WHATSAPP_TEMPLATE_LANGUAGE", "en_US").strip()
max_score = int(os.getenv("WHATSAPP_MIN_SCORE", "65"))
require_document_header = os.getenv("WHATSAPP_TEMPLATE_DOCUMENT_HEADER", "true").lower() == "true"
test_mode = os.getenv("WHATSAPP_TEST_MODE", "false").lower() == "true"
test_recipient = os.getenv("WHATSAPP_TEST_RECIPIENT", "").strip()

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
    print("WHATSAPP_ENABLED is false; WhatsApp sending skipped safely.")
    raise SystemExit(0)

if not token or not phone_number_id:
    print("WhatsApp credentials are not configured; sending skipped safely.")
    raise SystemExit(0)

if not template_name:
    print(
        "WHATSAPP_APPLICATION_TEMPLATE_NAME is not configured. "
        "No job-application WhatsApp messages were sent. "
        "Create/use an approved application template before enabling production sends."
    )
    raise SystemExit(0)

endpoint = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"

sent = 0
skipped = 0
failed = 0

if test_mode:
    # A safe test uses the configured test recipient, so it does not require
    # the sample job listing itself to publish a WhatsApp contact number.
    eligible_items = [
        item for item in QUEUE
        if (item.get("score") or 0) >= max_score
        and (item.get("cv_url") or (item.get("application", {}) or {}).get("cv_url"))
    ]
else:
    eligible_items = [
        item for item in QUEUE
        if item.get("whatsapp_ready") and (item.get("score") or 0) >= max_score
    ]
if test_mode and not test_recipient:
    print("WHATSAPP_TEST_MODE is true but WHATSAPP_TEST_RECIPIENT is empty; no messages sent.")
    raise SystemExit(0)
if test_mode:
    eligible_items = eligible_items[:1]
    print(f"WhatsApp TEST MODE: only the top eligible application will be sent to {test_recipient}.")

for item in eligible_items:
    if not test_mode and not item.get("whatsapp_ready"):
        continue
    if (item.get("score") or 0) < max_score:
        continue

    recipients = [test_recipient] if test_mode else (item.get("phones") or [])
    if not recipients:
        skipped += 1
        continue

    for raw_phone in dict.fromkeys(recipients):
        recipient = "".join(ch for ch in raw_phone if ch.isdigit())
        if recipient.startswith("03") and len(recipient) == 11:
            recipient = "92" + recipient[1:]
        elif recipient.startswith("92") and len(recipient) == 12:
            pass
        elif recipient.startswith("+92"):
            recipient = recipient[1:]
        if not recipient:
            skipped += 1
            continue

        key = (f"whatsapp-test|{item.get('url','')}|{recipient}" if test_mode else f"whatsapp|{item.get('url','')}|{recipient}")
        if key in sent_keys:
            skipped += 1
            continue

        app = item.get("application", {}) or {}
        cv_url = item.get("cv_url") or app.get("cv_url") or ""
        portfolio_url = item.get("portfolio_url") or app.get("portfolio_url") or ""
        job_title = item.get("title") or ""
        if not cv_url:
            print(f"WhatsApp skipped for {recipient}: no CV URL for this application.")
            skipped += 1
            continue

        components = []
        if require_document_header:
            components.append({
                "type": "header",
                "parameters": [{
                    "type": "document",
                    "document": {
                        "link": cv_url,
                        "filename": "Fahad_Asif_CV.pdf"
                    }
                }]
            })

        components.append({
            "type": "body",
            "parameters": [
                {"type": "text", "text": job_title},
                {"type": "text", "text": portfolio_url},
                {"type": "text", "text": cv_url}
            ]
        })

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": template_language},
                "components": components
            }
        }

        request = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
            message_id = (
                body.get("messages", [{}])[0].get("id")
                if isinstance(body.get("messages"), list)
                else None
            )
            status["sent"].append({
                "key": key,
                "channel": "whatsapp_test" if test_mode else "whatsapp",
                "recipient": recipient,
                "url": item.get("url"),
                "title": item.get("title"),
                "score": item.get("score"),
                "message_id": message_id,
            })
            sent_keys.add(key)
            sent += 1
            save_status()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"WhatsApp send failed for {recipient}: HTTP {exc.code} {detail[:500]}")
            failed += 1
        except Exception as exc:
            print(f"WhatsApp send failed for {recipient}: {exc}")
            failed += 1

print(f"WhatsApp sender: sent={sent}, skipped={skipped}, failed={failed}, WABA={waba_id or 'not set'}")
