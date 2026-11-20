import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import hashlib
from datetime import datetime, date, timedelta
import os
import urllib.request
import json

try:
    from fpdf import FPDF
    import arabic_reshaper
    from bidi.algorithm import get_display
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

# =========================================================================
# إعدادات الصفحة والتنسيق العام (هوية بصرية موحدة مريحة للعين وعالية الوضوح)
# =========================================================================
st.set_page_config(
    page_title="معامل أ.د/ أسامة عبدالمتعال",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

html, body, .stApp, [data-testid="stMain"], .main .block-container {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl !important;
    text-align: right !important;
    background: linear-gradient(160deg, #f1f5f9 0%, #e0f2fe 50%, #f8fafc 100%) !important;
    color: #0f172a !important;
}

[data-testid="stDataFrame"], [data-testid="stDataFrame"] > div {
    direction: rtl !important;
    text-align: right !important;
}

p, span, label, h1, h2, h3, h4, h5, h6, div[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"], [data-testid="stAlert"], .stSelectbox, .stMultiSelect, .stTextInput, .stNumberInput, .stDateInput {
    direction: rtl !important;
    text-align: right !important;
}

[data-testid="stWidgetLabel"] p {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 16px !important;
}

.page-header-banner {
    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
    border: 1.5px solid #bae6fd;
    border-right: 7px solid #0e4d92;
    border-left: 7px solid #0284c7;
    border-radius: 18px;
    padding: 16px 24px;
    margin-bottom: 22px;
    box-shadow: 0 6px 20px rgba(14, 77, 146, 0.08);
    text-align: center !important;
}
.page-header-banner h1 {
    text-align: center !important;
    color: #0e4d92 !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* الجدول الموحد النظيف مع دعم تلوين الصف بالكامل */
.unified-tbl {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 6px;
    direction: rtl !important;
    text-align: center !important;
    margin-bottom: 12px;
}
.unified-tbl thead th {
    background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%);
    color: #ffffff;
    font-size: 15px;
    font-weight: 800;
    padding: 11px 8px;
    text-align: center !important;
    border: none;
}
.unified-tbl thead th:first-child {
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
.unified-tbl thead th:last-child {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}
.unified-tbl tbody td {
    background-color: #ffffff;
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
    padding: 11px 8px;
    text-align: center !important;
    border-top: 1px solid #cbd5e1;
    border-bottom: 1px solid #cbd5e1;
    vertical-align: middle;
}
.unified-tbl tbody td:first-child {
    border-right: 1px solid #cbd5e1;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
.unified-tbl tbody td:last-child {
    border-left: 1px solid #cbd5e1;
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}
.unified-tbl tbody tr:hover td {
    filter: brightness(0.98);
}

/* خلايا الصفوف التفاعلية */
.tbl-hdr-cell {
    background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%);
    color: #ffffff;
    font-size: 15px;
    font-weight: 800;
    padding: 10px 6px;
    border-radius: 8px;
    text-align: center !important;
    margin-bottom: 6px;
}
.tbl-row-cell {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 6px;
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    text-align: center !important;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 6px;
    word-break: break-word;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    direction: rtl !important;
    background-color: #ffffff;
    padding: 8px;
    border-radius: 14px;
    border: 1.5px solid #cbd5e1;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}
.stTabs [data-baseweb="tab"] {
    background-color: #f1f5f9;
    color: #1e293b;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 16px;
    border: 1px solid transparent;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 10px rgba(14, 77, 146, 0.2);
}

[data-testid="stForm"], [data-testid="stExpander"], div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05) !important;
}

[data-baseweb="input"], [data-baseweb="select"] > div {
    background-color: #f8fafc !important;
    border: 1.5px solid #94a3b8 !important;
    border-radius: 10px !important;
    color: #0f172a !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within {
    border-color: #0284c7 !important;
    background-color: #ffffff !important;
    box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
}

.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stDownloadButton"] > button[kind="primary"] {
    background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 10px 16px !important;
    box-shadow: 0 3px 10px rgba(14, 77, 146, 0.2) !important;
}
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover,
[data-testid="stDownloadButton"] > button[kind="primary"]:hover {
    background: linear-gradient(90deg, #0b3d75 0%, #0369a1 100%) !important;
    transform: translateY(-1px);
}

[data-testid="stDownloadButton"] > button[kind="secondary"] {
    background: linear-gradient(90deg, #b91c1c 0%, #dc2626 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    padding: 10px 16px !important;
    box-shadow: 0 3px 10px rgba(185, 28, 28, 0.22) !important;
}
[data-testid="stDownloadButton"] > button[kind="secondary"]:hover {
    background: linear-gradient(90deg, #991b1b 0%, #b91c1c 100%) !important;
    transform: translateY(-1px);
}

.kpi-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 20px 16px;
    text-align: center !important;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
    border: 1.5px solid #cbd5e1;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    margin-bottom: 10px;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(14, 77, 146, 0.14);
}
.kpi-title {
    font-size: 16px;
    font-weight: 700;
    color: #334155;
    margin-bottom: 8px;
    text-align: center !important;
}
.kpi-value {
    font-size: 28px;
    font-weight: 800;
    text-align: center !important;
}
.section-center-title {
    text-align: center !important;
    color: #0e4d92 !important;
    font-weight: 800 !important;
    margin: 12px 0 16px 0 !important;
    background: #ffffff;
    padding: 10px;
    border-radius: 12px;
    border: 1px solid #bae6fd;
}

/* =====================================================================
   تنسيق القائمة الجانبية الاحترافي (كروت تنقل عريضة وخط كبير)
   ===================================================================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #e0f2fe 100%) !important;
    border-left: 2px solid #93c5fd !important;
    direction: rtl !important;
    text-align: right !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 10px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin: 0 !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04) !important;
    cursor: pointer !important;
    justify-content: flex-start !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    border-color: #0284c7 !important;
    background-color: #f0f9ff !important;
    transform: translateX(-3px);
}
[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    line-height: 1.4 !important;
    text-align: right !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%) !important;
    border-color: #0e4d92 !important;
    box-shadow: 0 4px 12px rgba(14, 77, 146, 0.25) !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}
[data-testid="stSidebar"] button {
    background-color: #fee2e2 !important;
    color: #b91c1c !important;
    border: 1.5px solid #fca5a5 !important;
    border-radius: 12px !important;
    font-size: 17px !important;
    font-weight: 700 !important;
    padding: 10px !important;
}
[data-testid="stSidebar"] button:hover {
    background-color: #dc2626 !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

def render_page_header(title_text: str):
    st.markdown(f'<div class="page-header-banner"><h1>{title_text}</h1></div>', unsafe_allow_html=True)

def render_styled_table(headers: list, rows_data: list, row_bg_colors: list = None):
    if not rows_data:
        return

    ths = "".join([f"<th>{str(h) if h is not None else ''}</th>" for h in headers])
    trs_list = []
    for r_idx, r_item in enumerate(rows_data):
        bg_color = row_bg_colors[r_idx] if (row_bg_colors and r_idx < len(row_bg_colors) and row_bg_colors[r_idx]) else "#ffffff"
        tds_list = []
        for cell_val in r_item:
            if isinstance(cell_val, tuple):
                raw_txt = cell_val[0]
                style_str = cell_val[1] if len(cell_val) > 1 and cell_val[1] else ""
            else:
                raw_txt = cell_val
                style_str = ""
            safe_txt = str(raw_txt) if raw_txt is not None else ""
            tds_list.append(f'<td style="background-color:{bg_color}; {style_str}">{safe_txt}</td>')
        trs_list.append("<tr>" + "".join(tds_list) + "</tr>")

    html_table = f'<table class="unified-tbl"><thead><tr>{ths}</tr></thead><tbody>{"".join(trs_list)}</tbody></table>'
    st.markdown(html_table, unsafe_allow_html=True)

def df_to_styled_table(df: pd.DataFrame):
    if df is None or df.empty:
        return
    headers = [str(c) for c in df.columns]
    rows_data = []
    for _, row in df.iterrows():
        rows_data.append(["" if pd.isna(row[c]) else str(row[c]) for c in df.columns])
    render_styled_table(headers, rows_data)

# =========================================================================
# دالة توليد ملف PDF عام للتقارير والطلبيات
# =========================================================================
@st.cache_resource
def get_arabic_font_path():
    font_path = "/tmp/Amiri-Regular.ttf"
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf"
            urllib.request.urlretrieve(url, font_path)
        except Exception:
            return None
    return font_path if os.path.exists(font_path) else None

def ar_text(text: str) -> str:
    if PDF_AVAILABLE:
        try:
            reshaped = arabic_reshaper.reshape(str(text))
            return get_display(reshaped)
        except Exception:
            return str(text)
    return str(text)

def _ascii_safe(text: str) -> str:
    return str(text).encode("latin1", errors="replace").decode("latin1")

def generate_pdf_report(df_rep: pd.DataFrame, report_title: str, subtitle_info: str = "") -> bytes:
    if df_rep is None or df_rep.empty:
        return b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<< /Root 1 0 R >>\n%%EOF"

    if not PDF_AVAILABLE:
        txt_payload = f"{report_title}\n{subtitle_info}\n\n" + df_rep.to_string(index=False)
        return _ascii_safe(txt_payload).encode("latin1", errors="replace")

    font_path = get_arabic_font_path()
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    use_ar_font = bool(font_path)
    if use_ar_font:
        try:
            pdf.add_font("Amiri", "", font_path, uni=True)
            pdf.set_font("Amiri", size=16)
        except Exception:
            use_ar_font = False
            pdf.set_font("Helvetica", size=14)
    else:
        pdf.set_font("Helvetica", size=14)

    pdf.set_text_color(14, 77, 146)
    header_line = f"معامل أ.د/ أسامة عبدالمتعال - {report_title}" if use_ar_font else _ascii_safe(f"Lab ERP - {report_title}")
    pdf.cell(0, 11, ar_text(header_line) if use_ar_font else header_line, ln=True, align="C")

    if use_ar_font:
        pdf.set_font("Amiri", size=11)
    else:
        pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(51, 65, 85)
    sub_line = subtitle_info if subtitle_info else f"تاريخ الطباعة: {date.today()}"
    if not use_ar_font:
        sub_line = _ascii_safe(f"Date: {date.today()}")
    pdf.cell(0, 8, ar_text(sub_line) if use_ar_font else sub_line, ln=True, align="C")
    pdf.ln(4)

    cols = list(df_rep.columns)[::-1]
    col_w = 270.0 / max(len(cols), 1)

    pdf.set_fill_color(14, 77, 146)
    pdf.set_text_color(255, 255, 255)
    for col_name in cols:
        c_lbl = ar_text(col_name) if use_ar_font else _ascii_safe(f"Col_{len(cols)}")
        pdf.cell(col_w, 10, c_lbl, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_text_color(15, 23, 42)
    for row_idx, row in df_rep.iterrows():
        fill_row = (row_idx % 2 == 1)
        pdf.set_fill_color(241, 245, 249) if fill_row else pdf.set_fill_color(255, 255, 255)
        for col_name in cols:
            val = row[col_name]
            val_str = f"{val:,.2f}" if isinstance(val, float) else (f"{val:,}" if isinstance(val, int) else str(val))
            cell_lbl = ar_text(val_str) if use_ar_font else _ascii_safe(val_str)
            pdf.cell(col_w, 10, cell_lbl, border=1, align="C", fill=True)
        pdf.ln()

    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return str(out).encode("latin1", errors="replace")

def render_export_buttons(df_export: pd.DataFrame, base_filename: str, report_title: str, subtitle_info: str = "", key_prefix: str = "exp"):
    if df_export is None or df_export.empty:
        return
    st.markdown("<br>", unsafe_allow_html=True)
    csv_bytes = df_export.to_csv(index=False).encode("utf-8-sig")
    pdf_bytes = generate_pdf_report(df_export, report_title, subtitle_info)

    c_ex, c_pdf = st.columns(2)
    with c_ex:
        st.download_button(
            "📥 تحميل التقرير (Excel / CSV)",
            data=csv_bytes,
            file_name=f"{base_filename}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
            key=f"{key_prefix}_csv"
        )
    with c_pdf:
        st.download_button(
            "📄 تحميل التقرير (PDF)",
            data=pdf_bytes,
            file_name=f"{base_filename}.pdf",
            mime="application/pdf",
            type="secondary",
            use_container_width=True,
            key=f"{key_prefix}_pdf"
        )

# =========================================================================
# الاتصال بقاعدة البيانات السحابية Supabase
# =========================================================================
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("⚠️ لم يتم ضبط مفاتيح الاتصال بقاعدة البيانات (Secrets) بعد.")
    st.stop()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================================
# نظام تسجيل الدخول
# =========================================================================
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("""
    <style>
        .stApp {
            background: radial-gradient(circle at top right, #bae6fd 0%, #f0f9ff 45%, #e0e7ff 100%) !important;
        }
        .login-header-box {
            max-width: 410px !important;
            margin: 20px auto 16px auto !important;
            text-align: center !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        .login-header-title {
            text-align: center !important;
            width: 100% !important;
            background: linear-gradient(90deg, #0e4d92, #0284c7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 32px !important;
            font-weight: 800 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="stForm"] {
            max-width: 410px !important;
            margin: 0 auto !important;
            background: rgba(255, 255, 255, 0.98) !important;
            border: 1.5px solid #bae6fd !important;
            border-top: 6px solid #0e4d92 !important;
            border-radius: 24px !important;
            padding: 32px 28px !important;
            box-shadow: 0 20px 40px rgba(14, 77, 146, 0.14) !important;
        }
        [data-testid="stForm"] [data-testid="stWidgetLabel"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            text-align: center !important;
        }
        [data-testid="stForm"] [data-testid="stWidgetLabel"] p {
            text-align: center !important;
            width: 100% !important;
            font-size: 19px !important;
            font-weight: 800 !important;
            color: #0e4d92 !important;
            margin-bottom: 6px !important;
        }
        [data-testid="stForm"] [data-baseweb="input"] {
            background-color: #f0f9ff !important;
            border: 1.5px solid #7dd3fc !important;
            border-radius: 14px !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stForm"] [data-baseweb="input"]:focus-within {
            border-color: #0284c7 !important;
            box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2) !important;
            background-color: #ffffff !important;
        }
        [data-testid="stForm"] input {
            text-align: center !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            padding: 10px !important;
            color: #0f172a !important;
        }
        [data-testid="stForm"] [data-testid="InputInstructions"] {
            display: none !important;
        }
        [data-testid="stForm"] button[kind="secondaryFormSubmit"],
        [data-testid="stForm"] button {
            background: linear-gradient(135deg, #0e4d92 0%, #0284c7 50%, #06b6d4 100%) !important;
            color: #ffffff !important;
            font-size: 20px !important;
            font-weight: 800 !important;
            border-radius: 14px !important;
            padding: 11px 0 !important;
            border: none !important;
            margin-top: 12px !important;
            box-shadow: 0 8px 20px rgba(2, 132, 199, 0.3) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        [data-testid="stForm"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 24px rgba(14, 77, 146, 0.38) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-header-box"><div class="login-header-title">🧬 معامل أ.د/ أسامة عبدالمتعال</div></div>', unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submit = st.form_submit_button("تسجيل الدخول", use_container_width=True)
        if submit:
            res = supabase.table("users").select("*, locations(name, location_type)").eq("username", username.strip()).eq("is_active", True).execute()
            if res.data and res.data[0]["password_hash"] == hash_password(password):
                st.session_state.user = res.data[0]
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة، أو الحساب موقوف.")
    st.stop()

user = st.session_state.user
role = user["role"]
user_loc_id = user["location_id"]
user_loc_name = user["locations"]["name"] if user.get("locations") else "غير محدد"

# =========================================================================
# القائمة الجانبية + تغيير كلمة المرور للموظف + الصلاحيات المخصصة
# =========================================================================
ROLE_LABELS = {
    "chairman": "رئيس مجلس الإدارة",
    "general_manager": "المدير العام",
    "main_storekeeper": "أمين المخزن الرئيسي",
    "unit_supervisor": "مشرف وحدة / فرع"
}

def get_default_pages_for_role(r_name: str, badge_txt: str = "") -> list:
    if r_name == "main_storekeeper":
        return [
            "🏢 المخزن الرئيسي",
            "🛒 الطلبيات",
            "📥 إضافة فاتورة",
            f"📦 أذونات الصرف المعتمدة{badge_txt}",
            "🔮 التنبؤ بكفاية المخزون الرئيسي",
            "📉 شاشة الهدر",
            "⚙️ التكويد"
        ]
    elif r_name in ["chairman", "general_manager"]:
        return [
            "📊 الرئيسية",
            "⏳ تنبيهات تاريخ الصلاحية",
            "🔮 التنبؤ بكفاية المخزون الرئيسي",
            "📉 شاشة الهدر",
            "🏢 المخزن الرئيسي",
            "🛒 الطلبيات",
            "🧪 المخازن الفرعية",
            "📥 إضافة فاتورة",
            "🔄 أذونات الصرف",
            "✍️ الموافقات",
            "📈 التقارير",
            "⚙️ التكويد",
            "👥 إدارة المستخدمين والصلاحيات"
        ]
    else:
        return [
            "🧪 المخازن الفرعية",
            "⏳ تنبيهات تاريخ الصلاحية",
            "🔮 التنبؤ بكفاية المخزون الرئيسي",
            "📉 شاشة الهدر",
            "🔄 أذونات الصرف"
        ]

ALL_SYSTEM_PAGES = [
    "📊 الرئيسية",
    "⏳ تنبيهات تاريخ الصلاحية",
    "🔮 التنبؤ بكفاية المخزون الرئيسي",
    "📉 شاشة الهدر",
    "🏢 المخزن الرئيسي",
    "🛒 الطلبيات",
    "🧪 المخازن الفرعية",
    "📥 إضافة فاتورة",
    "🔄 أذونات الصرف",
    "📦 أذونات الصرف المعتمدة",
    "✍️ الموافقات",
    "📈 التقارير",
    "⚙️ التكويد",
    "👥 إدارة المستخدمين والصلاحيات"
]

def parse_custom_pages(raw_val) -> list:
    if not raw_val:
        return []
    if isinstance(raw_val, list):
        return [str(x) for x in raw_val if x]
    try:
        parsed = json.loads(raw_val)
        if isinstance(parsed, list):
            return [str(x) for x in parsed if x]
    except Exception:
        pass
    return [p.strip() for p in str(raw_val).split("||") if p.strip()]

if "show_change_pass" not in st.session_state:
    st.session_state.show_change_pass = False

with st.sidebar:
    st.markdown("<h2 style='text-align: center !important; color: #0e4d92; font-weight: 800; margin-bottom: 12px;'>🧬 معامل أ.د/ أسامة عبدالمتعال</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0e4d92 0%, #0284c7 100%);
                color: white;
                padding: 14px 16px;
                border-radius: 14px;
                text-align: center !important;
                font-size: 20px;
                font-weight: 700;
                box-shadow: 0 4px 10px rgba(14, 77, 146, 0.2);
                margin-bottom: 18px;'>
        👤 {user['full_name']}
    </div>
    """, unsafe_allow_html=True)
    
    approved_count_res = supabase.table("transfer_requests").select("id", count="exact").eq("status", "approved_ready_to_issue").execute()
    approved_badge = f" ({approved_count_res.count})" if (approved_count_res.count and approved_count_res.count > 0) else ""

    custom_pages = parse_custom_pages(user.get("allowed_pages"))
    if custom_pages:
        menu_options = []
        for cp in custom_pages:
            if cp == "📦 أذونات الصرف المعتمدة" and approved_badge:
                menu_options.append(f"📦 أذونات الصرف المعتمدة{approved_badge}")
            elif cp in ALL_SYSTEM_PAGES:
                menu_options.append(cp)
        if not menu_options:
            menu_options = get_default_pages_for_role(role, approved_badge)
    else:
        menu_options = get_default_pages_for_role(role, approved_badge)

    selected_page = st.radio("القائمة الرئيسية", menu_options, label_visibility="collapsed")
    st.divider()

    # زر تغيير كلمة المرور للمستخدم نفسه
    if st.button("🔑 تغيير كلمة المرور", use_container_width=True, key="toggle_ch_pass_btn"):
        st.session_state.show_change_pass = not st.session_state.show_change_pass

    if st.session_state.show_change_pass:
        with st.form("self_change_pass_form"):
            cur_p = st.text_input("كلمة المرور الحالية", type="password", key="ch_cur_p")
            new_p1 = st.text_input("كلمة المرور الجديدة", type="password", key="ch_new_p1")
            new_p2 = st.text_input("تأكيد كلمة المرور الجديدة", type="password", key="ch_new_p2")
            if st.form_submit_button("💾 حفظ كلمة المرور", type="primary", use_container_width=True):
                if hash_password(cur_p) != user.get("password_hash"):
                    st.error("❌ كلمة المرور الحالية غير صحيحة.")
                elif len(new_p1) < 4:
                    st.error("❌ كلمة المرور الجديدة يجب أن تكون 4 أحرف/أرقام على الأقل.")
                elif new_p1 != new_p2:
                    st.error("❌ كلمة المرور الجديدة وتأكيدها غير متطابقين.")
                else:
                    new_h = hash_password(new_p1)
                    supabase.table("users").update({"password_hash": new_h}).eq("id", int(user["id"])).execute()
                    st.session_state.user["password_hash"] = new_h
                    st.session_state.show_change_pass = False
                    st.success("✅ تم تغيير كلمة المرور بنجاح!")
                    st.rerun()

    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.user = None
        st.rerun()

def get_df(table_name, select_query="*"):
    res = supabase.table(table_name).select(select_query).order("id").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def format_coverage_duration(tests_qty: float, monthly_rate: float) -> str:
    if monthly_rate <= 0:
        return "غير محدد"
    months = tests_qty / monthly_rate
    days = round(months * 30)
    if months >= 1:
        return f"{months:.1f} شهر ({days} يوم)"
    return f"{days} يوم"

# =========================================================================
# 1. الرئيسية
# =========================================================================
if selected_page == "📊 الرئيسية":
    render_page_header("📊 الرئيسية")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(name, variant, category, monthly_consumption_rate), suppliers(name)), locations(name, location_type)").execute()
    cons_res = supabase.table("consumption_logs").select("*, items(name, variant), suppliers(name), locations(name)").execute()
    
    inv_data = inv_res.data or []
    cons_data = cons_res.data or []
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        all_locs = ["جميع المخازن والوحدات"] + sorted(list({r["locations"]["name"] for r in inv_data if r.get("locations")}))
        sel_dash_loc = st.selectbox("🔍 تصفية حسب المخزن / الوحدة:", all_locs)
    with f_col2:
        period_days = st.selectbox("📅 فترة تحليل الاستهلاك:", [30, 60, 90, 180], format_func=lambda x: f"آخر {x} يوم")

    filtered_inv = [r for r in inv_data if sel_dash_loc == "جميع المخازن والوحدات" or (r.get("locations") and r["locations"]["name"] == sel_dash_loc)]
    
    total_stock_value = sum(r["tests_available"] * r["batches"]["unit_price_per_test"] for r in filtered_inv if r.get("batches"))
    
    cutoff_date = (datetime.now() - timedelta(days=period_days)).isoformat()
    recent_cons = [
        c for c in cons_data 
        if c["consumed_at"] >= cutoff_date and (sel_dash_loc == "جميع المخازن والوحدات" or (c.get("locations") and c["locations"]["name"] == sel_dash_loc))
    ]
    monthly_cost = sum(c["cost_incurred"] for c in recent_cons)
    monthly_tests = sum(c["tests_consumed"] for c in recent_cons)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card" style="border-top: 5px solid #0e4d92;"><div class="kpi-title">💰 إجمالي قيمة المخزون الحالي</div><div class="kpi-value" style="color: #0e4d92;">{total_stock_value:,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card" style="border-top: 5px solid #0284c7;"><div class="kpi-title">📉 تكلفة استهلاك آخر {period_days} يوم</div><div class="kpi-value" style="color: #0284c7;">{monthly_cost:,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card" style="border-top: 5px solid #0d9488;"><div class="kpi-title">🧪 إجمالي السحب ({period_days} يوم)</div><div class="kpi-value" style="color: #0d9488;">{monthly_tests:,.0f} اختبار/قطعة</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card" style="border-top: 5px solid #6366f1;"><div class="kpi-title">📦 عدد الأصناف النشطة</div><div class="kpi-value" style="color: #6366f1;">{len({r["batches"]["items"]["name"] for r in filtered_inv if r.get("batches") and r["batches"].get("items")})} صنف</div></div>', unsafe_allow_html=True)

    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("<h3 class='section-center-title'>🔥 أكثر الأصناف سحباً (حسب التكلفة المالية)</h3>", unsafe_allow_html=True)
        if recent_cons:
            df_c = pd.DataFrame([{
                "الصنف": c['items']['name'],
                "التكلفة": c["cost_incurred"],
                "الكمية": c["tests_consumed"]
            } for c in recent_cons])
            top_cost = df_c.groupby("الصنف")["التكلفة"].sum().reset_index().sort_values("التكلفة", ascending=False).head(10)
            fig1 = px.bar(top_cost, x="الصنف", y="التكلفة", color="التكلفة", color_continuous_scale="Blues", text_auto='.0f')
            fig1.update_layout(font_family="Cairo", title_x=0.5, paper_bgcolor="white", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("لا توجد حركات سحب مسجلة خلال هذه الفترة لعرض الرسم البياني.")

    with col_b:
        st.markdown("<h3 class='section-center-title'>🏭 توزيع قيمة المخزون حسب الشركات الموردة</h3>", unsafe_allow_html=True)
        if filtered_inv:
            df_s = pd.DataFrame([{
                "الشركة": r["batches"]["suppliers"]["name"],
                "القيمة": r["tests_available"] * r["batches"]["unit_price_per_test"]
            } for r in filtered_inv if r["tests_available"] > 0 and r.get("batches")])
            if not df_s.empty:
                sup_val = df_s.groupby("الشركة")["القيمة"].sum().reset_index()
                fig2 = px.pie(sup_val, names="الشركة", values="القيمة", hole=0.45, color_discrete_sequence=["#0e4d92", "#0284c7", "#0d9488", "#38bdf8", "#6366f1"])
                fig2.update_layout(font_family="Cairo", title_x=0.5, paper_bgcolor="white")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("المخزون الحالي فارغ.")
        else:
            st.info("لا توجد أرصدة مسجلة بعد.")

# =========================================================================
# 2. شاشة مستقلة: تنبيهات تاريخ الصلاحية
# =========================================================================
elif selected_page == "⏳ تنبيهات تاريخ الصلاحية":
    render_page_header("⏳ تنبيهات تاريخ الصلاحية")

    inv_res = supabase.table("inventory").select(
        "*, batches(*, items(id, name, category, unit_name, sub_unit_name), suppliers(name)), locations(id, name, location_type)"
    ).gt("tests_available", 0).execute()
    all_inv_rows = inv_res.data or []

    if role == "unit_supervisor" and user_loc_id != 1:
        scoped_rows = [r for r in all_inv_rows if int(r["location_id"]) == int(user_loc_id)]
        st.markdown(f"<h3 class='section-center-title'>🏥 صلاحيات مخزن: {user_loc_name}</h3>", unsafe_allow_html=True)
        ef2, ef3 = st.columns(2)
        sel_exp_loc = user_loc_name
    else:
        scoped_rows = all_inv_rows
        ef1, ef2, ef3 = st.columns(3)
        with ef1:
            exp_locs_list = ["الكل"] + sorted(list({r["locations"]["name"] for r in scoped_rows if r.get("locations")}))
            sel_exp_loc = st.selectbox("🏥 الوحدة / الفرع:", exp_locs_list, key="exp_filter_loc")

    with ef2:
        exp_items_list = ["الكل"] + sorted(list({r["batches"]["items"]["name"] for r in scoped_rows if r.get("batches") and r["batches"].get("items")}))
        sel_exp_item = st.selectbox("🧪 الصنف:", exp_items_list, key="exp_filter_item")

    with ef3:
        sel_exp_cat = st.selectbox("📂 التصنيف (محاليل / مستهلكات):", ["الكل", "محاليل وكواشف", "مستهلكات"], key="exp_filter_cat")

    st.markdown("""
    <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-radius:12px; padding:10px 16px; margin-bottom:16px; font-weight:700; font-size:15px;">
        🎨 <b>دليل ألوان الصلاحية:</b> &nbsp;
        <span style="background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:6px; border:1px solid #fca5a5;">🟥 أقل من شهر (≤ 30 يوم)</span> &nbsp;
        <span style="background:#fef9c3; color:#854d0e; padding:3px 10px; border-radius:6px; border:1px solid #fde047;">🟨 أقل من شهرين (31 - 60 يوم)</span> &nbsp;
        <span style="background:#dcfce7; color:#166534; padding:3px 10px; border-radius:6px; border:1px solid #86efac;">🟩 أقل من 3 شهور (61 - 90 يوم)</span>
    </div>
    """, unsafe_allow_html=True)

    today = date.today()
    exp_table_rows = []
    exp_row_colors = []

    for r in scoped_rows:
        if not r.get("batches") or not r["batches"].get("items"):
            continue
        b = r["batches"]
        it = b["items"]
        loc_n = r["locations"]["name"] if r.get("locations") else "غير محدد"
        cat_ar = "محاليل وكواشف" if it["category"] == "reagent" else "مستهلكات"

        if sel_exp_loc != "الكل" and loc_n != sel_exp_loc:
            continue
        if sel_exp_item != "الكل" and it["name"] != sel_exp_item:
            continue
        if sel_exp_cat != "الكل" and cat_ar != sel_exp_cat:
            continue

        exp_d = datetime.strptime(b["expiry_date"], "%Y-%m-%d").date()
        days_left = (exp_d - today).days

        if days_left <= 90:
            if days_left <= 30:
                row_bg = "#fee2e2"
                status_lbl = "أقل من شهر"
            elif days_left <= 60:
                row_bg = "#fef9c3"
                status_lbl = "أقل من شهرين"
            else:
                row_bg = "#dcfce7"
                status_lbl = "أقل من 3 شهور"

            sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
            exp_table_rows.append([
                (it["name"], "font-weight:800;"),
                cat_ar,
                b["suppliers"]["name"] if b.get("suppliers") else "-",
                loc_n,
                b["lot_number"],
                b["expiry_date"],
                (f"{days_left} يوم ({status_lbl})", "font-weight:800;"),
                f"{float(r['tests_available']):,.0f} {sub_u}"
            ])
            exp_row_colors.append(row_bg)

    if exp_table_rows:
        exp_headers = [
            "الصنف",
            "التصنيف",
            "الشركة",
            "الوحدة / الفرع",
            "رقم التشغيلة",
            "تاريخ الصلاحية",
            "الأيام المتبقية",
            "الرصيد"
        ]
        render_styled_table(exp_headers, exp_table_rows, row_bg_colors=exp_row_colors)
    else:
        st.success("✅ لا توجد تشغيلات صلاحيتها أقل من 3 شهور مطابقة للفلاتر المختارة.")

# =========================================================================
# 3. شاشة مستقلة: التنبؤ بكفاية المخزون الرئيسي / المخزن الفرعي
# =========================================================================
elif selected_page == "🔮 التنبؤ بكفاية المخزون الرئيسي":
    is_sub_only = (role == "unit_supervisor" and user_loc_id != 1)
    header_title = f"🔮 التنبؤ بكفاية مخزن ({user_loc_name})" if is_sub_only else "🔮 التنبؤ بكفاية المخزون الرئيسي"
    render_page_header(header_title)

    items_df = get_df("items")
    locs_df = get_df("locations")
    rates_df = get_df("location_consumption_rates")
    sub_locs_df = locs_df[locs_df["location_type"] != "main"] if not locs_df.empty else pd.DataFrame()

    if is_sub_only:
        tf2, tf3 = st.columns(2)
        sel_fc_loc = user_loc_name
    else:
        tf1, tf2, tf3 = st.columns(3)
        with tf1:
            fc_loc_opts = ["الكل"] + (sub_locs_df["name"].tolist() if not sub_locs_df.empty else [])
            sel_fc_loc = st.selectbox("🏥 الوحدة / الفرع:", fc_loc_opts, key="fc_filter_loc")

    with tf2:
        fc_item_opts = ["الكل"] + (sorted(items_df["name"].unique().tolist()) if not items_df.empty else [])
        sel_fc_item = st.selectbox("🧪 الصنف:", fc_item_opts, key="fc_filter_item")

    with tf3:
        sel_fc_cat = st.selectbox("📂 التصنيف (محاليل / مستهلكات):", ["الكل", "محاليل وكواشف", "مستهلكات"], key="fc_filter_cat")

    st.markdown("""
    <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-radius:12px; padding:10px 16px; margin-bottom:16px; font-weight:700; font-size:15px;">
        🎨 <b>دليل ألوان مدة الكفاية:</b> &nbsp;
        <span style="background:#fee2e2
