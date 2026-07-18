"""Enable My Growth branded Thinking Record PDF builder."""

import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Image, KeepTogether, PageBreak, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

from core.brand import ASSETS, ENDORSEMENT, PRODUCT_NAME, register_brand_fonts

W, H = A4
CONTENT_W = W - 36 * mm   # usable text width

# ── Palette ───────────────────────────────────────────────────────────────────
INK          = colors.HexColor("#0A0A0F")
DEEP         = colors.HexColor("#111118")
RULE         = colors.HexColor("#292832")
ACCENT       = colors.HexColor("#7A6038")
ACCENT_LIGHT = colors.HexColor("#EDEAE3")
WHITE        = colors.HexColor("#EDEAE3")
OFF_WHITE    = colors.HexColor("#F7F5EF")
GRAY_800     = colors.HexColor("#2B2926")
GRAY_500     = colors.HexColor("#706B63")
GRAY_300     = colors.HexColor("#B7B2A8")
GOLD         = colors.HexColor("#C9A96E")
GOLD_LIGHT   = colors.HexColor("#D7BB83")
GOLD_BG      = colors.HexColor("#F3EDE1")
GREEN        = ACCENT
GREEN_LIGHT  = GOLD_LIGHT
GREEN_BG     = GOLD_BG
TEAL         = ACCENT
TEAL_LIGHT   = GOLD_LIGHT
TEAL_BG      = GOLD_BG
RED_DARK     = ACCENT

SERIF, SANS, SANS_MEDIUM = register_brand_fonts()

FOOTER_TEXT  = "The purpose of this Studio is not to accelerate conclusions, but to deepen examination."

