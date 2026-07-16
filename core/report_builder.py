"""
core/report_builder.py
Builds the downloadable PDF Thinking Expedition Summary using ReportLab.
"""

import io
import re
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ── Palette ────────────────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#0D1117")
DEEP_BLUE  = colors.HexColor("#0F1B2D")
ACCENT     = colors.HexColor("#6C8EBF")
ACCENT_LIGHT = colors.HexColor("#A8C4E0")
WHITE      = colors.white
MID_GRAY   = colors.HexColor("#8899AA")
DARK_GRAY  = colors.HexColor("#2A3A4A")
GOLD       = colors.HexColor("#C9A84C")
GREEN      = colors.HexColor("#4CAF8E")
PANEL_BG   = colors.HexColor("#0B1420")

FOOTER_TEXT  = "The purpose of this Studio is not to accelerate conclusions, but to deepen examination."
PRODUCT_NAME = "AI Thinking Studio™ Lite"


# ── Styles ─────────────────────────────────────────────────────────────────────

def _styles():
    return {
        "cover_title": ParagraphStyle(
            "cover_title", fontName="Helvetica-Bold", fontSize=28, leading=34,
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=6,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", fontName="Helvetica", fontSize=13, leading=18,
            textColor=ACCENT_LIGHT, alignment=TA_CENTER, spaceAfter=4,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", fontName="Helvetica", fontSize=10, leading=14,
            textColor=MID_GRAY, alignment=TA_CENTER,
        ),
        "section_header": ParagraphStyle(
            "section_header", fontName="Helvetica-Bold", fontSize=14, leading=18,
            textColor=ACCENT, spaceBefore=18, spaceAfter=6,
        ),
        "room_title": ParagraphStyle(
            "room_title", fontName="Helvetica-Bold", fontSize=11, leading=15,
            textColor=GOLD, spaceBefore=14, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=DARK_GRAY, spaceAfter=6,
        ),
        "label": ParagraphStyle(
            "label", fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=MID_GRAY, spaceAfter=2,
        ),
        "challenge_text": ParagraphStyle(
            "challenge_text", fontName="Helvetica", fontSize=10, leading=15,
            textColor=DARK_GRAY, leftIndent=8, spaceAfter=8,
        ),
        "reflection": ParagraphStyle(
            "reflection", fontName="Helvetica-Oblique", fontSize=10, leading=15,
            textColor=DEEP_BLUE, leftIndent=12, rightIndent=12, spaceAfter=8,
        ),
        "doctrine": ParagraphStyle(
            "doctrine", fontName="Helvetica-Oblique", fontSize=9, leading=13,
            textColor=MID_GRAY, alignment=TA_CENTER,
        ),
        # Thinking Journey styles
        "journey_node_label": ParagraphStyle(
            "journey_node_label", fontName="Helvetica-Bold", fontSize=8, leading=11,
            textColor=MID_GRAY, spaceAfter=2,
        ),
        "journey_node_text": ParagraphStyle(
            "journey_node_text", fontName="Helvetica", fontSize=10, leading=14,
            textColor=ACCENT_LIGHT, spaceAfter=4,
        ),
        "journey_arrow": ParagraphStyle(
            "journey_arrow", fontName="Helvetica", fontSize=14, leading=18,
            textColor=ACCENT, alignment=TA_CENTER, spaceAfter=0,
        ),
        "journey_header": ParagraphStyle(
            "journey_header", fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=WHITE, spaceAfter=8,
        ),
    }


# ── Canvas footer ──────────────────────────────────────────────────────────────

