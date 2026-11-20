import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "config/profile.json").read_text(encoding="utf-8"))
QUEUE_PATH = ROOT / "data/application_queue.json"
STATUS_PATH = ROOT / "data/sent_applications.json"
QUEUE = json.loads(QUEUE_PATH.read_text(encoding="utf-8")).get("queue", [])
STATUS = json.loads(STATUS_PATH.read_text(encoding="utf-8")) if STATUS_PATH.exists() else {"sent": []}

ENABLED = os.getenv("WEB_AUTO_APPLY_ENABLED", "true").lower() == "true"
MIN_SCORE = int(os.getenv("WEB_AUTO_APPLY_MIN_SCORE", "65"))
MAX_PER_RUN = int(os.getenv("WEB_AUTO_APPLY_MAX_PER_RUN", "30"))
TODAY = datetime.now(timezone.utc).date().isoformat()
CVS = {
    "graphic_designer_cv": ROOT / "cvs/graphic_designer_cv.pdf",
    "business_computer_cv": ROOT / "cvs/business_computer_cv.pdf",
}
PORTFOLIO = PROFILE.get("behance", "")

def log(message):
    print("[web-apply] " + message)

def norm(value):
    return re.sub(r"\s+", " ", (value or "").strip().lower())

def is_blocked(page):
    url = page.url.lower()
    if any(x in url for x in ("login", "signin", "sign-in", "account/login", "member-login")):
        return "login_required"
    text = norm(page.locator("body").inner_text(timeout=3000)[:12000])
    selectors = [
        'iframe[src*="captcha"]', '[class*="captcha"]', '[id*="captcha"]',
        'iframe[src*="challenge"]', '[class*="cf-challenge"]',
        'input[name*="captcha"]', 'textarea[name*="g-recaptcha"]'
    ]
    if any(page.locator(s).count() for s in selectors):
        return "captcha_or_bot_check"
    if any(x in text for x in ("verify you are human", "security check", "unusual traffic", "complete the captcha", "robot check")):
        return "captcha_or_bot_check"
    return ""

def click_application_link(page):
    candidates = page.locator("a[href]")
    total = min(candidates.count(), 180)
    for i in range(total):
        link = candidates.nth(i)
        try:
            label = norm(link.inner_text(timeout=250))
            href = link.get_attribute("href") or ""
            if not href or href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            if re.search(r"\b(apply|application|submit\s+(?:your\s+)?cv|apply\s+now|apply\s+for\s+this\s+job)\b", label):
                target = urljoin(page.url, href)
                if urlparse(target).scheme in ("http", "https"):
                    return target
        except Exception:
            continue
    return ""

def label_for(locator):
    try:
        return norm(locator.get_attribute("aria-label") or locator.get_attribute("placeholder") or locator.get_attribute("name") or locator.get_attribute("id") or "")
    except Exception:
        return ""

def field_context(locator):
    bits = [label_for(locator)]
    try:
        bits.append(norm(locator.locator("xpath=..").inner_text(timeout=250)))
    except Exception:
        pass
    try:
        bits.append(norm(locator.get_attribute("autocomplete") or ""))
    except Exception:
        pass
    return " ".join(bits)

def choose_application_form(page):
    forms = page.locator("form")
    best = None
    best_score = -1
    for i in range(forms.count()):
        form = forms.nth(i)
        try:
            context = norm(form.inner_text(timeout=500))
            fields = form.locator("input, textarea, select").count()
            score = fields + (12 if any(x in context for x in ("apply", "application", "resume", "cv", "candidate", "job")) else 0)
            if score > best_score:
                best, best_score = form, score
        except Exception:
            continue
    return best

