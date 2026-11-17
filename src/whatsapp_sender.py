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
template_variables = item.get("whatsapp_template_variables", [])
max_score = int(os.getenv("WHATSAPP_MIN_SCORE", "65"))

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

for item in QUEUE:
    if not item.get("whatsapp_ready"):
        continue
    if (item.get("score") or 0) < max_score:
        continue

    recipients = item.get("phones") or []
    if not recipients:
        skipped += 1
        continue

    for raw_phone in dict.fromkeys(recipients):
        recipient = "".join(ch for ch in raw_phone if ch.isdigit())
        if not recipient:
            skipped += 1
            continue

        key = f"whatsapp|{item.get('url','')}|{recipient}"
        if key in sent_keys:
            skipped += 1
            continue

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": template_language},
                "components": [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(value)}
                        for value in template_variables
                    ]
                }]
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
                "channel": "whatsapp",
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