ROOM_PALETTE = {
    "Mirror Room":      (DEEP, ACCENT_LIGHT, GOLD),
    "Human Room":       (DEEP, ACCENT_LIGHT, GOLD),
    "Possibility Room": (DEEP, ACCENT_LIGHT, GOLD),
    "Challenge Room":   (DEEP, ACCENT_LIGHT, GOLD),
    "Future Room":      (DEEP, ACCENT_LIGHT, GOLD),
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
        "cover_product", fontName=SANS, fontSize=9, leading=13,
        textColor=GRAY_300, alignment=TA_CENTER, spaceAfter=0,
    )
    S["cover_title"] = ParagraphStyle(
        "cover_title", fontName=SERIF, fontSize=36, leading=42,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
    )
    S["cover_challenge"] = ParagraphStyle(
        "cover_challenge", fontName=SERIF, fontSize=18, leading=24,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
    )
    S["cover_meta"] = ParagraphStyle(
        "cover_meta", fontName=SANS, fontSize=9, leading=13,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    S["cover_doctrine"] = ParagraphStyle(
        "cover_doctrine", fontName=SANS, fontSize=9, leading=14,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    S["setup_label"] = ParagraphStyle(
        "setup_label", fontName=SANS_MEDIUM, fontSize=7.5, leading=11,
        textColor=GRAY_500, spaceAfter=2,
    )
    S["setup_value"] = ParagraphStyle(
        "setup_value", fontName=SANS, fontSize=10, leading=15,
        textColor=GRAY_800, spaceAfter=0,
    )
    S["setup_revised"] = ParagraphStyle(
        "setup_revised", fontName=SANS_MEDIUM, fontSize=11, leading=16,
        textColor=ACCENT, spaceAfter=0,
    )
    S["room_section"] = ParagraphStyle(
        "room_section", fontName=SANS_MEDIUM, fontSize=10, leading=14,
        textColor=ACCENT, spaceBefore=14, spaceAfter=3,
    )
    S["body"] = ParagraphStyle(
        "body", fontName=SANS, fontSize=9.5, leading=15,
        textColor=GRAY_800, spaceAfter=5,
    )
    S["bullet"] = ParagraphStyle(
        "bullet", fontName=SANS, fontSize=9.5, leading=14,
        textColor=GRAY_800, leftIndent=14, spaceAfter=3,
    )
    S["bold_line"] = ParagraphStyle(
        "bold_line", fontName=SANS_MEDIUM, fontSize=9.5, leading=14,
        textColor=GRAY_800, spaceBefore=6, spaceAfter=2,
    )
    S["risk_label"] = ParagraphStyle(
        "risk_label", fontName=SANS_MEDIUM, fontSize=7, leading=10,
        textColor=GRAY_500, spaceAfter=3,
    )
    S["risk_text"] = ParagraphStyle(
        "risk_text", fontName=SANS, fontSize=10, leading=15,
        textColor=ACCENT_LIGHT, spaceAfter=0,
    )
    S["doctrine"] = ParagraphStyle(
        "doctrine", fontName=SANS, fontSize=8, leading=12,
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
    canvas.setFont(SANS, 6.5)
    canvas.setFillColor(GRAY_500)
    canvas.drawCentredString(W / 2, 13 * mm, FOOTER_TEXT)
    canvas.setFont(SANS, 6.5)
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
        canvas.setFont(SERIF, 18)
        canvas.setFillColor(band_text)
        canvas.drawString(18 * mm, H - 16 * mm, room_name)
        canvas.setFont(SANS, 8)
        canvas.setFillColor(GRAY_500)
        canvas.drawString(18 * mm, H - 22 * mm, subtitle.upper())
        canvas.setFont(SANS, 6.5)
        canvas.setFillColor(GRAY_500)
        canvas.drawCentredString(W / 2, 13 * mm, FOOTER_TEXT)
        canvas.setFont(SANS, 6.5)
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
    "biggest blind spot":                  ("Biggest Blind Spot",                     GOLD,  GOLD_LIGHT,  colors.HexColor("#111118")),
    "most dangerous assumption":           ("Most Dangerous Assumption",               GOLD,  GOLD_LIGHT,  colors.HexColor("#111118")),
    "condition most likely to be absent":  ("Condition Most Likely To Be Absent",     TEAL,  TEAL_LIGHT,  colors.HexColor("#111118")),
    "most unexpected direction":           ("Most Unexpected Direction",               TEAL,  TEAL_LIGHT,  colors.HexColor("#111118")),
    "stakeholder most likely to surprise": ("Stakeholder Most Likely To Surprise You", TEAL, TEAL_LIGHT,  colors.HexColor("#111118")),
    "consequence most likely to be ignored":("Consequence Most Likely To Be Ignored", GREEN, GREEN_LIGHT, colors.HexColor("#111118")),
    "sign most likely to be missed":       ("Sign Most Likely To Be Missed",          GREEN, GREEN_LIGHT, colors.HexColor("#111118")),
}


def _callout_box(content: str, label: str, border_color, text_color, bg_color) -> list:
    """Render a visually distinct bordered callout panel."""
    label_p = ParagraphStyle(
        "cl_label", fontName=SANS_MEDIUM, fontSize=7, leading=10,
        textColor=border_color, spaceAfter=4,
    )
    text_p = ParagraphStyle(
        "cl_text", fontName=SANS_MEDIUM, fontSize=11, leading=16,
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
        "sb_label", fontName=SANS_MEDIUM, fontSize=9.5,
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

    bold_style = ParagraphStyle(
        "ai_bold", fontName=SANS_MEDIUM, fontSize=9.5, leading=14,
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
        "jh", fontName=SANS_MEDIUM, fontSize=20, leading=26,
        textColor=WHITE, spaceAfter=2,
    )
    sub_p = ParagraphStyle(
        "js", fontName=SANS, fontSize=9, leading=13,
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
            f"nl", fontName=SANS_MEDIUM, fontSize=7, leading=10,
            textColor=label_color, spaceAfter=3,
        )
        tp = ParagraphStyle(
            f"nt", fontName=SANS, fontSize=10, leading=15,
            textColor=text_color, spaceAfter=0,
        )
        bg_color = bg or colors.HexColor("#F7F5EF")
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
        ap = ParagraphStyle("arr", fontName=SANS, fontSize=11,
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
                          ACCENT, GRAY_800, colors.HexColor("#F3EDE1")))
        story.extend(arrow())
    elif items.get("best_reframe"):
        story.extend(node("Strongest alternative framing", items["best_reframe"],
                          ACCENT, GRAY_800, colors.HexColor("#F3EDE1")))
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


# ── Synthesis section renderers ───────────────────────────────────────────────

def _parse_synthesis(raw: str) -> dict:
    """
    Parse the AI synthesis output into four named sections.
    Splits on ## headers and returns a dict keyed by section name.
    """
    sections = {}
    current_key = None
    current_lines = []

    for line in raw.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## "):
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = stripped[3:].strip().upper()
            current_lines = []
        else:
            current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def _synthesis_page_title(title: str, subtitle: str, styles: dict,
                           accent=None) -> list:
    """Dark band title for synthesis pages."""
    accent = accent or ACCENT
    title_p = ParagraphStyle(
        "syn_title", fontName=SANS_MEDIUM, fontSize=20, leading=26,
        textColor=WHITE, spaceAfter=3,
    )
    sub_p = ParagraphStyle(
        "syn_sub", fontName=SANS, fontSize=9, leading=13,
        textColor=GRAY_300, spaceAfter=0,
    )
    t = Table(
        [[Paragraph(title, title_p)], [Paragraph(subtitle, sub_p)]],
        colWidths=[CONTENT_W],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), INK),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LINEBELOW",    (0, -1), (-1, -1), 1.5, accent),
    ]))
    return [t, Spacer(1, 16)]