def _footer_canvas(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.setFillColor(MID_GRAY)
    canvas.drawCentredString(A4[0] / 2, 14 * mm, FOOTER_TEXT)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(ACCENT)
    canvas.drawRightString(A4[0] - 15 * mm, 14 * mm, f"Page {doc.page}")
    canvas.drawString(15 * mm, 14 * mm, PRODUCT_NAME)
    canvas.restoreState()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _divider(color=ACCENT, thickness=0.5):
    return HRFlowable(
        width="100%", thickness=thickness, color=color,
        spaceBefore=4, spaceAfter=4, hAlign="CENTER",
    )


def _convert_inline_bold(text: str) -> str:
    """Convert **text** to <b>text</b> for ReportLab."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def _callout_box(text: str, label: str, border_color=GOLD, text_color=GOLD) -> list:
    """
    Render a visually distinct callout box for high-signal labelled items.
    Uses a single-cell Table to achieve a bordered panel effect.
    """
    label_style = ParagraphStyle(
        "callout_label", fontName="Helvetica-Bold", fontSize=7.5,
        leading=10, textColor=border_color, spaceAfter=3,
    )
    text_style = ParagraphStyle(
        "callout_text", fontName="Helvetica-Bold", fontSize=10.5,
        leading=15, textColor=text_color, spaceAfter=0,
    )
    cell_content = [
        Paragraph(label.upper(), label_style),
        Paragraph(text, text_style),
    ]
    table = Table(
        [[cell_content]],
        colWidths=["100%"],
    )
    table.setStyle(TableStyle([
        ("BOX",        (0, 0), (-1, -1), 1.2, border_color),
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
        ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor("#0D1A10")),
    ]))
    return [Spacer(1, 6), table, Spacer(1, 8)]


# Callout trigger patterns mapped to (label, border_color, text_color)
CALLOUT_PATTERNS = {
    "biggest blind spot":              ("Biggest Blind Spot",               GOLD,  GOLD),
    "most dangerous assumption":       ("Most Dangerous Assumption",         GOLD,  GOLD),
    "condition most likely to be absent": ("Condition Most Likely Absent",   ACCENT, ACCENT_LIGHT),
    "most unexpected direction":       ("Most Unexpected Direction",         ACCENT, ACCENT_LIGHT),
    "stakeholder most likely to surprise": ("Stakeholder Most Likely To Surprise You", ACCENT, ACCENT_LIGHT),
    "consequence most likely to be ignored": ("Consequence Most Likely To Be Ignored", GREEN, GREEN),
    "sign most likely to be missed":   ("Sign Most Likely To Be Missed",    GREEN, GREEN),
}


def _ai_content_block(text: str, styles: dict) -> list:
    """Convert markdown-ish AI output into ReportLab Paragraph elements.
    Key labelled lines are rendered as visual callout boxes."""
    elements = []
    if not text:
        elements.append(Paragraph("No content generated.", styles["body"]))
        return elements

    sub_header_style = ParagraphStyle(
        "sub_header", parent=styles["body"],
        fontName="Helvetica-Bold", fontSize=9.5,
        textColor=ACCENT, spaceBefore=8, spaceAfter=2,
    )
    bold_line_style = ParagraphStyle(
        "bold_line", parent=styles["body"],
        fontName="Helvetica-Bold", textColor=DARK_GRAY, spaceBefore=6,
    )
    bullet_style = ParagraphStyle(
        "bullet", parent=styles["body"], leftIndent=12, spaceAfter=3,
    )

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            elements.append(Spacer(1, 4))
            continue

        # Check for callout patterns first
        lower = stripped.lower()
        matched_callout = False
        for pattern, (label, border_color, text_color) in CALLOUT_PATTERNS.items():
            if pattern in lower:
                # Extract content after the colon
                clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
                content = clean.split(":", 1)[-1].strip() if ":" in clean else clean
                if content:
                    elements.extend(_callout_box(content, label, border_color, text_color))
                    matched_callout = True
                    break
        if matched_callout:
            continue

        if stripped.startswith("## "):
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(stripped[3:], styles["room_title"]))
        elif stripped.startswith("### "):
            elements.append(Paragraph(f"<b>{stripped[4:]}</b>", sub_header_style))
        elif stripped.startswith("**") and stripped.endswith("**"):
            elements.append(Paragraph(f"<b>{stripped[2:-2]}</b>", bold_line_style))
        elif stripped.startswith(("- ", "• ", "* ")):
            bullet_text = _convert_inline_bold(stripped[2:])
            elements.append(Paragraph(f"&bull;&nbsp;&nbsp;{bullet_text}", bullet_style))
        else:
            clean = _convert_inline_bold(stripped)
            elements.append(Paragraph(clean, styles["body"]))

    return elements


def _extract_starred_items(session_data: dict) -> dict:
    """
    Extract key labelled items from AI outputs for the Thinking Journey page.
    Looks for the room-specific personality labels introduced in prompts.py.
    Returns a dict of named items.
    """
    items = {}

    def first_match(text: str, patterns: list) -> str:
        """Return the first line in text matching any pattern, cleaned up."""
        if not text:
            return ""
        for line in text.split("\n"):
            for pattern in patterns:
                if pattern.lower() in line.lower():
                    # Strip markdown bold markers and the label prefix
                    clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
                    clean = re.sub(r"^[★\-\•\*\s]+", "", clean)
                    # Remove the label itself, keep the content after the colon
                    if ":" in clean:
                        clean = clean.split(":", 1)[-1].strip()
                    return clean[:200]  # hard cap
        return ""

    mirror = session_data.get("mirror_output", "")
    items["blind_spot"] = first_match(mirror, ["biggest blind spot"])
    items["missing_info"] = first_match(mirror, ["what may be missing", "missing"])

    # Best reframe: grab first Option A line
    for line in mirror.split("\n"):
        if "option a" in line.lower():
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            if ":" in clean:
                clean = clean.split(":", 1)[-1].strip()
            items["best_reframe"] = clean[:200]
            break
    else:
        items["best_reframe"] = ""

    human = session_data.get("human_output", "")
    items["surprise_stakeholder"] = first_match(human, ["stakeholder most likely to surprise"])

    possibility = session_data.get("possibility_output", "")
    items["unexpected_direction"] = first_match(possibility, ["most unexpected direction"])

    battlefield = session_data.get("battlefield_output", "")
    items["dangerous_assumption"] = first_match(battlefield, ["most dangerous assumption"])

    future = session_data.get("future_output", "")
    items["ignored_consequence"] = first_match(future, ["consequence most likely to be ignored"])
    items["missed_sign"] = first_match(future, ["sign most likely to be missed"])

    return items


def _thinking_journey_page(session_data: dict, styles: dict) -> list:
    """
    Build the Thinking Journey page — the transformation arc of the expedition.
    Shows where the participant started and what shifted.
    """
    story = []
    setup = session_data.get("expedition_setup", {})
    items = _extract_starred_items(session_data)

    story.append(Paragraph("Your Thinking Journey", styles["journey_header"]))
    story.append(Paragraph(
        "What changed in your understanding because of this expedition.",
        styles["doctrine"],
    ))
    story.append(_divider(color=GOLD, thickness=0.5))
    story.append(Spacer(1, 8))

    def node(label: str, text: str, color=ACCENT_LIGHT):
        """Render one node in the journey."""
        node_style = ParagraphStyle(
            f"node_{label}", fontName="Helvetica", fontSize=10, leading=14,
            textColor=color, leftIndent=0, spaceAfter=2,
        )
        label_style = ParagraphStyle(
            f"nodelabel_{label}", fontName="Helvetica-Bold", fontSize=7.5,
            leading=11, textColor=MID_GRAY, spaceAfter=1,
            borderPadding=(4, 8, 4, 8),
        )
        return [
            Paragraph(label.upper(), label_style),
            Paragraph(text if text else "—", node_style),
            Spacer(1, 2),
        ]

    def arrow():
        return [Paragraph("↓", styles["journey_arrow"]), Spacer(1, 2)]

    # Build the journey chain
    original = setup.get("challenge_statement", "—")
    revised  = session_data.get("revised_challenge", "")

    story.extend(node("Where you started", original))
    story.extend(arrow())

    if items.get("blind_spot"):
        story.extend(node("Biggest blind spot surfaced", items["blind_spot"], color=GOLD))
        story.extend(arrow())

    if items.get("missing_info"):
        story.extend(node("Most significant missing information", items["missing_info"]))
        story.extend(arrow())

    if revised:
        story.extend(node("How the challenge was reframed", revised, color=ACCENT_LIGHT))
        story.extend(arrow())
    elif items.get("best_reframe"):
        story.extend(node("Strongest alternative framing considered", items["best_reframe"], color=ACCENT_LIGHT))
        story.extend(arrow())

    if items.get("unexpected_direction"):
        story.extend(node("Most unexpected direction explored", items["unexpected_direction"]))
        story.extend(arrow())

    if items.get("dangerous_assumption"):
        story.extend(node("Most dangerous assumption identified", items["dangerous_assumption"], color=GOLD))
        story.extend(arrow())

    if items.get("ignored_consequence"):
        story.extend(node("Consequence most likely to be ignored", items["ignored_consequence"]))
        story.extend(arrow())

    # Completion counts
    rooms_done = sum(1 for k in [
        "mirror_output", "human_output", "possibility_output",
        "battlefield_output", "future_output",
    ] if session_data.get(k))
    selected_count = len(session_data.get("selected_ideas", []))

    summary_text = (
        f"{rooms_done} of 5 rooms completed  ·  "
        f"{selected_count} idea(s) stress-tested"
    )
    story.extend(node("What was examined", summary_text, color=MID_GRAY))
    story.extend(arrow())

    # Final reflection
    reflection = session_data.get("final_reflection", "")
    story.extend(node(
        "Your reflection",
        reflection if reflection else "No reflection recorded.",
        color=GREEN,
    ))

    story.append(Spacer(1, 12))
    story.append(_divider(color=GOLD, thickness=0.5))
    story.append(Spacer(1, 6))
    story.append(Paragraph(FOOTER_TEXT, styles["doctrine"]))

    return story


# ── Main PDF builder ───────────────────────────────────────────────────────────

def generate_pdf(session_data: dict) -> bytes:
    """
    Generate a complete Thinking Expedition PDF and return as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=22 * mm,
        title="AI Thinking Studio Lite — Thinking Expedition Summary",
        author="AI Thinking Studio™ Lite",
    )

    styles = _styles()
    story  = []
    setup  = session_data.get("expedition_setup", {})

    # ── Cover ──────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 30 * mm))
    story.append(Paragraph("AI Thinking Studio™ Lite", styles["cover_title"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Thinking Expedition Summary", styles["cover_subtitle"]))
    story.append(Spacer(1, 8))
    story.append(_divider(color=ACCENT, thickness=1))
    story.append(Spacer(1, 8))
    story.append(Paragraph(setup.get("challenge_title", "Untitled Expedition"), styles["cover_subtitle"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        styles["cover_meta"],
    ))
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph(FOOTER_TEXT, styles["doctrine"]))
    story.append(PageBreak())

    # ── Expedition Setup ───────────────────────────────────────────────────────
    story.append(Paragraph("Expedition Setup", styles["section_header"]))
    story.append(_divider())

    for label, value in [
        ("Challenge Title",              setup.get("challenge_title", "")),
        ("Original Challenge Statement", setup.get("challenge_statement", "")),
        ("Context & Background",         setup.get("context_background", "")),
        ("Who is Affected",              setup.get("who_is_affected", "")),
        ("Currently Being Considered",   setup.get("current_consideration", "")),
        ("What You Hope to Understand",  setup.get("hope_to_understand", "")),
    ]:
        story.append(Paragraph(label, styles["label"]))
        story.append(Paragraph(value or "—", styles["challenge_text"]))
        story.append(Spacer(1, 4))

    revised = session_data.get("revised_challenge", "")
    if revised:
        story.append(Spacer(1, 4))
        story.append(Paragraph("Revised Challenge Statement", styles["label"]))
        story.append(Paragraph(revised, styles["reflection"]))

    story.append(PageBreak())

    # ── Room Sections ──────────────────────────────────────────────────────────
    rooms = [
        ("mirror_output",      "Mirror Room",      "Assumption Inventory & Examination Gaps"),
        ("human_output",       "Human Room",       "Stakeholder Perspective Map"),
        ("possibility_output", "Possibility Room", "Directions Worth Examining"),
        ("battlefield_output", "Battlefield Room", "Where Ideas Get Challenged"),
        ("future_output",      "Future Room",      "How This Unfolds Over Time"),
    ]

    participant_risk_style = ParagraphStyle(
        "participant_risk", fontName="Helvetica-Oblique", fontSize=10, leading=15,
        textColor=ACCENT_LIGHT, leftIndent=12, rightIndent=12, spaceAfter=4,
    )
    participant_risk_label = ParagraphStyle(
        "participant_risk_label", fontName="Helvetica-Bold", fontSize=8,
        leading=11, textColor=MID_GRAY, spaceAfter=3,
    )

    for key, room_name, room_desc in rooms:
        content = session_data.get(key, "")
        story.append(Paragraph(room_name, styles["section_header"]))
        story.append(Paragraph(room_desc, styles["doctrine"]))
        story.append(_divider())

        # For Battlefield, show participant's own risk assessment first
        if key == "battlefield_output":
            participant_risk = session_data.get("participant_risk", "").strip()
            if participant_risk:
                story.append(Spacer(1, 4))
                story.append(Paragraph(
                    "BEFORE SEEING THE AI CHALLENGE — THE PARTICIPANT IDENTIFIED:",
                    participant_risk_label,
                ))
                story.append(Paragraph(f'"{participant_risk}"', participant_risk_style))
                story.append(_divider(color=ACCENT, thickness=0.3))
                story.append(Spacer(1, 4))

        if content:
            story.extend(_ai_content_block(content, styles))
        else:
            story.append(Paragraph(
                "This room was not completed during the expedition.",
                styles["body"],
            ))
        story.append(PageBreak())

    # ── Selected Ideas ─────────────────────────────────────────────────────────
    selected = session_data.get("selected_ideas", [])
    if selected:
        story.append(Paragraph("Selected Ideas", styles["section_header"]))
        story.append(_divider())
        bullet_style = ParagraphStyle("bullet_idea", parent=styles["body"], leftIndent=12)
        for idea in selected:
            story.append(Paragraph(f"&bull;&nbsp;&nbsp;{idea}", bullet_style))
        story.append(Spacer(1, 8))
        story.append(PageBreak())

    # ── Thinking Journey ───────────────────────────────────────────────────────
    story.extend(_thinking_journey_page(session_data, styles))

    # Build
    doc.build(story, onFirstPage=_footer_canvas, onLaterPages=_footer_canvas)
    buffer.seek(0)
    return buffer.read()
