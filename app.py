import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

st.set_page_config(
    page_title="PAS Groundworks",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAS_YELLOW = "#ffd400"
DARK = "#111827"
SLATE = "#1f2937"
SOFT_BG = "#f5f7fb"
BORDER = "#e5e7eb"

st.markdown(f"""
<style>
    .stApp {{ background: {SOFT_BG}; }}
    section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0b1220 0%, #151f32 100%); }}
    section[data-testid="stSidebar"] * {{ color: #f9fafb !important; }}
    .block-container {{ padding-top: 1.8rem; padding-bottom: 2rem; }}
    .hero {{
        background: linear-gradient(135deg, #111827 0%, #1f2937 60%, #3b3100 100%);
        border-radius: 26px;
        padding: 30px 34px;
        color: white;
        box-shadow: 0 18px 45px rgba(15,23,42,.22);
        margin-bottom: 24px;
    }}
    .hero h1 {{ margin: 0; font-size: 42px; letter-spacing: -1.2px; }}
    .hero p {{ margin: 8px 0 0 0; color: #d1d5db; font-size: 16px; }}
    .pill {{
        display: inline-block;
        background: rgba(255,212,0,.14);
        color: {PAS_YELLOW};
        border: 1px solid rgba(255,212,0,.35);
        border-radius: 999px;
        padding: 6px 12px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 13px;
    }}
    .kpi-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 22px 22px;
        box-shadow: 0 10px 30px rgba(15,23,42,.07);
        min-height: 145px;
    }}
    .kpi-label {{ color:#6b7280; font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing:.06em; }}
    .kpi-value {{ color:#111827; font-size: 30px; font-weight: 850; letter-spacing:-.8px; margin-top: 8px; }}
    .kpi-note {{ color:#6b7280; font-size: 13px; margin-top: 10px; }}
    .section-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 8px 25px rgba(15,23,42,.06);
        margin-bottom: 18px;
    }}
    .attention {{
        border-left: 5px solid #ef4444;
        background: #fff;
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 6px 18px rgba(15,23,42,.06);
    }}
    .muted {{ color: #6b7280; }}
    div.stButton > button:first-child {{
        background: {PAS_YELLOW};
        color: #111827;
        border: none;
        border-radius: 14px;
        padding: .65rem 1rem;
        font-weight: 800;
        box-shadow: 0 8px 18px rgba(255,212,0,.25);
    }}
</style>
""", unsafe_allow_html=True)

# Temporary demo data. This will be replaced by SharePoint + database outputs.
jobs = pd.DataFrame({
    "Job": ["P149 Peel Hall", "P151 Peel Hall M&N", "P164 Airport", "P170 Salford", "P181 Trafford"],
    "Budget": [1250000, 780000, 620000, 430000, 510000],
    "Actual": [1334000, 742000, 589000, 461000, 498000],
    "Forecast": [1418000, 802000, 612000, 486000, 522000],
    "Health": [42, 84, 91, 67, 88],
})
jobs["Variance"] = jobs["Forecast"] - jobs["Budget"]

costs = pd.DataFrame({
    "Category": ["Materials", "Plant", "Labour", "Site Fuel", "Vehicle Hire", "Fuel Card", "Overheads"],
    "Cost": [842000, 315000, 690000, 74500, 128000, 53500, 98000],
})

runs = pd.DataFrame({
    "Run Date": ["2026-06-29", "2026-06-22", "2026-06-15"],
    "Reporting Period": ["FYTD", "FYTD", "FYTD"],
    "Run By": ["Head of Procurement", "Head of Procurement", "Commercial Director"],
    "Status": ["Complete", "Complete", "Complete"],
})

with st.sidebar:
    st.markdown("### PAS Groundworks")
    st.caption("Commercial Management Platform")
    st.divider()
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Live Costs",
            "Report History",
            "Compare Runs",
            "Data Issues",
            "Settings",
            "Future Modules",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Prototype v0.1")
    st.caption("SharePoint + PostgreSQL ready")


def hero(title: str, subtitle: str, pill: str = "PAS Groundworks"):
    st.markdown(f"""
    <div class='hero'>
        <div class='pill'>{pill}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def kpi(label, value, note):
    st.markdown(f"""
    <div class='kpi-card'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-note'>{note}</div>
    </div>
    """, unsafe_allow_html=True)

if page == "Dashboard":
    hero("Executive Dashboard", "Instant view of budget health, live cost position and project risk.", "Commercial Control")
    total_budget = jobs["Budget"].sum()
    total_actual = jobs["Actual"].sum()
    total_forecast = jobs["Forecast"].sum()
    total_variance = total_forecast - total_budget
    over_budget = (jobs["Variance"] > 0).sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Budget Health", f"£{total_variance:,.0f} OVER", f"{over_budget} jobs forecast over budget")
    with c2: kpi("Actual Spend", f"£{total_actual:,.0f}", "Current processed live cost")
    with c3: kpi("Forecast Final Cost", f"£{total_forecast:,.0f}", "Based on latest Forecast workbook")
    with c4: kpi("Project Health", "74%", "Weighted average health score")

    left, right = st.columns([1.25, .75])
    with left:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Spend by Category")
        fig = px.bar(costs, x="Category", y="Cost", text_auto=True)
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=20,b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.subheader("Attention Required")
        for _, row in jobs.sort_values("Health").head(3).iterrows():
            st.markdown(f"""
            <div class='attention'>
                <strong>{row['Job']}</strong><br>
                <span class='muted'>Forecast variance: £{row['Variance']:,.0f} | Health score: {row['Health']}%</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Job Health")
    st.dataframe(jobs, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Live Costs":
    hero("Live Costs", "Build a live cost snapshot from SharePoint files and save the run to history.", "First Module")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Build Report")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.date_input("Reporting From", value=date(date.today().year, 4, 1))
    with c2:
        st.date_input("Reporting To", value=date.today())
    with c3:
        st.selectbox("Period", ["Financial Year To Date", "This Month", "This Week", "Custom"])

    st.info("Prototype mode: SharePoint selector will replace manual uploads once Microsoft Graph access is configured.")
    uploaded = st.file_uploader("Temporary upload area", accept_multiple_files=True, type=["xlsx", "xls", "csv"])
    st.button("Build Live Costs Report")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Expected SharePoint Sources")
    st.table(pd.DataFrame({
        "Source": ["Forecast", "Materials", "Labour", "Vehicles", "Fuel"],
        "Location": ["SharePoint / Commercial", "SharePoint / Procurement", "SharePoint / Labour", "SharePoint / Fleet", "SharePoint / Fuel"],
        "Status": ["Required", "Required", "Required", "Required", "Optional for v0.1"],
    }))
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Report History":
    hero("Report History", "Every report run will be stored, searchable and comparable.", "Database History")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.dataframe(runs, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Compare Runs":
    hero("Compare Runs", "Compare latest cost snapshots against previous weeks.", "Commercial Trends")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.selectbox("Current Run", runs["Run Date"])
    st.selectbox("Compare Against", runs["Run Date"])
    st.warning("Comparison engine will be connected once report snapshots are stored in PostgreSQL.")
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Data Issues":
    hero("Data Issues", "Highlight missing job numbers, date issues, duplicates and corrections required.", "Data Quality")
    issues = pd.DataFrame({
        "Severity": ["High", "Medium", "Low"],
        "Source": ["Materials", "Labour", "Vehicles"],
        "Issue": ["Missing job number", "Invalid date", "Duplicate registration"],
        "Status": ["Open", "Open", "Review"],
    })
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.dataframe(issues, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif page == "Settings":
    hero("Settings", "Platform configuration for SharePoint, database and reporting rules.", "Administration")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("SharePoint")
    st.text_input("Tenant ID", placeholder="To be provided by IT")
    st.text_input("Client ID", placeholder="To be provided by IT")
    st.text_input("SharePoint Site", placeholder="PAS NW Construction Ltd")
    st.subheader("Database")
    st.text_input("PostgreSQL Host", placeholder="localhost / cloud host")
    st.text_input("Database Name", value="pas_groundworks")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    hero("Future Modules", "The long-term PAS Groundworks module roadmap.", "Platform Vision")
    modules = pd.DataFrame({
        "Module": ["Forecasting", "Procurement", "Plant", "Vehicles", "Fuel", "Invoice Matching", "Hire Reports", "Documents"],
        "Status": ["Planned", "Planned", "Future", "Future", "Existing app to migrate", "Existing app to migrate", "Existing app to migrate", "Future"],
        "Target": ["v1.5", "v1.5", "v2.0", "v2.0", "v2.0", "v2.0", "v2.0", "v2.5"],
    })
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.dataframe(modules, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
