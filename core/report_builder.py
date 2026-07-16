"""
core/report_builder.py
AI Thinking Studio™ Lite — PDF Report Builder
Visual identity: dark premium, editorial, high contrast.
"""

import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

W, H = A4
CONTENT_W = W - 36 * mm   # usable text width

# ── Palette ───────────────────────────────────────────────────────────────────
INK          = colors.HexColor("#0D1117")
DEEP         = colors.HexColor("#0F1B2D")
RULE         = colors.HexColor("#1A2E45")
ACCENT       = colors.HexColor("#5B82B5")
ACCENT_LIGHT = colors.HexColor("#A8C4E0")
WHITE        = colors.white
OFF_WHITE    = colors.HexColor("#F0F4F8")
GRAY_800     = colors.HexColor("#2A3A4A")
GRAY_500     = colors.HexColor("#6B7F92")
GRAY_300     = colors.HexColor("#B0BEC8")
GOLD         = colors.HexColor("#C9A84C")
GOLD_LIGHT   = colors.HexColor("#E8D08A")
GOLD_BG      = colors.HexColor("#FDF8EC")
GREEN        = colors.HexColor("#3A9E7A")
GREEN_LIGHT  = colors.HexColor("#7ECFB0")
GREEN_BG     = colors.HexColor("#EDF7F3")
TEAL         = colors.HexColor("#3A7A9E")
TEAL_LIGHT   = colors.HexColor("#7EC0E0")
TEAL_BG      = colors.HexColor("#EDF6FA")
RED_DARK     = colors.HexColor("#C05050")

FOOTER_TEXT  = "The purpose of this Studio is not to accelerate conclusions, but to deepen examination."
PRODUCT_NAME = "AI Thinking Studio™ Lite"

ROOM_PALETTE = {
    "Mirror Room":      (colors.HexColor("#0F1B2D"), ACCENT_LIGHT,  ACCENT),
    "Human Room":       (colors.HexColor("#0D1F1A"), GREEN_LIGHT,   GREEN),
    "Possibility Room": (colors.HexColor("#1A1408"), GOLD_LIGHT,    GOLD),
    "Battlefield Room": (colors.HexColor("#1F0D0D"), colors.HexColor("#E8A0A0"), RED_DARK),
    "Future Room":      (colors.HexColor("#12101F"), colors.HexColor("#B0A8E0"), colors.HexColor("#6B5DB5")),
}

# Lines starting with these are AI sign-offs / meta-commentary to suppress
SUPPRESSED_PREFIXES = (
    "what now?",
    "---",
    "* * *",
)


# ── Styles ────────────────────────────────────────────────────────────────────

