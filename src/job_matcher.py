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
    text=(title+" "+description).lower()
    cv=choose_cv(title,description)
    if not cv:
        return 0, None
    keywords = GRAPHIC if cv=="graphic_designer_cv" else BUSINESS
    hits=sum(1 for x in keywords if x in text)
    score=min(95, 45 + hits*5)
    if any(x in text for x in ["visa sponsorship","visa sponsor","relocation","relocation assistance","overseas applicants"]):
        score=min(100,score+8)
    return score,cv
