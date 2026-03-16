"""
Generates a personalized one-pager PDF for each prospect.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                               Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ORANGE = HexColor("#ff6b35")
DARK = HexColor("#1a1a2e")
CYAN = HexColor("#00d9ff")
GREY = HexColor("#666666")
LIGHT_GREY = HexColor("#f5f5f5")

def generate_prospect_pdf(company: str,
                         contact: dict,
                         signals: list,
                         account_brief: str,
                         icp: str,
                         sender_name: str = "FireReach Team") -> str:
    filename = f"FireReach_{company.replace(' ','_')}.pdf"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    doc = SimpleDocTemplate(filepath,
                           pagesize=A4,
                           rightMargin=20*mm,
                           leftMargin=20*mm,
                           topMargin=15*mm,
                           bottomMargin=15*mm)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Header bar
    header_data = [[
        Paragraph("<font color='white' size='18'><b>🔥 FireReach</b></font>",
                 ParagraphStyle("h", fontName="Helvetica-Bold",
                               fontSize=18, textColor=white)),
        Paragraph(f"<font color='white' size='10'>Personalized Outreach Brief</font>",
                 ParagraphStyle("sub", fontName="Helvetica",
                               fontSize=10, textColor=white,
                               alignment=2))
    ]]
    
    header_table = Table(header_data, colWidths=[90*mm, 80*mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), DARK),
        ("PADDING", (0,0), (-1,-1), 12),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))
    
    # Company + Contact section
    elements.append(Paragraph(f"<font size='20' color='#1a1a2e'><b>{company}</b></font>",
                             ParagraphStyle("co", fontName="Helvetica-Bold",
                                           fontSize=20, textColor=DARK)))
    
    if contact.get("name"):
        elements.append(Paragraph(f"<font size='11' color='#666666'>Attention: "
                                 f"{contact.get('name')} — {contact.get('title','')}</font>",
                                 ParagraphStyle("ct", fontName="Helvetica",
                                               fontSize=11, textColor=GREY)))
    
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=2,
                              color=ORANGE, spaceAfter=4*mm))
    
    # Verified Signals section
    elements.append(Paragraph("<b>Verified Growth Signals</b>",
                             ParagraphStyle("sh", fontName="Helvetica-Bold",
                                           fontSize=13, textColor=DARK)))
    elements.append(Spacer(1, 3*mm))
    
    for s in signals[:5]:
        conf_color = "#00b894" if s["confidence"] == "HIGH" else "#fdcb6e"
        row = [[
            Paragraph(f"<font size='9' color='{conf_color}'><b>{s['confidence']}</b></font>",
                     ParagraphStyle("badge", fontName="Helvetica-Bold",
                                   fontSize=9)),
            Paragraph(f"<font size='10'>{s['signal']}</font>",
                     ParagraphStyle("sig", fontName="Helvetica",
                                   fontSize=10, textColor=DARK))
        ]]
        
        sig_table = Table(row, colWidths=[18*mm, 148*mm])
        sig_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), LIGHT_GREY),
            ("PADDING", (0,0), (-1,-1), 6),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ROUNDEDCORNERS", [4]),
        ]))
        elements.append(sig_table)
        elements.append(Spacer(1, 2*mm))
    
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=1,
                              color=LIGHT_GREY, spaceAfter=4*mm))
    
    # Account Brief
    elements.append(Paragraph("<b>Strategic Account Brief</b>",
                             ParagraphStyle("sh2", fontName="Helvetica-Bold",
                                           fontSize=13, textColor=DARK)))
    elements.append(Spacer(1, 3*mm))
    
    elements.append(Paragraph(account_brief.replace("\n\n", "<br/><br/>"),
                             ParagraphStyle("brief", fontName="Helvetica",
                                           fontSize=10, textColor=DARK,
                                           leading=16)))
    
    elements.append(Spacer(1, 6*mm))
    elements.append(HRFlowable(width="100%", thickness=2,
                              color=ORANGE, spaceAfter=4*mm))
    
    # CTA Footer
    elements.append(Paragraph("<b>Next Step</b>",
                             ParagraphStyle("cta_h", fontName="Helvetica-Bold",
                                           fontSize=12, textColor=DARK)))
    elements.append(Spacer(1, 2*mm))
    
    elements.append(Paragraph("We'd love to show you how our solution maps directly to your "
                             "current growth phase. Let's connect for a focused 15-minute call.",
                             ParagraphStyle("cta", fontName="Helvetica",
                                           fontSize=10, textColor=GREY, leading=15)))
    
    doc.build(elements)
    return filepath