def _render_executive_summary(text: str, styles: dict) -> list:
    """Render the Executive Summary section."""
    story = []
    story.extend(_synthesis_page_title(
        "Executive Summary",
        "The examination at a glance — not a recommendation, a record.",
        styles, ACCENT,
    ))

    body_p = ParagraphStyle(
        "exec_body", fontName=SANS, fontSize=10, leading=16,
        textColor=GRAY_800, spaceAfter=6,
    )

    for line in text.split("\n"):
        s = line.strip()
        if not s or _is_suppressed(s):
            story.append(Spacer(1, 3))
            continue
        if s.startswith("#"):
            continue  # skip any sub-headers in the summary
        if s.startswith(("- ", "• ", "* ")):
            story.append(Paragraph(
                f"–\u2002{_convert_inline_bold(s[2:])}",
                ParagraphStyle("exec_bull", parent=body_p, leftIndent=14),
            ))
        else:
            story.append(Paragraph(_convert_inline_bold(s), body_p))

    return story


def _render_evidence_gained(text: str, styles: dict) -> list:
    """Render the Evidence Gained section with Before/After panels."""
    story = []
    story.extend(_synthesis_page_title(
        "Evidence Gained",
        "How understanding evolved — not what to do, but what is now visible.",
        styles, TEAL,
    ))

    before_p = ParagraphStyle(
        "eg_label_b", fontName=SANS_MEDIUM, fontSize=7.5, leading=11,
        textColor=GRAY_500, spaceAfter=3,
    )
    after_p = ParagraphStyle(
        "eg_label_a", fontName=SANS_MEDIUM, fontSize=7.5, leading=11,
        textColor=TEAL, spaceAfter=3,
    )
    before_text_p = ParagraphStyle(
        "eg_before", fontName=SANS, fontSize=10, leading=15,
        textColor=GRAY_800, spaceAfter=0,
    )
    after_text_p = ParagraphStyle(
        "eg_after", fontName=SANS, fontSize=10, leading=15,
        textColor=GRAY_800, spaceAfter=0,
    )

    # Parse BEFORE:/AFTER: pairs
    pairs = []
    current_before = ""
    current_after  = ""

    for line in text.split("\n"):
        s = line.strip()
        if s.upper().startswith("BEFORE:"):
            if current_before and current_after:
                pairs.append((current_before, current_after))
                current_after = ""
            current_before = s.split(":", 1)[-1].strip()
        elif s.upper().startswith("AFTER:"):
            current_after = s.split(":", 1)[-1].strip()

    if current_before and current_after:
        pairs.append((current_before, current_after))

    # If AI didn't follow format, fall back to body text
    if not pairs:
        for line in text.split("\n"):
            s = line.strip()
            if s:
                story.append(Paragraph(_convert_inline_bold(s), styles["body"]))
        return story

    for before, after in pairs:
        col_w = CONTENT_W / 2 - 4 * mm
        before_cell = [
            Paragraph("BEFORE", before_p),
            Paragraph(before, before_text_p),
        ]
        after_cell = [
            Paragraph("AFTER", after_p),
            Paragraph(after, after_text_p),
        ]
        t = Table([[before_cell, after_cell]], colWidths=[col_w, col_w])
        t.setStyle(TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING",   (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
            ("BACKGROUND",   (0, 0), (0, -1),  colors.HexColor("#F7F5EF")),
            ("BACKGROUND",   (1, 0), (1, -1),  colors.HexColor("#F3EDE1")),
            ("LINEBEFORE",   (0, 0), (0, -1),  3, GRAY_500),
            ("LINEBEFORE",   (1, 0), (1, -1),  3, TEAL),
            ("LINEBELOW",    (0, 0), (-1, -1), 0.3, RULE),
        ]))
        story.append(KeepTogether([t]))
        story.append(Spacer(1, 10))

    return story


