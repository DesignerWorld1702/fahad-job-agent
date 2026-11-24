# Fahad Job Agent

Automated job discovery, matching, application preparation and tracking for Fahad Asif.

## Current pipeline

GitHub Actions (runs while the PC is off)
→ public job discovery
→ Pakistan + international relocation/sponsorship + remote/FlexJobs search
→ optional signed-in Facebook + Instagram discovery through TinyFish
→ duplicate filtering
→ job scoring
→ Graphic Designer CV vs Business/Computer CV selection
→ application generation
→ application-method queue
→ public employer-page inspection
→ supported web-form filling + submission
→ tailored email with CV when explicitly invited
→ report + downloadable artifact

## Sources currently configured

- Indeed Pakistan (dedicated role-by-role and city-level discovery across Lahore, Karachi, Islamabad, Rawalpindi, Faisalabad, Multan, Gujranwala and Sialkot)
- Rozee.pk (dedicated role-by-role and city-level discovery across the same Pakistan cities)
- LinkedIn (profile URL pending)
- Company career pages
- Google job/news-indexed public listings
- Pakistani job boards and public vacancy pages
- International public listings
- FlexJobs publicly indexed listings (membership/login-protected applications remain manual)
- Remote-first and work-from-home vacancies in Pakistan and internationally
- Publicly indexed Facebook and Instagram hiring posts
- Optional authenticated Facebook and Instagram searches through TinyFish when enabled and configured
- Email / WhatsApp / phone contact opportunities when the listing exposes them

## Signed-in Facebook and Instagram search (optional)

The repository includes `src/social_media_search.py`. It uses the official TinyFish Agent API and your saved TinyFish browser profile to search Facebook and Instagram from GitHub Actions. It adds matching posts to `data/jobs.json` before CV selection and application preparation.

This feature is deliberately **opt-in** so scheduled GitHub runs do not unexpectedly incur TinyFish usage charges. To enable it:

1. Open TinyFish and create an API key at https://agent.tinyfish.ai/api-keys.
2. In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**.
3. Add these three repository secrets:
   - `TINYFISH_API_KEY` — your TinyFish API key (keep it private).
   - `TINYFISH_PROFILE_ID` — the saved TinyFish profile ID that has both `facebook.com` and `instagram.com` signed in.
   - `TINYFISH_SOCIAL_SEARCH_ENABLED` — set the value to `true` only when you want to enable scheduled signed-in social searches.
4. Run **Actions → Fahad Job Agent → Run workflow** to test it.

If the enable flag or credentials are missing, the script safely skips authenticated social searches and the existing public/indexed search continues. TinyFish API usage may be billable under your TinyFish account. Review its current pricing and wallet before enabling. Do not put the API key or browser cookies in repository files, commits, or logs.

The script only reads hiring posts visible to the signed-in account. It does not message employers, apply through social media, follow accounts, join groups, post, comment, or change account settings. It records only published contacts and distinguishes an explicitly invited email/WhatsApp application from a contact detail alone. Instagram/Facebook search is not exhaustive; post dates and vacancies still need verification. Expired sessions or platform restrictions can cause a source to return no results.

## Application modes

- **EMAIL_READY** — employer email found; sending is allowed only when the employer explicitly invites email applications and Yahoo secrets are configured.
- **WHATSAPP_READY** — a WhatsApp contact and explicit invitation to apply via WhatsApp are required. A public phone number alone is not consent.
- **PHONE_ACTION** — phone number and application details are prepared for a call.
- **WEB_APPLICATION** — the agent opens public employer pages, fills known profile fields and uploads the selected CV; it stops for CAPTCHA, login, 2FA or unknown required answers.
- **REVIEW** — unknown required questions, unsupported fields, social-media DM-only instructions, or an inaccessible form are queued for manual completion.

## Security / platform rules

The agent does not bypass CAPTCHA, 2FA, anti-bot systems, login walls, paid memberships, rate limits, or platform restrictions. It will not invent answers about work authorization, salary expectations, sponsorship eligibility, or other unknown personal facts. If a form requires information not present in the verified profile, it stops before submission and records the missing fields for review. After a submit click, it records a submission only when the page shows a confirmation; ambiguous outcomes are flagged so it does not blindly submit again. Remote roles are checked for location eligibility; 'remote' does not necessarily mean worldwide.

## WhatsApp applications (free click-to-send mode)

The free workflow does not send WhatsApp Cloud API messages and does not require Meta API credentials or approved templates. Instead, `JOB_REPORT.md` includes an **Open WhatsApp** link only when the employer's published post/page explicitly invites applications through WhatsApp and a phone number is available. A public phone number by itself is never treated as permission.

Open the link, review the prefilled message, and press Send yourself. Attach the selected CV manually if the employer requests it. GitHub Actions cannot press Send inside your WhatsApp account. The Cloud API sender remains in the repository for possible future use, but the scheduled workflow explicitly disables it to avoid paid messaging and test-recipient restrictions.

## Yahoo email

When the two CV PDFs are present, Yahoo delivery can be enabled with GitHub Actions secrets:

- `YAHOO_EMAIL`
- `YAHOO_APP_PASSWORD`

Production email is enabled for relevant listings with a match score of 65 or higher, but only when the job post or employer page explicitly invites candidates to apply by email. The sender attaches the selected CV, avoids a separate CV download link in the email, deduplicates previously sent applications, and shares daily maximums of 30 Pakistan and 20 international applications across web forms, email and WhatsApp. These are ceilings, not targets: the agent continues searching and processing even when fewer suitable jobs are available.

Never put a Yahoo password directly in repository files.

## Run it now

In GitHub:
1. Open **Actions**
2. Open **Fahad Job Agent**
3. Click **Run workflow**

The workflow runs automatically twice daily (10:00 AM and 6:00 PM Pakistan time), after relevant code/configuration/CV changes, and can also be started manually. Data/report commits do not retrigger the workflow.

## Main files

- `config/profile.json` — master profile and account sources
- `config/job_preferences.json` — job targeting rules
- `src/job_search.py` — public job discovery
- `src/social_media_search.py` — optional authenticated Facebook/Instagram discovery via TinyFish
- `src/job_matcher.py` — CV selection and scoring
- `src/application_generator.py` — tailored application content
- `src/application_queue.py` — compliant action routing
- `src/email_sender.py` — optional Yahoo SMTP delivery
- `src/web_apply.py` — public application-page inspection, form filling and permitted submission
- `src/report_generator.py` — report with employer-invited WhatsApp click-to-send links
- `.github/workflows/job-agent.yml` — scheduled execution
- `data/application_queue.json` — current application action queue
- `JOB_REPORT.md` — latest human-readable report

<!-- CV build trigger: tailored cover letter + CV + portfolio PDFs are generated by GitHub Actions. -->
