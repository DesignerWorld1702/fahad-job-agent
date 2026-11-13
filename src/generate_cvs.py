from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from textwrap import wrap

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"cvs"; OUT.mkdir(exist_ok=True)
W,H=A4
NAVY=colors.HexColor("#14213D"); BLUE=colors.HexColor("#2563EB"); ORANGE=colors.HexColor("#F59E0B")
TEAL=colors.HexColor("#0F766E"); LIGHT=colors.HexColor("#F4F7FB"); MID=colors.HexColor("#64748B")
DARK=colors.HexColor("#172033")
NAME="FAHAD ASIF"; EMAIL="Fahadasif77@yahoo.com"; PHONE="+92 340 7301498"
LOCATION="Lahore, Pakistan"; BEHANCE="https://www.behance.net/zubairkhan1"

EXPERIENCE=[
("Graphic Designer","Tech Troops","Jan 2025 – Present",[
"Created social media graphics for 8+ brands including USA Carship, American Carship, American X Logistic, American Car Move, Northside Family and Weightloss, Enablers Tech, Atlanta E-Waste and Tech Troops.",
"Developed printed marketing materials, aligned creative with brand guidelines and managed post scheduling through Meta Business Suite."]),
("Graphic Designer","ODR Foods","Jan 2024 – Jan 2025",[
"Designed brochures, packaging, standees, flyers and social graphics.",
"Collaborated with sales and marketing teams and delivered approved production-ready artwork."]),
("Graphic Designer","Zahid Packages (Pvt) Ltd","Sep 2021 – Jan 2024",[
"Led a team of designers and produced packaging, banners, flyers, corporate materials and promotional displays.",
"Collaborated with clients and improved workflow through structured processes and templates."]),
("Sales Coordinator","Zahid Packages","Mar 2021 – Aug 2021",[
"Prepared production planning schedules, maintained Oracle cheque records and supported sales performance reporting."]),
("Photo Editor","Cresset Technologies","Feb 2020 – Dec 2020",[
"Edited photographic content for marketing and web use, including colour correction, retouching and compositing."])]

EDUCATION=[
"University of the Punjab — B.Com (2 Years), Mar 2018 – Jan 2021",
"Vocational Training — Graphic Designing (1 Year), Mar 2018 – Jan 2021",
"Government College Township — F.Sc (Pre-Engineering), Mar 2013 – Mar 2015",
"Sacred Heart High School — Matric, Mar 2010 – Mar 2012"]

def T(c,x,y,s,size=8,lead=10,color=DARK,b=False,maxchars=105):
    c.setFont("Helvetica-Bold" if b else "Helvetica",size); c.setFillColor(color)
    for line in wrap(s,maxchars):
        c.drawString(x,y,line); y-=lead
    return y

