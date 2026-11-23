import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://agent.tinyfish.ai/v1"
MAX_WAIT_SECONDS = 720
POLL_SECONDS = 15
RECENT_DAYS = 20

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "posts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "employer": {"type": "string"},
                    "role": {"type": "string"},
                    "city": {"type": "string"},
                    "published_date": {"type": "string"},
                    "post_url": {"type": "string"},
                    "description": {"type": "string"},
                    "emails": {"type": "array", "items": {"type": "string"}},
                    "phones": {"type": "array", "items": {"type": "string"}},
                    "application_instructions": {"type": "string"},
                    "whatsapp_application_invited": {"type": "boolean"},
                    "email_application_invited": {"type": "boolean"}
                },
                "required": [
                    "employer", "role", "city", "published_date", "post_url",
                    "description", "emails", "phones", "application_instructions",
                    "whatsapp_application_invited", "email_application_invited"
                ]
            }
        }
    },
    "required": ["posts"]
}

def api_request(method, path, api_key, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        API + path,
        data=body,
        method=method,
        headers={
            "X-API-Key": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1200]
        raise RuntimeError(f"TinyFish API HTTP {exc.code}: {detail}") from exc

def parse_date(value):
    value = (value or "").strip()
    if not value:
        return None
    relative = re.search(r"\b(\d+)\s+(day|days|week|weeks)\s+ago\b", value, re.I)
    if relative:
        amount = int(relative.group(1))
        days = amount * (7 if relative.group(2).lower().startswith("week") else 1)
        return datetime.now(timezone.utc) - timedelta(days=days)
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except ValueError:
        return None

def normalize_contact_list(values, phone=False):
    output = []
    for value in values or []:
        value = str(value).strip()
        if phone:
            digits = re.sub(r"\D", "", value)
            if not 10 <= len(digits) <= 15:
                continue
            if digits.startswith("92") and len(digits) == 12:
                value = "+" + digits
            elif digits.startswith("0") and len(digits) == 11:
                value = digits
            else:
                value = "+" + digits
        else:
            if not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value):
                continue
            value = value.lower()
        if value not in output:
            output.append(value)
    return output[:8]

def run_platform(platform, url, api_key, profile_id):
    goal = (
        f"Search {platform} using the saved signed-in browser session for Pakistan-based hiring posts "
        f"published within the last {RECENT_DAYS} days. Search these roles: Graphic Designer, Visual "
        "Designer, Creative Designer, Social Media Designer, Marketing Designer, Packaging Designer, "
        "Business Coordinator, Sales Coordinator, Administrative Assistant, Office Assistant, "
        "Computer Operator, Data Entry Operator and Business Support. Use the platform's native "
        "search and relevant hiring hashtags. Inspect original posts, not just snippets. Return up to "
        "15 genuinely relevant individual hiring posts. Include only dates, employer names, post URLs, "
        "emails and phone numbers actually visible in the post/account. Capture exact application "
        "instructions. Set whatsapp_application_invited true only if the post explicitly tells candidates "
        "to apply/send a CV/contact HR via WhatsApp. Set email_application_invited true only if it "
        "explicitly invites applications by email. Do not infer permission from a displayed contact alone. "
        "Exclude posts older than 20 days when their date is visible; do not invent dates or contacts. "
        "Do not send messages, apply, follow accounts, join groups, comment, or change account settings. "
        "If search is blocked or the saved login has expired, return an empty posts array and explain that "
        "in the description of the run result."
    )
    payload = {
        "url": url,
        "goal": goal,
        "output_schema": OUTPUT_SCHEMA,
        "use_profile": True,
        "profile_id": profile_id,
        "browser_profile": "lite",
        "agent_config": {"max_duration_seconds": 480}
    }
    started = api_request("POST", "/automation/run-async", api_key, payload)
    run_id = started.get("run_id")
    if not run_id:
        raise RuntimeError(f"TinyFish did not return a run_id for {platform}: {started}")
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(POLL_SECONDS)
        state = api_request("GET", "/runs/" + run_id, api_key)
        status = state.get("status")
        if status == "COMPLETED":
            result = state.get("result") or {}
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    result = {}
            return result.get("posts", []) if isinstance(result, dict) else []
        if status in ("FAILED", "CANCELLED"):
            raise RuntimeError(f"TinyFish {platform} run {status}: {state.get('error')}")
    raise RuntimeError(f"TinyFish {platform} run exceeded the {MAX_WAIT_SECONDS}s polling window; run_id={run_id}")

