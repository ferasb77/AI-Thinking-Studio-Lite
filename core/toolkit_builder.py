"""
core/toolkit_builder.py
Generates the AI Thinking Studio™ Lite — Examination Prompt Toolkit PDF.
Workshop companion giveaway. Standalone document.
"""

import io
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

from core.toolkit_data import TOOLKIT_SECTIONS

W, H = A4

# ── Palette ───────────────────────────────────────────────────────────────────
INK       = colors.HexColor("#0D1117")
DEEP      = colors.HexColor("#0F1B2D")
RULE      = colors.HexColor("#1A2E45")
WHITE     = colors.white
GRAY_800  = colors.HexColor("#2A3A4A")
GRAY_500  = colors.HexColor("#6B7F92")
GRAY_200  = colors.HexColor("#E8EDF2")
GOLD      = colors.HexColor("#C9A84C")
GOLD_DARK = colors.HexColor("#8A6A20")
ACCENT    = colors.HexColor("#5B82B5")

FOOTER_TEXT  = "These prompts are not designed to help you reach conclusions faster. They are designed to help you examine challenges more thoroughly before reaching them."
PRODUCT_NAME = "AI Thinking Studio™ Lite"
DOC_TITLE    = "Examination Prompt Toolkit"


# ── Canvas callbacks ──────────────────────────────────────────────────────────

def _cover_canvas(canvas, doc):
    canvas.saveState()
    # Full bleed dark background
    canvas.setFillColor(INK)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Gold bottom bar
    canvas.setFillColor(GOLD)
    canvas.rect(0, 0, W, 2.5 * mm, fill=1, stroke=0)
    # Subtle left rule
    canvas.setFillColor(colors.HexColor("#1A2E45"))
    canvas.rect(0, 0, 3 * mm, H, fill=1, stroke=0)
    canvas.restoreState()


def _section_canvas(section_accent_hex: str):
    accent = colors.HexColor(section_accent_hex)

    def callback(canvas, doc):
        canvas.saveState()
        # Left bar in section accent colour
        canvas.setFillColor(accent)
        canvas.rect(0, 0, 3 * mm, H, fill=1, stroke=0)
        # Footer rule
        canvas.setStrokeColor(colors.HexColor("#D0D8E0"))
        canvas.setLineWidth(0.3)
        canvas.line(15 * mm, 18 * mm, W - 15 * mm, 18 * mm)
        
        # ── Fixed Footer Layout (Two Lines) ──────────────────────────────────
        # Line 1: Meta info right under the rule line
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(accent)
        canvas.drawString(15 * mm, 14 * mm, PRODUCT_NAME)
        canvas.drawRightString(W - 15 * mm, 14 * mm, DOC_TITLE)
        
        # Line 2: Centered long philosophy text safely below
        canvas.setFont("Helvetica-Oblique", 6)
        canvas.setFillColor(GRAY_500)
        canvas.drawCentredString(W / 2, 9 * mm, FOOTER_TEXT)
        canvas.restoreState()

    return callback


def _intro_canvas(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, 0, 3 * mm, H, fill=1, stroke=0)
    canvas.setStrokeColor(GRAY_200)
    canvas.setLineWidth(0.3)
    canvas.line(15 * mm, 18 * mm, W - 15 * mm, 18 * mm)
    
    # ── Fixed Footer Layout (Two Lines) ──────────────────────────────────
    # Line 1: Meta info right under the rule line
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(ACCENT)
    canvas.drawString(15 * mm, 14 * mm, PRODUCT_NAME)
    canvas.drawRightString(W - 15 * mm, 14 * mm, DOC_TITLE)
    
    # Line 2: Centered long philosophy text safely below
    canvas.setFont("Helvetica-Oblique", 6)
    canvas.setFillColor(GRAY_500)
    canvas.drawCentredString(W / 2, 9 * mm, FOOTER_TEXT)
    canvas.restoreState()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rule(color=RULE, thickness=0.4, sb=4, sa=6):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=sb, spaceAfter=sa)


