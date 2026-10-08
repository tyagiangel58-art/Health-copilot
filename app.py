import streamlit as st
from pypdf import PdfReader
from openai import OpenAI
import json
import sqlite3
from datetime import datetime
import pandas as pd
import re


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Health Copilot",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

client = OpenAI()

DB_NAME = "health_history.db"


# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

.stApp {
    background: #f7f8fc;
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", Arial, sans-serif;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #172554 0%,
        #1e3a8a 55%,
        #312e81 100%
    );
    border-right: none;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

section[data-testid="stSidebar"] * {
    color: #f8fafc;
}

.sidebar-brand {
    padding: 8px 8px 25px 8px;
}

.sidebar-brand-title {
    font-size: 25px;
    font-weight: 750;
    letter-spacing: -0.7px;
}

.sidebar-brand-subtitle {
    font-size: 12px;
    color: #c7d2fe !important;
    margin-top: 4px;
}

.sidebar-section {
    font-size: 10px;
    font-weight: 700;
    color: #a5b4fc !important;
    letter-spacing: 1.4px;
    margin: 20px 8px 7px 8px;
}

section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    text-align: left;
    border: none;
    background: transparent;
    color: #e0e7ff;
    padding: 9px 12px;
    border-radius: 9px;
    font-size: 14px;
    font-weight: 500;
    margin: 1px 0;
    transition: all 0.15s ease;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.10);
    color: white;
}

section[data-testid="stSidebar"] .stButton button:focus {
    box-shadow: none;
}

.sidebar-patient {
    margin-top: 25px;
    padding: 14px;
    border-radius: 12px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.10);
}

.sidebar-patient-name {
    font-weight: 650;
    font-size: 14px;
}

.sidebar-patient-id {
    font-size: 11px;
    color: #c7d2fe !important;
    margin-top: 3px;
}


/* ---------- PAGE HEADERS ---------- */

.page-title {
    font-size: 32px;
    line-height: 1.15;
    font-weight: 760;
    color: #172554;
    letter-spacing: -1px;
    margin-bottom: 5px;
}

.page-subtitle {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 24px;
}

.section-title {
    color: #172554;
    font-size: 19px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 13px;
}

.section-caption {
    color: #64748b;
    font-size: 13px;
}


/* ---------- HERO ---------- */

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        115deg,
        #1d4ed8 0%,
        #4f46e5 48%,
        #7c3aed 100%
    );
    border-radius: 20px;
    padding: 30px 34px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(37,99,235,0.15);
}

.hero:after {
    content: "";
    position: absolute;
    width: 230px;
    height: 230px;
    border-radius: 50%;
    right: -80px;
    top: -100px;
    background: rgba(255,255,255,0.09);
}

.hero-title {
    font-size: 28px;
    font-weight: 750;
    letter-spacing: -0.7px;
    position: relative;
    z-index: 1;
}

.hero-text {
    margin-top: 7px;
    color: #dbeafe;
    font-size: 14px;
    position: relative;
    z-index: 1;
}


/* ---------- STAT CARDS ---------- */

.stat-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 19px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(15,23,42,0.04);
}

.stat-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
}

.stat-value {
    font-size: 30px;
    color: #172554;
    font-weight: 750;
    margin-top: 8px;
}

.stat-small {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 3px;
}

.stat-blue {
    border-top: 4px solid #2563eb;
}

.stat-purple {
    border-top: 4px solid #7c3aed;
}

.stat-green {
    border-top: 4px solid #16a34a;
}

.stat-orange {
    border-top: 4px solid #f59e0b;
}


/* ---------- CONTENT CARDS ---------- */

.content-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 21px;
    box-shadow: 0 3px 14px rgba(15,23,42,0.035);
}

.card-heading {
    color: #172554;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 4px;
}

.card-description {
    color: #64748b;
    font-size: 12px;
}


/* ---------- STATUS ---------- */

.status-normal {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    background: #dcfce7;
    color: #166534;
    font-size: 11px;
    font-weight: 700;
}

.status-high {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    background: #fef3c7;
    color: #92400e;
    font-size: 11px;
    font-weight: 700;
}

.status-low {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    background: #fee2e2;
    color: #991b1b;
    font-size: 11px;
    font-weight: 700;
}

.status-unknown {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    background: #f1f5f9;
    color: #475569;
    font-size: 11px;
    font-weight: 700;
}


/* ---------- BUTTONS ---------- */

.stButton > button {
    border-radius: 9px;
    border: 1px solid #dbe2ea;
    background: white;
    color: #172554;
    font-weight: 600;
    min-height: 40px;
    transition: all 0.15s ease;
}

.stButton > button:hover {
    border-color: #2563eb;
    color: #2563eb;
    background: #eff6ff;
}

.stButton > button[kind="primary"] {
    background: #2563eb;
    border-color: #2563eb;
    color: white;
}

.stButton > button[kind="primary"]:hover {
    background: #1d4ed8;
    border-color: #1d4ed8;
    color: white;
}


/* ---------- FILE UPLOADER ---------- */

section[data-testid="stFileUploaderDropzone"] {
    background: #f8faff;
    border: 2px dashed #93c5fd;
    border-radius: 15px;
    padding: 20px;
}

section[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #2563eb;
    background: #eff6ff;
}


/* ---------- INPUTS ---------- */

.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stTextArea textarea {
    border-radius: 9px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #2563eb !important;
}


/* ---------- METRICS ---------- */

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e5e7eb;
    padding: 15px;
    border-radius: 13px;
}

div[data-testid="stMetricLabel"] {
    color: #64748b;
}

div[data-testid="stMetricValue"] {
    color: #172554;
}


/* ---------- DATAFRAMES ---------- */

