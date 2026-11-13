from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from textwrap import wrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cvs"
OUT.mkdir(exist_ok=True)
W, H = A4

NAVY = colors.HexColor("#12233F")
BLUE = colors.HexColor("#1E5AA8")
ORANGE = colors.HexColor("#F39A24")
TEAL = colors.HexColor("#087E8B")
LIGHT = colors.HexColor("#F4F6F8")
MID = colors.HexColor("#667085")
DARK = colors.HexColor("#17202A")

NAME = "FAHAD ASIF"
EMAIL = "Fahadasif77@yahoo.com"
PHONE = "+92 340 7301498"
LOCATION = "Lahore, Pakistan"
BEHANCE = "https://www.behance.net/zubairkhan1"

EXPERIENCE = [
    ("Graphic Designer — Tech Troops", "Jan 2025 – Present", [
        "Created social media graphics for 8+ brands including USA Carship, American Carship, American X Logistic, American Car Move, Northside Family and Weightloss, Enablers Tech, Atlanta E-Waste and Tech Troops.",
        "Developed printed marketing materials, aligned creative with brand guidelines and managed post scheduling through Meta Business Suite."
    ]),
    ("Graphic Designer — ODR Foods", "Jan 2024 – Jan 2025", [
        "Designed brochures, packaging, standees, flyers and social graphics.",
        "Collaborated with sales and marketing teams and delivered approved production-ready artwork."
    ]),
    ("Graphic Designer — Zahid Packages (Pvt) Ltd", "Sep 2021 – Jan 2024", [
        "Led a team of designers and produced packaging, banners, flyers, corporate materials and promotional displays.",
        "Collaborated with clients and improved workflow through structured processes and templates."
    ]),
    ("Sales Coordinator — Zahid Packages", "Mar 2021 – Aug 2021", [
        "Prepared production planning schedules, maintained Oracle cheque records and supported sales performance reporting."
    ]),
    ("Photo Editor — Cresset Technologies", "Feb 2020 – Dec 2020", [
        "Edited photographic content for marketing and web use, including colour correction, retouching and compositing."
    ])
]

EDUCATION = [
    "University of the Punjab — B.Com (2 Years), Mar 2018 – Jan 2021",
    "Vocational Training — Graphic Designing (1 Year), Mar 2018 – Jan 2021",
    "Government College Township — F.Sc (Pre-Engineering), Mar 2013 – Mar 2015",
    "Sacred Heart High School — Matric, Mar 2010 – Mar 2012"
]