def _hex(h): return colors.HexColor(h)


def _card(card: dict, accent_hex: str, accent_light_hex: str) -> list:
    """Render one Thinking Card as a Table-based panel."""
    accent    = _hex(accent_hex)
    bg        = colors.HexColor("#F7F9FB")
    prompt_bg    = colors.HexColor("#EDF3FA")

    num_p = ParagraphStyle(
        "cn", fontName="Helvetica-Bold", fontSize=7.5,
        leading=10, textColor=accent, spaceAfter=0,
    )
    title_p = ParagraphStyle(
        "ct", fontName="Helvetica-Bold", fontSize=13,
        leading=17, textColor=GRAY_800, spaceAfter=3,
    )
    label_p = ParagraphStyle(
        "cl", fontName="Helvetica-Bold", fontSize=7,
        leading=10, textColor=GRAY_500, spaceAfter=2,
        letterSpacing=1.2,
    )
    purpose_p = ParagraphStyle(
        "cp", fontName="Helvetica-Oblique", fontSize=9,
        leading=13, textColor=GRAY_800, spaceAfter=0,
    )
    prompt_p = ParagraphStyle(
        "cpr", fontName="Helvetica", fontSize=9.5,
        leading=14, textColor=GRAY_800, spaceAfter=0,
    )
    why_p = ParagraphStyle(
        "cw", fontName="Helvetica", fontSize=8.5,
        leading=13, textColor=GRAY_500, spaceAfter=0,
    )
    when_p = ParagraphStyle(
        "cwh", fontName="Helvetica-Bold", fontSize=8.5,
        leading=13, textColor=accent, spaceAfter=0,
    )

    col_w = W - 36 * mm

    # Header row: number + title
    header_cell = [
        Paragraph(f"#{card['number']}", num_p),
        Paragraph(card["title"], title_p),
    ]
    header_t = Table([[header_cell]], colWidths=[col_w])
    header_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("LEFTPADDING",  (0,0),(-1,-1), 14),
        ("RIGHTPADDING", (0,0),(-1,-1), 14),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEBEFORE",   (0,0),(0,-1),  4, accent),
    ]))

    # Purpose row
    purpose_cell = [
        Paragraph("PURPOSE", label_p),
        Paragraph(card["purpose"], purpose_p),
    ]
    purpose_t = Table([[purpose_cell]], colWidths=[col_w])
    purpose_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("LEFTPADDING",  (0,0),(-1,-1), 14),
        ("RIGHTPADDING", (0,0),(-1,-1), 14),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEBEFORE",   (0,0),(0,-1),  4, accent),
        ("LINEABOVE",    (0,0),(-1,0),  0.3, GRAY_200),
    ]))

    # Prompt row — distinct background
    prompt_cell = [
        Paragraph("PROMPT", label_p),
        Paragraph(f'"{card["prompt"]}"', prompt_p),
    ]
    prompt_t = Table([[prompt_cell]], colWidths=[col_w])
    prompt_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), prompt_bg),
        ("LEFTPADDING",  (0,0),(-1,-1), 14),
        ("RIGHTPADDING", (0,0),(-1,-1), 14),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEBEFORE",   (0,0),(0,-1),  4, accent),
        ("LINEABOVE",    (0,0),(-1,0),  0.5, accent),
    ]))

    # Why + When row — two columns
    why_col  = col_w * 0.58
    when_col = col_w * 0.42

    why_cell = [
        Paragraph("WHY IT MATTERS", label_p),
        Paragraph(card["why"], why_p),
    ]
    when_cell = [
        Paragraph("WHEN TO USE", label_p),
        Paragraph(card["when"], when_p),
    ]
    footer_t = Table([[why_cell, when_cell]], colWidths=[why_col, when_col])
    footer_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("LEFTPADDING",  (0,0),(-1,-1), 14),
        ("RIGHTPADDING", (0,0),(-1,-1), 14),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LINEBEFORE",   (0,0),(0,-1),  4, accent),
        ("LINEABOVE",    (0,0),(-1,0),  0.3, GRAY_200),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LINEAFTER",    (0,0),(0,-1),  0.3, GRAY_200),
    ]))

    return [
        KeepTogether([header_t, purpose_t, prompt_t, footer_t]),
        Spacer(1, 10),
    ]


