"""Shared Enable My Growth identity for AI Thinking Studio."""

from __future__ import annotations

import base64
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

NIGHT = "#0A0A0F"
SURFACE = "#111118"
IVORY = "#EDEAE3"
GOLD = "#C9A96E"
DEEP_GOLD = "#7A6038"
MUTED = "#918E86"
RULE = "#292832"

PRODUCT_NAME = "AI Thinking Studio™"
PRODUCT_EDITION = "Workshop Edition"
PRODUCT_DESCRIPTOR = "A structured environment for examining decisions before reaching conclusions."
ENDORSEMENT = "An Enable My Growth application, developed by Feras Banna."
BRAND_LINE = "Perspective changes what becomes possible."


def asset_data_uri(filename: str) -> str:
    """Return a local PNG as an embeddable data URI."""
    path = ASSETS / filename
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def register_brand_fonts() -> tuple[str, str, str]:
    """Register the licensed brand fonts with ReportLab."""
    fonts = {
        "EMG-Serif": FONTS / "CormorantGaramond-Regular.otf",
        "EMG-Serif-Semibold": FONTS / "CormorantGaramond-SemiBold.otf",
        "EMG-Sans": FONTS / "Inter-Regular.otf",
        "EMG-Sans-Medium": FONTS / "Inter-Medium.otf",
    }
    for name, path in fonts.items():
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(path)))
    return "EMG-Serif", "EMG-Sans", "EMG-Sans-Medium"


def sidebar_brand_html() -> str:
    return f"""
    <div class="emg-sidebar-brand">
        <img src="{asset_data_uri('emg-3d-mark.png')}" alt="Enable My Growth Möbius mark">
        <div>
            <div class="emg-product-name">AI Thinking Studio™</div>
            <div class="emg-edition">Workshop Edition</div>
        </div>
    </div>
    <div class="emg-endorsement">BY ENABLE MY GROWTH · FERAS BANNA</div>
    <hr class="emg-rule">
    """


def auth_brand_html() -> str:
    return f"""
    <div class="emg-auth-brand">
        <img src="{asset_data_uri('emg-3d-lockup.png')}" alt="Enable My Growth">
        <div class="emg-auth-product">AI Thinking Studio™</div>
        <div class="emg-auth-edition">WORKSHOP EDITION</div>
        <div class="emg-auth-descriptor">{PRODUCT_DESCRIPTOR}</div>
        <div class="emg-auth-endorsement">{ENDORSEMENT}</div>
    </div>
    """


