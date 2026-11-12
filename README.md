# Fahad Job Agent

Automated job discovery, matching, application preparation and tracking for Fahad Asif.

## Current pipeline

GitHub Actions (runs while the PC is off)
→ public job discovery
→ Pakistan + international relocation/sponsorship search
→ duplicate filtering
→ job scoring
→ Graphic Designer CV vs Business/Computer CV selection
→ application generation
→ application-method queue
→ report + downloadable artifact

## Sources currently configured

- Indeed Pakistan
- Rozee.pk
- LinkedIn (profile URL pending)
- Company career pages
- Google job/news-indexed public listings
- Pakistani job boards and public vacancy pages
- International public listings
- Email / WhatsApp / phone contact opportunities when the listing exposes them

## Application modes

- **EMAIL_READY** — employer email detected; email content is prepared. Actual Yahoo sending is disabled by default.
- **WHATSAPP_READY** — WhatsApp number and ready-to-send message are prepared. The agent does not bypass WhatsApp controls.
- **PHONE_ACTION** — phone number and application details are prepared.
- **WEB_APPLICATION** — direct URL is saved; login/CAPTCHA/2FA steps remain manual when required.
- **REVIEW** — listing needs review.

## Security / platform rules

The agent does not bypass CAPTCHA, 2FA, anti-bot systems, login walls, rate limits, or platform restrictions. It automates everything around those protected steps and places protected applications into a clear action queue.

## Yahoo email

When the two CV PDFs are present, Yahoo delivery can be enabled with GitHub Actions secrets:

- `YAHOO_EMAIL`
- `YAHOO_APP_PASSWORD`

The workflow currently keeps `AUTO_EMAIL_ENABLED=false` until the user explicitly enables sending. The sender also requires the appropriate CV attachment and uses a minimum match score.

Never put a Yahoo password directly in repository files.

## Run it now

In GitHub:
1. Open **Actions**
2. Open **Fahad Job Agent**
3. Click **Run workflow**

The workflow also runs automatically twice daily.

## Main files

- `config/profile.json` — master profile and account sources
- `config/job_preferences.json` — job targeting rules
- `src/job_search.py` — public job discovery
- `src/job_matcher.py` — CV selection and scoring
- `src/application_generator.py` — tailored application content
- `src/application_queue.py` — compliant action routing
- `src/email_sender.py` — optional Yahoo SMTP delivery
- `.github/workflows/job-agent.yml` — scheduled execution
- `data/application_queue.json` — current application action queue
- `JOB_REPORT.md` — latest human-readable report
