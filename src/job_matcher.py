import re

GRAPHIC = {
    "graphic","designer","visual","creative","branding","brand","social media",
    "packaging","print","marketing design","digital design","photoshop","illustrator"
}
BUSINESS = {
    "business","coordinator","sales","operations","administrative","admin","office",
    "data entry","computer operator","data processing","document controller",
    "records","back office","support","commercial","customer service","procurement","mis"
}
EXCLUDE = {"accountant","senior accountant","accounts manager","auditor","tax accountant"}

def choose_cv(title, description=""):
    text=(title+" "+description).lower()
    if any(x in text for x in EXCLUDE):
        return None
    g=sum(1 for x in GRAPHIC if x in text)
    b=sum(1 for x in BUSINESS if x in text)
    return "graphic_designer_cv" if g >= b else "business_computer_cv"

def score_job(title, description=""):
    title_text=title.lower()
    text=(title+" "+description).lower()
    cv=choose_cv(title,description)
    if not cv:
        return 0, None

    keywords = GRAPHIC if cv=="graphic_designer_cv" else BUSINESS
    hits=sum(1 for x in keywords if x in text)

    # A clear job title should qualify even when the public RSS description is short.
    score=45 + hits*5
    if cv=="graphic_designer_cv" and ("graphic designer" in title_text or "visual designer" in title_text or "creative designer" in title_text):
        score=max(score,65)
    if cv=="business_computer_cv" and any(x in title_text for x in [
        "business coordinator","sales coordinator","marketing coordinator","operations coordinator",
        "administrative assistant","office assistant","business support","data entry",
        "computer operator","computer assistant","data processing","document controller",
        "records assistant","back office","sales support"
    ]):
        score=max(score,65)

    if any(x in text for x in ["visa sponsorship","visa sponsor","relocation","relocation assistance","overseas applicants"]):
        score=min(100,score+8)

    return min(100,score),cv