def _render_current_state(text: str, styles: dict) -> list:
    """Render the Current State of Understanding section."""
    story = []
    story.extend(_synthesis_page_title(
        "Current State of Understanding",
        "What the expedition made clearer — and what it did not resolve.",
        styles, GOLD,
    ))

    sub_p = ParagraphStyle(
        "cs_sub", fontName=SANS_MEDIUM, fontSize=10, leading=14,
        textColor=GOLD, spaceBefore=12, spaceAfter=4,
    )
    body_p = styles["body"]
    bullet_p = ParagraphStyle(
        "cs_bull", parent=body_p, leftIndent=14, spaceAfter=3,
    )
    check_p = ParagraphStyle(
        "cs_check", fontName=SANS, fontSize=9.5, leading=14,
        textColor=GRAY_800, leftIndent=8, spaceAfter=3,
    )
    check_done_p = ParagraphStyle(
        "cs_check_done", fontName=SANS_MEDIUM, fontSize=9.5, leading=14,
        textColor=GREEN, leftIndent=8, spaceAfter=3,
    )

    in_checklist = False

    for line in text.split("\n"):
        s = line.strip()
        if not s or _is_suppressed(s):
            story.append(Spacer(1, 3))
            continue

        # Detect checklist block
        if "EXAMINATION INDICATORS" in s.upper():
            in_checklist = True
            story.append(Spacer(1, 10))
            story.append(_rule(GOLD, thickness=0.3, sb=2, sa=6))
            story.append(Paragraph(
                "EXAMINATION INDICATORS",
                ParagraphStyle("ci_hdr", fontName=SANS_MEDIUM, fontSize=8,
                               leading=12, textColor=GRAY_500, spaceAfter=6),
            ))
            continue

        if in_checklist:
            if s.startswith("✓"):
                story.append(Paragraph(s, check_done_p))
            elif s.startswith("○"):
                story.append(Paragraph(s, check_p))
            else:
                in_checklist = False

        if not in_checklist:
            if s.startswith("### "):
                story.append(Paragraph(s[4:], sub_p))
            elif s.startswith("#"):
                pass  # skip top-level headers already handled
            elif s.startswith(("- ", "• ", "* ")):
                story.append(Paragraph(
                    f"–\u2002{_convert_inline_bold(s[2:])}", bullet_p
                ))
            else:
                story.append(Paragraph(_convert_inline_bold(s), body_p))

    return story


