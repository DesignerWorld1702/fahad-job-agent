from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from textwrap import wrap

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"cvs"
OUT.mkdir(exist_ok=True)
W,H=A4

EXPERIENCE=[
("Tech Troops — Graphic Designer","Jan 2025 – Present","Created social graphics for 8+ brands including USA Carship, American Carship, American X Logistic, American Car Move, Northside Family and Weightloss, Enablers Tech, Atlanta E-Waste and Tech Troops. Developed printed marketing materials, aligned designs with brand guidelines and managed Meta Business Suite scheduling."),
("ODR Foods — Graphic Designer","Jan 2024 – Jan 2025","Designed brochures, packaging, standees, flyers and social graphics. Applied brand guidelines, collaborated with sales and marketing, and delivered production-ready artwork."),
("Zahid Packages (Pvt) Ltd — Graphic Designer","Sep 2021 – Jan 2024","Led a team of designers and produced packaging, banners, flyers, corporate materials and promotional displays. Collaborated with clients and streamlined workflow through structured processes and templates."),
("Zahid Packages — Sales Coordinator","Mar 2021 – Aug 2021","Prepared production planning schedules, maintained Oracle cheque records and supported sales performance reporting."),
("Cresset Technologies — Photo Editor","Feb 2020 – Dec 2020","Edited photographic content for marketing and web use, including color correction, retouching and compositing, while maintaining consistent quality and branding.")
]
EDU=["University of Punjab — B.Com (2 Years), Mar 2018 – Jan 2021","Vocational Training — Graphic Designing (1 Year), Mar 2018 – Jan 2021","Government College Township — F.Sc (Pre-Engineering), Mar 2013 – Mar 2015","Sacred Heart High School — Matric, Mar 2010 – Mar 2012"]

def make(path, subtitle, profile, skills, targets):
    c=canvas.Canvas(str(path),pagesize=A4); y=H-42
    c.setFont("Helvetica-Bold",20); c.drawString(42,y,"FAHAD ASIF"); y-=22
    c.setFont("Helvetica-Bold",8.5); c.drawString(42,y,subtitle); y-=18
    c.setFont("Helvetica",8); c.drawString(42,y,"Lahore, Pakistan | +92 340 7301498 | Fahadasif77@yahoo.com"); y-=11
    c.drawString(42,y,"Portfolio: https://www.behance.net/zubairkhan1"); y-=20
    sections=[("PROFILE",profile),("CORE SKILLS",skills),("PROFESSIONAL EXPERIENCE",""),("EDUCATION",""),("TARGET ROLES",targets)]
    for head,text in sections:
        c.setFont("Helvetica-Bold",10); c.drawString(42,y,head); y-=14
        c.setFont("Helvetica",8)
        items=[]
        if head=="PROFESSIONAL EXPERIENCE":
            for role,dates,desc in EXPERIENCE: items.append((role+" ("+dates+")",desc))
        elif head=="EDUCATION":
            items=[("",x) for x in EDU]
        else: items=[("",text)]
        for label,body in items:
            if label:
                c.setFont("Helvetica-Bold",8); 
                if y<45: c.showPage(); y=H-42; c.setFont("Helvetica-Bold",8)
                c.drawString(42,y,label); y-=11
                c.setFont("Helvetica",8)
            for line in wrap(body,112):
                if y<42: c.showPage(); y=H-42; c.setFont("Helvetica",8)
                c.drawString(42,y,line); y-=10
            y-=4
    c.save()

make(OUT/"graphic_designer_cv.pdf",
"GRAPHIC DESIGNER | BRANDING • SOCIAL MEDIA • PACKAGING • PRINT • AI-ASSISTED DESIGN",
"Creative and results-driven Graphic Designer with 4+ years of professional experience across branding, social media, packaging, print, marketing collateral, photo editing and digital content. Experienced in supporting multiple brands, collaborating with marketing and sales teams, managing production-ready artwork and using AI-assisted creative tools.",
"Adobe Photoshop; Adobe Illustrator; CorelDRAW; InPage; branding; social media graphics; marketing collateral; packaging; print design; photo editing; retouching; compositing; content creation; Meta Business Suite; ChatGPT; Midjourney; Leonardo AI; Kling AI; Hailuo AI; PixVerse; Figma (Basic); Blender (Basic); Clipchamp.",
"Graphic Designer • Visual Designer • Creative Designer • Social Media Designer • Marketing Designer • Brand Designer • Packaging Designer • Digital Designer • Content Designer • Graphic Artist")

make(OUT/"business_computer_cv.pdf",
"BUSINESS & COMPUTER PROFESSIONAL | COORDINATION • OPERATIONS • DATA • ADMIN SUPPORT",
"Business and computer-focused professional with a B.Com background and experience spanning sales coordination, production planning, reporting, records management, digital marketing support and graphic design. Strong in computer-based office work, documentation, coordination, data handling, reporting and communication.",
"Sales coordination; production planning; reporting; records management; team coordination; computer-based office work; data entry; document handling; Oracle records; report preparation; social media management; Meta Business Suite; marketing support; Photoshop; Illustrator; CorelDRAW; InPage; Figma (Basic).",
"Business Coordinator • Sales Coordinator • Marketing Coordinator • Operations Coordinator • Administrative Assistant • Office Assistant • Business Support Executive • Data Entry Operator • Data Entry Clerk • Computer Operator • Data Processing Assistant • Document Controller • Records/Data Assistant • Back Office Executive • MIS/Data Assistant • Customer Support Executive • Sales Support • Administrative Support • Business Assistant • Commercial Assistant • Operations Assistant")