def header(c,title,accent):
    c.setFillColor(NAVY); c.rect(0,H-86,W,86,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",24); c.drawString(38,H-40,NAME)
    c.setFont("Helvetica-Bold",8.5); c.setFillColor(accent); c.drawString(38,H-56,title.upper())
    c.setFont("Helvetica",7); c.setFillColor(colors.HexColor("#DDE5EF"))
    c.drawRightString(W-38,H-56,PHONE+"  •  "+EMAIL)
    c.drawRightString(W-38,H-69,LOCATION+"  •  "+BEHANCE)

def footer(c,accent):
    c.setStrokeColor(colors.HexColor("#D8DEE8")); c.line(38,27,W-38,27)
    c.setFont("Helvetica",6.5); c.setFillColor(MID); c.drawString(38,16,"FAHAD ASIF")
    c.setFillColor(accent); c.drawRightString(W-38,16,str(c.getPageNumber()))

def section(c,y,title,accent):
    c.setFillColor(accent); c.rect(38,y-2,4,13,fill=1,stroke=0)
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold",9.5); c.drawString(50,y,title.upper())
    c.setStrokeColor(colors.HexColor("#D8DEE8")); c.line(50,y-4,W-38,y-4)
    return y-18

def bullets(c,y,items,accent,size=7.6,lead=9.2):
    for item in items:
        c.setFillColor(accent); c.circle(44,y+2,1.3,fill=1,stroke=0)
        y=T(c,52,y,item,size,lead,DARK,False,101)-2
    return y

def cover(c,role,accent,paras):
    header(c,role,accent); y=H-116; y=section(c,y,"Cover Letter",accent)
    y=T(c,38,y,"Dear Hiring Manager,",9,12,DARK,False,100)-9
    for q in paras: y=T(c,38,y,q,8.8,12.2,DARK,False,100)-8
    y=T(c,38,y,"Sincerely,",8.8,12,DARK,False,100)-18
    T(c,38,y,"Fahad Asif",9,10,NAVY,True,100); footer(c,accent); c.showPage()

def cv(c,title,accent,profile,skills,target):
    header(c,title,accent); y=H-116
    y=section(c,y,"Professional Profile",accent); y=T(c,38,y,profile,8.1,10.2,DARK,False,106)-7
    y=section(c,y,"Core Skills",accent)
    c.setFillColor(LIGHT); c.roundRect(38,y-58,W-76,61,5,fill=1,stroke=0)
    y=T(c,48,y-12,skills,7.2,9.2,DARK,False,108)-7
    y-=9; y=section(c,y,"Professional Experience",accent)
    for role,company,date,items in EXPERIENCE:
        y=T(c,38,y,role+" — "+company,8.4,9.8,NAVY,True,106)
        y=T(c,38,y,date,7.1,8.5,accent,True,106)
        y=bullets(c,y,items,accent)
        if y<65:
            footer(c,accent); c.showPage(); header(c,title,accent); y=H-116
    footer(c,accent); c.showPage()
    header(c,title,accent); y=H-116
    y=section(c,y,"Education",accent); y=bullets(c,y,EDUCATION,accent,7.8,9.5)-4
    y=section(c,y,"Languages & Interests",accent)
    y=T(c,38,y,"Languages: English • Urdu • Punjabi",8,10,DARK,False,106)-4
    y=T(c,38,y,"Interests: Travel • Music • Writing",8,10,DARK,False,106)-7
    y=section(c,y,"Target Roles",accent); y=T(c,38,y,target,7.8,10,DARK,False,106)-8
    c.setFillColor(LIGHT); c.roundRect(38,y-48,W-76,50,5,fill=1,stroke=0)
    T(c,48,y-14,"OPEN TO",8,10,NAVY,True,106)
    T(c,48,y-25,"Pakistan • UAE • Saudi Arabia • Qatar • Oman • Bahrain • Kuwait • UK • Germany • Netherlands • Ireland • Australia • Canada • New Zealand",7.1,9,DARK,False,108)
    footer(c,accent); c.showPage()

def portfolio(c,title,accent,items,page):
    header(c,"Selected Portfolio",accent); y=H-116; y=section(c,y,title,accent)
    for name,desc in items:
        c.setFillColor(NAVY); c.roundRect(38,y-68,W-76,68,5,fill=1,stroke=0)
        c.setFillColor(accent); c.rect(38,y-68,5,68,fill=1,stroke=0)
        y=T(c,52,y-16,name,9,10,colors.white,True,100)
        T(c,52,y-3,desc,7.4,9.4,colors.HexColor("#DDE5EF"),False,100); y-=81
    T(c,38,y,"Portfolio: "+BEHANCE,7.5,9,MID,False,106); footer(c,accent); c.showPage()

def graphic(path):
    c=canvas.Canvas(str(path),pagesize=A4)
    cover(c,"Graphic Designer",ORANGE,[
    "I am applying for Graphic Designer and related creative roles. I bring 4+ years of professional experience across branding, social media, packaging, print, marketing collateral, photo editing and digital content.",
    "My work includes supporting multiple brands, collaborating with sales and marketing teams, maintaining brand consistency and delivering production-ready artwork to deadlines. My core tools include Adobe Photoshop, Illustrator, CorelDRAW and InPage, with Figma and Blender at a basic level.",
    "I also use AI-assisted creative tools including ChatGPT, Midjourney, Leonardo AI, Kling AI, Hailuo AI and PixVerse to support ideation and content development. I am open to Pakistan and international relocation opportunities."])
    cv(c,"Graphic Designer",ORANGE,
    "Creative and results-driven Graphic Designer with 4+ years of professional experience across branding, social media, packaging, print, marketing collateral, photo editing and digital content. Experienced in supporting multiple brands, collaborating with marketing and sales teams, managing production-ready artwork and using AI-assisted creative tools.",
    "Adobe Photoshop • Adobe Illustrator • CorelDRAW • InPage • Branding • Social Media Graphics • Marketing Collateral • Packaging • Print Design • Photo Editing • Retouching • Compositing • Content Creation • Meta Business Suite • ChatGPT • Midjourney • Leonardo AI • Kling AI • Hailuo AI • PixVerse • Figma (Basic) • Blender (Basic) • Clipchamp",
    "Graphic Designer • Visual Designer • Creative Designer • Social Media Designer • Marketing Designer • Brand Designer • Packaging Designer • Digital Designer • Content Designer • Graphic Artist")
    portfolio(c,"Social Media & Digital Marketing",ORANGE,[("Tech Troops — Multi-brand Social Content","Social graphics and scheduled content supporting USA Carship, American Carship, American X Logistic, American Car Move, Northside Family and Weightloss, Enablers Tech, Atlanta E-Waste and Tech Troops."),("Campaign & Content Design","Digital marketing visuals developed for social platforms with attention to hierarchy, brand identity and marketing communication.")],4)
    portfolio(c,"Branding, Packaging & Print",ORANGE,[("ODR Foods — Packaging & Marketing","Brochures, packaging, standees, flyers and social graphics developed alongside sales and marketing requirements."),("Zahid Packages — Packaging & Corporate","Packaging, banners, flyers, corporate materials and promotional displays, including team-led production workflows.")],5)
    c.save()

def business(path):
    c=canvas.Canvas(str(path),pagesize=A4)
    cover(c,"Business & Computer Professional",TEAL,[
    "I am interested in business support, sales coordination, operations, administrative, data-entry and computer-based office roles. I hold a B.Com background and bring practical experience in sales coordination, production planning, reporting, records management, digital marketing support and graphic design.",
    "As a Sales Coordinator, I prepared production planning schedules, maintained Oracle cheque records and supported sales performance reporting. My wider experience strengthened my ability to handle computer-based tasks, documentation, coordination, deadlines and structured workflows.",
    "My design background is an additional advantage for marketing support, presentations, visual communication, social media and customer-facing business materials. I am open to Pakistan and international relocation opportunities."])
    cv(c,"Business / Computer / Administrative",TEAL,
    "Business and computer-focused professional with a B.Com background and experience spanning sales coordination, production planning, reporting, records management, digital marketing support and graphic design. Strong in computer-based office work, documentation, coordination, data handling, reporting and communication.",
    "Sales Coordination • Production Planning • Reporting • Records Management • Team Coordination • Computer-based Office Work • Data Entry • Document Handling • Oracle Records • Report Preparation • Social Media Support • Meta Business Suite • Marketing Support • Photoshop • Illustrator • CorelDRAW • InPage • Figma (Basic)",
    "Business Coordinator • Sales Coordinator • Marketing Coordinator • Operations Coordinator • Administrative Assistant • Office Assistant • Business Support Executive • Commercial Coordinator • Data Entry Operator • Data Entry Clerk • Computer Operator • Computer Assistant • Data Processing Assistant • Document Controller • Records/Data Assistant • Back Office Executive • MIS/Data Assistant • Customer Support Executive • Sales Support • Administrative Support • Business Assistant • Commercial Assistant • Operations Assistant")
    portfolio(c,"Marketing & Communication Work",TEAL,[("Digital Marketing Support","Social media graphics, content scheduling and marketing materials for multiple brands and client accounts."),("Packaging & Corporate Materials","Brochures, packaging, flyers, standees, banners and promotional materials produced with business and marketing teams.")],4)
    portfolio(c,"Selected Professional Work",TEAL,[("Multi-brand Client Support","Work across multiple client brands requiring coordination, brand consistency, deadlines and repeatable workflows."),("Production & Workflow Support","Experience connecting creative requirements with approvals, production-ready files and structured processes.")],5)
    c.save()

graphic(OUT/"graphic_designer_cv.pdf"); business(OUT/"business_computer_cv.pdf")