def _render_edge_of_understanding(text: str, styles: dict) -> list:
    """Render The Edge of Understanding — the final page."""
    story = []
    story.extend(_synthesis_page_title(
        "The Edge of Understanding",
        "Not a recommendations page. The final boundary of what this expedition made visible.",
        styles, colors.HexColor("#7A6038"),
    ))

    sub_p = ParagraphStyle(
        "eu_sub", fontName=SANS_MEDIUM, fontSize=11, leading=15,
        textColor=colors.HexColor("#7A6038"), spaceBefore=14, spaceAfter=5,
    )
    body_p = ParagraphStyle(
        "eu_body", fontName=SANS, fontSize=10, leading=16,
        textColor=GRAY_800, spaceAfter=5,
    )
    bullet_p = ParagraphStyle(
        "eu_bull", parent=body_p, leftIndent=14, spaceAfter=3,
    )

    for line in text.split("\n"):
        s = line.strip()
        if not s or _is_suppressed(s):
            story.append(Spacer(1, 3))
            continue
        if s.startswith("### "):
            story.append(Paragraph(s[4:], sub_p))
        elif s.startswith("#"):
            pass
        elif s.startswith(("- ", "• ", "* ")):
            story.append(Paragraph(
                f"–\u2002{_convert_inline_bold(s[2:])}", bullet_p
            ))
        else:
            story.append(Paragraph(_convert_inline_bold(s), body_p))

    # Closing doctrine line
    story.append(Spacer(1, 20))
    story.append(_rule(colors.HexColor("#7A6038"), thickness=0.8))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The purpose of the expedition is not to produce certainty. "
        "It is to make the current limits of understanding visible.",
        ParagraphStyle(
            "eu_close", fontName=SANS, fontSize=10, leading=16,
            textColor=colors.HexColor("#7A6038"), alignment=TA_CENTER,
        ),
    ))

    return story


# ── Main PDF builder ──────────────────────────────────────────────────────────