def main():
    enabled = os.getenv("TINYFISH_SOCIAL_SEARCH_ENABLED", "").strip().lower() == "true"
    api_key = os.getenv("TINYFISH_API_KEY", "").strip()
    profile_id = os.getenv("TINYFISH_PROFILE_ID", "").strip()
    if not enabled:
        print("Signed-in social search is disabled. Publicly indexed social searches remain enabled.")
        return
    if not api_key or not profile_id:
        print("Signed-in social search skipped: add TINYFISH_API_KEY and TINYFISH_PROFILE_ID GitHub secrets.")
        return

    jobs_path = ROOT / "data" / "jobs.json"
    payload = json.loads(jobs_path.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", [])
    seen_urls = {str(j.get("url", "")).rstrip("/") for j in jobs}
    from job_matcher import score_job

    sources = [
        ("Facebook", "https://www.facebook.com/search/posts/?q=jobs%20hiring%20Pakistan"),
        ("Instagram", "https://www.instagram.com/")
    ]
    added = 0
    for platform, url in sources:
        try:
            posts = run_platform(platform, url, api_key, profile_id)
            print(f"TinyFish {platform}: received {len(posts)} candidate posts.")
            for post in posts:
                role = str(post.get("role") or "").strip()
                employer = str(post.get("employer") or "").strip()
                post_url = str(post.get("post_url") or "").strip()
                if not role or not post_url.startswith("https://"):
                    continue
                normalized_url = post_url.rstrip("/")
                if normalized_url in seen_urls:
                    continue
                published = str(post.get("published_date") or "").strip()
                parsed = parse_date(published)
                if parsed and parsed < datetime.now(timezone.utc) - timedelta(days=RECENT_DAYS):
                    continue

                emails = normalize_contact_list(post.get("emails"))
                phones = normalize_contact_list(post.get("phones"), phone=True)
                instructions = str(post.get("application_instructions") or "").strip()
                description_parts = [
                    str(post.get("description") or "").strip(),
                    "Employer: " + employer if employer else "",
                    "Location: " + str(post.get("city") or "").strip() if post.get("city") else "",
                    "Published: " + published if published else "Publication date not verified.",
                    "Application instructions: " + instructions if instructions else "",
                    "Published application email: " + ", ".join(emails) if emails else "",
                    "Published phone: " + ", ".join(phones) if phones else ""
                ]
                if post.get("email_application_invited") is True:
                    description_parts.append("The post explicitly invites applications by email.")
                if post.get("whatsapp_application_invited") is True:
                    description_parts.append("The post explicitly invites applications via WhatsApp.")
                description = "\n".join(x for x in description_parts if x)
                title = f"{role} — {employer}" if employer else role
                score, cv = score_job(title, description)
                if score < 55 or not cv:
                    continue
                row = {
                    "title": title,
                    "url": post_url,
                    "published": published,
                    "description": description,
                    "source": f"{platform} (TinyFish signed-in search)",
                    "match_score": score,
                    "cv": cv,
                    "query": f"authenticated {platform} hiring search Pakistan",
                    "social_platform": platform,
                    "social_emails": emails,
                    "social_phones": phones,
                    "application_instructions": instructions,
                    "date_unverified": not bool(parsed),
                    "email_application_invited": post.get("email_application_invited") is True,
                    "whatsapp_application_invited": post.get("whatsapp_application_invited") is True
                }
                jobs.append(row)
                seen_urls.add(normalized_url)
                added += 1
        except Exception as exc:
            print(f"TinyFish {platform} search failed: {type(exc).__name__}: {exc}")
            # Keep the main job pipeline running if one social source is temporarily unavailable.

    jobs.sort(key=lambda item: (item.get("match_score", 0), item.get("published", "")), reverse=True)
    payload["jobs"] = jobs[:150]
    payload["signed_in_social_search"] = {
        "provider": "TinyFish",
        "enabled": True,
        "added_this_run": added,
        "platforms": ["Facebook", "Instagram"],
        "recent_window_days": RECENT_DAYS
    }
    jobs_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Added {added} signed-in social hiring posts; total stored jobs: {len(payload['jobs'])}.")

if __name__ == "__main__":
    main()
