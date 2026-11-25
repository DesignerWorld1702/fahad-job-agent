import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
jobs_data = json.loads((ROOT / "data/jobs.json").read_text(encoding="utf-8"))
queue_data = json.loads((ROOT / "data/application_queue.json").read_text(encoding="utf-8"))
sent_data = json.loads((ROOT / "data/sent_applications.json").read_text(encoding="utf-8")) if (ROOT / "data/sent_applications.json").exists() else {"sent": []}
jobs = jobs_data.get("jobs", [])
queue = queue_data.get("queue", [])
sent_rows = sent_data.get("sent", [])
email_sent = [x for x in sent_rows if x.get("channel") == "email"]
web_sent = [x for x in sent_rows if x.get("channel") == "web_form"]
wa_ready = [x for x in queue if x.get("whatsapp_ready") and x.get("whatsapp_opt_in")]

def whatsapp_link(item):
    if not item.get("whatsapp_ready") or not item.get("whatsapp_opt_in"):
        return ""
    message = item.get("whatsapp_message") or (
        "Hello, I am interested in applying for the " + (item.get("title") or "advertised position") +
        ". Please find my CV and portfolio for your consideration."
    )
    for phone in item.get("phones") or []:
        digits = "".join(ch for ch in str(phone) if ch.isdigit())
        if digits.startswith("03") and len(digits) == 11:
            digits = "92" + digits[1:]
        elif digits.startswith("00"):
            digits = digits[2:]
        if 10 <= len(digits) <= 15:
            return "https://wa.me/" + digits + "?text=" + quote(message)
    return ""

lines = [
    "# Fahad Job Agent Report", "",
    "Generated matches: **%d**" % len(jobs), "",
    "Confirmed email applications: **%d**; confirmed web-form applications: **%d**." % (len(email_sent), len(web_sent)), "",
    "Email applications are sent automatically to the email address published in the hiring post. WhatsApp applications are prepared as free prefilled **one-click daily send** links; clicking opens WhatsApp with the message ready, then press Send." , "",
    "## CVs in use", "",
    "- Graphic Designer: `cvs/graphic_designer_cv.pdf`",
    "- Business Support: `cvs/business_computer_cv.pdf`", "",
    "## Application modes", "",
    "| Mode | Meaning |",
    "|---|---|",
    "| EMAIL_READY | Automatically email the tailored CV when a public hiring email is available and Yahoo SMTP is configured |",
    "| WHATSAPP_READY | Prefilled free WhatsApp link for the daily one-click send; no API/payment required |",
    "| PHONE_ACTION | Phone-only route is skipped automatically |",
    "| WEB_APPLICATION | Public forms are completed/submitted only when supported and all required answers are known |",
    "| REVIEW | Protected/unknown/unsupported route is skipped automatically; the agent continues with other jobs and email routes |", "",
    "## Top matches", "",
    "| Score | CV | Mode | Web status | Job | Source | Hiring email | Contacts | WhatsApp | Application |",
    "|---:|---|---|---|---|---|---|---|---|"
]
for item in queue[:100]:
    title = (item.get("title") or "").replace("|", "/")
    source = (item.get("source") or "").replace("|", "/")
    contacts = ", ".join(dict.fromkeys((item.get("emails") or []) + (item.get("page_emails") or []) + (item.get("phones") or []))).replace("|", "/")
    hiring_email = ", ".join(item.get("hiring_post_emails") or []) or item.get("email_destination") or "—"
    wa = whatsapp_link(item)
    wa_cell = "[Open WhatsApp](%s)" % wa if wa else "—"
    application_url = item.get("application_url") or item.get("url") or ""
    application_cell = "[Open application](%s)" % application_url if application_url else "—"
    lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        item.get("score", ""), item.get("cv", ""), item.get("mode", ""),
        item.get("web_apply_status", "not_checked"), title, source,
        hiring_email, contacts, wa_cell, application_cell
    ))
Path("JOB_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Report generated: %d matches, %d explicit WhatsApp click-to-send links." % (len(jobs), len(wa_ready)))