def fill_form(form, cv_path, cover_letter):
    filled = []
    unknown_required = []
    inputs = form.locator("input, textarea, select")
    for i in range(min(inputs.count(), 100)):
        el = inputs.nth(i)
        try:
            if not el.is_visible() or not el.is_enabled():
                continue
            tag = el.evaluate("(e) => e.tagName.toLowerCase()")
            typ = norm(el.get_attribute("type") or "text")
            if typ in ("hidden", "submit", "button", "reset", "image", "password"):
                continue
            ctx = field_context(el)
            required = el.get_attribute("required") is not None or el.get_attribute("aria-required") == "true"

            if tag == "input" and typ == "file":
                if any(k in ctx for k in ("resume", "cv", "curriculum", "attachment", "upload")):
                    el.set_input_files(str(cv_path))
                    filled.append("resume_upload")
                elif required:
                    unknown_required.append("required_file_upload")
                continue

            if tag == "input" and typ in ("checkbox", "radio"):
                if required and any(k in ctx for k in ("privacy", "terms", "data protection", "acknowledge")):
                    el.check()
                    filled.append("terms_consent")
                elif required and not el.is_checked():
                    unknown_required.append("required_choice:" + (ctx[:80] or "unlabelled"))
                continue

            value = None
            if any(k in ctx for k in ("email", "e-mail")):
                value = PROFILE.get("email")
            elif any(k in ctx for k in ("phone", "mobile", "telephone")):
                value = PROFILE.get("phone")
            elif "first name" in ctx or "given name" in ctx:
                value = PROFILE.get("name", "").split(" ")[0]
            elif "last name" in ctx or "surname" in ctx or "family name" in ctx:
                value = " ".join(PROFILE.get("name", "").split(" ")[1:])
            elif any(k in ctx for k in ("full name", "your name", "candidate name", "name")) and not any(k in ctx for k in ("company", "school", "reference")):
                value = PROFILE.get("name")
            elif any(k in ctx for k in ("city", "location", "current address", "address")):
                value = PROFILE.get("location")
            elif any(k in ctx for k in ("portfolio", "behance", "website", "personal site")):
                value = PORTFOLIO
            elif any(k in ctx for k in ("cover letter", "message to hiring", "additional information", "why are you interested", "application message")):
                value = cover_letter

            if tag == "select":
                if value:
                    options = el.locator("option")
                    chosen = False
                    for j in range(options.count()):
                        opt = options.nth(j)
                        txt = norm(opt.inner_text(timeout=200))
                        val = opt.get_attribute("value") or ""
                        if value and (norm(value) in txt or norm(value) == norm(val)):
                            el.select_option(value=val)
                            chosen = True
                            break
                    if chosen:
                        filled.append(ctx[:60] or "select")
                    elif required:
                        unknown_required.append("required_select:" + (ctx[:80] or "unlabelled"))
                elif required:
                    unknown_required.append("required_select:" + (ctx[:80] or "unlabelled"))
                continue

            if value:
                current = el.input_value(timeout=500)
                if not current:
                    el.fill(str(value))
                    filled.append(ctx[:60] or "field")
            elif required:
                unknown_required.append("required_field:" + (ctx[:80] or "unlabelled"))
        except Exception:
            continue

    return filled, unknown_required

