import calendar
from datetime import date, datetime, timedelta
from io import BytesIO
from html import escape
import re

import numpy as np
import pandas as pd
import streamlit as st

PAS_YELLOW = "#FFD400"
PAS_BLACK = "#0A0A0A"
PAS_DARK = "#171717"
PAS_GREY = "#F4F4F4"

st.set_page_config(page_title="PAS Live Cost Dashboard", page_icon="pas_logo.png", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{ background: #f7f8fa !important; color: #0A0A0A !important; font-family: Inter, "Segoe UI", Arial, sans-serif; }}
    .block-container {{ max-width: 1580px !important; padding-top: 1.35rem !important; padding-left: 2rem !important; padding-right: 2rem !important; padding-bottom: 2rem !important; }}

    /* Keep date input and form labels readable on the main page */
    div[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] *,
    label,
    label * {{ color:#0A0A0A !important; font-weight:900 !important; }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] label *,
    section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] * {{ color:#ffffff !important; }}

    /* Date inputs: keep as clean calendar fields, not dark blocks */
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] button,
    div[data-baseweb="input"] input {{
        background:#ffffff !important;
        color:#0A0A0A !important;
        border-color:#d7dce3 !important;
        border-radius:10px !important;
        font-weight:850 !important;
    }}
    div[data-testid="stDateInput"] svg {{ color:#0A0A0A !important; fill:#0A0A0A !important; }}


    section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #050606 0%, #0b1015 100%) !important; border-right: 1px solid #161b22; }}
    section[data-testid="stSidebar"] > div:first-child {{ padding-top: 1.05rem !important; }}
    section[data-testid="stSidebar"] * {{ color: white; }}
    section[data-testid="stSidebar"] img {{ border-radius: 14px !important; box-shadow: 0 10px 24px rgba(0,0,0,.26); }}
    .pas-sidebar-title {{ color:#fff; font-size:18px; font-weight:950; line-height:1.15; text-align:center; margin: 20px 0 8px; }}
    .pas-yellow-line {{ width:72px; height:4px; background:{PAS_YELLOW}; border-radius:99px; margin: 0 auto 22px; }}
    .pas-sidebar-copy {{ color:#fff !important; font-size:14px; line-height:1.52; font-weight:650; margin-bottom:24px; }}
    .pas-sidebar-rule {{ border-top:1px solid rgba(255,255,255,.22); margin:22px 0; }}
    .pas-sidebar-heading {{ color:{PAS_YELLOW}; font-size:19px; font-weight:950; margin: 0 0 16px; }}
    .pas-nav-row {{ display:grid; grid-template-columns: 26px 1fr; gap:10px; align-items:start; margin: 15px 0; color:#fff; font-weight:750; line-height:1.25; font-size:14px; }}
    .pas-nav-icon svg {{ width:21px; height:21px; stroke:{PAS_YELLOW}; stroke-width:2.4; fill:none; stroke-linecap:round; stroke-linejoin:round; }}
    .pas-sidebar-footer {{ color:#fff; font-size:12px; font-weight:800; margin-top:28px; }}

    .pas-hero {{ display:flex; align-items:center; gap:16px; background: linear-gradient(100deg, #08090b 0%, #151718 70%, #c9aa00 130%) !important; border-radius: 16px !important; padding: 12px 22px !important; margin: 24px 0 18px 0 !important; box-shadow: 0 9px 25px rgba(0,0,0,.13) !important; min-height:60px; }}
    .pas-hero-logo {{ width:37px; height:37px; border-radius:7px; background:{PAS_YELLOW}; color:#000; display:inline-flex; align-items:center; justify-content:center; font-weight:950; font-size:14px; letter-spacing:-1px; }}
    .pas-hero-text {{ color:#fff; font-size:18px; font-weight:950; letter-spacing:-.02em; }}
    .pas-hero-dot {{ color:#fff; opacity:.8; margin: 0 7px; }}
    .pas-hero-version {{ color:{PAS_YELLOW}; font-weight:950; }}

    .pas-upload-card {{ background:#fff; border:1px solid #e5e7eb; border-radius:18px; box-shadow:0 5px 18px rgba(15,23,42,.08); padding:28px 34px 30px; margin-bottom:24px; }}
    .pas-upload-head {{ display:flex; align-items:center; gap:18px; margin-bottom:22px; }}
    .pas-upload-icon {{ width:56px; height:56px; border-radius:16px; background:#FFD400; color:#0A0A0A; display:flex; align-items:center; justify-content:center; font-size:28px; font-weight:950; box-shadow:0 6px 18px rgba(255,212,0,.22); }}
    .pas-upload-title {{ color:#0A0A0A; font-size:26px; font-weight:950; line-height:1.05; margin:0; }}
    .pas-upload-subtitle {{ color:#64748b; font-size:16px; font-weight:750; margin-top:4px; }}
    .pas-upload-status {{ display:flex; align-items:center; gap:18px; min-height:72px; background:#ffffff; border:1px solid #dfe3e8; border-radius:16px; padding:16px 22px; color:#0A0A0A; font-size:18px; font-weight:950; margin:9px 0; box-shadow:0 2px 10px rgba(15,23,42,.03); }}
    .pas-upload-status.missing {{ background:#f7f8fa; border:1px solid #dfe3e8; color:#475569; }}
    .pas-upload-tick {{ width:38px; height:38px; border-radius:50%; background:#0ca13a; color:white; display:inline-flex; align-items:center; justify-content:center; font-size:24px; font-weight:950; flex:none; }}

    .pas-period-title {{ text-align:center; color:#0A0A0A; font-size:28px; font-weight:950; line-height:1.1; margin:2px 0 24px; }}
    .pas-period-card-note {{ text-align:center; color:#64748b; font-weight:750; font-size:14px; margin:-14px 0 22px; }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background:#ffffff !important;
        border:1px solid #e5e7eb !important;
        border-radius:22px !important;
        box-shadow:0 8px 28px rgba(15,23,42,.08) !important;
        padding:30px 36px 34px !important;
        margin: 2px 0 24px !important;
    }}
    div[data-testid="stDateInput"] {{
        background:#f7f8fa !important;
        border:1px solid #dfe3e8 !important;
        border-radius:18px !important;
        padding:16px 18px 18px !important;
        box-shadow:0 2px 10px rgba(15,23,42,.035) !important;
        max-width:100% !important;
    }}
    div[data-testid="stDateInput"] > label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stDateInput"] label * {{
        color:#0A0A0A !important;
        font-size:16px !important;
        font-weight:950 !important;
        margin-bottom:8px !important;
    }}
    div[data-testid="stDateInput"] [data-testid="InputInstructions"],
    div[data-testid="stDateInput"] [data-testid="stTooltipHoverTarget"] {{ display:none !important; }}
    div[data-testid="stDateInput"] > div {{ max-width:100% !important; }}
    div[data-testid="stDateInput"] input {{
        min-height:54px !important;
        height:54px !important;
        padding:12px 16px !important;
        font-size:20px !important;
        font-weight:900 !important;
        border-radius:14px !important;
        border:1px solid #d1d7de !important;
        background:#ffffff !important;
        box-shadow:none !important;
    }}
    div[data-testid="stDateInput"] button {{ min-height:54px !important; border-radius:14px !important; background:#ffffff !important; border-color:#d1d7de !important; }}
    .pas-period-button-row {{ margin-top:22px; }}
    .pas-period-button-row div.stButton > button {{ min-height:62px !important; font-size:18px !important; border-radius:15px !important; box-shadow:0 8px 18px rgba(255,212,0,.22) !important; }}
    div[data-testid="stFileUploader"] {{ margin:0 !important; }}
    div[data-testid="stFileUploader"] label {{ display:none !important; }}
    div[data-testid="stFileUploader"] section {{ background: transparent !important; border: 0 !important; min-height: 0 !important; padding: 0 !important; }}
    div[data-testid="stFileUploaderDropzone"] {{ background: transparent !important; border: 0 !important; padding: 0 !important; min-height: 0 !important; }}
    div[data-testid="stFileUploaderDropzoneInstructions"] {{ display: none !important; }}
    /* Hide Streamlit's ugly uploaded-file chips globally. Streamlit renders these
       outside/inside the uploader depending on version, so both global and
       descendant selectors are needed. */
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploaderFileSize"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"],
    div[data-testid="stFileUploader"] ul,
    div[data-testid="stFileUploader"] div[role="list"],
    div[data-testid="stFileUploader"] div[role="listitem"],
    div[data-testid="stFileUploader"] div:has(button[title*="Remove"]),
    div[data-testid="stFileUploader"] div:has(button[aria-label*="Remove"]),
    div[data-testid="stFileUploader"] div:has(svg[data-testid="DeleteIcon"]) {{
        display:none !important; visibility:hidden !important; height:0 !important;
        max-height:0 !important; min-height:0 !important; width:0 !important;
        max-width:0 !important; margin:0 !important; padding:0 !important;
        overflow:hidden !important; opacity:0 !important; pointer-events:none !important;
    }}
    /* When files are already uploaded, hide the extra +/browse button as well. */
    div[data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"]) button {{
        display:none !important; visibility:hidden !important; height:0 !important;
        min-height:0 !important; margin:0 !important; padding:0 !important;
        overflow:hidden !important; opacity:0 !important; pointer-events:none !important;
    }}
    div[data-testid="stFileUploader"] button {{ background:#FFD400 !important; color:#0A0A0A !important; border:1px solid #0A0A0A !important; border-radius:12px !important; font-weight:950 !important; min-height:48px !important; box-shadow:0 4px 14px rgba(255,212,0,.18) !important; }}
    div[data-testid="stFileUploader"] button * {{ color:#0A0A0A !important; fill:#0A0A0A !important; stroke:#0A0A0A !important; }}
    div[data-testid="stFileUploader"] small {{ color:#4b5563 !important; }}

    .stButton > button, .stDownloadButton > button {{ background: {PAS_YELLOW} !important; color: {PAS_BLACK} !important; border: 1px solid {PAS_BLACK} !important; border-radius: 12px !important; font-weight: 900 !important; min-height:52px !important; box-shadow:0 6px 18px rgba(255,212,0,.25) !important; }}
    .stDownloadButton > button {{ min-height:62px !important; font-size:20px !important; }}

    .kpi-card {{ background:#fff !important; border-radius:18px !important; border:1px solid #e4e7eb !important; box-shadow:0 5px 20px rgba(15,23,42,.08) !important; height:116px !important; min-height:116px !important; padding:18px 18px !important; display:flex; align-items:center; gap:14px; overflow:hidden; }}
    .kpi-icon {{ width:56px; height:56px; border-radius:50%; background:#fff5bd; display:flex; align-items:center; justify-content:center; flex:none; }}
    .kpi-icon svg {{ width:30px; height:30px; stroke:#0A0A0A; stroke-width:2.5; fill:none; stroke-linecap:round; stroke-linejoin:round; }}
    .kpi-label {{ color:#111 !important; font-size:15px !important; font-weight:950 !important; margin:0 0 3px !important; }}
    .kpi-value {{ color:#e9b900 !important; font-size:32px !important; line-height:1.02 !important; font-weight:950 !important; text-shadow:none !important; white-space:nowrap; }}
    .kpi-sub {{ display:none !important; }}

    .pas-results-title {{ color:#0A0A0A !important; font-size:28px !important; font-weight:950 !important; margin: 22px 0 8px !important; }}
    .pas-unmatched-pill {{ display:inline-flex; background:{PAS_YELLOW} !important; color:#0A0A0A !important; border:0 !important; border-radius:14px 14px 0 0 !important; padding:13px 20px !important; font-size:18px; font-weight:950; box-shadow:0 4px 14px rgba(0,0,0,.09); margin-top:12px; }}
    .pas-table-wrap {{ background:#fff !important; border:1px solid #e0e4e9 !important; border-radius:0 16px 16px 16px !important; max-height:430px !important; overflow:auto !important; box-shadow:0 7px 25px rgba(15,23,42,.10) !important; margin-bottom:18px; }}
    table.pas-table {{ width:100%; border-collapse:collapse; font-size:14px !important; color:#0A0A0A !important; }}
    table.pas-table thead th {{ background:{PAS_YELLOW} !important; color:#0A0A0A !important; border:1px solid #e2ba00 !important; padding:12px 14px !important; font-weight:950 !important; position:sticky; top:0; z-index:5; text-align:left; white-space:nowrap; }}
    table.pas-table tbody td {{ background:#fff !important; color:#0A0A0A !important; border:1px solid #e1e5eb !important; padding:10px 14px !important; }}
    table.pas-table tbody tr:nth-child(even) td {{ background:#fbfcfd !important; }}

    .pas-file-card {{ display:flex; align-items:center; gap:14px; background:#f4f6f8; border:1px solid #dfe4ea; border-radius:12px; padding:11px 14px; min-height:54px; margin: 4px 0 12px; }}
    .pas-file-icon {{ width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:950; font-size:11px; box-shadow:0 2px 8px rgba(0,0,0,.12); flex:none; }}
    .pas-file-icon.excel {{ background:#118a3b; }}
    .pas-file-main {{ flex:1; min-width:0; }}
    .pas-file-name {{ color:#0A0A0A; font-weight:950; font-size:15px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .pas-file-size {{ color:#4b5563; font-weight:650; font-size:13px; margin-top:2px; }}
    .pas-file-check {{ width:24px; height:24px; border-radius:50%; background:#108a37; color:white; display:flex; align-items:center; justify-content:center; font-size:15px; font-weight:950; flex:none; }}

    .pas-bottom-chase-wrap {{ position: fixed; left: calc(18rem + 22px); right: 42px; bottom: 12px; height: 58px; pointer-events: none; z-index: 1; overflow: hidden; }}
    .pas-bottom-ground {{ position: absolute; left: 0; right: 0; bottom: 6px; border-bottom: 1px solid rgba(0,0,0,0.11); }}
    .pas-chase-pack {{ position: absolute; bottom: 8px; left: -150px; width: 150px; height: 48px; animation: pas-chase-run 13s linear 1 forwards; }}
    @keyframes pas-chase-run {{ 0% {{ transform: translateX(-120px); opacity: 0; }} 8% {{ opacity: 1; }} 88% {{ opacity: 1; }} 100% {{ transform: translateX(calc(100vw - 90px)); opacity: 0; }} }}
    .pas-truck-mini {{ position: absolute; left: 0; bottom: 5px; width: 54px; height: 30px; filter: drop-shadow(0 1px 1px rgba(0,0,0,.22)); }}
    .pas-truck-bed {{ position:absolute; left:0; top:5px; width:34px; height:19px; background:#FFD400; border:3px solid #0A0A0A; border-radius:4px 2px 3px 5px; transform:skewX(-10deg); }}
    .pas-truck-logo {{ position:absolute; left:7px; top:9px; font-size:9px; font-weight:950; color:#0A0A0A; line-height:1; z-index:3; }}
    .pas-truck-cab {{ position:absolute; left:30px; top:7px; width:19px; height:18px; background:#FFD400; border:3px solid #0A0A0A; border-radius:3px 5px 3px 2px; z-index:2; }}
    .pas-truck-window {{ position:absolute; left:34px; top:10px; width:7px; height:7px; background:#a8d8e8; border:2px solid #0A0A0A; border-radius:2px; z-index:4; }}
    .pas-truck-nose {{ position:absolute; left:47px; top:17px; width:8px; height:8px; background:#FFD400; border:3px solid #0A0A0A; border-left:none; border-radius:0 3px 3px 0; }}
    .pas-wheel {{ position:absolute; bottom:0; width:9px; height:9px; background:#0A0A0A; border:2px solid #222; border-radius:50%; animation: pas-wheel-spin .32s linear infinite; z-index:5; }}
    .pas-wheel::after {{ content:""; position:absolute; inset:2px; background:#FFD400; border-radius:50%; }}
    .pas-wheel.back {{ left:13px; }} .pas-wheel.front {{ left:41px; }} @keyframes pas-wheel-spin {{ to {{ transform: rotate(360deg); }} }}
    .pas-stickman {{ position:absolute; left:92px; bottom:5px; width:28px; height:34px; animation:pas-runner-bob .35s ease-in-out infinite alternate; }}
    @keyframes pas-runner-bob {{ from {{ transform:translateY(1px); }} to {{ transform:translateY(-2px); }} }}
    .pas-stick-head {{ position:absolute; top:0; left:11px; width:8px; height:8px; border:2px solid #111; border-radius:50%; background:white; }}
    .pas-stick-body {{ position:absolute; left:15px; top:9px; width:2px; height:13px; background:#111; transform:rotate(12deg); transform-origin:top; }}
    .pas-stick-arm-a,.pas-stick-arm-b,.pas-stick-leg-a,.pas-stick-leg-b {{ position:absolute; width:2px; height:12px; background:#111; transform-origin:top; border-radius:2px; }}
    .pas-stick-arm-a {{ left:15px; top:11px; transform:rotate(58deg); animation:pas-arm-a .35s linear infinite alternate; }}
    .pas-stick-arm-b {{ left:15px; top:11px; transform:rotate(-50deg); animation:pas-arm-b .35s linear infinite alternate; }}
    .pas-stick-leg-a {{ left:16px; top:21px; height:14px; transform:rotate(48deg); animation:pas-leg-a .35s linear infinite alternate; }}
    .pas-stick-leg-b {{ left:16px; top:21px; height:14px; transform:rotate(-42deg); animation:pas-leg-b .35s linear infinite alternate; }}
    @keyframes pas-arm-a {{ to {{ transform:rotate(-45deg); }} }} @keyframes pas-arm-b {{ to {{ transform:rotate(55deg); }} }} @keyframes pas-leg-a {{ to {{ transform:rotate(-45deg); }} }} @keyframes pas-leg-b {{ to {{ transform:rotate(48deg); }} }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image("pas_logo.png", use_container_width=True)
    st.markdown(
        """
        <div class="pas-sidebar-title">PAS Live Cost<br>Dashboard</div>
        <div class="pas-yellow-line"></div>
        <div class="pas-sidebar-copy">Upload the weekly cost spreadsheets, then export a clean live cost report by site.</div>
        <div class="pas-sidebar-rule"></div>
        <div class="pas-sidebar-heading">Instructions</div>
        <div class="pas-nav-row"><span class="pas-nav-icon"><svg viewBox="0 0 24 24"><path d="M16 16l-4-4-4 4"/><path d="M12 12v9"/><path d="M20 16.6A5 5 0 0 0 18 7h-1.3A8 8 0 1 0 4 15.3"/></svg></span><span>Upload all four<br>spreadsheets</span></div>
        <div class="pas-nav-row"><span class="pas-nav-icon"><svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M9 13h6"/><path d="M9 17h6"/></svg></span><span>Set reporting<br>period</span></div>
        <div class="pas-nav-row"><span class="pas-nav-icon"><svg viewBox="0 0 24 24"><path d="M5 3l14 9-14 9V3z"/></svg></span><span>Build Live Cost Report</span></div>
        <div class="pas-nav-row"><span class="pas-nav-icon"><svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg></span><span>Download Excel<br>Spreadsheet</span></div>
        <div class="pas-nav-row"><span class="pas-nav-icon"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.3-4.3"/></svg></span><span>Smoke Crack</span></div>
        <div class="pas-sidebar-rule"></div>
        <div class="pas-sidebar-footer">PAS NW Ltd • v1.13 Prototype Build</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="pas-hero">
      <div class="pas-hero-logo">PAS</div>
      <div class="pas-hero-text">PAS Live Cost Dashboard<span class="pas-hero-dot">•</span><span class="pas-hero-version">v1.13 Prototype Build</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_bottom_chase():
    st.markdown(
        """
        <div class="pas-bottom-chase-wrap" aria-hidden="true">
            <div class="pas-bottom-ground"></div>
            <div class="pas-chase-pack">
                <div class="pas-truck-mini">
                    <div class="pas-truck-bed"></div><div class="pas-truck-logo">PAS</div><div class="pas-truck-cab"></div>
                    <div class="pas-truck-window"></div><div class="pas-truck-nose"></div><div class="pas-wheel back"></div><div class="pas-wheel front"></div>
                </div>
                <div class="pas-stickman"><div class="pas-stick-head"></div><div class="pas-stick-body"></div><div class="pas-stick-arm-a"></div><div class="pas-stick-arm-b"></div><div class="pas-stick-leg-a"></div><div class="pas-stick-leg-b"></div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _file_size_label(uploaded_file):
    try:
        pos = uploaded_file.tell()
        uploaded_file.seek(0, 2)
        size = uploaded_file.tell()
        uploaded_file.seek(pos)
    except Exception:
        size = getattr(uploaded_file, "size", 0) or 0
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"


def render_selected_file_card(uploaded_file):
    """Native uploader only. Avoid extra uploaded-file cards/black boxes."""
    return


def _stored_upload_to_file(state_key):
    item = st.session_state.get(state_key)
    if not item:
        return None
    bio = BytesIO(item["bytes"])
    bio.name = item.get("name", "uploaded.xlsx")
    return bio


def upload_slot(title, state_key, widget_key):
    """Show a clean PAS upload slot.

    Once a file is uploaded, store it in session state and replace Streamlit's
    native uploaded-file chip with a simple PAS green tick status.
    """
    stored = st.session_state.get(state_key)
    st.markdown(f'<div class="pas-upload-card"><div class="pas-upload-title">{escape(title)}</div>', unsafe_allow_html=True)
    if stored:
        st.markdown(
            f'<div class="pas-upload-status"><span class="pas-upload-tick">✓</span><span>{escape(title)} uploaded</span></div>',
            unsafe_allow_html=True,
        )
        if st.button(f"Replace {title}", key=f"replace_{widget_key}", use_container_width=True):
            st.session_state.pop(state_key, None)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return _stored_upload_to_file(state_key)

    uploaded = st.file_uploader(title, type=["xlsx", "xlsm", "xls"], label_visibility="collapsed", key=widget_key)
    if uploaded is not None:
        st.session_state[state_key] = {"name": uploaded.name, "bytes": uploaded.getvalue(), "size": getattr(uploaded, "size", 0)}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    return None




def file_to_bytesio(info):
    if not info:
        return None
    bio = BytesIO(info["bytes"])
    bio.name = info.get("name", "uploaded.xlsx")
    return bio


def detect_uploaded_files(uploaded_files):
    """Detect the four required workbooks from a single multi-file uploader."""
    detected = {"materials": None, "vehicles": None, "labour": None, "forecast": None}
    for uploaded in uploaded_files or []:
        name = uploaded.name.lower()
        data = uploaded.getvalue()
        sheet_names = []
        try:
            sheet_names = [str(x).lower() for x in pd.ExcelFile(BytesIO(data)).sheet_names]
        except Exception:
            sheet_names = []
        sheet_blob = " ".join(sheet_names)
        info = {"name": uploaded.name, "bytes": data}

        if ("forecast" in name) or ("forecast" in sheet_names):
            detected["forecast"] = info
        elif ("labour" in name) or ("labour" in sheet_blob):
            detected["labour"] = info
        elif ("vehicle" in name) or ("vehicles" in sheet_blob) or ("off hire" in sheet_blob and "sold" in sheet_blob):
            detected["vehicles"] = info
        elif ("material" in name and "plant" in name) or ("plant" in sheet_names and ("materials" in sheet_blob or "agg" in sheet_blob or "subby" in sheet_blob)):
            detected["materials"] = info
        elif detected["materials"] is None and ("plant" in sheet_blob or "materials" in sheet_blob):
            detected["materials"] = info

    return detected


def render_detection_status(label, info):
    if info:
        st.markdown(
            f'<div class="pas-upload-status"><span class="pas-upload-tick">✓</span><span>{escape(label)} detected</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="pas-upload-status missing"><span>○</span><span>{escape(label)} not detected</span></div>',
            unsafe_allow_html=True,
        )

def render_kpi(label, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon"><svg viewBox="0 0 24 24"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-7"/></svg></div>
            <div><div class="kpi-label">{escape(label)}</div><div class="kpi-value">{escape(str(value))}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_table(df, max_rows=None):
    if df is None or df.empty:
        st.info("No records to display.")
        return
    shown = df.head(max_rows).copy() if max_rows else df.copy()
    html = shown.to_html(index=False, escape=False, classes="pas-table")
    st.markdown(f'<div class="pas-table-wrap">{html}</div>', unsafe_allow_html=True)

COST_CATEGORIES = [
    "Labour",
    "Plant",
    "Materials",
    "Muck Away",
    "Subbies",
    "Vehicles",
    "Fuel Card",
    "Site Fuel",
]

FORECAST_RENAME = {
    "job": "Job",
    "job no": "Job",
    "job no.": "Job",
    "material": "Materials",
    "materials": "Materials",
    "vans": "Vehicles",
    "van": "Vehicles",
    "vehicles": "Vehicles",
    "subby": "Subbies",
    "subbies": "Subbies",
    "muck away": "Muck Away",
    "site fuel": "Site Fuel",
    "fuel card": "Fuel Card",
    "overhead": "Overhead",
    "profit": "Profit",
    "labour": "Labour",
    "plant": "Plant",
}

# England & Wales bank holidays relevant to the current programme.
# Add future years here if needed.
UK_BANK_HOLIDAYS = {
    date(2025, 1, 1), date(2025, 4, 18), date(2025, 4, 21), date(2025, 5, 5),
    date(2025, 5, 26), date(2025, 8, 25), date(2025, 12, 25), date(2025, 12, 26),
    date(2026, 1, 1), date(2026, 4, 3), date(2026, 4, 6), date(2026, 5, 4),
    date(2026, 5, 25), date(2026, 8, 31), date(2026, 12, 25), date(2026, 12, 28),
    date(2027, 1, 1), date(2027, 3, 26), date(2027, 3, 29), date(2027, 5, 3),
    date(2027, 5, 31), date(2027, 8, 30), date(2027, 12, 27), date(2027, 12, 28),
}


def clean_col(col):
    if col is None:
        return ""
    return re.sub(r"\s+", " ", str(col).strip())


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).strip().lower()).strip()


def money(x):
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float, np.number)):
        return float(x)
    text = str(x).strip()
    if not text:
        return 0.0
    text = text.replace("£", "").replace(",", "").replace(" ", "")
    text = text.replace("−", "-")
    # Handle values like £12102,12 where comma may have been used as decimal.
    if re.match(r"^-?\d+,\d{1,2}$", str(x).replace("£", "").replace(" ", "")):
        text = str(x).replace("£", "").replace(" ", "").replace(",", ".")
    try:
        return float(text)
    except Exception:
        return 0.0


def to_date(value):
    if pd.isna(value) or value == "":
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        return value.normalize()
    if isinstance(value, datetime):
        return pd.Timestamp(value.date())
    if isinstance(value, date):
        return pd.Timestamp(value)
    return pd.to_datetime(value, errors="coerce", dayfirst=True)


def month_start(value):
    d = to_date(value)
    if pd.isna(d):
        return pd.NaT
    return pd.Timestamp(date(d.year, d.month, 1))


def month_label(value):
    d = to_date(value)
    if pd.isna(d):
        return "Unknown"
    return d.strftime("%b %Y")


def end_of_month(d):
    return date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])


def find_col(df, candidates, required=False):
    cols = {norm(c): c for c in df.columns}
    for cand in candidates:
        nc = norm(cand)
        if nc in cols:
            return cols[nc]
    # fuzzy contains fallback
    for cand in candidates:
        nc = norm(cand)
        for key, original in cols.items():
            if nc and (nc in key or key in nc):
                return original
    if required:
        raise KeyError(f"Missing required column. Tried: {candidates}")
    return None


def load_sheet(upload, sheet_name):
    try:
        df = pd.read_excel(upload, sheet_name=sheet_name)
        df.columns = [clean_col(c) for c in df.columns]
        df = df.dropna(how="all")
        return df
    except Exception:
        return pd.DataFrame()


def add_issue(issues, source, row_ref, job, issue, detail=""):
    issues.append({
        "Source": source,
        "Row": row_ref,
        "Job": "" if pd.isna(job) else str(job).strip(),
        "Issue": issue,
        "Detail": detail,
    })


def weekdays_between(start, end, exclude_bank_holidays=True):
    start = to_date(start)
    end = to_date(end)
    if pd.isna(start) or pd.isna(end) or end < start:
        return 0
    count = 0
    current = start.date()
    finish = end.date()
    while current <= finish:
        if current.weekday() < 5:
            if exclude_bank_holidays and current in UK_BANK_HOLIDAYS:
                pass
            else:
                count += 1
        current += timedelta(days=1)
    return count


def calendar_days_between(start, end):
    start = to_date(start)
    end = to_date(end)
    if pd.isna(start) or pd.isna(end) or end < start:
        return 0
    return (end.date() - start.date()).days + 1


def split_period_by_month(start, end):
    start = to_date(start)
    end = to_date(end)
    if pd.isna(start) or pd.isna(end) or end < start:
        return []
    periods = []
    cur = date(start.year, start.month, 1)
    last = date(end.year, end.month, 1)
    while cur <= last:
        m_start = cur
        m_end = end_of_month(cur)
        seg_start = max(start.date(), m_start)
        seg_end = min(end.date(), m_end)
        if seg_start <= seg_end:
            periods.append((pd.Timestamp(seg_start), pd.Timestamp(seg_end), pd.Timestamp(m_start)))
        cur = date(cur.year + (cur.month // 12), (cur.month % 12) + 1, 1)
    return periods


def normalise_job(value):
    if pd.isna(value):
        return ""
    return str(value).strip().upper().replace(" ", "")


def read_sites(material_file, labour_file=None):
    sites = {}
    for file_obj, sheet in [(material_file, "Sites"), (labour_file, "Sites")]:
        if file_obj is None:
            continue
        df = load_sheet(file_obj, sheet)
        if df.empty:
            continue
        job_col = find_col(df, ["Job No", "Job", "Job No."])
        site_col = find_col(df, ["Address", "Site", "Site Name"])
        if not job_col or not site_col:
            continue
        for _, row in df.iterrows():
            job = normalise_job(row.get(job_col))
            if job and job not in sites:
                sites[job] = str(row.get(site_col, "")).strip()
    return sites


def process_forecast(forecast_file, issues):
    df = load_sheet(forecast_file, "Forecast")
    if df.empty:
        add_issue(issues, "Forecast", "", "", "Forecast tab missing or empty")
        return pd.DataFrame(columns=["Job"] + COST_CATEGORIES + ["Overhead", "Profit"])

    renamed = {}
    for c in df.columns:
        key = norm(c)
        renamed[c] = FORECAST_RENAME.get(key, clean_col(c))
    df = df.rename(columns=renamed)

    if "Job" not in df.columns:
        add_issue(issues, "Forecast", "", "", "Missing Job column")
        return pd.DataFrame(columns=["Job"] + COST_CATEGORIES + ["Overhead", "Profit"])

    keep_cols = ["Job"] + COST_CATEGORIES + ["Overhead", "Profit"]
    for c in keep_cols:
        if c not in df.columns:
            df[c] = 0
            if c != "Job":
                add_issue(issues, "Forecast", "Header", "", f"Missing forecast column: {c}", "Filled as zero")

    out = df[keep_cols].copy()
    out["Job"] = out["Job"].apply(normalise_job)
    out = out[out["Job"] != ""]
    for c in keep_cols[1:]:
        out[c] = out[c].apply(money)
    return out.groupby("Job", as_index=False).sum(numeric_only=True)


def record(source, job, site, category, cost, cost_date, description="", supplier="", ref=""):
    return {
        "Source": source,
        "Job": normalise_job(job),
        "Site": "" if pd.isna(site) else str(site).strip(),
        "Category": category,
        "Cost": float(cost or 0),
        "Cost Date": to_date(cost_date),
        "Month": month_start(cost_date),
        "Month Label": month_label(cost_date),
        "Description": "" if pd.isna(description) else str(description).strip(),
        "Supplier": "" if pd.isna(supplier) else str(supplier).strip(),
        "Reference": "" if pd.isna(ref) else str(ref).strip(),
    }


def process_material_like(material_file, sheet_name, default_category, issues):
    df = load_sheet(material_file, sheet_name)
    rows = []
    if df.empty:
        return rows

    job_col = find_col(df, ["Job No.", "Job No", "Job"])
    site_col = find_col(df, ["Site Name", "Site", "Address"])
    desc_col = find_col(df, ["Description", "Item Description"])
    qty_col = find_col(df, ["Qty", "Ordered Qty", "Quantity"])
    cost_col = find_col(df, ["Cost", "Rate", "Unit Cost"])
    total_col = find_col(df, ["Total", "Total Cost", "Value", "Line Value"])
    supplier_col = find_col(df, ["Supplier", "Vendor"])
    deliv_col = find_col(df, ["Delivery Date", "Date Delivered", "Start Date"])
    ref_col = find_col(df, ["Sage Order No", "Order Number", "PO", "Sage Order No."])

    for idx, row in df.iterrows():
        excel_row = idx + 2
        job = row.get(job_col) if job_col else ""
        job_norm = normalise_job(job)
        desc = row.get(desc_col, "") if desc_col else ""
        d = row.get(deliv_col) if deliv_col else pd.NaT
        if not job_norm:
            add_issue(issues, sheet_name, excel_row, job, "Missing Job Number")
            continue
        if pd.isna(to_date(d)):
            add_issue(issues, sheet_name, excel_row, job, "Missing or invalid delivery/start date")
            continue

        if total_col and not pd.isna(row.get(total_col)):
            value = money(row.get(total_col))
        else:
            qty = money(row.get(qty_col)) if qty_col else 1
            unit_cost = money(row.get(cost_col)) if cost_col else 0
            value = qty * unit_cost

        desc_norm = norm(desc)
        if "muck away" in desc_norm:
            category = "Muck Away"
        elif sheet_name.lower() == "materials" and "diesel" in desc_norm:
            category = "Site Fuel"
        else:
            category = default_category

        if value == 0:
            add_issue(issues, sheet_name, excel_row, job, "Zero or missing cost", str(desc))

        rows.append(record(
            sheet_name, job, row.get(site_col, "") if site_col else "", category, value, d,
            description=desc,
            supplier=row.get(supplier_col, "") if supplier_col else "",
            ref=row.get(ref_col, "") if ref_col else "",
        ))
    return rows


def process_subbies(material_file, issues):
    df = load_sheet(material_file, "Subby")
    rows = []
    if df.empty:
        return rows
    job_col = find_col(df, ["Job No.", "Job No", "Job"])
    site_col = find_col(df, ["Site Name", "Site", "Address"])
    desc_col = find_col(df, ["Description", "Item Description"])
    qty_col = find_col(df, ["Qty", "Quantity"])
    cost_col = find_col(df, ["Cost", "Value", "Total", "Line Value"])
    supplier_col = find_col(df, ["Supplier", "Vendor"])
    start_col = find_col(df, ["Start Date", "Delivery Date", "Date"])
    ref_col = find_col(df, ["Sage Order No", "Order Number", "PO"])

    for idx, row in df.iterrows():
        excel_row = idx + 2
        job = row.get(job_col) if job_col else ""
        job_norm = normalise_job(job)
        d = row.get(start_col) if start_col else pd.NaT
        if not job_norm:
            add_issue(issues, "Subby", excel_row, job, "Missing Job Number")
            continue
        if pd.isna(to_date(d)):
            add_issue(issues, "Subby", excel_row, job, "Missing or invalid start date")
            continue
        qty = money(row.get(qty_col)) if qty_col else 1
        value = money(row.get(cost_col)) * (qty if qty_col else 1)
        rows.append(record(
            "Subby", job, row.get(site_col, "") if site_col else "", "Subbies", value, d,
            description=row.get(desc_col, "") if desc_col else "",
            supplier=row.get(supplier_col, "") if supplier_col else "",
            ref=row.get(ref_col, "") if ref_col else "",
        ))
    return rows


def process_plant(material_file, report_date, issues):
    df = load_sheet(material_file, "Plant")
    rows = []
    if df.empty:
        return rows
    job_col = find_col(df, ["Job No", "Job No.", "Job"])
    site_col = find_col(df, ["Site Name", "Site", "Address"])
    desc_col = find_col(df, ["Description", "Item Description"])
    supplier_col = find_col(df, ["Supplier", "Vendor"])
    weekly_col = find_col(df, ["Cost", "Weekly Rate", "Weekly Cost", "Rate"])
    on_col = find_col(df, ["On Hire / Delivery Date", "On Hire Date", "Delivery Date"])
    off_col = find_col(df, ["Off Hire Date", "Off-Hire Date", "Date Off Hired"])
    order_col = find_col(df, ["Order Number", "Sage Order No", "PO"])

    for idx, row in df.iterrows():
        excel_row = idx + 2
        job = row.get(job_col) if job_col else ""
        job_norm = normalise_job(job)
        if not job_norm:
            add_issue(issues, "Plant", excel_row, job, "Missing Job Number")
            continue
        on = to_date(row.get(on_col)) if on_col else pd.NaT
        off = to_date(row.get(off_col)) if off_col and not pd.isna(row.get(off_col)) else pd.Timestamp(report_date)
        if pd.isna(on):
            add_issue(issues, "Plant", excel_row, job, "Missing or invalid on-hire date")
            continue
        if off < on:
            add_issue(issues, "Plant", excel_row, job, "Off-hire date before on-hire date")
            continue
        weekly = money(row.get(weekly_col)) if weekly_col else 0
        if weekly == 0:
            add_issue(issues, "Plant", excel_row, job, "Missing weekly rate", str(row.get(desc_col, "")))
            continue
        daily = weekly / 5
        for seg_start, seg_end, m in split_period_by_month(on, off):
            charge_days = weekdays_between(seg_start, seg_end, exclude_bank_holidays=True)
            if charge_days > 0:
                rows.append(record(
                    "Plant", job, row.get(site_col, "") if site_col else "", "Plant", daily * charge_days, m,
                    description=row.get(desc_col, "") if desc_col else "",
                    supplier=row.get(supplier_col, "") if supplier_col else "",
                    ref=row.get(order_col, "") if order_col else "",
                ))
    return rows


def process_labour(labour_file, issues):
    df = load_sheet(labour_file, "Labour")
    rows = []
    if df.empty:
        add_issue(issues, "Labour", "", "", "Labour tab missing or empty")
        return rows
    job_col = find_col(df, ["Job No", "Job No.", "Job"])
    site_col = find_col(df, ["Site", "Site Name", "Address"])
    date_col = find_col(df, ["Week Ending", "Date"])
    cost_col = find_col(df, ["Total Cost", "Cost", "Value"])
    operatives_col = find_col(df, ["Operatives", "Men"])
    hours_col = find_col(df, ["Hours", "Total Hours"])

    for idx, row in df.iterrows():
        excel_row = idx + 2
        # skip summary/formula side columns rows without cost/job
        job = row.get(job_col) if job_col else ""
        job_norm = normalise_job(job)
        if not job_norm:
            continue
        d = row.get(date_col) if date_col else pd.NaT
        if pd.isna(to_date(d)):
            add_issue(issues, "Labour", excel_row, job, "Missing or invalid week ending date")
            continue
        value = money(row.get(cost_col)) if cost_col else 0
        if value == 0:
            add_issue(issues, "Labour", excel_row, job, "Zero or missing labour cost")
        desc = f"Operatives: {row.get(operatives_col, '')}; Hours: {row.get(hours_col, '')}"
        rows.append(record(
            "Labour", job, row.get(site_col, "") if site_col else "", "Labour", value, d,
            description=desc,
        ))
    return rows


def process_vehicle_sheet(vehicle_file, report_date, issues):
    if vehicle_file is None:
        return []

    xls = pd.ExcelFile(vehicle_file)
    selected_sheet = None
    for name in xls.sheet_names:
        if norm(name) in ["vehicles", "vehicle", "vehicle sheet", "vans", "hire"]:
            selected_sheet = name
            break
    if selected_sheet is None:
        selected_sheet = xls.sheet_names[0]

    df = pd.read_excel(vehicle_file, sheet_name=selected_sheet)
    df.columns = [clean_col(c) for c in df.columns]
    df = df.dropna(how="all")
    rows = []

    job_col = find_col(df, ["Job No", "Job No.", "Job", "Job Number"])
    site_col = find_col(df, ["Site", "Site Name", "Address"])
    desc_col = find_col(df, ["Description", "Vehicle", "Vehicle Reg", "Reg", "Registration"])
    weekly_col = find_col(df, ["Weekly Cost", "Weekly Rate", "Cost Per Week", "Hire Cost", "Vehicle Cost"])
    on_col = find_col(df, ["On Hire Date", "Start Date", "From", "Date From"])
    off_col = find_col(df, ["Off Hire Date", "End Date", "To", "Date To"])
    fuel_cost_col = find_col(df, ["Fuel Card", "Fuel Cost", "Fuel Spend", "Total Fuel", "Fuel"])
    fuel_date_col = find_col(df, ["Fuel Date", "Transaction Date", "Date", "Week Ending"])

    if not job_col:
        add_issue(issues, "Vehicles", "Header", "", "Missing Job Number column")
        return rows

    for idx, row in df.iterrows():
        excel_row = idx + 2
        job = row.get(job_col)
        job_norm = normalise_job(job)
        if not job_norm:
            add_issue(issues, "Vehicles", excel_row, job, "Missing Job Number")
            continue

        # Vehicle hire cost: 7-day week, bank holidays charged.
        if weekly_col and on_col:
            weekly = money(row.get(weekly_col))
            on = to_date(row.get(on_col))
            off = to_date(row.get(off_col)) if off_col and not pd.isna(row.get(off_col)) else pd.Timestamp(report_date)
            if weekly > 0 and not pd.isna(on) and not pd.isna(off) and off >= on:
                daily = weekly / 7
                for seg_start, seg_end, m in split_period_by_month(on, off):
                    days = calendar_days_between(seg_start, seg_end)
                    if days > 0:
                        rows.append(record(
                            "Vehicles", job, row.get(site_col, "") if site_col else "", "Vehicles", daily * days, m,
                            description=row.get(desc_col, "") if desc_col else "",
                        ))
            elif weekly > 0:
                add_issue(issues, "Vehicles", excel_row, job, "Missing/invalid vehicle hire dates")

        # Fuel card spend from vehicle sheet, allocated by transaction/week date if available.
        if fuel_cost_col:
            fuel_value = money(row.get(fuel_cost_col))
            if fuel_value != 0:
                fuel_date = row.get(fuel_date_col) if fuel_date_col else report_date
                if pd.isna(to_date(fuel_date)):
                    fuel_date = report_date
                    add_issue(issues, "Vehicles", excel_row, job, "Missing fuel date", "Used report date")
                rows.append(record(
                    "Vehicles", job, row.get(site_col, "") if site_col else "", "Fuel Card", fuel_value, fuel_date,
                    description=row.get(desc_col, "") if desc_col else "",
                ))

    return rows


def build_actuals(material_file, labour_file, vehicle_file, report_date, issues):
    rows = []
    rows += process_material_like(material_file, "Materials", "Materials", issues)
    rows += process_material_like(material_file, "Agg-Conc", "Materials", issues)
    rows += process_subbies(material_file, issues)
    rows += process_plant(material_file, report_date, issues)
    rows += process_labour(labour_file, issues)
    rows += process_vehicle_sheet(vehicle_file, report_date, issues)
    if not rows:
        return pd.DataFrame(columns=["Source", "Job", "Site", "Category", "Cost", "Cost Date", "Month", "Month Label", "Description", "Supplier", "Reference"])
    out = pd.DataFrame(rows)
    out = out[out["Job"] != ""].copy()
    return out


def format_currency(v):
    try:
        return f"£{float(v):,.0f}"
    except Exception:
        return "£0"


def build_summary(actuals, forecast, sites):
    actual_pivot = actuals.pivot_table(index="Job", columns="Category", values="Cost", aggfunc="sum", fill_value=0).reset_index() if not actuals.empty else pd.DataFrame(columns=["Job"])
    forecast_pivot = forecast.copy()
    for c in COST_CATEGORIES:
        if c not in actual_pivot.columns:
            actual_pivot[c] = 0
        if c not in forecast_pivot.columns:
            forecast_pivot[c] = 0
    for c in ["Overhead", "Profit"]:
        if c not in forecast_pivot.columns:
            forecast_pivot[c] = 0

    jobs = sorted(set(actual_pivot.get("Job", pd.Series(dtype=str))).union(set(forecast_pivot.get("Job", pd.Series(dtype=str)))))
    base = pd.DataFrame({"Job": jobs})
    base["Site"] = base["Job"].map(sites).fillna("")

    a = actual_pivot[["Job"] + COST_CATEGORIES].rename(columns={c: f"Actual {c}" for c in COST_CATEGORIES})
    f = forecast_pivot[["Job"] + COST_CATEGORIES + ["Overhead", "Profit"]].rename(columns={c: f"Forecast {c}" for c in COST_CATEGORIES})

    summary = base.merge(f, on="Job", how="left").merge(a, on="Job", how="left")
    for col in summary.columns:
        if col.startswith("Forecast ") or col.startswith("Actual ") or col in ["Overhead", "Profit"]:
            summary[col] = summary[col].fillna(0)

    summary["Overall Forecast"] = summary[[f"Forecast {c}" for c in COST_CATEGORIES]].sum(axis=1) + summary["Overhead"] + summary["Profit"]
    summary["Actual Cost"] = summary[[f"Actual {c}" for c in COST_CATEGORIES]].sum(axis=1)
    summary["Actual Profit"] = summary["Overall Forecast"] - summary["Actual Cost"] - summary["Overhead"]
    summary["Live Variance"] = summary["Overall Forecast"] - summary["Actual Cost"]
    # Safe percentage calculations: avoid division by zero when a job has actual costs
    # but no forecast loaded/entered yet.
    def safe_pct(numerator, denominator):
        try:
            denominator = float(denominator)
            if denominator == 0:
                return 0.0
            return float(numerator) / denominator
        except Exception:
            return 0.0

    summary["Profit %"] = summary.apply(lambda r: safe_pct(r["Profit"], r["Overall Forecast"]), axis=1)
    summary["Actual Profit %"] = summary.apply(lambda r: safe_pct(r["Actual Profit"], r["Overall Forecast"]), axis=1)

    display_cols = ["Job", "Site", "Overall Forecast", "Actual Cost", "Live Variance", "Profit", "Profit %", "Actual Profit", "Actual Profit %"]
    display_cols += [f"Forecast {c}" for c in COST_CATEGORIES]
    display_cols += [f"Actual {c}" for c in COST_CATEGORIES]
    display_cols += ["Overhead"]
    return summary[display_cols].sort_values("Job")


def build_monthly(actuals):
    if actuals.empty:
        return pd.DataFrame(columns=["Job", "Month", "Month Label", "Category", "Cost"])
    monthly = actuals.groupby(["Job", "Month", "Month Label", "Category"], dropna=False, as_index=False)["Cost"].sum()
    monthly = monthly.sort_values(["Month", "Job", "Category"])
    return monthly


def safe_excel_sheet_name(value, used_names=None):
    """Return a valid, unique Excel worksheet name.

    XlsxWriter is very strict: sheet names cannot contain []:*?/\\,
    cannot start/end with apostrophes, and must be 31 characters or fewer.
    This version is deliberately aggressive and keeps only safe characters so
    job references like P123/H456 or site names with punctuation never crash
    the export.
    """
    if used_names is None:
        used_names = set()

    raw = "" if value is None else str(value)
    raw = raw.replace("\u00a0", " ").strip()

    # Remove Excel-forbidden characters and any other punctuation that may be
    # rejected by cloud Excel writers. Keep letters, numbers, spaces, hyphens
    # and underscores only.
    name = re.sub(r"[\x00-\x1F\x7F]", "", raw)
    name = re.sub(r"[^A-Za-z0-9 _-]+", "-", name)
    name = re.sub(r"[- ]+", " ", name).strip(" .'-_")

    if not name:
        name = "Site"

    base = name[:31].strip(" .'-_") or "Site"
    candidate = base
    counter = 1
    while candidate.lower() in used_names:
        suffix = f"_{counter}"
        candidate = (base[:31 - len(suffix)] + suffix).strip(" .'-_") or f"Site_{counter}"
        counter += 1

    used_names.add(candidate.lower())
    return candidate


def excel_export(summary, monthly, raw, issues):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="dd/mm/yyyy", date_format="dd/mm/yyyy") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        raw.to_excel(writer, sheet_name="Raw Data", index=False)

        workbook = writer.book
        header_fmt = workbook.add_format({"bold": True, "bg_color": "#FFD400", "font_color": "#111111", "border": 1})
        money_fmt = workbook.add_format({"num_format": "£#,##0", "border": 1})
        pct_fmt = workbook.add_format({"num_format": "0.0%", "border": 1})
        body_fmt = workbook.add_format({"border": 1})

        for sheet_name, df in [("Summary", summary), ("Raw Data", raw)]:
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            ws.set_row(0, 24, header_fmt)
            for i, col in enumerate(df.columns):
                width = min(max(len(str(col)) + 3, 12), 34)
                if "Description" in str(col):
                    width = 36
                if "Cost" in str(col) or "Forecast" in str(col) or "Profit" in str(col) or "Variance" in str(col) or col in ["Overhead"]:
                    ws.set_column(i, i, width, money_fmt)
                elif "%" in str(col):
                    ws.set_column(i, i, width, pct_fmt)
                else:
                    ws.set_column(i, i, width, body_fmt)

        # One tab per site/job
        used_sheet_names = {"summary", "raw data"}
        for _, srow in summary.iterrows():
            job = srow["Job"]
            tab = safe_excel_sheet_name(job, used_sheet_names)
            site_detail = []
            for cat in COST_CATEGORIES:
                forecast_col = f"Forecast {cat}"
                actual_col = f"Actual {cat}"
                # Forecast columns are not in displayed summary, recover from raw merge not available here -> leave blank if missing.
                forecast_val = srow.get(forecast_col, np.nan)
                actual_val = srow.get(actual_col, 0)
                site_detail.append({
                    "Category": cat,
                    "Forecast": forecast_val if not pd.isna(forecast_val) else "",
                    "Actual": actual_val,
                    "Variance": (forecast_val - actual_val) if not pd.isna(forecast_val) and forecast_val != "" else "",
                })
            site_df = pd.DataFrame(site_detail)
            site_df.to_excel(writer, sheet_name=tab, index=False, startrow=2)
            ws = writer.sheets[tab]
            ws.write(0, 0, f"{job} - {srow.get('Site', '')}", workbook.add_format({"bold": True, "font_size": 14}))
            ws.set_row(2, 24, header_fmt)
            ws.set_column(0, 0, 20, body_fmt)
            ws.set_column(1, 3, 15, money_fmt)

    output.seek(0)
    return output



# ============================================================
# PAS Live Cost UI
# ============================================================

st.markdown("""
<div class="pas-upload-card">
  <div class="pas-upload-head">
    <div class="pas-upload-icon">☁</div>
    <div>
      <div class="pas-upload-title">Upload Live Cost Spreadsheets</div>
      <div class="pas-upload-subtitle">Upload your latest spreadsheets to build the live cost report</div>
    </div>
  </div>
""", unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Upload Live Cost Spreadsheets",
    type=["xlsx", "xlsm", "xls"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload the Materials & Plant, Vehicles, Labour and Forecast spreadsheets together.",
    key="single_live_cost_uploader",
)
detected_files = detect_uploaded_files(uploaded_files)

s1, s2 = st.columns(2)
with s1:
    render_detection_status("Materials & Plant Spreadsheet", detected_files.get("materials"))
    render_detection_status("Labour Spreadsheet", detected_files.get("labour"))
with s2:
    render_detection_status("Vehicles Spreadsheet", detected_files.get("vehicles"))
    render_detection_status("Forecast Spreadsheet", detected_files.get("forecast"))
st.markdown('</div>', unsafe_allow_html=True)

material_file = file_to_bytesio(detected_files.get("materials"))
vehicle_file = file_to_bytesio(detected_files.get("vehicles"))
labour_file = file_to_bytesio(detected_files.get("labour"))
forecast_file = file_to_bytesio(detected_files.get("forecast"))

with st.container(border=True):
    st.markdown('<div class="pas-period-title">Reporting Period</div>', unsafe_allow_html=True)
    outer_l, centre, outer_r = st.columns([0.45, 3.1, 0.45])
    with centre:
        date_col_1, date_col_2 = st.columns(2, gap="large")
        with date_col_1:
            report_from = st.date_input(
                "From",
                value=date(date.today().year, 1, 1),
                format="DD/MM/YYYY",
                label_visibility="visible",
                key="report_from_date",
            )
        with date_col_2:
            report_to = st.date_input(
                "To",
                value=date.today(),
                format="DD/MM/YYYY",
                label_visibility="visible",
                key="report_to_date",
            )
        st.markdown('<div class="pas-period-button-row">', unsafe_allow_html=True)
        button_col_1, button_col_2 = st.columns(2, gap="large")
        with button_col_1:
            run_all = st.button("▷  Build Report - All Sites", use_container_width=True)
        with button_col_2:
            run_forecast_only = st.button("▷  Build Report - Forecast Sites Only", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

run = run_all or run_forecast_only
run_mode = "forecast_only" if run_forecast_only else "all_sites"

if report_from > report_to:
    st.error("The From date must be before or the same as the To date.")
    render_bottom_chase()
    st.stop()

if "live_cost_results" not in st.session_state:
    st.session_state["live_cost_results"] = None

if run:
    if not all([material_file, labour_file, forecast_file]):
        st.warning("Please upload the Materials & Plant, Labour and Forecast spreadsheets. Vehicles spreadsheet is optional for first testing.")
        render_bottom_chase()
        st.stop()
    try:
        issues = []
        with st.spinner("Reading site data..."):
            sites = read_sites(material_file, labour_file)
        with st.spinner("Reading forecast spreadsheet..."):
            forecast = process_forecast(forecast_file, issues)
        with st.spinner("Calculating actual costs..."):
            actuals = build_actuals(material_file, labour_file, vehicle_file, report_to, issues)
        if not actuals.empty:
            actuals["Cost Date"] = pd.to_datetime(actuals["Cost Date"], errors="coerce")
            from_ts = pd.Timestamp(report_from)
            to_ts = pd.Timestamp(report_to)
            actuals = actuals[(actuals["Cost Date"] >= from_ts) & (actuals["Cost Date"] <= to_ts)].copy()
            actuals["Site"] = actuals.apply(lambda r: r["Site"] if str(r["Site"]).strip() else sites.get(r["Job"], ""), axis=1)
        if run_mode == "forecast_only":
            forecast_jobs = set(forecast["Job"].dropna().astype(str)) if not forecast.empty and "Job" in forecast.columns else set()
            if forecast_jobs:
                actuals = actuals[actuals["Job"].isin(forecast_jobs)].copy() if not actuals.empty else actuals
                forecast_for_summary = forecast[forecast["Job"].isin(forecast_jobs)].copy()
            else:
                forecast_for_summary = forecast
        else:
            forecast_for_summary = forecast
        summary = build_summary(actuals, forecast_for_summary, sites)
        monthly = build_monthly(actuals)
        st.session_state["live_cost_results"] = {
            "issues": issues,
            "sites": sites,
            "forecast": forecast_for_summary,
            "actuals": actuals,
            "summary": summary,
            "monthly": monthly,
            "report_from": report_from,
            "report_to": report_to,
            "run_mode": run_mode,
        }
    except Exception as exc:
        st.error(f"Could not build the report: {exc}")
        render_bottom_chase()
        st.stop()

if not st.session_state["live_cost_results"]:
    render_bottom_chase()
    st.stop()

results = st.session_state["live_cost_results"]
issues = results["issues"]
actuals = results["actuals"]
summary = results["summary"]
monthly = results["monthly"]
report_from = results.get("report_from")
report_to = results.get("report_to")
if report_from and report_to:
    st.caption(f"Reporting period: {pd.Timestamp(report_from).strftime('%d/%m/%Y')} to {pd.Timestamp(report_to).strftime('%d/%m/%Y')}")

forecast_total = summary["Overall Forecast"].sum() if not summary.empty else 0
actual_total = summary["Actual Cost"].sum() if not summary.empty else 0
profit_total = summary["Profit"].sum() if not summary.empty else 0
actual_profit_total = summary["Actual Profit"].sum() if "Actual Profit" in summary.columns and not summary.empty else 0
variance_total = summary["Live Variance"].sum() if not summary.empty else 0

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    render_kpi("Forecast Cost", format_currency(forecast_total))
with k2:
    render_kpi("Actual Cost", format_currency(actual_total))
with k3:
    render_kpi("Forecast Profit", format_currency(profit_total))
with k4:
    render_kpi("Actual Profit", format_currency(actual_profit_total))
with k5:
    render_kpi("Variance", format_currency(variance_total))

st.markdown('<div class="pas-results-title">Live Cost Results</div>', unsafe_allow_html=True)
st.markdown('<div class="pas-unmatched-pill">Site Summary</div>', unsafe_allow_html=True)
summary_display_cols = ["Job", "Site", "Overall Forecast", "Actual Cost", "Live Variance", "Profit", "Profit %", "Actual Profit", "Actual Profit %"]
summary_display = summary[summary_display_cols].copy() if not summary.empty else pd.DataFrame(columns=summary_display_cols)
for c in summary_display.columns:
    if c in ["Profit %", "Actual Profit %"]:
        summary_display[c] = summary_display[c].map(lambda x: f"{x:.1%}" if pd.notna(x) else "")
    elif c not in ["Job", "Site"]:
        summary_display[c] = summary_display[c].map(format_currency)
render_table(summary_display)

st.markdown('<div class="pas-unmatched-pill">Download Report</div>', unsafe_allow_html=True)
export_bytes = excel_export(summary, monthly, actuals, issues)
st.download_button(
    "Download Excel Report",
    data=export_bytes,
    file_name=f"PAS_Live_Cost_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

render_bottom_chase()