def _section_header(section: dict) -> list:
    """Dark band header for each section — rendered as a Table."""
    bg      = _hex(section["room_color"])
    accent  = _hex(section["accent"])
    a_light = _hex(section["accent_light"])

    title_p = ParagraphStyle(
        "sh_title", fontName="Helvetica-Bold", fontSize=20,
        leading=26, textColor=a_light, spaceAfter=2,
    )
    obj_p = ParagraphStyle(
        "sh_obj", fontName="Helvetica-Bold", fontSize=8,
        leading=12, textColor=accent, spaceAfter=4, letterSpacing=1.5,
    )
    purpose_p = ParagraphStyle(
        "sh_purpose", fontName="Helvetica", fontSize=9,
        leading=14, textColor=colors.HexColor("#8899AA"), spaceAfter=0,
    )

    col_w = W - 36 * mm
    cell = [
        Paragraph(section["objective"].upper(), obj_p),
        Paragraph(section["title"], title_p),
        Paragraph(section["purpose"], purpose_p),
    ]
    t = Table([[cell]], colWidths=[col_w])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("LEFTPADDING",  (0,0),(-1,-1), 18),
        ("RIGHTPADDING", (0,0),(-1,-1), 18),
        ("TOPPADDING",   (0,0),(-1,-1), 18),
        ("BOTTOMPADDING",(0,0),(-1,-1), 18),
        ("LINEBELOW",    (0,0),(-1,-1), 2, accent),
    ]))
    return [t, Spacer(1, 14)]


# ── Main builder ──────────────────────────────────────────────────────────────