def main():
    if not ENABLED:
        log("WEB_AUTO_APPLY_ENABLED=false; skipped.")
        return
    daily_counts = {"pakistan": 0, "international": 0}
    for record in STATUS.get("sent", []):
        if record.get("channel") == "web_form" and record.get("sent_date") == TODAY:
            region = record.get("region", "international")
            daily_counts[region if region in daily_counts else "international"] += 1
    done = {x.get("key") for x in STATUS.get("sent", []) if x.get("key")}
    attempted = 0
    submitted = 0
    review = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            accept_downloads=False,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
        )
        page = context.new_page()
        for item in sorted(QUEUE, key=lambda x: x.get("score") or 0, reverse=True):
            if attempted >= MAX_PER_RUN:
                break
            region = item.get("region", "international")
            if region not in ("pakistan", "international"):
                region = "international"
            if daily_counts[region] >= (30 if region == "pakistan" else 20):
                continue
            if (item.get("score") or 0) < MIN_SCORE or not item.get("url"):
                continue
            if item.get("mode") not in ("WEB_APPLICATION", "REVIEW", "PHONE_ACTION", "EMAIL_READY", "EMAIL_AND_WHATSAPP_READY"):
                continue
            cv_path = CVS.get(item.get("cv"))
            if not cv_path or not cv_path.exists():
                continue
            key = "web_form|" + item.get("url", "")
            if key in done:
                continue
            attempted += 1
            item["web_apply_status"] = "inspecting"
            try:
                page.goto(item["url"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1200)
                block = is_blocked(page)
                if block:
                    item["web_apply_status"] = block
                    review += 1
                    continue

                apply_url = click_application_link(page)
                if apply_url and apply_url != page.url:
                    page.goto(apply_url, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1000)
                    block = is_blocked(page)
                    if block:
                        item["web_apply_status"] = block
                        item["application_url"] = page.url
                        review += 1
                        continue
                item["application_url"] = page.url

                # Capture employer-published application contacts from the public page.
                body_text = page.locator("body").inner_text(timeout=5000)
                emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", body_text)
                relevant = []
                for email in emails:
                    e = email.lower()
                    if any(x in e for x in ("noreply", "no-reply", "donotreply", "example.com")):
                        continue
                    if re.search(r"(?:career|recruit|hr|hiring|jobs?|talent|apply)", e) or re.search(r"(?:apply|send|email|resume|cv|hiring|recruit|career)", norm(body_text)):
                        relevant.append(e)
                item["page_emails"] = list(dict.fromkeys(relevant))[:5]
                email_invite = re.search(
                    r"(?:send|email|submit|share)\s+(?:your\s+)?(?:cv|resume|application)|"
                    r"(?:apply|application)\s+(?:by|via|through|to)\s+email|"
                    r"email\s+(?:your\s+)?(?:cv|resume|application)",
                    body_text, re.I
                )
                if email_invite and item.get("page_emails"):
                    item["email_application_invited"] = True
                if item.get("email_application_invited") and (item.get("emails") or item.get("page_emails")):
                    item["web_apply_status"] = "email_route_available"
                    continue

                form_count = page.locator("form").count()
                if not form_count:
                    item["web_apply_status"] = "no_public_form_found"
                    review += 1
                    continue

                cover = item.get("email_body") or (
                    "Dear Hiring Team,\n\nI am applying for the " + (item.get("title") or "advertised position") +
                    ". My experience and skills are relevant to this opportunity. Please find my CV attached.\n\n" +
                    "Portfolio: " + PORTFOLIO + "\n\nKind regards,\n" + PROFILE.get("name", "")
                )
                application_form = choose_application_form(page)
                if application_form is None:
                    item["web_apply_status"] = "application_form_not_identified"
                    review += 1
                    continue
                filled, unknown = fill_form(application_form, cv_path, cover)
                item["form_fields_filled"] = filled
                item["form_fields_requiring_review"] = unknown

                # Submit only when all required visible fields are answerable from verified profile data.
                if unknown:
                    item["web_apply_status"] = "needs_manual_answers"
                    review += 1
                    continue

                submit = application_form.get_by_role("button", name=re.compile(r"(submit application|submit|send application|apply now|apply for this job)", re.I))
                if submit.count() == 0:
                    submit = application_form.locator('button[type="submit"], input[type="submit"]')
                if submit.count() == 0:
                    item["web_apply_status"] = "form_filled_submit_control_not_found"
                    review += 1
                    continue

                submit.first.click(timeout=5000)
                page.wait_for_timeout(1800)
                after = norm(page.locator("body").inner_text(timeout=4000)[:10000])
                success_words = ("application submitted", "thank you for applying", "thank you for your application", "successfully submitted", "we have received your application", "application received")
                if any(w in after for w in success_words):
                    item["web_apply_status"] = "submitted_confirmed"
                    STATUS.setdefault("sent", []).append({
                        "key": key, "channel": "web_form", "sent_date": TODAY,
                        "url": item.get("url"), "application_url": page.url,
                        "title": item.get("title"), "score": item.get("score"),
                        "cv": item.get("cv"), "region": region, "confirmation": "page_text"
                    })
                    done.add(key)
                    submitted += 1
                    daily_counts[region] += 1
                else:
                    item["web_apply_status"] = "submitted_unconfirmed_check_manually"
                    STATUS.setdefault("sent", []).append({
                        "key": key, "channel": "web_form_attempt", "sent_date": TODAY,
                        "url": item.get("url"), "application_url": page.url,
                        "title": item.get("title"), "score": item.get("score"),
                        "cv": item.get("cv"), "region": region,
                        "confirmation": "not_detected"
                    })
                    done.add(key)
                    review += 1
            except PlaywrightTimeoutError:
                item["web_apply_status"] = "page_timeout"
                review += 1
            except Exception as exc:
                item["web_apply_status"] = "inspection_error:" + type(exc).__name__
                review += 1
            finally:
                STATUS_PATH.write_text(json.dumps(STATUS, indent=2, ensure_ascii=False), encoding="utf-8")

        browser.close()

    QUEUE_PATH.write_text(json.dumps({"queue": QUEUE}, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"inspected={attempted}, submitted_confirmed={submitted}, manual_review={review}, today_Pakistan={daily_counts['pakistan']}/30, international={daily_counts['international']}/20")

if __name__ == "__main__":
    main()