def _styles():
    S = {}
    S["cover_product"] = ParagraphStyle(
        "cover_product", fontName="Helvetica", fontSize=9, leading=13,
        textColor=GRAY_300, alignment=TA_CENTER, spaceAfter=0,
    )
    S["cover_title"] = ParagraphStyle(
        "cover_title", fontName="Helvetica-Bold", fontSize=36, leading=42,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
    )
    S["cover_challenge"] = ParagraphStyle(
        "cover_challenge", fontName="Helvetica-Bold", fontSize=18, leading=24,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
    )
    S["cover_meta"] = ParagraphStyle(
        "cover_meta", fontName="Helvetica", fontSize=9, leading=13,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    S["cover_doctrine"] = ParagraphStyle(
        "cover_doctrine", fontName="Helvetica-Oblique", fontSize=9, leading=14,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    S["setup_label"] = ParagraphStyle(
        "setup_label", fontName="Helvetica-Bold", fontSize=7.5, leading=11,
        textColor=GRAY_500, spaceAfter=2,
    )
    S["setup_value"] = ParagraphStyle(
        "setup_value", fontName="Helvetica", fontSize=10, leading=15,
        textColor=GRAY_800, spaceAfter=0,
    )
    S["setup_revised"] = ParagraphStyle(
        "setup_revised", fontName="Helvetica-Bold", fontSize=11, leading=16,
        textColor=ACCENT, spaceAfter=0,
    )
    S["room_section"] = ParagraphStyle(
        "room_section", fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=ACCENT, spaceBefore=14, spaceAfter=3,
    )
    S["body"] = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=9.5, leading=15,
        textColor=GRAY_800, spaceAfter=5,
    )
    S["bullet"] = ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=9.5, leading=14,
        textColor=GRAY_800, leftIndent=14, spaceAfter=3,
    )
    S["bold_line"] = ParagraphStyle(
        "bold_line", fontName="Helvetica-Bold", fontSize=9.5, leading=14,
        textColor=GRAY_800, spaceBefore=6, spaceAfter=2,
    )
    S["risk_label"] = ParagraphStyle(
        "risk_label", fontName="Helvetica-Bold", fontSize=7, leading=10,
        textColor=GRAY_500, spaceAfter=3,
    )
    S["risk_text"] = ParagraphStyle(
        "risk_text", fontName="Helvetica-Oblique", fontSize=10, leading=15,
        textColor=ACCENT_LIGHT, spaceAfter=0,
    )
    S["doctrine"] = ParagraphStyle(
        "doctrine", fontName="Helvetica-Oblique", fontSize=8, leading=12,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    return S


# ── Canvas callbacks ──────────────────────────────────────────────────────────

def _cover_canvas(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 0, W, 2.5 * mm, fill=1, stroke=0)
    canvas.setFillColor(RULE)
    canvas.rect(0, H - 1 * mm, W, 1 * mm, fill=1, stroke=0)
    canvas.restoreState()


def _interior_canvas(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(RULE)
    canvas.rect(0, 0, 3 * mm, H, fill=1, stroke=0)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.4)
    canvas.line(15 * mm, 18 * mm, W - 15 * mm, 18 * mm)
    canvas.setFont("Helvetica-Oblique", 6.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawCentredString(W / 2, 13 * mm, FOOTER_TEXT)
    canvas.setFont("Helvetica", 6.5)
    canvas.setFillColor(ACCENT)
    canvas.drawString(15 * mm, 13 * mm, PRODUCT_NAME)
    canvas.drawRightString(W - 15 * mm, 13 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _room_canvas(room_name: str, subtitle: str):
    band_bg, band_text, _ = ROOM_PALETTE.get(room_name, (DEEP, ACCENT_LIGHT, ACCENT))

    def callback(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(RULE)
        canvas.rect(0, 0, 3 * mm, H, fill=1, stroke=0)
        band_h = 28 * mm
        canvas.setFillColor(band_bg)
        canvas.rect(0, H - band_h, W, band_h, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 18)
        canvas.setFillColor(band_text)
        canvas.drawString(18 * mm, H - 16 * mm, room_name)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY_500)
        canvas.drawString(18 * mm, H - 22 * mm, subtitle.upper())
        canvas.setFont("Helvetica-Oblique", 6.5)
        canvas.setFillColor(GRAY_500)
        canvas.drawCentredString(W / 2, 13 * mm, FOOTER_TEXT)
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(ACCENT)
        canvas.drawString(15 * mm, 13 * mm, PRODUCT_NAME)
        canvas.drawRightString(W - 15 * mm, 13 * mm, f"Page {doc.page}")
        canvas.restoreState()
    return callback


# ── Helpers ───────────────────────────────────────────────────────────────────

def _rule(color=RULE, thickness=0.4, sb=4, sa=6):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=sb, spaceAfter=sa)


def _convert_inline_bold(text: str) -> str:
    """Convert **text** to <b>text</b> and *text* to <i>text</i>."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+?)\*", r"<i>\1</i>", text)
    return text


def _strip_markdown_symbols(text: str) -> str:
    """Remove leading markdown heading symbols."""
    return re.sub(r"^#{1,6}\s+", "", text).strip()


def _is_suppressed(line: str) -> bool:
    """Return True if this line should be silently dropped from the PDF."""
    lower = line.lower().strip()
    if not lower:
        return False
    for prefix in SUPPRESSED_PREFIXES:
        if lower.startswith(prefix):
            return True
    return False


def _extract_callout_content(line: str) -> str:
    """
    Extract the content portion after a callout label.
    Strips the label itself, bold markers, and leading punctuation.
    """
    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
    # Remove the pattern label before the colon
    if ":" in clean:
        content = clean.split(":", 1)[-1].strip()
    else:
        content = clean.strip()
    # Remove leading dashes or bullets
    content = re.sub(r"^[-–•]\s*", "", content).strip()
    return content


# Callout trigger patterns → (display label, border, text, bg)
CALLOUT_PATTERNS = {
    "biggest blind spot":                  ("Biggest Blind Spot",                     GOLD,  GOLD_LIGHT,  colors.HexColor("#17120A")),
    "most dangerous assumption":           ("Most Dangerous Assumption",               GOLD,  GOLD_LIGHT,  colors.HexColor("#17120A")),
    "condition most likely to be absent":  ("Condition Most Likely To Be Absent",     TEAL,  TEAL_LIGHT,  colors.HexColor("#0A1520")),
    "most unexpected direction":           ("Most Unexpected Direction",               TEAL,  TEAL_LIGHT,  colors.HexColor("#0A1520")),
    "stakeholder most likely to surprise": ("Stakeholder Most Likely To Surprise You", TEAL, TEAL_LIGHT,  colors.HexColor("#0A1520")),
    "consequence most likely to be ignored":("Consequence Most Likely To Be Ignored", GREEN, GREEN_LIGHT, colors.HexColor("#0A1710")),
    "sign most likely to be missed":       ("Sign Most Likely To Be Missed",          GREEN, GREEN_LIGHT, colors.HexColor("#0A1710")),
}


def _callout_box(content: str, label: str, border_color, text_color, bg_color) -> list:
    """Render a visually distinct bordered callout panel."""
    label_p = ParagraphStyle(
        "cl_label", fontName="Helvetica-Bold", fontSize=7, leading=10,
        textColor=border_color, spaceAfter=4,
    )
    text_p = ParagraphStyle(
        "cl_text", fontName="Helvetica-Bold", fontSize=11, leading=16,
        textColor=text_color, spaceAfter=0,
    )
    cell = [Paragraph(label.upper(), label_p), Paragraph(content, text_p)]
    t = Table([[cell]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BOX",          (0, 0), (-1, -1), 1.5, border_color),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("BACKGROUND",   (0, 0), (-1, -1), bg_color),
    ]))
    return [Spacer(1, 8), KeepTogether([t]), Spacer(1, 10)]


def _section_underline(title: str, room_accent) -> list:
    """Section sub-header with coloured underline."""
    label_p = ParagraphStyle(
        "sb_label", fontName="Helvetica-Bold", fontSize=9.5,
        leading=13, textColor=room_accent, spaceAfter=0,
    )
    t = Table([[Paragraph(title, label_p)]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("LINEBELOW",    (0, 0), (-1, -1), 0.5, room_accent),
    ]))
    return [Spacer(1, 10), t, Spacer(1, 5)]


def _ai_content_block(text: str, styles: dict, room_name: str = "") -> list:
    """Parse AI markdown output into styled ReportLab elements."""
    elements = []
    if not text:
        elements.append(Paragraph("No content generated.", styles["body"]))
        return elements

    _, _, room_accent = ROOM_PALETTE.get(room_name, (DEEP, ACCENT_LIGHT, ACCENT))

    sub_style = ParagraphStyle(
        "ai_sub", fontName="Helvetica-Bold", fontSize=9.5, leading=14,
        textColor=room_accent, spaceBefore=10, spaceAfter=3,
    )
    bold_style = ParagraphStyle(
        "ai_bold", fontName="Helvetica-Bold", fontSize=9.5, leading=14,
        textColor=GRAY_800, spaceBefore=6, spaceAfter=2,
    )

    for line in text.split("\n"):
        s = line.strip()

        # Empty line
        if not s:
            elements.append(Spacer(1, 3))
            continue

        # Suppress sign-offs and horizontal rules
        if _is_suppressed(s):
            continue

        # Callout patterns — check before any other formatting
        lower = s.lower()
        matched = False
        for pattern, (label, border, txt_color, bg) in CALLOUT_PATTERNS.items():
            if pattern in lower:
                content = _extract_callout_content(s)
                # Skip if the content is just the label itself (AI repeated it)
                if content and pattern not in content.lower():
                    elements.extend(_callout_box(content, label, border, txt_color, bg))
                matched = True
                break
        if matched:
            continue

        # Markdown headers: ## ### # (strip symbols, render as section header)
        if s.startswith("#"):
            title = _strip_markdown_symbols(s)
            if title:
                elements.extend(_section_underline(title, room_accent))
            continue

        # Bold-only line: **text**
        if s.startswith("**") and s.endswith("**") and s.count("**") == 2:
            inner = s[2:-2]
            elements.append(Paragraph(f"<b>{inner}</b>", bold_style))
            continue

        # Bullet line
        if s.startswith(("- ", "• ", "* ")):
            content = _convert_inline_bold(s[2:])
            elements.append(Paragraph(f"–\u2002{content}", styles["bullet"]))
            continue

        # Numbered list: "1. " "2. " etc.
        if re.match(r"^\d+\.\s", s):
            content = _convert_inline_bold(re.sub(r"^\d+\.\s+", "", s))
            elements.append(Paragraph(f"–\u2002{content}", styles["bullet"]))
            continue

        # Plain body text
        elements.append(Paragraph(_convert_inline_bold(s), styles["body"]))

    return elements


# ── Starred item extractor ────────────────────────────────────────────────────

def _extract_starred_items(session_data: dict) -> dict:
    """Extract key labelled items from AI outputs for the Thinking Journey page."""
    items = {}

    def first_match(text: str, patterns: list) -> str:
        if not text:
            return ""
        for line in text.split("\n"):
            for p in patterns:
                if p.lower() in line.lower():
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
                    clean = re.sub(r"^[★\-–•*\s#]+", "", clean).strip()
                    if ":" in clean:
                        content = clean.split(":", 1)[-1].strip()
                    else:
                        content = clean
                    # Trim to a clean sentence boundary (max ~180 chars)
                    if len(content) > 180:
                        # Try to cut at sentence boundary
                        cutoff = content[:180]
                        last_period = max(cutoff.rfind("."), cutoff.rfind("—"))
                        content = cutoff[:last_period + 1] if last_period > 80 else cutoff + "…"
                    return content
        return ""

    mirror = session_data.get("mirror_output", "")
    items["blind_spot"]   = first_match(mirror, ["biggest blind spot"])
    items["missing_info"] = first_match(mirror, ["examination gap"])

    # Best reframe: first Option A line
    for line in mirror.split("\n"):
        if "option a" in line.lower():
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            content = clean.split(":", 1)[-1].strip() if ":" in clean else clean
            items["best_reframe"] = content[:200]
            break
    else:
        items["best_reframe"] = ""

    items["surprise_stakeholder"] = first_match(
        session_data.get("human_output", ""), ["stakeholder most likely to surprise"])
    items["unexpected_direction"] = first_match(
        session_data.get("possibility_output", ""), ["most unexpected direction"])
    items["dangerous_assumption"] = first_match(
        session_data.get("battlefield_output", ""), ["most dangerous assumption"])
    items["ignored_consequence"]  = first_match(
        session_data.get("future_output", ""), ["consequence most likely to be ignored"])

    return items


# ── Thinking Journey page ─────────────────────────────────────────────────────

def _thinking_journey_page(session_data: dict, styles: dict) -> list:
    story = []
    setup = session_data.get("expedition_setup", {})
    items = _extract_starred_items(session_data)

    # Header
    header_p = ParagraphStyle(
        "jh", fontName="Helvetica-Bold", fontSize=20, leading=26,
        textColor=WHITE, spaceAfter=2,
    )
    sub_p = ParagraphStyle(
        "js", fontName="Helvetica", fontSize=9, leading=13,
        textColor=GRAY_300, spaceAfter=0,
    )
    header_t = Table(
        [[Paragraph("Your Thinking Journey", header_p)],
         [Paragraph("What changed in your understanding because of this expedition.", sub_p)]],
        colWidths=[CONTENT_W],
    )
    header_t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), INK),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LINEBELOW",    (0, -1), (-1, -1), 1, GOLD),
    ]))
    story.append(header_t)
    story.append(Spacer(1, 14))

    def node(label: str, content: str, label_color=GRAY_500,
             text_color=GRAY_800, bg=None):
        lp = ParagraphStyle(
            f"nl", fontName="Helvetica-Bold", fontSize=7, leading=10,
            textColor=label_color, spaceAfter=3,
        )
        tp = ParagraphStyle(
            f"nt", fontName="Helvetica", fontSize=10, leading=15,
            textColor=text_color, spaceAfter=0,
        )
        bg_color = bg or colors.HexColor("#F7F9FB")
        cell = [Paragraph(label.upper(), lp), Paragraph(content or "—", tp)]
        t = Table([[cell]], colWidths=[CONTENT_W])
        t.setStyle(TableStyle([
            ("LEFTPADDING",  (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING",   (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
            ("BACKGROUND",   (0, 0), (-1, -1), bg_color),
            ("LINEBEFORE",   (0, 0), (0, -1),  3, label_color),
        ]))
        return [KeepTogether([t]), Spacer(1, 2)]

    def arrow():
        ap = ParagraphStyle("arr", fontName="Helvetica", fontSize=11,
                            leading=14, textColor=GRAY_500, alignment=TA_CENTER)
        return [Paragraph("↓", ap), Spacer(1, 2)]

    story.extend(node("Where you started",
                       setup.get("challenge_statement", "—"), GRAY_500, GRAY_800))
    story.extend(arrow())

    if items.get("blind_spot"):
        story.extend(node("Biggest blind spot surfaced", items["blind_spot"],
                          GOLD, GRAY_800, GOLD_BG))
        story.extend(arrow())

    revised = session_data.get("revised_challenge", "")
    if revised:
        story.extend(node("How the challenge was reframed", revised,
                          ACCENT, GRAY_800, colors.HexColor("#EDF3FA")))
        story.extend(arrow())
    elif items.get("best_reframe"):
        story.extend(node("Strongest alternative framing", items["best_reframe"],
                          ACCENT, GRAY_800, colors.HexColor("#EDF3FA")))
        story.extend(arrow())

    if items.get("unexpected_direction"):
        story.extend(node("Most unexpected direction explored",
                          items["unexpected_direction"],
                          TEAL, GRAY_800, TEAL_BG))
        story.extend(arrow())

    if items.get("dangerous_assumption"):
        story.extend(node("Most dangerous assumption identified",
                          items["dangerous_assumption"],
                          GOLD, GRAY_800, GOLD_BG))
        story.extend(arrow())

    if items.get("ignored_consequence"):
        story.extend(node("Consequence most likely to be ignored",
                          items["ignored_consequence"],
                          GREEN, GRAY_800, GREEN_BG))
        story.extend(arrow())

    rooms_done     = sum(1 for k in ["mirror_output", "human_output",
                                      "possibility_output", "battlefield_output",
                                      "future_output"] if session_data.get(k))
    selected_count = len(session_data.get("selected_ideas", []))
    story.extend(node(
        "What was examined",
        f"{rooms_done} of 5 rooms completed  ·  {selected_count} idea(s) stress-tested",
        GRAY_500, GRAY_800,
    ))
    story.extend(arrow())

    reflection = session_data.get("final_reflection", "")
    story.extend(node(
        "Your reflection",
        reflection if reflection else "No reflection recorded.",
        GREEN, GRAY_800, GREEN_BG,
    ))

    story.append(Spacer(1, 16))
    story.append(_rule(GOLD, thickness=0.8))
    story.append(Spacer(1, 6))
    story.append(Paragraph(FOOTER_TEXT, styles["doctrine"]))
    return story


# ── Main PDF builder ──────────────────────────────────────────────────────────

def generate_pdf(session_data: dict) -> bytes:
    buffer   = io.BytesIO()
    setup    = session_data.get("expedition_setup", {})
    styles   = _styles()

    page_callbacks = {}

    def dispatch(canvas, doc):
        cb = page_callbacks.get(doc.page)
        if cb:
            cb(canvas, doc)
        elif doc.page == 1:
            _cover_canvas(canvas, doc)
        else:
            _interior_canvas(canvas, doc)

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=20 * mm, bottomMargin=24 * mm,
        title="AI Thinking Studio™ Lite — Thinking Expedition Summary",
        author=PRODUCT_NAME,
    )

    story = []

    # ── COVER ────────────────────────────────────────────────────────────────
    cover_product_p = ParagraphStyle(
        "cov_prod", fontName="Helvetica", fontSize=9, leading=13,
        textColor=GRAY_300, alignment=TA_CENTER,
    )
    cover_title_p = ParagraphStyle(
        "cov_t", fontName="Helvetica-Bold", fontSize=36, leading=42,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
    )
    cover_sub_p = ParagraphStyle(
        "cov_s", fontName="Helvetica-Bold", fontSize=18, leading=24,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
    )
    cover_meta_p = ParagraphStyle(
        "cov_m", fontName="Helvetica", fontSize=9, leading=13,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    cover_doc_p = ParagraphStyle(
        "cov_d", fontName="Helvetica-Oblique", fontSize=9, leading=14,
        textColor=GRAY_500, alignment=TA_CENTER,
    )

    story.append(Spacer(1, 38 * mm))
    story.append(Paragraph("AI THINKING STUDIO™ LITE", cover_product_p))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Thinking Expedition", cover_title_p))
    story.append(Spacer(1, 4))

    # Gold centred rule
    gr = Table([[""]], colWidths=[80 * mm])
    gr.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 1.5, GOLD),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    gr_wrap = Table([[gr]], colWidths=[CONTENT_W])
    gr_wrap.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(gr_wrap)

    challenge_title = setup.get("challenge_title", "Untitled Expedition")
    story.append(Paragraph(challenge_title, cover_sub_p))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%d %B %Y')}",
        cover_meta_p,
    ))
    story.append(Spacer(1, 48 * mm))
    story.append(Paragraph(FOOTER_TEXT, cover_doc_p))
    story.append(PageBreak())

    # ── EXPEDITION SETUP ─────────────────────────────────────────────────────
    page_callbacks[2] = _interior_canvas

    setup_title_p = ParagraphStyle(
        "st", fontName="Helvetica-Bold", fontSize=16, leading=20,
        textColor=GRAY_800, spaceAfter=2,
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph("Expedition Setup", setup_title_p))
    story.append(_rule(ACCENT, thickness=1, sb=4, sa=12))

    col_w = [CONTENT_W * 0.32, CONTENT_W * 0.68]
    rows = []
    for label, value in [
        ("Challenge Title",          setup.get("challenge_title", "")),
        ("Original Challenge",       setup.get("challenge_statement", "")),
        ("Context & Background",     setup.get("context_background", "")),
        ("Who is Affected",          setup.get("who_is_affected", "")),
        ("Currently Considered",     setup.get("current_consideration", "")),
        ("Hope to Understand",       setup.get("hope_to_understand", "")),
    ]:
        rows.append([
            Paragraph(label.upper(), styles["setup_label"]),
            Paragraph(value or "—", styles["setup_value"]),
        ])

    st = Table(rows, colWidths=col_w, hAlign="LEFT")
    st.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1),  12),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LINEBELOW",    (0, 0), (-1, -1), 0.3, RULE),
    ]))
    story.append(st)

    revised = session_data.get("revised_challenge", "")
    if revised:
        story.append(Spacer(1, 12))
        story.append(_rule(ACCENT, thickness=0.5, sb=0, sa=8))
        story.append(Paragraph("REVISED CHALLENGE STATEMENT", styles["setup_label"]))
        story.append(Spacer(1, 4))
        story.append(Paragraph(revised, styles["setup_revised"]))

    story.append(PageBreak())

    # ── ROOM SECTIONS ─────────────────────────────────────────────────────────
    rooms = [
        ("mirror_output",      "Mirror Room",      "Assumption Inventory & Examination Gaps"),
        ("human_output",       "Human Room",       "Stakeholder Perspective Map"),
        ("possibility_output", "Possibility Room", "Directions Worth Examining"),
        ("battlefield_output", "Battlefield Room", "Where Ideas Get Challenged"),
        ("future_output",      "Future Room",      "How This Unfolds Over Time"),
    ]

    page_counter = [3]

    for key, room_name, room_desc in rooms:
        content = session_data.get(key, "")
        room_cb = _room_canvas(room_name, room_desc)
        for p in range(page_counter[0], page_counter[0] + 8):
            page_callbacks[p] = room_cb
        page_counter[0] += 8

        story.append(Spacer(1, 30 * mm))  # space below header band

        # Participant risk block (Battlefield only)
        if key == "battlefield_output":
            participant_risk = session_data.get("participant_risk", "").strip()
            if participant_risk:
                risk_cell = [
                    Paragraph(
                        "BEFORE SEEING THE AI CHALLENGE — THE PARTICIPANT IDENTIFIED:",
                        styles["risk_label"],
                    ),
                    Paragraph(f'"{participant_risk}"', styles["risk_text"]),
                ]
                risk_t = Table([[risk_cell]], colWidths=[CONTENT_W])
                risk_t.setStyle(TableStyle([
                    ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#0F1824")),
                    ("LEFTPADDING",  (0, 0), (-1, -1), 14),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                    ("TOPPADDING",   (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
                    ("LINEBEFORE",   (0, 0), (0, -1),  3, ACCENT),
                ]))
                story.append(risk_t)
                story.append(Spacer(1, 10))
                story.append(_rule(RULE, thickness=0.3, sb=0, sa=10))

        if content:
            story.extend(_ai_content_block(content, styles, room_name))
        else:
            story.append(Paragraph(
                "This room was not completed during the expedition.",
                styles["body"],
            ))

        story.append(PageBreak())

    # ── SELECTED IDEAS ────────────────────────────────────────────────────────
    selected = session_data.get("selected_ideas", [])
    if selected:
        for p in range(page_counter[0], page_counter[0] + 3):
            page_callbacks[p] = _interior_canvas
        page_counter[0] += 3

        si_p = ParagraphStyle(
            "si", fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=GRAY_800, spaceAfter=2,
        )
        story.append(Spacer(1, 4))
        story.append(Paragraph("Selected Ideas", si_p))
        story.append(_rule(ACCENT, thickness=1, sb=4, sa=12))
        idea_p = ParagraphStyle(
            "idea", fontName="Helvetica", fontSize=10, leading=15,
            textColor=GRAY_800, leftIndent=14, spaceAfter=6,
        )
        for idea in selected:
            story.append(Paragraph(f"–\u2002{idea}", idea_p))
        story.append(PageBreak())

    # ── THINKING JOURNEY ──────────────────────────────────────────────────────
    for p in range(page_counter[0], page_counter[0] + 4):
        page_callbacks[p] = _interior_canvas

    story.extend(_thinking_journey_page(session_data, styles))

    doc.build(story, onFirstPage=dispatch, onLaterPages=dispatch)
    buffer.seek(0)
    return buffer.read()