BRAND_CSS = f"""
<style>
    @font-face {{
        font-family: 'EMG Cormorant';
        src: url(data:font/otf;base64,{base64.b64encode((FONTS / 'CormorantGaramond-Regular.otf').read_bytes()).decode('ascii')}) format('opentype');
        font-weight: 400;
    }}
    @font-face {{
        font-family: 'EMG Cormorant';
        src: url(data:font/otf;base64,{base64.b64encode((FONTS / 'CormorantGaramond-SemiBold.otf').read_bytes()).decode('ascii')}) format('opentype');
        font-weight: 600;
    }}
    @font-face {{
        font-family: 'EMG Inter';
        src: url(data:font/otf;base64,{base64.b64encode((FONTS / 'Inter-Regular.otf').read_bytes()).decode('ascii')}) format('opentype');
        font-weight: 400;
    }}
    @font-face {{
        font-family: 'EMG Inter';
        src: url(data:font/otf;base64,{base64.b64encode((FONTS / 'Inter-Medium.otf').read_bytes()).decode('ascii')}) format('opentype');
        font-weight: 500;
    }}

    :root {{
        --emg-night: {NIGHT};
        --emg-surface: {SURFACE};
        --emg-ivory: {IVORY};
        --emg-gold: {GOLD};
        --emg-deep-gold: {DEEP_GOLD};
        --emg-muted: {MUTED};
        --emg-rule: {RULE};
    }}

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
        font-family: 'EMG Inter', sans-serif;
    }}
    .stApp {{ background-color: var(--emg-night); color: var(--emg-ivory); }}
    [data-testid="stSidebar"] {{
        background-color: var(--emg-surface);
        border-right: 1px solid var(--emg-rule);
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent; border: none; color: var(--emg-muted);
        font-size: 0.82rem; font-weight: 400; text-align: left;
        padding: 7px 12px; width: 100%; border-radius: 4px;
        transition: all 0.15s ease;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background: #1A191F; color: var(--emg-ivory);
    }}
    .emg-sidebar-brand {{ display:flex; align-items:center; gap:10px; padding:16px 10px 6px; }}
    .emg-sidebar-brand img {{ width:54px; height:54px; object-fit:contain; }}
    .emg-product-name {{ font-family:'EMG Cormorant', serif; font-size:1.18rem; color:var(--emg-ivory); line-height:1.05; }}
    .emg-edition, .emg-endorsement {{ font-size:0.64rem; color:var(--emg-gold); letter-spacing:0.12em; text-transform:uppercase; }}
    .emg-endorsement {{ padding:0 12px 8px; color:var(--emg-muted); }}
    .emg-rule {{ border:none; border-top:1px solid var(--emg-rule); margin:7px 12px 12px; }}

    .emg-auth-brand {{ max-width:640px; margin:18px auto 26px; text-align:center; }}
    .emg-auth-brand img {{ width:280px; max-width:72%; height:auto; margin-bottom:16px; }}
    .emg-auth-product {{ font-family:'EMG Cormorant', serif; color:var(--emg-ivory); font-size:2.45rem; line-height:1; }}
    .emg-auth-edition {{ color:var(--emg-gold); font-size:0.69rem; letter-spacing:0.2em; margin-top:8px; }}
    .emg-auth-descriptor {{ color:var(--emg-muted); font-size:0.93rem; margin:20px auto 8px; max-width:520px; }}
    .emg-auth-endorsement {{ color:var(--emg-gold); font-size:0.72rem; letter-spacing:0.06em; }}

    .room-header {{ font-family:'EMG Cormorant', serif; font-size:2rem; font-weight:500; color:var(--emg-ivory); margin-bottom:4px; }}
    .room-subtitle {{ font-size:0.76rem; color:var(--emg-gold); margin-bottom:20px; letter-spacing:0.11em; text-transform:uppercase; }}
    .room-description {{ font-size:0.93rem; color:var(--emg-muted); line-height:1.75; margin-bottom:24px; border-left:2px solid var(--emg-gold); padding-left:16px; max-width:920px; }}
    .promise-card {{ background:linear-gradient(135deg, #111118 0%, #0A0A0F 100%); border:1px solid var(--emg-deep-gold); border-radius:8px; padding:40px 48px; margin:24px 0; }}
    .promise-title {{ font-family:'EMG Cormorant', serif; font-size:2.7rem; font-weight:500; color:var(--emg-ivory); margin-bottom:8px; }}
    .promise-line {{ font-size:1.02rem; color:#D8D3CA; line-height:1.9; padding:6px 0; }}
    .section-divider {{ border:none; border-top:1px solid var(--emg-rule); margin:24px 0; }}
    .expedition-card {{ background:var(--emg-surface); border:1px solid var(--emg-rule); border-radius:6px; padding:16px 20px; margin-bottom:8px; }}
    .expedition-title {{ font-size:0.95rem; color:var(--emg-ivory); font-weight:500; margin-bottom:4px; }}
    .expedition-meta {{ font-size:0.78rem; color:var(--emg-muted); }}

    .stTextInput > div > div > input, .stTextArea > div > div > textarea {{
        background-color:var(--emg-surface) !important; border:1px solid var(--emg-rule) !important;
        color:var(--emg-ivory) !important; border-radius:5px; font-size:0.92rem;
    }}
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {{
        border-color:var(--emg-gold) !important; box-shadow:0 0 0 2px rgba(201,169,110,0.13) !important;
    }}
    .stButton > button, .stFormSubmitButton > button {{
        background:var(--emg-gold); color:var(--emg-night); border:1px solid var(--emg-gold);
        border-radius:4px; font-size:0.84rem; font-weight:500; letter-spacing:0.035em;
        padding:10px 24px; transition:all 0.15s ease;
    }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{ background:#D7BB83; border-color:#D7BB83; color:var(--emg-night); }}
    label, .stTextInput label, .stTextArea label {{ color:var(--emg-gold) !important; font-size:0.78rem !important; font-weight:500 !important; letter-spacing:0.07em !important; text-transform:uppercase !important; }}
    .stDownloadButton > button {{ background:var(--emg-surface); color:var(--emg-gold); border:1px solid var(--emg-deep-gold); border-radius:4px; }}
    [data-testid="stExpander"] {{ background:var(--emg-surface); border:1px solid var(--emg-rule); border-radius:6px; }}
    a {{ color:var(--emg-gold) !important; }}
    #MainMenu, footer, header {{ visibility:hidden; }}
</style>
"""