div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}


/* ---------- EXPANDERS ---------- */

div[data-testid="stExpander"] {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: white;
}


/* ---------- ALERTS ---------- */

div[data-testid="stAlert"] {
    border-radius: 10px;
}


/* ---------- DIVIDER ---------- */

hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 25px 0;
}


/* ---------- REPORT PREVIEW ---------- */

.report-preview {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 22px;
    margin-bottom: 15px;
}

.report-date {
    font-size: 12px;
    color: #64748b;
}

.report-name {
    font-size: 17px;
    color: #172554;
    font-weight: 700;
    margin-top: 3px;
}


/* ---------- TIMELINE ---------- */

.timeline-card {
    position: relative;
    background: white;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #2563eb;
    border-radius: 12px;
    padding: 17px 20px;
    margin-bottom: 12px;
}

.timeline-date {
    color: #2563eb;
    font-size: 12px;
    font-weight: 700;
}

.timeline-title {
    color: #172554;
    font-size: 15px;
    font-weight: 700;
    margin-top: 4px;
}


/* ---------- MEDICINE CARD ---------- */

.medicine-card {
    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #f5f3ff 100%
    );
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px;
}

.medicine-name {
    color: #312e81;
    font-size: 16px;
    font-weight: 700;
}

.medicine-detail {
    color: #64748b;
    font-size: 12px;
    margin-top: 5px;
}


/* ---------- CHAT / ASK RECORDS ---------- */

.chat-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 15px;
    padding: 20px;
}

.question-box {
    background: #eff6ff;
    border-left: 4px solid #2563eb;
    border-radius: 9px;
    padding: 13px 16px;
    color: #1e3a8a;
    font-size: 14px;
}

.answer-box {
    background: #f5f3ff;
    border-left: 4px solid #7c3aed;
    border-radius: 9px;
    padding: 15px 17px;
    color: #312e81;
    font-size: 14px;
    line-height: 1.6;
}


/* ---------- MOBILE ---------- */