def generate_pdf(session_data: dict, synthesis_text: str = "") -> bytes:
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
        topMargin=24 * mm, bottomMargin=24 * mm,
        title="AI Thinking Studio™ — Thinking Record",
        author=PRODUCT_NAME,
    )

    story = []

    # ── COVER ────────────────────────────────────────────────────────────────
    cover_product_p = ParagraphStyle(
        "cov_prod", fontName=SANS, fontSize=9, leading=13,
        textColor=GRAY_300, alignment=TA_CENTER,
    )
    cover_title_p = ParagraphStyle(
        "cov_t", fontName=SERIF, fontSize=36, leading=42,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=4,
    )
    cover_sub_p = ParagraphStyle(
        "cov_s", fontName=SERIF, fontSize=18, leading=24,
        textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
    )
    cover_meta_p = ParagraphStyle(
        "cov_m", fontName=SANS, fontSize=9, leading=13,
        textColor=GRAY_500, alignment=TA_CENTER,
    )
    cover_doc_p = ParagraphStyle(
        "cov_d", fontName=SANS, fontSize=9, leading=14,
        textColor=GRAY_500, alignment=TA_CENTER,
    )

    story.append(Spacer(1, 17 * mm))
    logo = Image(str(ASSETS / "emg-3d-lockup.png"), width=72 * mm, height=21 * mm)
    logo.hAlign = "CENTER"
    story.append(logo)
    story.append(Spacer(1, 11 * mm))
    story.append(Paragraph("AI THINKING STUDIO™ · WORKSHOP EDITION", cover_product_p))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Thinking Record", cover_title_p))
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

    challenge_title = setup.get("challenge_title", "Untitled Session")
    story.append(Paragraph(challenge_title, cover_sub_p))
    story.append(Spacer(1, 4))
    story.append(Paragraph(ENDORSEMENT, cover_meta_p))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%d %B %Y')}",
        cover_meta_p,
    ))
    story.append(Spacer(1, 35 * mm))
    story.append(Paragraph(FOOTER_TEXT, cover_doc_p))
    story.append(PageBreak())

    # ── EXPEDITION SETUP ─────────────────────────────────────────────────────
    page_callbacks[2] = _interior_canvas

    setup_title_p = ParagraphStyle(
        "st", fontName=SANS_MEDIUM, fontSize=16, leading=20,
        textColor=GRAY_800, spaceAfter=2,
    )
    story.append(Spacer(1, 4))
    story.append(Paragraph("Session Setup", setup_title_p))
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

    # ── EXECUTIVE SUMMARY (AI-generated) ──────────────────────────────────────
    if synthesis_text:
        page_callbacks[3] = _interior_canvas
        sections = _parse_synthesis(synthesis_text)
        exec_text = sections.get("EXECUTIVE SUMMARY", "")
        if exec_text:
            story.append(Spacer(1, 4))
            story.extend(_render_executive_summary(exec_text, styles))
            story.append(PageBreak())

    # ── ROOM SECTIONS ─────────────────────────────────────────────────────────
    rooms = [
        ("mirror_output",      "Mirror Room",      "Assumption Inventory & Examination Gaps"),
        ("human_output",       "Human Room",       "Stakeholder Perspective Map"),
        ("possibility_output", "Possibility Room", "Directions Worth Examining"),
        ("battlefield_output", "Challenge Room", "Where Ideas Get Challenged"),
        ("future_output",      "Future Room",      "How This Unfolds Over Time"),
    ]

    page_counter = [4 if synthesis_text else 3]

    for key, room_name, room_desc in rooms:
        content = session_data.get(key, "")
        room_cb = _room_canvas(room_name, room_desc)
        page_callbacks[page_counter[0]] = room_cb
        page_counter[0] += 8

        story.append(Spacer(1, 34 * mm))

        # Participant risk block (Challenge Room only)
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
                    ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#111118")),
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
            "si", fontName=SANS_MEDIUM, fontSize=16, leading=20,
            textColor=GRAY_800, spaceAfter=2,
        )
        story.append(Spacer(1, 4))
        story.append(Paragraph("Selected Ideas", si_p))
        story.append(_rule(ACCENT, thickness=1, sb=4, sa=12))
        idea_p = ParagraphStyle(
            "idea", fontName=SANS, fontSize=10, leading=15,
            textColor=GRAY_800, leftIndent=14, spaceAfter=6,
        )
        for idea in selected:
            story.append(Paragraph(f"–\u2002{idea}", idea_p))
        story.append(PageBreak())

    # ── EVIDENCE GAINED (AI-generated) ────────────────────────────────────────
    if synthesis_text:
        for p in range(page_counter[0], page_counter[0] + 4):
            page_callbacks[p] = _interior_canvas
        page_counter[0] += 4

        evidence_text = sections.get("EVIDENCE GAINED", "")
        if evidence_text:
            story.append(Spacer(1, 4))
            story.extend(_render_evidence_gained(evidence_text, styles))
            story.append(PageBreak())

        # ── CURRENT STATE OF UNDERSTANDING ────────────────────────────────────
        for p in range(page_counter[0], page_counter[0] + 4):
            page_callbacks[p] = _interior_canvas
        page_counter[0] += 4

        current_state_text = sections.get("CURRENT STATE OF UNDERSTANDING", "")
        if current_state_text:
            story.append(Spacer(1, 4))
            story.extend(_render_current_state(current_state_text, styles))
            story.append(PageBreak())

    # ── THINKING JOURNEY ──────────────────────────────────────────────────────
    for p in range(page_counter[0], page_counter[0] + 4):
        page_callbacks[p] = _interior_canvas
    page_counter[0] += 4

    story.extend(_thinking_journey_page(session_data, styles))
    story.append(PageBreak())

    # ── THE EDGE OF UNDERSTANDING (AI-generated) ──────────────────────────────
    if synthesis_text:
        for p in range(page_counter[0], page_counter[0] + 3):
            page_callbacks[p] = _interior_canvas

        edge_text = sections.get("THE EDGE OF UNDERSTANDING", "")
        if edge_text:
            story.append(Spacer(1, 4))
            story.extend(_render_edge_of_understanding(edge_text, styles))

    doc.build(story, onFirstPage=dispatch, onLaterPages=dispatch)
    buffer.seek(0)
    return buffer.read()