def header(c, title, subtitle, accent):
    c.setFillColor(NAVY)
    c.rect(0, H-92, W, 92, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(42, H-43, NAME)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(accent)
    c.drawString(42, H-61, title.upper())
    c.setFont("Helvetica", 7.5)
    c.setFillColor(colors.HexColor("#DDE5EF"))
    c.drawRightString(W-42, H-61, PHONE + "  •  " + EMAIL)
    c.drawRightString(W-42, H-75, LOCATION + "  •  " + BEHANCE)

def footer(c, page, accent):
    c.setStrokeColor(colors.HexColor("#D8DEE6"))
    c.line(42, 30, W-42, 30)
    c.setFillColor(MID)
    c.setFont("Helvetica", 6.8)
    c.drawString(42, 19, "FAHAD ASIF  •  PROFESSIONAL APPLICATION PORTFOLIO")
    c.setFillColor(accent)
    c.drawRightString(W-42, 19, str(page))

def section(c, y, title, accent):
    c.setFillColor(accent)
    c.rect(42, y-2, 5, 14, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(54, y, title.upper())
    c.setStrokeColor(colors.HexColor("#D8DEE6"))
    c.line(54, y-4, W-42, y-4)
    return y-20

def text(c, x, y, value, size=8.2, leading=10.5, color=DARK, bold=False, width=112):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    for line in wrap(value, width):
        c.drawString(x, y, line)
        y -= leading
    return y

def bullets(c, y, items, width=106):
    for item in items:
        c.setFillColor(ORANGE)
        c.circle(48, y+2, 1.5, fill=1, stroke=0)
        y = text(c, 56, y, item, 8.1, 10.4, DARK, False, width)
        y -= 2
    return y

def cover_letter(c, role, accent, body_paragraphs):
    header(c, role, "", accent)
    y = H-125
    y = section(c, y, "Cover Letter", accent)
    y = text(c, 42, y, "Dear Hiring Manager,", 9.2, 13, DARK, False, 96) - 8
    for p in body_paragraphs:
        y = text(c, 42, y, p, 9.1, 13.2, DARK, False, 96) - 7
    y = text(c, 42, y, "Sincerely,", 9.1, 13, DARK, False, 96) - 18
    y = text(c, 42, y, "Fahad Asif", 9.2, 13, NAVY, True, 96)
    text(c, 42, y-1, role, 8.3, 11, MID, False, 96)
    footer(c, 1, accent)
    c.showPage()

def cv_page(c, role, subtitle, profile, skills, accent):
    header(c, role, subtitle, accent)
    y = H-125
    y = section(c, y, "Professional Profile", accent)
    y = text(c, 42, y, profile, 8.4, 11.2, DARK, False, 108) - 8
    y = section(c, y, "Core Skills", accent)
    c.setFillColor(LIGHT)
    c.roundRect(42, y-57, W-84, 60, 5, fill=1, stroke=0)
    y2 = y-14
    for i, line in enumerate(wrap(skills, 105)):
        y2 = text(c, 50, y2, line, 7.7, 10.2, DARK, False, 105)
    y -= 72
    y = section(c, y, "Professional Experience", accent)
    for title, dates, items in EXPERIENCE:
        y = text(c, 42, y, title, 8.7, 10.5, NAVY, True, 105)
        y = text(c, 42, y, dates, 7.4, 9.5, accent, True, 105)
        y = bullets(c, y-1, items, 103)
        y -= 3
        if y < 95:
            footer(c, 2, accent); c.showPage(); header(c, role, subtitle, accent); y=H-125
    footer(c, 2, accent)
    c.showPage()

def cv_page_two(c, role, targets, accent):
    header(c, role, "", accent)
    y=H-125
    y=section(c,y,"Education",accent)
    for item in EDUCATION:
        y=bullets(c,y,[item],105)
        y-=1
    y-=5
    y=section(c,y,"Languages & Interests",accent)
    y=text(c,42,y,"Languages: English • Urdu • Punjabi",8.3,11,DARK,False,105)-4
    y=text(c,42,y,"Interests: Travel • Music • Writing",8.3,11,DARK,False,105)-8
    y=section(c,y,"Target Roles",accent)
    y=text(c,42,y,targets,8.2,11.1,DARK,False,105)-8
    c.setFillColor(LIGHT)
    c.roundRect(42,y-48,W-84,50,5,fill=1,stroke=0)
    y-=15
    y=text(c,50,y,"OPEN TO",8.2,10,NAVY,True,105)
    text(c,50,y,"Pakistan • UAE • Saudi Arabia • Qatar • Oman • Bahrain • Kuwait • UK • Germany • Netherlands • Ireland • Australia • Canada • New Zealand",7.6,10.2,DARK,False,105)
    footer(c,3,accent)
    c.showPage()

def portfolio_page(c, title, intro, projects, accent, page):
    header(c, "Selected Portfolio", "", accent)
    y=H-125
    y=section(c,y,title,accent)
    y=text(c,42,y,intro,8.4,11.2,DARK,False,105)-8
    for name, desc in projects:
        c.setFillColor(NAVY)
        c.roundRect(42,y-62,W-84,62,5,fill=1,stroke=0)
        c.setFillColor(accent)
        c.rect(42,y-62,6,62,fill=1,stroke=0)
        y=text(c,56,y-17,name,9.3,11,NAVY if False else colors.white,True,100)
        text(c,56,y-2,desc,7.7,10.2,colors.HexColor("#DDE5EF"),False,100)
        y-=75
    y=text(c,42,y,"Portfolio source: Behance",8,10,MID,True,105)
    text(c,42,y,BEHANCE,7.8,10,MID,False,105)
    footer(c,page,accent)
    c.showPage()

def make_graphic(path):
    c=canvas.Canvas(str(path),pagesize=A4)
    cover_letter(c,"Graphic Designer",ORANGE,[
        "I am applying for Graphic Designer and related creative roles. I bring 4+ years of professional experience across branding, social media, packaging, print, marketing collateral, photo editing and digital content.",
        "My professional work has included supporting multiple brands, collaborating with sales and marketing teams, managing brand consistency and delivering production-ready artwork to deadlines. My core tools include Adobe Photoshop, Illustrator, CorelDRAW and InPage, with Figma and Blender at a basic level.",
        "I also use AI-assisted creative tools including ChatGPT, Midjourney, Leonardo AI, Kling AI, Hailuo AI and PixVerse to support ideation and content development. I am open to opportunities in Pakistan and internationally, including relocation."
    ])
    cv_page(c,"Graphic Designer","BRANDING • SOCIAL MEDIA • PACKAGING • PRINT • AI-ASSISTED DESIGN",
        "Creative and results-driven Graphic Designer with 4+ years of professional experience across branding, social media, packaging, print, marketing collateral, photo editing and digital content. Experienced in supporting multiple brands, collaborating with marketing and sales teams, managing production-ready artwork and using AI-assisted creative tools.",
        "Adobe Photoshop • Adobe Illustrator • CorelDRAW • InPage • Branding • Social Media Graphics • Marketing Collateral • Packaging • Print Design • Photo Editing • Retouching • Compositing • Content Creation • Meta Business Suite • ChatGPT • Midjourney • Leonardo AI • Kling AI • Hailuo AI • PixVerse • Figma (Basic) • Blender (Basic) • Clipchamp",ORANGE)
    cv_page_two(c,"Graphic Designer","Graphic Designer • Visual Designer • Creative Designer • Social Media Designer • Marketing Designer • Brand Designer • Packaging Designer • Digital Designer • Content Designer • Graphic Artist",ORANGE)
    portfolio_page(c,"Social Media & Digital Marketing","Selected client-facing work demonstrating social content, campaign graphics, brand consistency and marketing communication.",[
        ("Tech Troops — Multi-brand Social Content","Social graphics and scheduled content supporting USA Carship, American Carship, American X Logistic, American Car Move, Northside Family and Weightloss, Enablers Tech, Atlanta E-Waste and Tech Troops."),
        ("Campaign & Content Design","Digital marketing visuals developed for social platforms with attention to hierarchy, brand identity and conversion-oriented communication.")
    ],ORANGE,4)
    portfolio_page(c,"Branding, Packaging & Print","Work spanning product presentation, packaging, promotional collateral and production-ready print assets.",[
        ("ODR Foods — Packaging & Marketing","Brochures, packaging, standees, flyers and social graphics developed alongside sales and marketing requirements."),
        ("Zahid Packages — Packaging & Corporate","Packaging, banners, flyers, corporate materials and promotional displays, including team-led production workflows.")
    ],ORANGE,5)
    c.save()

def make_business(path):
    c=canvas.Canvas(str(path),pagesize=A4)
    cover_letter(c,"Business & Computer Professional",TEAL,[
        "I am interested in business support, sales coordination, operations, administrative, data-entry and computer-based office roles. I hold a B.Com background and bring practical experience in sales coordination, production planning, reporting, records management, digital marketing support and graphic design.",
        "As a Sales Coordinator, I prepared production planning schedules, maintained Oracle cheque records and supported sales performance reporting. My wider experience has strengthened my ability to handle computer-based tasks, documentation, coordination, deadlines and structured workflows.",
        "My design background is an additional advantage for marketing support, presentations, visual communication, social media and customer-facing business materials. I am open to opportunities in Pakistan and internationally where relocation is supported."
    ])
    cv_page(c,"Business & Computer Professional","COORDINATION • OPERATIONS • DATA • ADMIN SUPPORT",
        "Business and computer-focused professional with a B.Com background and experience spanning sales coordination, production planning, reporting, records management, digital marketing support and graphic design. Strong in computer-based office work, documentation, coordination, data handling, reporting and communication.",
        "Sales Coordination • Production Planning • Reporting • Records Management • Team Coordination • Computer-based Office Work • Data Entry • Document Handling • Oracle Records • Report Preparation • Social Media Support • Meta Business Suite • Marketing Support • Photoshop • Illustrator • CorelDRAW • InPage • Figma (Basic)",TEAL)
    cv_page_two(c,"Business & Computer Professional","Business Coordinator • Sales Coordinator • Marketing Coordinator • Operations Coordinator • Administrative Assistant • Office Assistant • Business Support Executive • Commercial Coordinator • Data Entry Operator • Data Entry Clerk • Computer Operator • Computer Assistant • Data Processing Assistant • Document Controller • Records/Data Assistant • Back Office Executive • MIS/Data Assistant • Customer Support Executive • Sales Support • Administrative Support • Business Assistant • Commercial Assistant • Operations Assistant",TEAL)
    portfolio_page(c,"Marketing & Communication Work","Supporting evidence of practical computer-based creative, marketing and communication capability.",[
        ("Digital Marketing Support","Social media graphics, content scheduling and marketing materials for multiple brands and client accounts."),
        ("Packaging & Corporate Materials","Brochures, packaging, flyers, standees, banners and promotional materials produced in collaboration with business and marketing teams.")
    ],TEAL,4)
    portfolio_page(c,"Selected Professional Work","A concise presentation of relevant creative projects that complement business, coordination and marketing-support applications.",[
        ("Multi-brand Client Support","Work across multiple client brands requiring coordination, brand consistency, deadlines and repeatable workflows."),
        ("Production & Workflow Support","Experience connecting creative requirements with approvals, production-ready files and structured processes.")
    ],TEAL,5)
    c.save()

make_graphic(OUT/"graphic_designer_cv.pdf")
make_business(OUT/"business_computer_cv.pdf")
print("Generated:", OUT/"graphic_designer_cv.pdf", OUT/"business_computer_cv.pdf")