@media (max-width: 768px) {

    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .page-title {
        font-size: 25px;
    }

    .hero {
        padding: 24px;
    }

    .hero-title {
        font-size: 23px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================

def init_database():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            patient_id TEXT,
            report_date TEXT,
            file_name TEXT,
            report_data TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_report(patient, health_data, file_name):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports
        (
            patient_name,
            patient_id,
            report_date,
            file_name,
            report_data,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        patient.get("name", "Not provided"),
        patient.get("patient_id", "Not provided"),
        patient.get("report_date", "Not provided"),
        file_name,
        json.dumps(health_data),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


def get_previous_reports():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            patient_name,
            patient_id,
            report_date,
            file_name,
            report_data
        FROM reports
        ORDER BY id DESC
    """)

    reports = cursor.fetchall()

    conn.close()

    return reports


def init_app():
    init_database()


init_app()


# =========================================================
# HELPERS
# =========================================================

def parse_json_response(text):

    text = text.strip()

    try:
        return json.loads(text)
    except:
        pass

    text = text.replace(
        "```json",
        ""
    ).replace(
        "```",
        ""
    ).strip()

    try:
        return json.loads(text)
    except:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:

        try:
            return json.loads(
                text[start:end + 1]
            )
        except:
            pass

    return None


def safe_id(value, fallback="unknown"):

    value = str(value or fallback)

    value = re.sub(
        r"[^A-Za-z0-9\-_\.]",
        "-",
        value
    )

    value = value.strip("-")

    return value[:64] or fallback


def load_report_data(report):

    try:
        return json.loads(report[5])
    except:
        return {}


def get_numeric_value(value):

    try:
        return float(value)
    except:
        return None


# =========================================================
# FHIR
# =========================================================

def create_fhir_bundle(health_data):

    patient = health_data.get(
        "patient",
        {}
    )

    labs = health_data.get(
        "lab_results",
        []
    )

    medicines = health_data.get(
        "medicines",
        []
    )

    patient_id_raw = patient.get(
        "patient_id",
        "unknown-patient"
    )

    patient_id = safe_id(
        patient_id_raw,
        "unknown-patient"
    )

    patient_name = patient.get(
        "name",
        "Not provided"
    )

    report_date = patient.get(
        "report_date",
        "Not provided"
    )

    entries = []

    patient_resource = {
        "resourceType": "Patient",
        "id": patient_id,
        "identifier": [
            {
                "system": "https://healthcopilot.local/patient-id",
                "value": str(patient_id_raw)
            }
        ],
        "name": [
            {
                "text": patient_name
            }
        ]
    }

    entries.append({
        "fullUrl": f"urn:uuid:{patient_id}",
        "resource": patient_resource
    })

    for index, lab in enumerate(labs):

        test_name = lab.get(
            "test",
            "Unknown test"
        )

        observation_id = safe_id(
            f"observation-{index}-{test_name}"
        )

        observation = {
            "resourceType": "Observation",
            "id": observation_id,
            "status": "final",
            "code": {
                "text": test_name
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": report_date,
            "interpretation": [
                {
                    "text": lab.get(
                        "status",
                        "Unknown"
                    )
                }
            ]
        }

        numeric_value = get_numeric_value(
            lab.get("value", "")
        )

        if numeric_value is not None:

            observation["valueQuantity"] = {
                "value": numeric_value,
                "unit": lab.get(
                    "unit",
                    ""
                )
            }

        else:

            observation["valueString"] = str(
                lab.get(
                    "value",
                    ""
                )
            )

        reference_range = lab.get(
            "reference_range",
            ""
        )

        if reference_range:

            observation["referenceRange"] = [
                {
                    "text": reference_range
                }
            ]

        entries.append({
            "fullUrl": f"urn:uuid:{observation_id}",
            "resource": observation
        })

    for index, medicine in enumerate(medicines):

        medicine_name = medicine.get(
            "name",
            "Unknown medicine"
        )

        medication_id = safe_id(
            f"medication-{index}-{medicine_name}"
        )

        medication_resource = {
            "resourceType": "MedicationStatement",
            "id": medication_id,
            "status": "unknown",
            "medicationCodeableConcept": {
                "text": medicine_name
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": report_date,
            "dosage": [
                {
                    "text": (
                        f"Dosage: "
                        f"{medicine.get('dosage', 'Not provided')}; "
                        f"Frequency: "
                        f"{medicine.get('frequency', 'Not provided')}"
                    )
                }
            ]
        }

        entries.append({
            "fullUrl": f"urn:uuid:{medication_id}",
            "resource": medication_resource
        })

    return {
        "resourceType": "Bundle",
        "id": safe_id(
            f"healthcopilot-{patient_id}-{report_date}"
        ),
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "entry": entries
    }


def create_complete_fhir_history(reports):

    entries = []

    for report in reports:

        data = load_report_data(report)

        if data:

            bundle = create_fhir_bundle(
                data
            )

            entries.extend(
                bundle.get(
                    "entry",
                    []
                )
            )

    return {
        "resourceType": "Bundle",
        "id": "healthcopilot-complete-history",
        "type": "collection",
        "timestamp": datetime.now().isoformat(),
        "entry": entries
    }


# =========================================================
# TREND DATA
# =========================================================

def get_trend_data(reports):

    rows = []

    for report in reports:

        data = load_report_data(report)

        labs = data.get(
            "lab_results",
            []
        )

        for lab in labs:

            value = get_numeric_value(
                lab.get(
                    "value",
                    ""
                )
            )

            if value is None:
                continue

            rows.append({
                "report_id": report[0],
                "date": report[3],
                "test": lab.get(
                    "test",
                    "Unknown"
                ),
                "value": value,
                "unit": lab.get(
                    "unit",
                    ""
                ),
                "reference_range": lab.get(
                    "reference_range",
                    "Not provided"
                ),
                "status": lab.get(
                    "status",
                    "Unknown"
                )
            })

    return rows


# =========================================================
# RANGE CHECK
# =========================================================

def get_range_status(value, reference_range):

    if not reference_range:
        return "Unknown"

    text = str(
        reference_range
    ).strip()

    if text.lower() in [
        "",
        "unknown",
        "not provided",
        "n/a"
    ]:
        return "Unknown"

    range_match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*[-–]\s*(-?\d+(?:\.\d+)?)",
        text
    )

    if range_match:

        lower = float(
            range_match.group(1)
        )

        upper = float(
            range_match.group(2)
        )

        if value < lower:
            return "Below"

        if value > upper:
            return "Above"

        return "Normal"

    upper_match = re.search(
        r"<\s*(-?\d+(?:\.\d+)?)",
        text
    )

    if upper_match:

        upper = float(
            upper_match.group(1)
        )

        if value < upper:
            return "Normal"

        if value >= upper:
            return "Above"

    lower_match = re.search(
        r">\s*(-?\d+(?:\.\d+)?)",
        text
    )

    if lower_match:

        lower = float(
            lower_match.group(1)
        )

        if value > lower:
            return "Normal"

        if value <= lower:
            return "Below"

    return "Unknown"


# =========================================================
# STATUS HTML
# =========================================================

def status_badge(status):

    status = str(status or "Unknown")

    if status.lower() == "normal":

        return (
            '<span class="status-normal">'
            'Normal'
            '</span>'
        )

    if status.lower() == "above":

        return (
            '<span class="status-high">'
            'Above range'
            '</span>'
        )

    if status.lower() == "below":

        return (
            '<span class="status-low">'
            'Below range'
            '</span>'
        )

    return (
        '<span class="status-unknown">'
        'Unknown'
        '</span>'
    )


# =========================================================
# SMART INSIGHTS
# =========================================================

def get_smart_insights(health_data):

    labs = health_data.get(
        "lab_results",
        []
    )

    insights = []

    for lab in labs:

        status = str(
            lab.get(
                "status",
                "Unknown"
            )
        )

        if status.lower() == "above":

            insights.append({
                "test": lab.get(
                    "test",
                    "Unknown test"
                ),
                "status": status,
                "category": "Above provided range"
            })

        elif status.lower() == "below":

            insights.append({
                "test": lab.get(
                    "test",
                    "Unknown test"
                ),
                "status": status,
                "category": "Below provided range"
            })

    return insights


# =========================================================
# LANGUAGE
# =========================================================

translations = {

    "English": {

        "dashboard": "Dashboard",
        "upload": "Upload & Analyze",
        "health": "My Health",
        "timeline": "Timeline",
        "medicines": "Medicines",
        "ask": "Ask My Records",
        "compare": "Compare Reports",
        "data": "Health Data",
        "saved": "Saved Reports"

    },

    "Hindi / हिंदी": {

        "dashboard": "डैशबोर्ड",
        "upload": "रिपोर्ट अपलोड करें",
        "health": "मेरा स्वास्थ्य",
        "timeline": "टाइमलाइन",
        "medicines": "दवाइयाँ",
        "ask": "मेरे रिकॉर्ड से पूछें",
        "compare": "रिपोर्ट की तुलना",
        "data": "स्वास्थ्य डेटा",
        "saved": "सेव की गई रिपोर्ट"

    }

}


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

language = st.sidebar.selectbox(
    "Language",
    [
        "English",
        "Hindi / हिंदी"
    ]
)

T = translations[language]

st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-title">
        Health Copilot
    </div>
    <div class="sidebar-brand-subtitle">
        Your personal health record assistant
    </div>
</div>
""", unsafe_allow_html=True)


st.sidebar.markdown(
    '<div class="sidebar-section">OVERVIEW</div>',
    unsafe_allow_html=True
)

nav_items = [

    ("dashboard", T["dashboard"]),

    ("upload", T["upload"]),

    ("health", T["health"]),

    ("timeline", T["timeline"]),

    ("medicines", T["medicines"]),

    ("ask", T["ask"]),

    ("compare", T["compare"]),

    ("data", T["data"]),

    ("saved", T["saved"])

]


if "page" not in st.session_state:
    st.session_state.page = "dashboard"


for key, label in nav_items:

    if st.sidebar.button(
        label,
        key=f"nav_{key}"
    ):

        st.session_state.page = key


page = st.session_state.page


# =========================================================
# PATIENT CARD
# =========================================================

reports = get_previous_reports()

if reports:

    latest_data = load_report_data(
        reports[0]
    )

    latest_patient = latest_data.get(
        "patient",
        {}
    )

    patient_name = latest_patient.get(
        "name",
        reports[0][1]
    )

    patient_id = latest_patient.get(
        "patient_id",
        reports[0][2]
    )

else:

    patient_name = "No patient loaded"
    patient_id = "Upload a report"


st.sidebar.markdown(
    f"""
    <div class="sidebar-patient">
        <div class="sidebar-patient-name">
            {patient_name}
        </div>
        <div class="sidebar-patient-id">
            {patient_id}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "dashboard":

    if language == "Hindi / हिंदी":

        greeting = "नमस्ते"
        dashboard_subtitle = (
            "आपकी स्वास्थ्य जानकारी का एक आसान अवलोकन।"
        )

    else:

        greeting = "Good to see you"
        dashboard_subtitle = (
            "A simple overview of your health journey."
        )

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-title">
                {greeting}, {patient_name}
            </div>
            <div class="hero-text">
                {dashboard_subtitle}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    total_reports = len(reports)

    all_trends = get_trend_data(
        reports
    )

    unique_tests = len(
        set(
            row["test"]
            for row in all_trends
        )
    )

    attention_count = 0

    if reports:

        latest = load_report_data(
            reports[0]
        )

        latest_labs = latest.get(
            "lab_results",
            []
        )

        attention_count = len([
            lab
            for lab in latest_labs
            if str(
                lab.get(
                    "status",
                    "Unknown"
                )
            ).lower()
            in ["above", "below"]
        ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="stat-card stat-blue">
                <div class="stat-label">
                    Reports
                </div>
                <div class="stat-value">
                    {total_reports}
                </div>
                <div class="stat-small">
                    Saved health reports
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="stat-card stat-purple">
                <div class="stat-label">
                    Tests tracked
                </div>
                <div class="stat-value">
                    {unique_tests}
                </div>
                <div class="stat-small">
                    Across your reports
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            f"""
            <div class="stat-card stat-orange">
                <div class="stat-label">
                    Need attention
                </div>
                <div class="stat-value">
                    {attention_count}
                </div>
                <div class="stat-small">
                    Based on report ranges
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div class="stat-card stat-green">
                <div class="stat-label">
                    Health records
                </div>
                <div class="stat-value">
                    {len(all_trends)}
                </div>
                <div class="stat-small">
                    Values extracted
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-title">Recent health activity</div>',
        unsafe_allow_html=True
    )

    if reports:

        for report in reports[:3]:

            st.markdown(
                f"""
                <div class="report-preview">
                    <div class="report-date">
                        {report[3]}
                    </div>
                    <div class="report-name">
                        {report[4]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.info(
            "Upload your first medical report to start building your health history."
        )

    if reports:

        st.markdown(
            '<div class="section-title">Latest health snapshot</div>',
            unsafe_allow_html=True
        )

        latest_data = load_report_data(
            reports[0]
        )

        latest_labs = latest_data.get(
            "lab_results",
            []
        )

        if latest_labs:

            cols = st.columns(
                min(4, len(latest_labs))
            )

            for index, lab in enumerate(
                latest_labs[:4]
            ):

                with cols[index]:

                    test = lab.get(
                        "test",
                        "Test"
                    )

                    value = lab.get(
                        "value",
                        "—"
                    )

                    unit = lab.get(
                        "unit",
                        ""
                    )

                    status = lab.get(
                        "status",
                        "Unknown"
                    )

                    badge = status_badge(
                        status
                    )

                    st.markdown(
                        f"""
                        <div class="content-card">
                            <div class="card-description">
                                {test}
                            </div>
                            <div style="
                                font-size:25px;
                                font-weight:750;
                                color:#172554;
                                margin-top:8px;
                            ">
                                {value}
                                <span style="
                                    font-size:11px;
                                    color:#64748b;
                                    font-weight:500;
                                ">
                                    {unit}
                                </span>
                            </div>
                            <div style="margin-top:9px;">
                                {badge}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        insights = get_smart_insights(
            latest_data
        )

        if insights:

            st.markdown(
                '<div class="section-title">What your latest report shows</div>',
                unsafe_allow_html=True
            )

            for insight in insights[:3]:

                st.markdown(
                    f"""
                    <div class="timeline-card">
                        <div class="timeline-title">
                            {insight["test"]}
                        </div>
                        <div class="card-description">
                            {insight["category"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.caption(
        "Health Copilot provides informational support based on uploaded records. It does not provide a medical diagnosis or treatment advice."
    )
    

    if language == "Hindi / हिंदी":
        title = "रिपोर्ट अपलोड करें"
        subtitle = "अपनी मेडिकल रिपोर्ट अपलोड करें और स्वास्थ्य जानकारी निकालें।"
    else:
        title = "Upload & Analyze"
        subtitle = "Upload a medical report and let Health Copilot organize the information."

    st.markdown(
        f'<div class="page-title">{title}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="content-card">
            <div class="card-heading">Medical report</div>
            <div class="card-description">
                PDF reports, laboratory reports, prescriptions and scanned documents are supported.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose a medical report",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file:

        st.markdown(
            f"""
            <div class="report-preview">
                <div class="report-date">Selected file</div>
                <div class="report-name">{uploaded_file.name}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        analyze_button = st.button(
            "Analyze Report",
            type="primary",
            use_container_width=True
        )

        if analyze_button:

            with st.spinner("Reading and analyzing the report..."):

                try:

                    reader = PdfReader(
                        uploaded_file
                    )

                    extracted_text = ""

                    for page_obj in reader.pages:

                        page_text = page_obj.extract_text()

                        if page_text:
                            extracted_text += page_text + "\n"

                    if not extracted_text.strip():

                        st.warning(
                            "This appears to be a scanned PDF. AI document reading will be used instead."
                        )

                        uploaded_file.seek(0)

                        file_bytes = uploaded_file.read()

                        response = client.responses.create(
                            model="gpt-6-luna",
                            input=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "input_file",
                                            "filename": uploaded_file.name,
                                            "file_data": (
                                                "data:application/pdf;base64,"
                                                + __import__("base64")
                                                .b64encode(file_bytes)
                                                .decode()
                                            )
                                        },
                                        {
                                            "type": "input_text",
                                            "text": """
Read this medical report carefully.

Extract the following information:

1. Patient name
2. Patient ID
3. Report date
4. Laboratory tests
5. Test values
6. Units
7. Reference ranges
8. Status based only on the provided reference range
9. Medicines
10. Dosage
11. Frequency
12. Diagnoses or observations explicitly written in the report

Return valid JSON only using this structure:

{
    "patient": {
        "name": "",
        "patient_id": "",
        "report_date": ""
    },
    "lab_results": [
        {
            "test": "",
            "value": "",
            "unit": "",
            "reference_range": "",
            "status": ""
        }
    ],
    "medicines": [
        {
            "name": "",
            "dosage": "",
            "frequency": ""
        }
    ],
    "diagnoses": [],
    "observations": []
}

Do not diagnose the patient.
Do not invent missing information.
"""
                                        }
                                    ]
                                }
                            ]
                        )

                        result_text = response.output_text

                    else:

                        extraction_prompt = f"""
You are extracting structured information from a medical report.

Read the report below carefully.

Return valid JSON only using this structure:

{{
    "patient": {{
        "name": "",
        "patient_id": "",
        "report_date": ""
    }},
    "lab_results": [
        {{
            "test": "",
            "value": "",
            "unit": "",
            "reference_range": "",
            "status": ""
        }}
    ],
    "medicines": [
        {{
            "name": "",
            "dosage": "",
            "frequency": ""
        }}
    ],
    "diagnoses": [],
    "observations": []
}}

Rules:

- Extract only information actually present.
- Do not invent missing values.
- Use the report's reference ranges.
- If a value is below the given range, status should be "Below".
- If a value is above the given range, status should be "Above".
- If it is within the range, status should be "Normal".
- If there is no usable reference range, status should be "Unknown".
- Do not provide a diagnosis.
- Do not provide treatment recommendations.

MEDICAL REPORT:

{extracted_text}
"""

                        response = client.responses.create(
                            model="gpt-6-luna",
                            input=extraction_prompt
                        )

                        result_text = response.output_text

                    health_data = parse_json_response(
                        result_text
                    )

                    if not health_data:

                        st.error(
                            "The report could not be converted into structured information."
                        )

                    else:

                        patient = health_data.get(
                            "patient",
                            {}
                        )

                        labs = health_data.get(
                            "lab_results",
                            []
                        )

                        medicines = health_data.get(
                            "medicines",
                            []
                        )

                        for lab in labs:

                            numeric_value = get_numeric_value(
                                lab.get(
                                    "value",
                                    ""
                                )
                            )

                            if numeric_value is not None:

                                lab["status"] = get_range_status(
                                    numeric_value,
                                    lab.get(
                                        "reference_range",
                                        ""
                                    )
                                )

                        health_data["lab_results"] = labs

                        save_report(
                            patient,
                            health_data,
                            uploaded_file.name
                        )

                        st.session_state.last_health_data = health_data

                        st.success(
                            "Report analyzed and saved successfully."
                        )

                except Exception as e:

                    st.error(
                        f"Something went wrong while analyzing the report: {e}"
                    )

    if "last_health_data" in st.session_state:

        health_data = st.session_state.last_health_data

        st.markdown(
            '<div class="section-title">Report summary</div>',
            unsafe_allow_html=True
        )

        patient = health_data.get(
            "patient",
            {}
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                f"""
                <div class="content-card">
                    <div class="card-description">
                        Patient
                    </div>
                    <div style="
                        font-size:18px;
                        font-weight:700;
                        color:#172554;
                        margin-top:7px;
                    ">
                        {patient.get("name", "Not provided")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="content-card">
                    <div class="card-description">
                        Patient ID
                    </div>
                    <div style="
                        font-size:18px;
                        font-weight:700;
                        color:#172554;
                        margin-top:7px;
                    ">
                        {patient.get("patient_id", "Not provided")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:

            st.markdown(
                f"""
                <div class="content-card">
                    <div class="card-description">
                        Report date
                    </div>
                    <div style="
                        font-size:18px;
                        font-weight:700;
                        color:#172554;
                        margin-top:7px;
                    ">
                        {patient.get("report_date", "Not provided")}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        labs = health_data.get(
            "lab_results",
            []
        )

        if labs:

            st.markdown(
                '<div class="section-title">Lab results</div>',
                unsafe_allow_html=True
            )

            table_rows = []

            for lab in labs:

                table_rows.append({
                    "Test": lab.get(
                        "test",
                        "Unknown"
                    ),
                    "Value": lab.get(
                        "value",
                        ""
                    ),
                    "Unit": lab.get(
                        "unit",
                        ""
                    ),
                    "Reference range": lab.get(
                        "reference_range",
                        "Not provided"
                    ),
                    "Status": lab.get(
                        "status",
                        "Unknown"
                    )
                })

            st.dataframe(
                pd.DataFrame(table_rows),
                use_container_width=True,
                hide_index=True
            )

        medicines = health_data.get(
            "medicines",
            []
        )

        if medicines:

            st.markdown(
                '<div class="section-title">Medicines mentioned in the report</div>',
                unsafe_allow_html=True
            )

            cols = st.columns(
                min(3, len(medicines))
            )

            for index, medicine in enumerate(
                medicines
            ):

                with cols[index]:

                    st.markdown(
                        f"""
                        <div class="medicine-card">
                            <div class="medicine-name">
                                {medicine.get("name", "Medicine")}
                            </div>
                            <div class="medicine-detail">
                                Dosage: {medicine.get("dosage", "Not provided")}
                            </div>
                            <div class="medicine-detail">
                                Frequency: {medicine.get("frequency", "Not provided")}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown(
            '<div class="section-title">What your report shows</div>',
            unsafe_allow_html=True
        )

        summary_prompt = f"""
Create a short, simple health-information summary from this structured medical report.

Rules:

- Do not diagnose.
- Do not recommend starting or stopping medicines.
- Do not recommend treatment.
- Mention abnormal values and their provided reference ranges.
- Mention normal values only as a brief overview.
- Explain technical terms in simple language.
- Keep the tone calm and human.
- Do not say that a condition is definitely present.

Report:

{json.dumps(health_data, indent=2)}
"""

        try:

            summary_response = client.responses.create(
                model="gpt-6-luna",
                input=summary_prompt
            )

            summary_text = (
                summary_response.output_text
            )

            st.markdown(
                f"""
                <div class="answer-box">
                    {summary_text.replace(chr(10), "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

        except:

            st.info(
                "The structured report is available above."
            )

        st.caption(
            "This information is based on the uploaded report and is not a medical diagnosis or treatment recommendation."
        )


# =========================================================
# MY HEALTH
# =========================================================

elif page == "health":

    st.markdown(
        '<div class="page-title">My Health</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Your latest health information in one place.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    if not reports:

        st.info(
            "Upload a medical report to build your health profile."
        )

    else:

        latest_data = load_report_data(
            reports[0]
        )

        patient = latest_data.get(
            "patient",
            {}
        )

        st.markdown(
            """
            <div class="content-card">
                <div class="card-heading">
                    Health profile
                </div>
                <div class="card-description">
                    Information extracted from your latest saved report.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Patient",
                patient.get(
                    "name",
                    "Not provided"
                )
            )

        with col2:

            st.metric(
                "Patient ID",
                patient.get(
                    "patient_id",
                    "Not provided"
                )
            )

        with col3:

            st.metric(
                "Latest report",
                patient.get(
                    "report_date",
                    "Not provided"
                )
            )

        labs = latest_data.get(
            "lab_results",
            []
        )

        if labs:

            st.markdown(
                '<div class="section-title">Latest lab results</div>',
                unsafe_allow_html=True
            )

            for lab in labs:

                status = lab.get(
                    "status",
                    "Unknown"
                )

                badge = status_badge(
                    status
                )

                col1, col2, col3 = st.columns(
                    [2.2, 1.2, 2]
                )

                with col1:

                    st.markdown(
                        f"""
                        <div style="
                            font-weight:650;
                            color:#172554;
                            padding-top:8px;
                        ">
                            {lab.get("test", "Unknown")}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown(
                        f"""
                        <div style="
                            font-size:18px;
                            font-weight:700;
                            color:#172554;
                            padding-top:5px;
                        ">
                            {lab.get("value", "—")}
                            <span style="
                                font-size:11px;
                                color:#64748b;
                            ">
                                {lab.get("unit", "")}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col3:

                    st.markdown(
                        f"""
                        <div style="padding-top:7px;">
                            {badge}
                            <span style="
                                color:#94a3b8;
                                font-size:11px;
                                margin-left:8px;
                            ">
                                Ref: {lab.get("reference_range", "Not provided")}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    "<hr style='margin:8px 0;'>",
                    unsafe_allow_html=True
                )

        insights = get_smart_insights(
            latest_data
        )

        if insights:

            st.markdown(
                '<div class="section-title">Needs attention</div>',
                unsafe_allow_html=True
            )

            for item in insights:

                st.markdown(
                    f"""
                    <div class="timeline-card">
                        <div class="timeline-title">
                            {item["test"]}
                        </div>
                        <div class="card-description">
                            {item["category"]}. This reflects the reference range provided in the report.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# =========================================================
# TIMELINE
# =========================================================

elif page == "timeline":

    st.markdown(
        '<div class="page-title">Health Timeline</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">A chronological view of your saved medical reports.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    if not reports:

        st.info(
            "Your timeline will appear here after you upload reports."
        )

    else:

        for report in reports:

            data = load_report_data(
                report
            )

            patient = data.get(
                "patient",
                {}
            )

            labs = data.get(
                "lab_results",
                []
            )

            normal_count = len([
                lab
                for lab in labs
                if str(
                    lab.get(
                        "status",
                        ""
                    )
                ).lower() == "normal"
            ])

            attention_count = len([
                lab
                for lab in labs
                if str(
                    lab.get(
                        "status",
                        ""
                    )
                ).lower()
                in ["above", "below"]
            ])

            st.markdown(
                f"""
                <div class="timeline-card">
                    <div class="timeline-date">
                        {patient.get("report_date", report[3])}
                    </div>
                    <div class="timeline-title">
                        {report[4]}
                    </div>
                    <div class="card-description">
                        {len(labs)} tests extracted
                        &nbsp; | &nbsp;
                        {normal_count} within range
                        &nbsp; | &nbsp;
                        {attention_count} outside range
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# MEDICINES
# =========================================================

elif page == "medicines":

    st.markdown(
        '<div class="page-title">Medicines</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Medicines mentioned in your saved medical records.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    medicine_rows = []

    for report in reports:

        data = load_report_data(
            report
        )

        patient = data.get(
            "patient",
            {}
        )

        for medicine in data.get(
            "medicines",
            []
        ):

            medicine_rows.append({
                "Medicine": medicine.get(
                    "name",
                    "Not provided"
                ),
                "Dosage": medicine.get(
                    "dosage",
                    "Not provided"
                ),
                "Frequency": medicine.get(
                    "frequency",
                    "Not provided"
                ),
                "Report date": patient.get(
                    "report_date",
                    report[3]
                )
            })

    if not medicine_rows:

        st.info(
            "No medicines have been extracted from your saved reports."
        )

    else:

        for medicine in medicine_rows:

            st.markdown(
                f"""
                <div class="medicine-card" style="margin-bottom:12px;">
                    <div class="medicine-name">
                        {medicine["Medicine"]}
                    </div>
                    <div class="medicine-detail">
                        Dosage: {medicine["Dosage"]}
                    </div>
                    <div class="medicine-detail">
                        Frequency: {medicine["Frequency"]}
                    </div>
                    <div class="medicine-detail">
                        From report dated {medicine["Report date"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "Medicine information is displayed as recorded in your uploaded reports. Health Copilot does not recommend starting, stopping or changing medicines."
    )


# =========================================================
# ASK MY RECORDS
# =========================================================

elif page == "ask":

    st.markdown(
        '<div class="page-title">Ask My Records</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Ask questions about information contained in your saved health reports.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    if not reports:

        st.info(
            "Upload at least one report before asking questions."
        )

    else:

        st.markdown(
            """
            <div class="chat-card">
                <div class="card-heading">
                    Your health records
                </div>
                <div class="card-description">
                    Ask about test values, dates, medicines or changes across your saved reports.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        question = st.text_area(
            "Your question",
            placeholder="Example: How has my vitamin D changed across my reports?",
            height=100
        )

        if st.button(
            "Ask",
            type="primary"
        ):

            if not question.strip():

                st.warning(
                    "Please enter a question first."
                )

            else:

                records_text = []

                for report in reports:

                    data = load_report_data(
                        report
                    )

                    records_text.append(
                        json.dumps(
                            data,
                            indent=2
                        )
                    )

                combined_records = "\n\n".join(
                    records_text
                )

                ask_prompt = f"""
You are a health-record information assistant.

Answer the user's question using ONLY the saved health records below.

Rules:

- Do not diagnose.
- Do not recommend treatment.
- Do not tell the user to start or stop medicines.
- Clearly distinguish facts from the records.
- If the records do not contain the answer, say that.
- Numeric increases or decreases should be described neutrally.
- Keep the answer simple and understandable.

USER QUESTION:

{question}

SAVED HEALTH RECORDS:

{combined_records}
"""

                with st.spinner(
                    "Looking through your records..."
                ):

                    try:

                        response = client.responses.create(
                            model="gpt-6-luna",
                            input=ask_prompt
                        )

                        answer = (
                            response.output_text
                        )

                        st.markdown(
                            '<div class="section-title">Answer</div>',
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"""
                            <div class="question-box">
                                {question}
                            </div>
                            <br>
                            <div class="answer-box">
                                {answer.replace(chr(10), "<br>")}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    except Exception as e:

                        st.error(
                            f"Unable to answer from the records: {e}"
                        )

        st.caption(
            "Answers are based on the information stored in your uploaded reports and are not medical advice."
        )


# =========================================================
# COMPARE REPORTS
# =========================================================

elif page == "compare":

    st.markdown(
        '<div class="page-title">Compare Reports</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Compare two saved reports side by side.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    if len(reports) < 2:

        st.info(
            "Upload at least two reports to compare them."
        )

    else:

        report_labels = {}

        for report in reports:

            label = (
                f"{report[3]} — "
                f"{report[4]}"
            )

            report_labels[label] = report

        labels = list(
            report_labels.keys()
        )

        col1, col2 = st.columns(2)

        with col1:

            first_label = st.selectbox(
                "Earlier report",
                labels,
                index=min(1, len(labels) - 1)
            )

        with col2:

            second_label = st.selectbox(
                "Later report",
                labels,
                index=0
            )

        if first_label == second_label:

            st.warning(
                "Please select two different reports."
            )

        else:

            first_report = report_labels[
                first_label
            ]

            second_report = report_labels[
                second_label
            ]

            first_data = load_report_data(
                first_report
            )

            second_data = load_report_data(
                second_report
            )

            first_labs = {
                lab.get("test"): lab
                for lab in first_data.get(
                    "lab_results",
                    []
                )
            }

            second_labs = {
                lab.get("test"): lab
                for lab in second_data.get(
                    "lab_results",
                    []
                )
            }

            common_tests = sorted(
                set(first_labs.keys())
                &
                set(second_labs.keys())
            )

            if not common_tests:

                st.info(
                    "There are no common numeric tests between these reports."
                )

            else:

                comparison_rows = []

                for test in common_tests:

                    old = first_labs[test]
                    new = second_labs[test]

                    old_value = get_numeric_value(
                        old.get("value", "")
                    )

                    new_value = get_numeric_value(
                        new.get("value", "")
                    )

                    change = None

                    if (
                        old_value is not None
                        and new_value is not None
                    ):

                        change = (
                            new_value
                            - old_value
                        )

                    comparison_rows.append({
                        "Test": test,
                        "Earlier": old.get(
                            "value",
                            ""
                        ),
                        "Later": new.get(
                            "value",
                            ""
                        ),
                        "Change": (
                            round(change, 2)
                            if change is not None
                            else "—"
                        ),
                        "Unit": new.get(
                            "unit",
                            ""
                        )
                    })

                st.markdown(
                    '<div class="section-title">Report comparison</div>',
                    unsafe_allow_html=True
                )

                st.dataframe(
                    pd.DataFrame(
                        comparison_rows
                    ),
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Change represents the numerical difference between the two reports. It does not automatically mean improvement or deterioration."
                )


# =========================================================
# HEALTH DATA
# =========================================================

elif page == "data":

    st.markdown(
        '<div class="page-title">Health Data</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">Structured health information prepared in a FHIR-style format.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    if not reports:

        st.info(
            "Upload a report to generate structured health data."
        )

    else:

        st.markdown(
            """
            <div class="content-card">
                <div class="card-heading">
                    Interoperable health data
                </div>
                <div class="card-description">
                    This prototype organizes patient, observation and medication information using a FHIR-style structure.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        report_labels = {}

        for report in reports:

            report_labels[
                f"{report[3]} — {report[4]}"
            ] = report

        selected_label = st.selectbox(
            "Select a report",
            list(report_labels.keys())
        )

        selected_report = report_labels[
            selected_label
        ]

        selected_data = load_report_data(
            selected_report
        )

        fhir_bundle = create_fhir_bundle(
            selected_data
        )

        st.download_button(
            "Download selected FHIR-style JSON",
            data=json.dumps(
                fhir_bundle,
                indent=2
            ),
            file_name="healthcopilot_fhir.json",
            mime="application/json",
            use_container_width=True
        )

        with st.expander(
            "Preview structured data"
        ):

            st.json(
                fhir_bundle
            )

        complete_history = (
            create_complete_fhir_history(
                reports
            )
        )

        st.markdown(
            '<div class="section-title">Complete history</div>',
            unsafe_allow_html=True
        )

        st.download_button(
            "Download complete health history",
            data=json.dumps(
                complete_history,
                indent=2
            ),
            file_name="healthcopilot_complete_history.json",
            mime="application/json",
            use_container_width=True
        )

        st.caption(
            "This is a prototype FHIR-style representation and is not an official ABDM integration."
        )


# =========================================================
# SAVED REPORTS
# =========================================================

elif page == "saved":

    st.markdown(
        '<div class="page-title">Saved Reports</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-subtitle">All reports stored in your Health Copilot history.</div>',
        unsafe_allow_html=True
    )

    reports = get_previous_reports()

    if not reports:

        st.info(
            "No reports have been saved yet."
        )

    else:

        st.markdown(
            f"""
            <div class="content-card">
                <div class="card-heading">
                    {len(reports)} saved report(s)
                </div>
                <div class="card-description">
                    Your extracted health information is stored locally in the application database.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        for report in reports:

            data = load_report_data(
                report
            )

            patient = data.get(
                "patient",
                {}
            )

            labs = data.get(
                "lab_results",
                []
            )

            medicines = data.get(
                "medicines",
                []
            )

            with st.expander(
                f"{report[3]} — {report[4]}"
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**Patient:** {patient.get('name', report[1])}"
                    )

                with col2:

                    st.write(
                        f"**Patient ID:** {patient.get('patient_id', report[2])}"
                    )

                with col3:

                    st.write(
                        f"**Tests:** {len(labs)}"
                    )

                if labs:

                    rows = []

                    for lab in labs:

                        rows.append({
                            "Test": lab.get(
                                "test",
                                ""
                            ),
                            "Value": lab.get(
                                "value",
                                ""
                            ),
                            "Unit": lab.get(
                                "unit",
                                ""
                            ),
                            "Status": lab.get(
                                "status",
                                "Unknown"
                            )
                        })

                    st.dataframe(
                        pd.DataFrame(rows),
                        use_container_width=True,
                        hide_index=True
                    )

                if medicines:

                    st.write(
                        "**Medicines mentioned:**"
                    )

                    for medicine in medicines:

                        st.write(
                            f"- {medicine.get('name', 'Not provided')} — "
                            f"{medicine.get('dosage', 'Not provided')} — "
                            f"{medicine.get('frequency', 'Not provided')}"
                        )

    st.caption(
        "Reports are stored locally by this prototype. Use synthetic/demo records during presentations."
    )


# =========================================================
# FINAL SAFETY NOTE
# =========================================================

st.markdown(
    """
    <div style="
        margin-top:35px;
        padding:13px 16px;
        background:#f8fafc;
        border:1px solid #e2e8f0;
        border-radius:10px;
        color:#64748b;
        font-size:11px;
        line-height:1.5;
    ">
        Health Copilot is an informational tool for organizing and understanding
        health records. It does not diagnose medical conditions or provide
        treatment instructions. Always consult a qualified healthcare professional
        for medical decisions.
    </div>
    """,
    unsafe_allow_html=True
)