def generate_toolkit_pdf() -> bytes:
    """Build and return the Examination Prompt Toolkit PDF as bytes."""
    buffer = io.BytesIO()

    page_callbacks = {}

    def dispatch(canvas, doc):
        cb = page_callbacks.get(doc.page)
        if cb:
            cb(canvas, doc)
        elif doc.page == 1:
            _cover_canvas(canvas, doc)
        else:
            _intro_canvas(canvas, doc)

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=24 * mm,
        title=f"{PRODUCT_NAME} — {DOC_TITLE}",
        author=PRODUCT_NAME,
    )

    story = []

    # ── COVER ────────────────────────────────────────────────────────────────
    cover_product_p = ParagraphStyle(
        "cov_prod", fontName="Helvetica", fontSize=9,
        leading=13, textColor=colors.HexColor("#8899AA"),
        alignment=TA_CENTER, letterSpacing=3,
    )
    cover_title_p = ParagraphStyle(
        "cov_title", fontName="Helvetica-Bold", fontSize=32,
        leading=38, textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
    )
    cover_tagline_p = ParagraphStyle(
        "cov_tag", fontName="Helvetica-Oblique", fontSize=10,
        leading=16, textColor=colors.HexColor("#6B7F92"),
        alignment=TA_CENTER, spaceAfter=4,
    )
    cover_count_p = ParagraphStyle(
        "cov_count", fontName="Helvetica", fontSize=9,
        leading=13, textColor=colors.HexColor("#3A5A79"),
        alignment=TA_CENTER,
    )

    story.append(Spacer(1, 44 * mm))
    story.append(Paragraph("AI THINKING STUDIO™ LITE", cover_product_p))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Examination Prompt", cover_title_p))
    story.append(Paragraph("Toolkit", cover_title_p))
    story.append(Spacer(1, 6))

    # Gold rule centred
    gr = Table([[""]],colWidths=[60*mm])
    gr.setStyle(TableStyle([
        ("LINEABOVE",(0,0),(-1,-1),1.5,GOLD),
        ("TOPPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    gr_wrap = Table([[gr]],colWidths=[W-36*mm])
    gr_wrap.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(gr_wrap)

    story.append(Paragraph(
        "A collection of examination prompts designed to deepen thinking — not accelerate conclusions.",
        cover_tagline_p,
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "6 Thinking Sections  ·  30 Examination Prompts",
        cover_count_p,
    ))
    story.append(Spacer(1, 48 * mm))
    story.append(Paragraph(
        "Every prompt in this toolkit exists to improve the quality of examination before decisions are made.",
        cover_tagline_p,
    ))
    story.append(PageBreak())

    # ── HOW TO USE ───────────────────────────────────────────────────────────
    page_callbacks[2] = _intro_canvas

    intro_title_p = ParagraphStyle(
        "it", fontName="Helvetica-Bold", fontSize=18,
        leading=24, textColor=GRAY_800, spaceAfter=4,
    )
    intro_body_p = ParagraphStyle(
        "ib", fontName="Helvetica", fontSize=10,
        leading=16, textColor=GRAY_800, spaceAfter=8,
    )
    intro_label_p = ParagraphStyle(
        "il", fontName="Helvetica-Bold", fontSize=7.5,
        leading=11, textColor=GRAY_500, spaceAfter=3, letterSpacing=1.2,
    )
    intro_note_p = ParagraphStyle(
        "in", fontName="Helvetica-Oblique", fontSize=9.5,
        leading=15, textColor=GRAY_500, spaceAfter=0,
    )

    story.append(Spacer(1, 4))
    story.append(Paragraph("How to Use This Toolkit", intro_title_p))
    story.append(_rule(ACCENT, thickness=1, sb=2, sa=12))

    story.append(Paragraph(
        "This toolkit is not a prompt library. It is an examination companion.",
        ParagraphStyle("ib2", parent=intro_body_p, fontName="Helvetica-Bold",
                       textColor=ACCENT),
    ))
    story.append(Paragraph(
        "Each prompt is designed to slow thinking down — not speed it up. "
        "Use these prompts when you want to examine a challenge more carefully "
        "before deciding how to respond to it.",
        intro_body_p,
    ))

    # Section index table
    story.append(Paragraph("SECTIONS IN THIS TOOLKIT", intro_label_p))
    story.append(Spacer(1, 4))

    index_rows = []
    for s in TOOLKIT_SECTIONS:
        accent_c = _hex(s["accent"])
        num_cards = len(s["cards"])
        sec_p = ParagraphStyle(
            f"idx_{s['id']}", fontName="Helvetica-Bold", fontSize=10,
            leading=14, textColor=accent_c,
        )
        obj_p2 = ParagraphStyle(
            f"idxo_{s['id']}", fontName="Helvetica", fontSize=9,
            leading=13, textColor=GRAY_500,
        )
        num_p2 = ParagraphStyle(
            f"idxn_{s['id']}", fontName="Helvetica", fontSize=9,
            leading=13, textColor=GRAY_500, alignment=TA_RIGHT,
        )
        index_rows.append([
            Paragraph(s["title"], sec_p),
            Paragraph(s["objective"], obj_p2),
            Paragraph(f"{num_cards} prompts", num_p2),
        ])

    idx_col_w = [(W-36*mm)*0.38, (W-36*mm)*0.42, (W-36*mm)*0.20]
    idx_t = Table(index_rows, colWidths=idx_col_w)
    idx_t.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LINEBELOW",    (0,0),(-1,-1), 0.3, GRAY_200),
    ]))
    story.append(idx_t)
    story.append(Spacer(1, 16))

    # Card anatomy explanation
    story.append(Paragraph("READING A THINKING CARD", intro_label_p))
    story.append(Spacer(1, 6))

    anatomy_rows = [
        ("#01  Card Title",        "The name and number of the prompt."),
        ("PURPOSE",                "What this prompt is designed to surface."),
        ("PROMPT",                 "The exact text to use with any AI assistant."),
        ("WHY IT MATTERS",         "The reasoning behind this line of examination."),
        ("WHEN TO USE",            "The moment in a thinking process where this prompt is most valuable."),
    ]
    anat_label_p = ParagraphStyle("al", fontName="Helvetica-Bold", fontSize=8.5,
                                   leading=13, textColor=ACCENT)
    anat_body_p  = ParagraphStyle("ab", fontName="Helvetica", fontSize=8.5,
                                   leading=13, textColor=GRAY_800)
    anat_col_w   = [(W-36*mm)*0.28, (W-36*mm)*0.72]
    anat_rows_fmt = [[Paragraph(r[0], anat_label_p), Paragraph(r[1], anat_body_p)]
                     for r in anatomy_rows]
    anat_t = Table(anat_rows_fmt, colWidths=anat_col_w)
    anat_t.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(0,-1),  0),
        ("RIGHTPADDING", (0,0),(0,-1),  10),
        ("LEFTPADDING",  (0,0),(1,-1),  0),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBELOW",    (0,0),(-1,-1), 0.3, GRAY_200),
    ]))
    story.append(anat_t)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "These prompts work with any AI assistant — ChatGPT, Gemini, Claude, or others. "
        "Copy the prompt, add your specific challenge context, and use the response "
        "to deepen your examination — not to replace your judgment.",
        intro_note_p,
    ))
    story.append(PageBreak())

    # ── SECTIONS ─────────────────────────────────────────────────────────────
    page_counter = [3]

    for section in TOOLKIT_SECTIONS:
        section_cb = _section_canvas(section["accent"])

        # Register this section's pages (generous range)
        for p in range(page_counter[0], page_counter[0] + 12):
            page_callbacks[p] = section_cb
        page_counter[0] += 12

        # Section header band
        story.extend(_section_header(section))

        # Cards
        for card in section["cards"]:
            story.extend(_card(card, section["accent"], section["accent_light"]))

        story.append(PageBreak())

    # ── BACK PAGE ────────────────────────────────────────────────────────────
    for p in range(page_counter[0], page_counter[0] + 2):
        page_callbacks[p] = _intro_canvas

    back_title_p = ParagraphStyle(
        "bt", fontName="Helvetica-Bold", fontSize=18,
        leading=24, textColor=GRAY_800, spaceAfter=4, alignment=TA_CENTER,
    )
    back_body_p = ParagraphStyle(
        "bb", fontName="Helvetica", fontSize=10,
        leading=16, textColor=GRAY_500, spaceAfter=8, alignment=TA_CENTER,
    )
    back_doctrine_p = ParagraphStyle(
        "bd", fontName="Helvetica-Bold", fontSize=12,
        leading=18, textColor=ACCENT, spaceAfter=4, alignment=TA_CENTER,
    )

    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("A Final Reminder", back_title_p))
    story.append(_rule(ACCENT, thickness=0.5, sb=8, sa=16))
    story.append(Paragraph(
        "AI Thinking Studio™ is not designed to help you reach conclusions faster.",
        back_doctrine_p,
    ))
    story.append(Paragraph(
        "It is designed to help you examine conclusions more thoroughly before reaching them.",
        back_doctrine_p,
    ))
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Every prompt in this toolkit exists to serve that purpose.\n"
        "Use them to slow down. To look again. To ask the question\n"
        "you were about to skip.",
        back_body_p,
    ))
    story.append(Spacer(1, 24))
    story.append(Paragraph(
        "Better thinking begins before better answers.",
        ParagraphStyle("bq", fontName="Helvetica-Oblique", fontSize=13,
                       leading=18, textColor=GOLD, alignment=TA_CENTER),
    ))

    doc.build(story, onFirstPage=dispatch, onLaterPages=dispatch)
    buffer.seek(0)
    return buffer.read()
