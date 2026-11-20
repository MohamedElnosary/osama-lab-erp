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

.stButton > button, [data-testid="stFormSubmitButton"] > button,
[data-testid="stDownloadButton"] > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 8px 18px !important;
    min-height: 40px !important;
}

.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"],
[data-testid="stDownloadButton"] > button[kind="primary"] {
    background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 3px 8px rgba(14, 77, 146, 0.18) !important;
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
    box-shadow: 0 3px 8px rgba(185, 28, 28, 0.2) !important;
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
    gap: 8px !important;
    width: 100% !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
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
    font-size: 16px !important;
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
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background-color: #fee2e2 !important;
    color: #b91c1c !important;
    border: 1.5px solid #fca5a5 !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 9px 12px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
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
# دالة توليد ملف PDF عام للتقارير والطلبيات وأذونات الصرف
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

    c_ex, c_pdf = st.columns([1, 1])
    with c_ex:
        st.download_button(
            "📥 تحميل التقرير (Excel / CSV)",
            data=csv_bytes,
            file_name=f"{base_filename}.csv",
            mime="text/csv",
            type="primary",
            key=f"{key_prefix}_csv"
        )
    with c_pdf:
        st.download_button(
            "📄 تحميل التقرير (PDF)",
            data=pdf_bytes,
            file_name=f"{base_filename}.pdf",
            mime="application/pdf",
            type="secondary",
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

def log_user_action(actor: dict, action_type: str, page_name: str, details: str, location_name: str = ""):
    """تسجيل كل أكشن يأخذه أي مستخدم في جدول audit_logs"""
    if not actor:
        return
    try:
        supabase.table("audit_logs").insert({
            "user_id": int(actor["id"]) if actor.get("id") is not None else None,
            "username": str(actor.get("username") or ""),
            "full_name": str(actor.get("full_name") or ""),
            "role": str(actor.get("role") or ""),
            "action_type": str(action_type),
            "page_name": str(page_name),
            "location_name": str(location_name),
            "details": str(details)
        }).execute()
    except Exception:
        pass

def issue_transfer_request_by_id(req_id: int, actor: dict):
    req_rows = supabase.table("transfer_requests").select("*, locations!transfer_requests_to_location_id_fkey(name), items(name, unit_name), suppliers(name), batches(lot_number)").eq("id", int(req_id)).execute().data or []
    if not req_rows:
        return False
    req = req_rows[0]
    if req.get("status") != "approved_ready_to_issue":
        return False

    m_inv_list = supabase.table("inventory").select("*").eq("location_id", 1).eq("batch_id", req["batch_id"]).execute().data or []
    if m_inv_list:
        m_inv = m_inv_list[0]
        new_m_kits = float(m_inv["kits_available"]) - float(req["kits_requested"])
        new_m_tests = float(m_inv["tests_available"]) - float(req["tests_requested"])
        supabase.table("inventory").update({
            "kits_available": max(0.0, new_m_kits),
            "tests_available": max(0.0, new_m_tests)
        }).eq("id", m_inv["id"]).execute()

    sub_inv_res = supabase.table("inventory").select("*").eq("location_id", req["to_location_id"]).eq("batch_id", req["batch_id"]).execute().data or []
    if sub_inv_res:
        s_inv = sub_inv_res[0]
        supabase.table("inventory").update({
            "kits_available": float(s_inv["kits_available"]) + float(req["kits_requested"]),
            "tests_available": float(s_inv["tests_available"]) + float(req["tests_requested"])
        }).eq("id", s_inv["id"]).execute()
    else:
        supabase.table("inventory").insert({
            "location_id": req["to_location_id"],
            "batch_id": req["batch_id"],
            "kits_available": float(req["kits_requested"]),
            "tests_available": float(req["tests_requested"])
        }).execute()

    supabase.table("transfer_requests").update({
        "status": "issued",
        "issued_by": int(actor["id"]),
        "issued_at": datetime.now().isoformat()
    }).eq("id", int(req_id)).execute()

    to_loc_n = req["locations"]["name"] if req.get("locations") else str(req["to_location_id"])
    it_n = req["items"]["name"] if req.get("items") else str(req["item_id"])
    u_n = req["items"]["unit_name"] if req.get("items") else "علبة"
    lot_n = req["batches"]["lot_number"] if req.get("batches") else "-"
    log_user_action(
        actor,
        "تنفيذ صرف إذن",
        "أذونات الصرف المعتمدة",
        f"صرف {req['kits_requested']} {u_n} ({req['tests_requested']} اختبار/قطعة) من صنف ({it_n}) تشغيلة ({lot_n}) إلى ({to_loc_n})",
        to_loc_n
    )
    return True

def render_approved_requests_storekeeper_view(key_prefix: str = "sk_app"):
    approved_res = supabase.table("transfer_requests").select(
        "*, locations!transfer_requests_to_location_id_fkey(name), items(name, variant, unit_name, sub_unit_name), suppliers(name), batches(lot_number, expiry_date, tests_per_kit)"
    ).eq("status", "approved_ready_to_issue").execute()
    all_approved = approved_res.data or []

    if not all_approved:
        st.info("✅ لا توجد أذونات صرف معتمدة من المدير العام بانتظار الصرف حالياً.")
        return

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        loc_opts = ["الكل"] + sorted(list({r["locations"]["name"] for r in all_approved if r.get("locations")}))
        sel_loc = st.selectbox("🏥 تصفية حسب الوحدة / الفرع:", loc_opts, key=f"{key_prefix}_loc_flt")
    with f_col2:
        loc_sub_list = [r for r in all_approved if sel_loc == "الكل" or (r.get("locations") and r["locations"]["name"] == sel_loc)]
        item_opts = ["الكل"] + sorted(list({r["items"]["name"] for r in loc_sub_list if r.get("items")}))
        sel_item = st.selectbox("🧪 تصفية حسب الصنف:", item_opts, key=f"{key_prefix}_item_flt")

    filtered_approved = [
        r for r in loc_sub_list
        if sel_item == "الكل" or (r.get("items") and r["items"]["name"] == sel_item)
    ]

    if not filtered_approved:
        st.warning("لا توجد طلبات مطابقة للفلاتر المختارة.")
        return

    export_rows = []
    for req in filtered_approved:
        sub_u = "اختبار" if req["items"].get("sub_unit_name") == "تست" else (req["items"].get("sub_unit_name") or "اختبار")
        export_rows.append({
            "الوحدة / الفرع": req["locations"]["name"],
            "الصنف": req["items"]["name"],
            "الشركة": req["suppliers"]["name"],
            "الكمية المعتمدة": f"{req['kits_requested']} {req['items']['unit_name']} ({req['tests_requested']} {sub_u})",
            "رقم التشغيلة": req["batches"]["lot_number"],
            "الصلاحية": req["batches"]["expiry_date"]
        })
    df_app_export = pd.DataFrame(export_rows)

    st.markdown("<br>", unsafe_allow_html=True)
    dl_c1, dl_c2 = st.columns([1, 1])
    with dl_c1:
        st.download_button(
            "📄 طباعة / تحميل أذونات الصرف المفلترة (PDF)",
            data=generate_pdf_report(
                df_app_export,
                "أذونات الصرف المعتمدة للطباعة",
                f"الجهة: {sel_loc} | الصنف: {sel_item} | التاريخ: {date.today()}"
            ),
            file_name=f"approved_transfers_{sel_loc}_{sel_item}_{date.today()}.pdf",
            mime="application/pdf",
            type="secondary",
            key=f"{key_prefix}_pdf_btn"
        )
    with dl_c2:
        st.download_button(
            "📥 تحميل أذونات الصرف المفلترة (Excel / CSV)",
            data=df_app_export.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"approved_transfers_{sel_loc}_{sel_item}_{date.today()}.csv",
            mime="text/csv",
            type="primary",
            key=f"{key_prefix}_csv_btn"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    app_widths = [1.5, 1.3, 1.1, 1.5, 1.1, 1.1, 1.4]
    app_headers = ["صرف إلى", "الصنف", "الشركة", "الكمية المعتمدة", "رقم التشغيلة", "الصلاحية", "تنفيذ الصرف"]
    a_hdr_cols = st.columns(app_widths)
    for idx, h_t in enumerate(app_headers):
        with a_hdr_cols[idx]:
            st.markdown(f"<div class='tbl-hdr-cell'>{h_t}</div>", unsafe_allow_html=True)

    for req in filtered_approved:
        sub_u = "اختبار" if req["items"].get("sub_unit_name") == "تست" else (req["items"].get("sub_unit_name") or "اختبار")
        qty_disp = f"{req['kits_requested']} {req['items']['unit_name']} ({req['tests_requested']} {sub_u})"

        r_cols = st.columns(app_widths)
        with r_cols[0]:
            st.markdown(f"<div class='tbl-row-cell' style='color:#0e4d92;'>{req['locations']['name']}</div>", unsafe_allow_html=True)
        with r_cols[1]:
            st.markdown(f"<div class='tbl-row-cell'>{req['items']['name']}</div>", unsafe_allow_html=True)
        with r_cols[2]:
            st.markdown(f"<div class='tbl-row-cell'>{req['suppliers']['name']}</div>", unsafe_allow_html=True)
        with r_cols[3]:
            st.markdown(f"<div class='tbl-row-cell' style='color:#0284c7;'>{qty_disp}</div>", unsafe_allow_html=True)
        with r_cols[4]:
            st.markdown(f"<div class='tbl-row-cell' dir='ltr'>{req['batches']['lot_number']}</div>", unsafe_allow_html=True)
        with r_cols[5]:
            st.markdown(f"<div class='tbl-row-cell' dir='ltr'>{req['batches']['expiry_date']}</div>", unsafe_allow_html=True)
        with r_cols[6]:
            if st.button("✅ موافقة وصرف", key=f"{key_prefix}_iss_{req['id']}", type="primary"):
                if issue_transfer_request_by_id(int(req["id"]), user):
                    st.success("🎉 تم الصرف وخصم الكمية من المخزن الرئيسي وترحيلها بنجاح!")
                    st.rerun()

    if len(filtered_approved) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"✅ موافقة وصرف All ({len(filtered_approved)} طلب مفلتر)", type="primary", key=f"{key_prefix}_iss_all"):
            for req in filtered_approved:
                issue_transfer_request_by_id(int(req["id"]), user)
            st.success(f"🎉 تم تنفيذ وصرف {len(filtered_approved)} طلب بنجاح!")
            st.rerun()

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
                log_user_action(
                    res.data[0],
                    "تسجيل دخول",
                    "تسجيل الدخول",
                    f"دخول المستخدم ({res.data[0]['username']}) إلى النظام",
                    res.data[0]["locations"]["name"] if res.data[0].get("locations") else ""
                )
                st.rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة، أو الحساب موقوف.")
    st.stop()

user = st.session_state.user
role = user["role"]
user_loc_id = user["location_id"]
user_loc_name = user["locations"]["name"] if user.get("locations") else "غير محدد"

# =========================================================================
# القائمة الجانبية + عداد الموافقات للمدير العام + تغيير كلمة المرور
# =========================================================================
ROLE_LABELS = {
    "chairman": "رئيس مجلس الإدارة",
    "general_manager": "المدير العام",
    "main_storekeeper": "أمين المخزن الرئيسي",
    "unit_supervisor": "مشرف وحدة / فرع",
    "employee": "موظف"
}

def get_default_pages_for_role(r_name: str, store_badge_txt: str = "", gm_badge_txt: str = "") -> list:
    if r_name == "main_storekeeper":
        return [
            "🏢 المخزن الرئيسي",
            "↳ ⏳ تنبيهات تاريخ الصلاحية",
            "↳ 🔮 التنبؤ بكفاية المخزون الرئيسي",
            "↳ 🛒 الطلبيات",
            "↳ 📥 إضافة فاتورة",
            f"📦 أذونات الصرف المعتمدة{store_badge_txt}",
            "⚙️ التكويد",
            "📉 حساب الهدر"
        ]
    elif r_name in ["chairman", "general_manager"]:
        return [
            "📊 الرئيسية",
            "🏢 المخزن الرئيسي",
            "↳ ⏳ تنبيهات تاريخ الصلاحية",
            "↳ 🔮 التنبؤ بكفاية المخزون الرئيسي",
            "↳ 🛒 الطلبيات",
            "↳ 📥 إضافة فاتورة",
            "🧪 المخازن الفرعية",
            "🔄 أذونات الصرف",
            f"✍️ الموافقات{gm_badge_txt}",
            "📈 التقارير",
            "⚙️ التكويد",
            "📉 حساب الهدر",
            "👥 إدارة المستخدمين والصلاحيات"
        ]
    elif r_name == "employee":
        return [
            "🧪 المخازن الفرعية"
        ]
    else:
        return [
            "🧪 المخازن الفرعية",
            "↳ ⏳ تنبيهات تاريخ الصلاحية",
            "↳ 🔮 التنبؤ بكفاية المخزون الرئيسي",
            "🔄 أذونات الصرف",
            "📉 حساب الهدر"
        ]

ALL_SYSTEM_PAGES = [
    "📊 الرئيسية",
    "🏢 المخزن الرئيسي",
    "↳ ⏳ تنبيهات تاريخ الصلاحية",
    "↳ 🔮 التنبؤ بكفاية المخزون الرئيسي",
    "↳ 🛒 الطلبيات",
    "↳ 📥 إضافة فاتورة",
    "🧪 المخازن الفرعية",
    "🔄 أذونات الصرف",
    "📦 أذونات الصرف المعتمدة",
    "✍️ الموافقات",
    "📈 التقارير",
    "⚙️ التكويد",
    "📉 حساب الهدر",
    "👥 إدارة المستخدمين والصلاحيات"
]

def normalize_page_key(p_str: str) -> str:
    clean = str(p_str).strip()
    if clean.startswith("📦 أذونات الصرف المعتمدة"):
        return "📦 أذونات الصرف المعتمدة"
    if clean.startswith("✍️ الموافقات"):
        return "✍️ الموافقات"
    if clean in ["⏳ تنبيهات تاريخ الصلاحية", "🔮 التنبؤ بكفاية المخزون الرئيسي", "🛒 الطلبيات", "📥 إضافة فاتورة"]:
        return f"↳ {clean}"
    if clean == "📉 شاشة الهدر":
        return "📉 حساب الهدر"
    return clean

def parse_custom_pages(raw_val) -> list:
    if not raw_val:
        return []
    if isinstance(raw_val, list):
        return [normalize_page_key(x) for x in raw_val if x]
    try:
        parsed = json.loads(raw_val)
        if isinstance(parsed, list):
            return [normalize_page_key(x) for x in parsed if x]
    except Exception:
        pass
    return [normalize_page_key(p.strip()) for p in str(raw_val).split("||") if p.strip()]

def get_effective_pages_for_user(u_obj: dict, store_badge_txt: str = "", gm_badge_txt: str = "") -> list:
    r_name = u_obj.get("role", "employee")
    default_list = get_default_pages_for_role(r_name, store_badge_txt, gm_badge_txt)
    custom_list = [p for p in parse_custom_pages(u_obj.get("allowed_pages")) if p in ALL_SYSTEM_PAGES]

    if not custom_list:
        return default_list

    custom_set = set(custom_list)
    result = []
    for p in default_list:
        norm_p = normalize_page_key(p)
        if norm_p in custom_set:
            result.append(p)
    for p in ALL_SYSTEM_PAGES:
        lbl = f"📦 أذونات الصرف المعتمدة{store_badge_txt}" if (p == "📦 أذونات الصرف المعتمدة" and store_badge_txt) else (
            f"✍️ الموافقات{gm_badge_txt}" if (p == "✍️ الموافقات" and gm_badge_txt) else p
        )
        if p in custom_set and lbl not in result:
            result.append(lbl)
    return result if result else default_list

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
                margin-bottom: 14px;'>
        👤 {user['full_name']}
    </div>
    """, unsafe_allow_html=True)
    
    approved_count_res = supabase.table("transfer_requests").select("id", count="exact").eq("status", "approved_ready_to_issue").execute()
    approved_badge = f" ({approved_count_res.count})" if (approved_count_res.count and approved_count_res.count > 0) else ""

    pending_gm_count_res = supabase.table("transfer_requests").select("id", count="exact").eq("status", "pending_gm").execute()
    pending_gm_badge = f" ({pending_gm_count_res.count})" if (pending_gm_count_res.count and pending_gm_count_res.count > 0) else ""

    menu_options = get_effective_pages_for_user(user, approved_badge, pending_gm_badge)

    selected_raw = st.radio("القائمة الرئيسية", menu_options, label_visibility="collapsed")
    selected_page = normalize_page_key(selected_raw)
    st.divider()

    if st.button("🔑 تغيير كلمة المرور", key="toggle_ch_pass_btn"):
        st.session_state.show_change_pass = not st.session_state.show_change_pass

    if st.session_state.show_change_pass:
        with st.container(border=True):
            cur_p = st.text_input("كلمة المرور الحالية", type="password", key="ch_cur_p")
            new_p1 = st.text_input("كلمة المرور الجديدة", type="password", key="ch_new_p1")
            new_p2 = st.text_input("تأكيد كلمة المرور الجديدة", type="password", key="ch_new_p2")
            if st.button("💾 حفظ كلمة المرور", type="primary", key="save_self_pass_btn"):
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
                    log_user_action(user, "تغيير كلمة المرور", "القائمة الجانبية", "قام المستخدم بتغيير كلمة المرور الخاصة به", user_loc_name)
                    st.success("✅ تم تغيير كلمة المرور بنجاح!")
                    st.rerun()

    if st.button("🚪 تسجيل الخروج", key="logout_btn"):
        log_user_action(user, "تسجيل خروج", "القائمة الجانبية", "قام المستخدم بتسجيل الخروج", user_loc_name)
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
# 2. شاشة: تنبيهات تاريخ الصلاحية
# =========================================================================
elif selected_page == "↳ ⏳ تنبيهات تاريخ الصلاحية":
    render_page_header("⏳ تنبيهات تاريخ الصلاحية")

    inv_res = supabase.table("inventory").select(
        "*, batches(*, items(id, name, category, unit_name, sub_unit_name), suppliers(name)), locations(id, name, location_type)"
    ).gt("tests_available", 0).execute()
    all_inv_rows = inv_res.data or []

    if role in ["unit_supervisor", "employee"] and user_loc_id != 1:
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
# 3. شاشة: التنبؤ بكفاية المخزون الرئيسي / المخزن الفرعي
# =========================================================================
elif selected_page == "↳ 🔮 التنبؤ بكفاية المخزون الرئيسي":
    is_sub_only = (role in ["unit_supervisor", "employee"] and user_loc_id != 1)
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
        <span style="background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:6px; border:1px solid #fca5a5;">🟥 تحت الشهر (&lt; 1 شهر - حرج)</span> &nbsp;
        <span style="background:#fef9c3; color:#854d0e; padding:3px 10px; border-radius:6px; border:1px solid #fde047;">🟨 تحت 3 شهور (1 إلى &lt; 3 شهور - تنبيه)</span> &nbsp;
        <span style="background:#dcfce7; color:#166534; padding:3px 10px; border-radius:6px; border:1px solid #86efac;">🟩 تحت 6 شهور (3 إلى &lt; 6 شهور)</span> &nbsp;
        <span style="background:#ffffff; color:#0f172a; padding:3px 10px; border-radius:6px; border:1px solid #94a3b8;">⬜ فوق 6 شهور (≥ 6 شهور)</span>
    </div>
    """, unsafe_allow_html=True)

    target_inv_loc_id = int(user_loc_id) if is_sub_only else 1
    inv_res = supabase.table("inventory").select("tests_available, batches(item_id)").eq("location_id", target_inv_loc_id).gt("tests_available", 0).execute()

    stock_by_item = {}
    for r in (inv_res.data or []):
        if r.get("batches"):
            iid = int(r["batches"]["item_id"])
            stock_by_item[iid] = stock_by_item.get(iid, 0.0) + float(r["tests_available"] or 0)

    fc_rows = []
    fc_colors = []

    for _, it in items_df.iterrows():
        iid = int(it["id"])
        cat_ar = "محاليل وكواشف" if it["category"] == "reagent" else "مستهلكات"

        if sel_fc_item != "الكل" and it["name"] != sel_fc_item:
            continue
        if sel_fc_cat != "الكل" and cat_ar != sel_fc_cat:
            continue

        if is_sub_only:
            if not rates_df.empty:
                m_sub = rates_df[(rates_df["location_id"] == int(user_loc_id)) & (rates_df["item_id"] == iid)]
                if m_sub.empty:
                    continue
                rate = float(m_sub.iloc[0]["monthly_tests_rate"] or 0)
            else:
                continue
        else:
            if sel_fc_loc != "الكل":
                chosen_sub_id = int(sub_locs_df[sub_locs_df["name"] == sel_fc_loc].iloc[0]["id"])
                if rates_df.empty:
                    continue
                m_loc = rates_df[(rates_df["location_id"] == chosen_sub_id) & (rates_df["item_id"] == iid)]
                if m_loc.empty:
                    continue
                rate = float(m_loc.iloc[0]["monthly_tests_rate"] or 0)
            else:
                rate = float(it["monthly_consumption_rate"] or 0)

        tot_stock = stock_by_item.get(iid, 0.0)
        if tot_stock <= 0 and rate <= 0:
            continue

        if rate > 0:
            months_left = tot_stock / rate
            months_disp = round(months_left, 1)
            if months_left < 1:
                row_bg = "#fee2e2"
                status_txt = "🔴 حرج (اطلب فوراً)"
            elif months_left < 3:
                row_bg = "#fef9c3"
                status_txt = "🟡 تنبيه (أقل من 3 شهور)"
            elif months_left < 6:
                row_bg = "#dcfce7"
                status_txt = "🟢 متوسط (أقل من 6 شهور)"
            else:
                row_bg = "#ffffff"
                status_txt = "⚪ آمن (فوق 6 شهور)"
        else:
            months_disp = "-"
            row_bg = "#ffffff"
            status_txt = "غير محدد"

        sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
        fc_rows.append([
            (it["name"], "font-weight:800;"),
            cat_ar,
            f"{tot_stock:,.0f} {sub_u}",
            f"{rate:,.0f} {sub_u}",
            (str(months_disp), "font-weight:800;"),
            (status_txt, "font-weight:800;")
        ])
        fc_colors.append(row_bg)

    if fc_rows:
        fc_headers = [
            "الصنف",
            "التصنيف",
            "الرصيد الحالي",
            "الاستهلاك الشهري",
            "يكفي لمدة (شهر)",
            "الحالة"
        ]
        render_styled_table(fc_headers, fc_rows, row_bg_colors=fc_colors)
    else:
        st.info("لا توجد بيانات مطابقة للفلاتر المختارة حالياً.")

# =========================================================================
# 4. شاشة: حساب الهدر
# =========================================================================
elif selected_page == "📉 حساب الهدر":
    render_page_header("📉 حساب الهدر")

    items_df = get_df("items")
    locs_df = get_df("locations")
    sub_locs_df = locs_df[locs_df["location_type"] != "main"] if not locs_df.empty else pd.DataFrame()

    if items_df.empty:
        st.warning("⚠️ برجاء إضافة الأصناف أولاً من صفحة '⚙️ التكويد'.")
    else:
        with st.container(border=True):
            w1, w2 = st.columns(2)
            with w1:
                w_item_name = st.selectbox("🧪 اختر الصنف (مثال: ALT):", items_df["name"].tolist(), key="w_item_sel")
                sel_w_item = items_df[items_df["name"] == w_item_name].iloc[0]
                w_item_id = int(sel_w_item["id"])
                w_sub_u = "اختبار" if sel_w_item["sub_unit_name"] == "تست" else sel_w_item["sub_unit_name"]

                if role in ["unit_supervisor", "employee"] and user_loc_id != 1:
                    w_loc_label = user_loc_name
                    w_loc_id = int(user_loc_id)
                    st.text_input("🏥 الوحدة / الفرع:", value=w_loc_label, disabled=True)
                else:
                    loc_opts = ["الكل (إجمالي المعمل)"] + (sub_locs_df["name"].tolist() if not sub_locs_df.empty else [])
                    w_loc_label = st.selectbox("🏥 الوحدة / الفرع:", loc_opts, key="w_loc_sel")
                    w_loc_id = None if w_loc_label == "الكل (إجمالي المعمل)" else int(sub_locs_df[sub_locs_df["name"] == w_loc_label].iloc[0]["id"])

                actual_tests = st.number_input(
                    f"🩺 عدد التيستات الفعلية التي خرجت للمرضى من سيستم التحاليل ({w_sub_u}):",
                    min_value=0.0,
                    step=10.0,
                    key="w_actual_tests"
                )

            with w2:
                p_col1, p_col2 = st.columns(2)
                w_from = p_col1.date_input("📅 من تاريخ:", value=date.today().replace(month=1, day=1), key="w_from_date")
                w_to = p_col2.date_input("📅 إلى تاريخ:", value=date.today(), key="w_to_date")

                allowed_pct = st.number_input(
                    "📏 الهدر المسموح به (%):",
                    min_value=0.0,
                    max_value=100.0,
                    value=0.0,
                    step=1.0,
                    key="w_allowed_pct"
                )

            w_notes = st.text_input("📝 ملاحظات / سبب الهدر (معايرة، كنترول، إعادة تحليل، إلخ - اختياري):", key="w_notes_input")

            cons_query = supabase.table("consumption_logs").select("tests_consumed, cost_incurred").eq("item_id", w_item_id).gte("consumed_at", str(w_from)).lte("consumed_at", str(w_to) + "T23:59:59")
            if w_loc_id is not None:
                cons_query = cons_query.eq("location_id", w_loc_id)
            cons_rows = cons_query.execute().data or []
            issued_qty = sum(float(c.get("tests_consumed") or 0) for c in cons_rows)

            allowed_qty = issued_qty * (float(allowed_pct) / 100.0)
            net_expected_qty = issued_qty - allowed_qty
            wastage_qty = net_expected_qty - float(actual_tests)
            wastage_pct = (wastage_qty / issued_qty * 100.0) if issued_qty > 0 else 0.0

            batches_rows = supabase.table("batches").select("unit_price_per_test").eq("item_id", w_item_id).execute().data or []
            avg_unit_price = (sum(float(b.get("unit_price_per_test") or 0) for b in batches_rows) / len(batches_rows)) if batches_rows else 0.0
            wastage_cost = max(0.0, wastage_qty) * avg_unit_price

            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric(f"📦 المسحوب/المصروف ({w_sub_u})", f"{issued_qty:,.0f}")
            with m2:
                st.metric(f"✂️ بعد خصم المسموح ({allowed_pct:.0f}%)", f"{net_expected_qty:,.0f}")
            with m3:
                st.metric(f"📉 كمية الهدر ({w_sub_u})", f"{wastage_qty:,.0f}")
            with m4:
                st.metric("📊 نسبة الهدر %", f"{wastage_pct:.1f}%")

            if wastage_cost > 0:
                st.info(f"💰 التكلفة المالية التقديرية للهدر: **{wastage_cost:,.2f} ج.م** (بناءً على متوسط سعر الوحدة **{avg_unit_price:,.2f} ج.م**)")

            if st.button("💾 حفظ سجل الهدر وترحيله للتقارير", type="primary", key="save_wastage_btn"):
                if w_from > w_to:
                    st.error("❌ تاريخ البداية يجب أن يكون قبل أو مساوياً لتاريخ النهاية.")
                else:
                    dup_q = supabase.table("wastage_logs").select("id").eq("item_id", w_item_id).eq("period_from", str(w_from)).eq("period_to", str(w_to)).eq("issued_qty", float(issued_qty))
                    if w_loc_id is None:
                        dup_q = dup_q.is_("location_id", "null")
                    else:
                        dup_q = dup_q.eq("location_id", w_loc_id)
                    existing_dup = dup_q.limit(1).execute().data or []

                    if existing_dup:
                        st.error("❌ هذا الصنف مسجل قبل كده بنفس البيانات (الصنف، الوحدة/الفرع، الفترة الزمنية، والكمية المسحوبة).")
                    else:
                        payload_w = {
                            "item_id": w_item_id,
                            "location_id": w_loc_id,
                            "period_from": str(w_from),
                            "period_to": str(w_to),
                            "issued_qty": float(issued_qty),
                            "actual_patient_tests": float(actual_tests),
                            "wastage_qty": float(wastage_qty),
                            "wastage_pct": float(round(wastage_pct, 2)),
                            "wastage_cost": float(round(wastage_cost, 2)),
                            "notes": w_notes.strip(),
                            "created_by": int(user["id"])
                        }
                        try:
                            supabase.table("wastage_logs").insert({**payload_w, "allowed_wastage_pct": float(allowed_pct)}).execute()
                        except Exception:
                            supabase.table("wastage_logs").insert(payload_w).execute()
                        log_user_action(
                            user,
                            "حساب هدر",
                            "حساب الهدر",
                            f"حساب هدر ({w_item_name}) للفترة {w_from} إلى {w_to} | المسحوب: {issued_qty:,.0f} | الفعلي: {actual_tests:,.0f} | الهدر: {wastage_qty:,.0f} ({wastage_pct:.1f}%)",
                            w_loc_label
                        )
                        st.success("✅ تم حفظ سجل الهدر بنجاح! يمكنك مراجعته في شاشة **📈 التقارير**.")
                        st.rerun()

# =========================================================================
# 5. المخزن الرئيسي
# =========================================================================
elif selected_page == "🏢 المخزن الرئيسي":
    render_page_header("🏢 المخزن الرئيسي")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(id, name, variant, category, unit_name, sub_unit_name, monthly_consumption_rate), suppliers(name))").eq("location_id", 1).gt("tests_available", 0).execute()
    rows = inv_res.data or []
    
    if not rows:
        st.warning("المخزن الرئيسي فارغ حالياً. اذهب إلى '↳ 📥 إضافة فاتورة' لإضافة الأرصدة.")
    else:
        tab1, tab2, tab3 = st.tabs([
            "📊 العرض التجميعي الذكي (كل الشركات معاً + مدة الكفاية)",
            "🏢 العرض التفصيلي (مفصول حسب الشركة ورقم التشغيلة)",
            "🛠️ إجراءات المخزون (استرجاع / إعدام / تحديث الجرد)"
        ])
        
        with tab1:
            st.markdown("<h3 class='section-center-title'>إجمالي الرصيد الكلي لكل تحليل/صنف ومدة كفايته</h3>", unsafe_allow_html=True)
            agg = {}
            for r in rows:
                it = r["batches"]["items"]
                sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
                key = (it["id"], it["name"], it["category"], sub_u, float(it["monthly_consumption_rate"] or 0))
                if key not in agg:
                    agg[key] = {"kits": 0.0, "tests": 0.0, "value": 0.0, "companies": set()}
                agg[key]["kits"] += float(r["kits_available"])
                agg[key]["tests"] += float(r["tests_available"])
                agg[key]["value"] += float(r["tests_available"]) * float(r["batches"]["unit_price_per_test"])
                agg[key]["companies"].add(r["batches"]["suppliers"]["name"])
            
            agg_list = []
            for k, v in agg.items():
                rate = k[4]
                months_cov = round(v["tests"] / rate, 2) if rate > 0 else 0
                agg_list.append([
                    (k[1], "color:#0e4d92; font-weight:800;"),
                    "محاليل وكواشف" if k[2] == "reagent" else "مستهلكات",
                    " + ".join(v["companies"]),
                    f"{v['kits']:,.0f}",
                    (f"{v['tests']:,.0f}", "color:#0284c7; font-weight:800;"),
                    (k[3], "color:#0d9488; font-weight:800;"),
                    f"{rate:,.0f}",
                    f"{months_cov} شهر" if rate > 0 else "غير محدد",
                    f"{v['value']:,.2f} ج.م"
                ])
            agg_headers = [
                "الصنف",
                "التصنيف",
                "الشركات المتوفرة",
                "إجمالي العلب/الباكيت",
                "إجمالي الرصيد",
                "الوحدة",
                "الاستهلاك الشهري",
                "يكفي لمدة",
                "القيمة المالية"
            ]
            render_styled_table(agg_headers, agg_list)

        with tab2:
            st.markdown("<h3 class='section-center-title'>تفاصيل الأرصدة حسب الشركة الموردة ورقم التشغيلة</h3>", unsafe_allow_html=True)
            det_rows = []
            sorted_rows = sorted(rows, key=lambda x: (x["batches"]["items"]["name"], x["batches"]["expiry_date"]))
            filter_item = st.selectbox("فلترة باسم الصنف (اختياري):", ["الكل"] + sorted(list({r["batches"]["items"]["name"] for r in rows})))
            
            for r in sorted_rows:
                b = r["batches"]
                it = b["items"]
                if filter_item != "الكل" and it["name"] != filter_item:
                    continue
                sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
                tot_val = float(r["tests_available"]) * float(b["unit_price_per_test"])
                det_rows.append([
                    (it['name'], "color:#0e4d92; font-weight:800;"),
                    b["suppliers"]["name"],
                    b["lot_number"],
                    b["expiry_date"],
                    f"{float(r['kits_available']):,.0f}",
                    (f"{float(r['tests_available']):,.0f}", "color:#0284c7; font-weight:800;"),
                    (sub_u, "color:#0d9488; font-weight:800;"),
                    f"{float(b['unit_price_per_test']):,.2f}",
                    f"{tot_val:,.2f} ج.م"
                ])
            det_headers = [
                "الصنف",
                "الشركة الموردة",
                "رقم التشغيلة",
                "تاريخ الصلاحية",
                "العلب المتاحة",
                "الكمية المتاحة",
                "الوحدة",
                "سعر الوحدة",
                "إجمالي القيمة"
            ]
            render_styled_table(det_headers, det_rows)

        with tab3:
            st.markdown("<h3 class='section-center-title'>🛠️ استرجاع للمورد / إعدام / تحديث الجرد الدوري</h3>", unsafe_allow_html=True)
            inv_choice_labels = [
                f"{r['batches']['items']['name']} — شركة: {r['batches']['suppliers']['name']} | تشغيلة: {r['batches']['lot_number']} | المتاح: {int(r['kits_available'])} {r['batches']['items']['unit_name']} | الصلاحية: {r['batches']['expiry_date']}"
                for r in rows
            ]
            sel_inv_idx = st.selectbox("اختر الصنف والتشغيلة من المخزن الرئيسي:", range(len(rows)), format_func=lambda i: inv_choice_labels[i], key="m_act_inv_sel")
            cur_inv_r = rows[sel_inv_idx]
            cur_b = cur_inv_r["batches"]
            cur_it = cur_b["items"]
            cur_sup = cur_b["suppliers"]
            cur_tpk = float(cur_b.get("tests_per_kit") or 1)
            cur_kits_avail = float(cur_inv_r.get("kits_available") or 0)
            sub_u = "اختبار" if cur_it["sub_unit_name"] == "تست" else cur_it["sub_unit_name"]

            act_type = st.radio(
                "اختر نوع الإجراء:",
                ["return_supplier", "destroy_item", "stock_audit"],
                format_func=lambda x: {
                    "return_supplier": "↩️ استرجاع للمورد (خصم مرتجع/تالف/عدم احتياج)",
                    "destroy_item": "🔥 إعدام (خصم منتهي الصلاحية أو تالف)",
                    "stock_audit": "📋 تحديث الجرد (تسوية الرصيد الفعلي بعد الجرد)"
                }[x],
                horizontal=True,
                key="m_act_type_radio"
            )

            with st.container(border=True):
                if act_type in ["return_supplier", "destroy_item"]:
                    max_k = max(1, int(cur_kits_avail))
                    action_kits = st.number_input(
                        f"الكمية المراد {'استرجاعها' if act_type == 'return_supplier' else 'إعدامها'} (عدد الـ {cur_it['unit_name']}):",
                        min_value=1,
                        max_value=max_k,
                        value=1,
                        step=1,
                        key="m_act_kits_val"
                    )
                    reason_txt = st.text_input(
                        "السبب / البيان (مثال: تلف أثناء الشحن، انتهاء صلاحية، عدم الحاجة للصنف):",
                        key="m_act_reason"
                    )
                    btn_lbl = "↩️ تأكيد الاسترجاع وخصم الرصيد" if act_type == "return_supplier" else "🔥 تأكيد الإعدام وخصم الرصيد"
                else:
                    action_kits = st.number_input(
                        f"الرصيد الفعلي بعد الجرد (عدد الـ {cur_it['unit_name']}):",
                        min_value=0,
                        value=int(cur_kits_avail),
                        step=1,
                        key="m_audit_kits_val"
                    )
                    reason_txt = st.text_input(
                        "ملاحظات الجرد الدوري (مثال: جرد ربع سنوي):",
                        value="جرد دوري",
                        key="m_audit_reason"
                    )
                    btn_lbl = "📋 حفظ تحديث الجرد"

                if st.button(btn_lbl, type="primary", key="exec_main_store_action_btn"):
                    if act_type == "return_supplier":
                        new_k = max(0.0, cur_kits_avail - float(action_kits))
                        new_t = max(0.0, new_k * cur_tpk)
                        supabase.table("inventory").update({"kits_available": new_k, "tests_available": new_t}).eq("id", int(cur_inv_r["id"])).execute()
                        log_user_action(
                            user,
                            "استرجاع للمورد",
                            "المخزن الرئيسي",
                            f"استرجاع {action_kits} {cur_it['unit_name']} من صنف ({cur_it['name']}) تشغيلة ({cur_b['lot_number']}) لشركة ({cur_sup['name']}) | السبب: {reason_txt.strip() or '-'}",
                            "المخزن الرئيسي"
                        )
                        st.success(f"✅ تم تسجيل استرجاع {action_kits} {cur_it['unit_name']} ({int(action_kits * cur_tpk)} {sub_u}) لشركة {cur_sup['name']} وتحديث الرصيد!")
                        st.rerun()
                    elif act_type == "destroy_item":
                        new_k = max(0.0, cur_kits_avail - float(action_kits))
                        new_t = max(0.0, new_k * cur_tpk)
                        supabase.table("inventory").update({"kits_available": new_k, "tests_available": new_t}).eq("id", int(cur_inv_r["id"])).execute()
                        log_user_action(
                            user,
                            "إعدام صنف",
                            "المخزن الرئيسي",
                            f"إعدام {action_kits} {cur_it['unit_name']} من صنف ({cur_it['name']}) تشغيلة ({cur_b['lot_number']}) | السبب: {reason_txt.strip() or '-'}",
                            "المخزن الرئيسي"
                        )
                        st.success(f"🔥 تم إعدام {action_kits} {cur_it['unit_name']} ({int(action_kits * cur_tpk)} {sub_u}) وخصمها من المخزن الرئيسي!")
                        st.rerun()
                    else:
                        new_k = float(action_kits)
                        new_t = new_k * cur_tpk
                        supabase.table("inventory").update({"kits_available": new_k, "tests_available": new_t}).eq("id", int(cur_inv_r["id"])).execute()
                        log_user_action(
                            user,
                            "تحديث جرد",
                            "المخزن الرئيسي",
                            f"تحديث جرد صنف ({cur_it['name']}) تشغيلة ({cur_b['lot_number']}) من {int(cur_kits_avail)} إلى {int(new_k)} {cur_it['unit_name']} | ملاحظات: {reason_txt.strip() or '-'}",
                            "المخزن الرئيسي"
                        )
                        st.success(f"📋 تم تحديث الجرد ليصبح الرصيد الفعلي {int(new_k)} {cur_it['unit_name']} ({int(new_t)} {sub_u})!")
                        st.rerun()

# =========================================================================
# 6. شاشة: الطلبيات
# =========================================================================
elif selected_page == "↳ 🛒 الطلبيات":
    render_page_header("🛒 الطلبيات")
    
    items_df = get_df("items")
    locs_df = get_df("locations")
    rates_df = get_df("location_consumption_rates")
    
    f1, f2, f3 = st.columns(3)
    with f1:
        sub_locs = locs_df[locs_df["location_type"] != "main"] if not locs_df.empty else pd.DataFrame()
        loc_options = ["الكل (إجمالي المعمل)"] + (sub_locs["name"].tolist() if not sub_locs.empty else [])
        sel_order_loc = st.selectbox("🏥 تصفية حسب الوحدة / الفرع:", loc_options)
    with f2:
        cat_filter = st.selectbox("📂 تصفية حسب التصنيف:", ["الكل", "محاليل وكواشف", "مستهلكات"])
    with f3:
        item_names_list = ["الكل"] + (sorted(items_df["name"].unique().tolist()) if not items_df.empty else [])
        sel_order_item = st.selectbox("🧪 تصفية حسب الصنف / الاختبار:", item_names_list)

    months_cover = st.slider("📅 حدد عدد الشهور المطلوب تغطيتها في الطلبية:", min_value=1, max_value=12, value=3)
    
    if sel_order_loc == "الكل (إجمالي المعمل)":
        inv_res = supabase.table("inventory").select("tests_available, batches(item_id)").eq("location_id", 1).execute()
        stock_col_title = "الرصيد الحالي بالمخزن الرئيسي"
    else:
        target_loc_id = int(sub_locs[sub_locs["name"] == sel_order_loc].iloc[0]["id"])
        inv_res = supabase.table("inventory").select("tests_available, batches(item_id)").eq("location_id", target_loc_id).execute()
        stock_col_title = f"الرصيد الحالي في ({sel_order_loc})"
    
    stock_by_item = {}
    for r in (inv_res.data or []):
        if r.get("batches"):
            iid = r["batches"]["item_id"]
            stock_by_item[iid] = stock_by_item.get(iid, 0) + float(r["tests_available"])
    
    order_rows = []
    for _, it in items_df.iterrows():
        iid = int(it["id"])
        it_cat_ar = "محاليل وكواشف" if it["category"] == "reagent" else "مستهلكات"
        
        if cat_filter != "الكل" and it_cat_ar != cat_filter:
            continue
        if sel_order_item != "الكل" and it["name"] != sel_order_item:
            continue
        
        if sel_order_loc == "الكل (إجمالي المعمل)":
            rate = float(it["monthly_consumption_rate"] or 0)
        else:
            if not rates_df.empty:
                match_r = rates_df[(rates_df["location_id"] == target_loc_id) & (rates_df["item_id"] == iid)]
                rate = float(match_r.iloc[0]["monthly_tests_rate"]) if not match_r.empty else 0.0
            else:
                rate = 0.0

        if rate > 0:
            needed_total = rate * months_cover
            current_stock = stock_by_item.get(iid, 0)
            deficit = max(0, needed_total - current_stock)
            unit_label = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
            
            if deficit > 0:
                order_rows.append({
                    "الصنف": str(it["name"]),
                    "التصنيف": str(it_cat_ar),
                    "الاستهلاك الشهري": float(rate),
                    f"الاحتياج لـ {months_cover} شهور": float(needed_total),
                    stock_col_title: float(current_stock),
                    "العجز المطلوب شراؤه": float(deficit),
                    "الوحدة": str(unit_label)
                })
    
    if order_rows:
        st.markdown("<br>", unsafe_allow_html=True)

        ord_headers = [
            "الصنف",
            "التصنيف",
            "الاستهلاك الشهري",
            f"الاحتياج ({months_cover} شهور)",
            stock_col_title,
            "العجز المطلوب شراؤه",
            "الوحدة"
        ]
        styled_ord_rows = []
        for r_item in order_rows:
            styled_ord_rows.append([
                (r_item["الصنف"], "color:#0e4d92; font-weight:800;"),
                r_item["التصنيف"],
                f"{r_item['الاستهلاك الشهري']:,.0f}",
                f"{r_item[f'الاحتياج لـ {months_cover} شهور']:,.0f}",
                f"{r_item[stock_col_title]:,.0f}",
                (f"{r_item['العجز المطلوب شراؤه']:,.0f}", "color:#dc2626; font-weight:800;"),
                (r_item["الوحدة"], "color:#0d9488; font-weight:800;")
            ])
        render_styled_table(ord_headers, styled_ord_rows)

        df_ord = pd.DataFrame(order_rows)
        file_tag = "all_lab" if sel_order_loc == "الكل (إجمالي المعمل)" else sel_order_loc
        render_export_buttons(
            df_ord,
            f"order_{file_tag}_{months_cover}_months",
            "طلبية شراء واحتياجات",
            f"الجهة: {sel_order_loc} | المدة: {months_cover} شهور | التاريخ: {date.today()}",
            key_prefix="ord_dl"
        )
    else:
        st.success("✅ لا يوجد عجز مطلوب شراؤه بناءً على الفلاتر والمدة المحددة!")

# =========================================================================
# 7. شاشة: إضافة فاتورة + تعديل فاتورة
# =========================================================================
elif selected_page == "↳ 📥 إضافة فاتورة":
    render_page_header("📥 إضافة فاتورة")
    
    items_df = get_df("items")
    suppliers_df = get_df("suppliers")
    
    if items_df.empty or suppliers_df.empty:
        st.warning("⚠️ برجاء إضافة الأصناف والشركات أولاً من صفحة '⚙️ التكويد'.")
    else:
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                item_choice = st.selectbox("اختر الصنف / التحليل", items_df["name"].tolist(), key="add_inv_item_sel")
                selected_item = items_df[items_df["name"] == item_choice].iloc[0]
                sub_u = "اختبار" if selected_item["sub_unit_name"] == "تست" else selected_item["sub_unit_name"]
                
                sup_choice = st.selectbox("الشركة الموردة", suppliers_df["name"].tolist(), key="add_inv_sup_sel")
                selected_sup = suppliers_df[suppliers_df["name"] == sup_choice].iloc[0]
                
                lot_number = st.text_input("رقم التشغيلة (Lot Number)", key="add_inv_lot")
                expiry_date = st.date_input("تاريخ الصلاحية", min_value=date.today(), key="add_inv_exp")

            with col2:
                kits_qty = st.number_input(f"الكمية الواردة (عدد الـ {selected_item['unit_name']})", min_value=1, step=1, key="add_inv_kits")
                tests_per_kit = st.number_input(f"عدد الـ ({sub_u}) داخل كل {selected_item['unit_name']}", min_value=1, value=100, step=1, key="add_inv_tpk")
                unit_price = st.number_input(f"سعر الـ ({sub_u}) الواحد بالجنيه", min_value=0.0, step=0.1, format="%.2f", key="add_inv_up")
                rec_date = st.date_input("تاريخ التوريد", value=date.today(), key="add_inv_rec")

            total_tests = kits_qty * tests_per_kit
            kit_price = unit_price * tests_per_kit
            st.info(f"📌 ملخص الإضافة: **{kits_qty}** {selected_item['unit_name']} × **{tests_per_kit}** = **{total_tests}** {sub_u} | سعر العلبة: **{kit_price:,.2f} ج.م** | إجمالي الفاتورة: **{total_tests * unit_price:,.2f} ج.م**")
            
            if st.button("✅ تأكيد إضافة الفاتورة للمخزن الرئيسي", type="primary", key="confirm_add_inv_btn"):
                if not lot_number.strip():
                    st.error("برجاء إدخال رقم التشغيلة.")
                else:
                    batch_insert = supabase.table("batches").insert({
                        "item_id": int(selected_item["id"]),
                        "supplier_id": int(selected_sup["id"]),
                        "lot_number": lot_number.strip(),
                        "expiry_date": str(expiry_date),
                        "tests_per_kit": int(tests_per_kit),
                        "unit_price_per_test": float(unit_price),
                        "kit_price": float(kit_price),
                        "initial_kits": int(kits_qty),
                        "received_date": str(rec_date),
                        "created_by": user["id"]
                    }).execute()
                    
                    new_batch_id = batch_insert.data[0]["id"]
                    supabase.table("inventory").insert({
                        "location_id": 1,
                        "batch_id": new_batch_id,
                        "kits_available": float(kits_qty),
                        "tests_available": float(total_tests)
                    }).execute()
                    log_user_action(
                        user,
                        "إضافة فاتورة",
                        "إضافة فاتورة",
                        f"إضافة {kits_qty} {selected_item['unit_name']} ({total_tests} {sub_u}) من صنف ({selected_item['name']}) شركة ({selected_sup['name']}) تشغيلة ({lot_number.strip()})",
                        "المخزن الرئيسي"
                    )
                    st.success(f"🎉 تم إضافة {kits_qty} {selected_item['unit_name']} ({total_tests} {sub_u}) بنجاح إلى المخزن الرئيسي!")

        can_edit_invoice = (role in ["chairman", "general_manager"]) or ("↳ 📥 إضافة فاتورة" in parse_custom_pages(user.get("allowed_pages")))
        if can_edit_invoice:
            st.divider()
            st.subheader("✏️ تعديل فاتورة سابقة (Edit)")
            batches_all = supabase.table("batches").select("*, items(name, unit_name, sub_unit_name), suppliers(name)").order("id", desc=True).limit(50).execute().data or []
            if batches_all:
                b_labels = [
                    f"فاتورة #{b['id']} | {b['items']['name']} ({b['suppliers']['name']}) | تشغيلة: {b['lot_number']} | {b['initial_kits']} {b['items']['unit_name']}"
                    for b in batches_all if b.get("items") and b.get("suppliers")
                ]
                if b_labels:
                    sel_b_idx = st.selectbox("اختر الفاتورة لتعديل بياناتها:", range(len(b_labels)), format_func=lambda i: b_labels[i], key="edit_inv_b_sel")
                    target_b = batches_all[sel_b_idx]
                    target_b_id = int(target_b["id"])
                    t_sub_u = "اختبار" if target_b["items"]["sub_unit_name"] == "تست" else target_b["items"]["sub_unit_name"]

                    with st.container(border=True):
                        ec1, ec2 = st.columns(2)
                        upd_lot = ec1.text_input("رقم التشغيلة (Lot Number)", value=target_b["lot_number"], key=f"eb_lot_{target_b_id}")
                        try:
                            init_exp_d = datetime.strptime(target_b["expiry_date"], "%Y-%m-%d").date()
                        except Exception:
                            init_exp_d = date.today()
                        upd_exp = ec2.date_input("تاريخ الصلاحية", value=init_exp_d, key=f"eb_exp_{target_b_id}")

                        upd_kits = ec1.number_input(f"الكمية الواردة (عدد الـ {target_b['items']['unit_name']})", min_value=1, value=max(1, int(target_b.get("initial_kits") or 1)), step=1, key=f"eb_kits_{target_b_id}")
                        upd_tpk = ec2.number_input(f"عدد الـ ({t_sub_u}) داخل كل {target_b['items']['unit_name']}", min_value=1, value=max(1, int(target_b.get("tests_per_kit") or 100)), step=1, key=f"eb_tpk_{target_b_id}")

                        upd_u_price = ec1.number_input(f"سعر الـ ({t_sub_u}) الواحد بالجنيه", min_value=0.0, value=float(target_b.get("unit_price_per_test") or 0.0), step=0.1, format="%.2f", key=f"eb_up_{target_b_id}")
                        try:
                            init_rec_d = datetime.strptime(target_b["received_date"], "%Y-%m-%d").date()
                        except Exception:
                            init_rec_d = date.today()
                        upd_rec = ec2.date_input("تاريخ التوريد", value=init_rec_d, key=f"eb_rec_{target_b_id}")

                        if st.button("💾 حفظ تعديل الفاتورة", type="primary", key=f"save_eb_btn_{target_b_id}"):
                            if not upd_lot.strip():
                                st.error("❌ برجاء إدخال رقم التشغيلة.")
                            else:
                                new_kit_p = float(upd_u_price) * int(upd_tpk)
                                supabase.table("batches").update({
                                    "lot_number": upd_lot.strip(),
                                    "expiry_date": str(upd_exp),
                                    "tests_per_kit": int(upd_tpk),
                                    "unit_price_per_test": float(upd_u_price),
                                    "kit_price": new_kit_p,
                                    "initial_kits": int(upd_kits),
                                    "received_date": str(upd_rec)
                                }).eq("id", target_b_id).execute()

                                m_inv_list = supabase.table("inventory").select("*").eq("location_id", 1).eq("batch_id", target_b_id).execute().data or []
                                if m_inv_list:
                                    m_inv_row = m_inv_list[0]
                                    old_init_k = float(target_b.get("initial_kits") or 0)
                                    diff_k = float(upd_kits) - old_init_k
                                    new_avail_k = max(0.0, float(m_inv_row.get("kits_available") or 0) + diff_k)
                                    new_avail_t = new_avail_k * float(upd_tpk)
                                    supabase.table("inventory").update({
                                        "kits_available": new_avail_k,
                                        "tests_available": new_avail_t
                                    }).eq("id", int(m_inv_row["id"])).execute()

                                log_user_action(
                                    user,
                                    "تعديل فاتورة",
                                    "إضافة فاتورة",
                                    f"تعديل فاتورة #{target_b_id} لصنف ({target_b['items']['name']}) تشغيلة ({upd_lot.strip()}) كمية ({upd_kits} {target_b['items']['unit_name']})",
                                    "المخزن الرئيسي"
                                )
                                st.success("✅ تم تعديل الفاتورة وتحديث البيانات بنجاح!")
                                st.rerun()

# =========================================================================
# 8. المخازن الفرعية
# =========================================================================
elif selected_page == "🧪 المخازن الفرعية":
    render_page_header("🧪 المخازن الفرعية")
    
    locs_df = get_df("locations")
    sub_locs = locs_df[locs_df["location_type"] != "main"]
    
    if role in ["chairman", "general_manager"]:
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            loc_name = st.selectbox("🏥 الوحدة / الفرع:", sub_locs["name"].tolist(), key="sub_loc_gm")
            sel_loc_id = int(sub_locs[sub_locs["name"] == loc_name].iloc[0]["id"])
        with fc2:
            sub_cat_filter = st.selectbox("📂 التصنيف:", ["الكل", "محاليل وكواشف", "مستهلكات"], key="sub_cat_gm")
    else:
        sel_loc_id = user_loc_id
        loc_name = user_loc_name
        st.markdown(f"<h3 class='section-center-title'>🏥 مخزن: {user_loc_name}</h3>", unsafe_allow_html=True)
        fc2, fc3, fc4 = st.columns(3)
        with fc2:
            sub_cat_filter = st.selectbox("📂 التصنيف:", ["الكل", "محاليل وكواشف", "مستهلكات"], key="sub_cat_sup")

    sub_inv = supabase.table("inventory").select("*, batches(*, items(id, name, category, unit_name, sub_unit_name), suppliers(id, name))").eq("location_id", sel_loc_id).gt("kits_available", 0).execute()
    raw_rows = sub_inv.data or []

    cat_filtered_rows = []
    for r in raw_rows:
        it_cat = "محاليل وكواشف" if r["batches"]["items"]["category"] == "reagent" else "مستهلكات"
        if sub_cat_filter == "الكل" or it_cat == sub_cat_filter:
            cat_filtered_rows.append(r)

    available_item_names = sorted(list({r["batches"]["items"]["name"] for r in cat_filtered_rows}))
    with fc3:
        item_label_title = "🧪 اسم المحلول:" if sub_cat_filter == "محاليل وكواشف" else ("🧤 اسم المستهلك:" if sub_cat_filter == "مستهلكات" else "🔍 اسم الصنف:")
        sel_sub_item = st.selectbox(item_label_title, ["الكل"] + available_item_names, key="sub_item_filter")

    item_filtered_rows = [
        r for r in cat_filtered_rows 
        if sel_sub_item == "الكل" or r["batches"]["items"]["name"] == sel_sub_item
    ]

    available_sup_names = sorted(list({r["batches"]["suppliers"]["name"] for r in item_filtered_rows}))
    with fc4:
        sel_sub_sup = st.selectbox("🏭 الشركة الموردة:", ["الكل"] + available_sup_names, key="sub_sup_filter")

    final_sub_rows = [
        r for r in item_filtered_rows 
        if sel_sub_sup == "الكل" or r["batches"]["suppliers"]["name"] == sel_sub_sup
    ]

    if not final_sub_rows:
        st.info("لا توجد أرصدة مطابقة للفلاتر المختارة في هذه الوحدة حالياً.")
    else:
        st.markdown("<br>", unsafe_allow_html=True)

        sub_col_widths = [1.4, 1.0, 1.1, 1.5, 1.0, 1.0, 0.9, 1.1]
        sub_headers = [
            "الصنف",
            "التصنيف",
            "الشركة الموردة",
            "الرصيد المتاح",
            "رقم التشغيلة",
            "الصلاحية",
            "الكمية",
            "الإجراء"
        ]
        s_hdr_cols = st.columns(sub_col_widths)
        for idx, h_title in enumerate(sub_headers):
            with s_hdr_cols[idx]:
                st.markdown(f"<div class='tbl-hdr-cell'>{h_title}</div>", unsafe_allow_html=True)

        for row in final_sub_rows:
            b = row["batches"]
            it = b["items"]
            sup = b["suppliers"]
            sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
            cat_badge = "محاليل وكواشف" if it["category"] == "reagent" else "مستهلكات"
            avail_txt = f"{int(row['kits_available'])} {it['unit_name']} ({int(row['tests_available'])} {sub_u})"

            s_row_cols = st.columns(sub_col_widths)
            with s_row_cols[0]:
                st.markdown(f"<div class='tbl-row-cell' style='color:#0e4d92;'>{it['name']}</div>", unsafe_allow_html=True)
            with s_row_cols[1]:
                st.markdown(f"<div class='tbl-row-cell'>{cat_badge}</div>", unsafe_allow_html=True)
            with s_row_cols[2]:
                st.markdown(f"<div class='tbl-row-cell'>{sup['name']}</div>", unsafe_allow_html=True)
            with s_row_cols[3]:
                st.markdown(f"<div class='tbl-row-cell' style='color:#0d9488;'>{avail_txt}</div>", unsafe_allow_html=True)
            with s_row_cols[4]:
                st.markdown(f"<div class='tbl-row-cell' dir='ltr'>{b['lot_number']}</div>", unsafe_allow_html=True)
            with s_row_cols[5]:
                st.markdown(f"<div class='tbl-row-cell' dir='ltr'>{b['expiry_date']}</div>", unsafe_allow_html=True)

            with s_row_cols[6]:
                kits_pull = st.number_input(
                    f"كمية السحب ({it['unit_name']})",
                    min_value=1,
                    max_value=int(row["kits_available"]),
                    value=1,
                    label_visibility="collapsed",
                    key=f"pull_qty_{row['id']}"
                )

            with s_row_cols[7]:
                if st.button("🧪 سحب للجهاز", key=f"pull_btn_{row['id']}", type="primary"):
                    tests_pulled = kits_pull * b["tests_per_kit"]
                    cost_pulled = tests_pulled * float(b["unit_price_per_test"])
                    
                    supabase.table("inventory").update({
                        "kits_available": float(row["kits_available"]) - kits_pull,
                        "tests_available": float(row["tests_available"]) - tests_pulled
                    }).eq("id", row["id"]).execute()
                    
                    supabase.table("consumption_logs").insert({
                        "location_id": sel_loc_id,
                        "batch_id": b["id"],
                        "item_id": it["id"],
                        "supplier_id": sup["id"],
                        "kits_consumed": float(kits_pull),
                        "tests_consumed": float(tests_pulled),
                        "cost_incurred": float(cost_pulled),
                        "logged_by": user["id"]
                    }).execute()

                    log_user_action(
                        user,
                        "سحب للجهاز",
                        "المخازن الفرعية",
                        f"سحب {kits_pull} {it['unit_name']} ({tests_pulled} {sub_u}) من صنف ({it['name']}) شركة ({sup['name']}) تشغيلة ({b['lot_number']})",
                        loc_name
                    )
                    st.success(f"تم سحب {kits_pull} {it['unit_name']} ({tests_pulled} {sub_u}) وخصمها من رصيد الوحدة.")
                    st.rerun()

# =========================================================================
# 9. أذونات الصرف المعتمدة
# =========================================================================
elif selected_page == "📦 أذونات الصرف المعتمدة":
    render_page_header("📦 أذونات الصرف المعتمدة من المدير العام")
    render_approved_requests_storekeeper_view(key_prefix="sk_main_app")

# =========================================================================
# 10. أذونات الصرف
# =========================================================================
elif selected_page == "🔄 أذونات الصرف":
    render_page_header("🔄 أذونات الصرف")
    
    t1, t2 = st.tabs(["📝 إنشاء إذن صرف جديد (للوحدات والفروع)", "📦 أذونات الصرف المعتمدة (طباعة PDF وتنفيذ الصرف)"])
    
    with t1:
        st.subheader("طلب صرف من المخزن الرئيسي")
        locs_df = get_df("locations")
        sub_locs = locs_df[locs_df["location_type"] != "main"]
        items_df = get_df("items")
        suppliers_df = get_df("suppliers")
        rates_df = get_df("location_consumption_rates")
        
        if sub_locs.empty or items_df.empty:
            st.warning("تأكد من وجود وحدات/فروع وأصناف مسجلة.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                if role in ["unit_supervisor", "employee"] and user_loc_id != 1:
                    target_loc_id = user_loc_id
                    target_loc_name = user_loc_name
                    st.text_input("الوحدة / الفرع الطالب", value=user_loc_name, disabled=True)
                else:
                    loc_choice = st.selectbox("اختر الوحدة / الفرع الطالب", sub_locs["name"].tolist())
                    target_loc_name = loc_choice
                    target_loc_id = int(sub_locs[sub_locs["name"] == loc_choice].iloc[0]["id"])
                
                if not rates_df.empty and "location_id" in rates_df.columns:
                    linked_item_ids = rates_df[rates_df["location_id"] == target_loc_id]["item_id"].tolist()
                    if linked_item_ids:
                        filtered_items_df = items_df[items_df["id"].isin(linked_item_ids)]
                    else:
                        filtered_items_df = items_df
                else:
                    filtered_items_df = items_df

                item_choice = st.selectbox("اختر الصنف المطلوب (المخصص لهذه الوحدة/الفرع)", filtered_items_df["name"].tolist(), key="req_item")
                sel_item = filtered_items_df[filtered_items_df["name"] == item_choice].iloc[0]
                sub_u = "اختبار" if sel_item["sub_unit_name"] == "تست" else sel_item["sub_unit_name"]
                
                sup_choice = st.selectbox("اختر الشركة الموردة", suppliers_df["name"].tolist(), key="req_sup")
                sel_sup = suppliers_df[suppliers_df["name"] == sup_choice].iloc[0]

            with c2:
                rate_res = supabase.table("location_consumption_rates").select("monthly_tests_rate").eq("location_id", target_loc_id).eq("item_id", int(sel_item["id"])).execute()
                unit_monthly_rate = float(rate_res.data[0]["monthly_tests_rate"]) if rate_res.data else 0.0
                
                months_needed = st.number_input("المدة المطلوب تغطيتها (بالشهور)", min_value=0.5, max_value=12.0, value=1.0, step=0.5)
                
                avail_batches = supabase.table("inventory").select("*, batches!inner(*)").eq("location_id", 1).eq("batches.item_id", int(sel_item["id"])).eq("batches.supplier_id", int(sel_sup["id"])).gt("kits_available", 0).execute()
                
                if avail_batches.data:
                    sorted_b = sorted(avail_batches.data, key=lambda x: x["batches"]["expiry_date"])
                    best_b = sorted_b[0]
                    tpk = best_b["batches"]["tests_per_kit"]
                    suggested_kits = max(1, round((unit_monthly_rate * months_needed) / tpk)) if unit_monthly_rate > 0 else 1
                    
                    st.success(f"💡 ترشيح النظام (الأقرب صلاحية): **تشغيلة {best_b['batches']['lot_number']}** (تنتهي في `{best_b['batches']['expiry_date']}`) | المتاح بالمخزن الرئيسي: **{int(best_b['kits_available'])}** {sel_item['unit_name']}")
                    if unit_monthly_rate > 0:
                        st.caption(f"بناءً على استهلاك هذه الوحدة/الفرع ({unit_monthly_rate} {sub_u}/شهر)، الكمية المقترحة لـ {months_needed} شهر هي **{suggested_kits}** {sel_item['unit_name']}.")
                    
                    kits_to_req = st.number_input(f"عدد الـ ({sel_item['unit_name']}) المطلوب صرفها", min_value=1, max_value=int(best_b["kits_available"]), value=min(suggested_kits, int(best_b["kits_available"])))
                    
                    if st.button("🚀 إرسال الإذن إلى قسم الموافقات", type="primary"):
                        supabase.table("transfer_requests").insert({
                            "from_location_id": 1,
                            "to_location_id": target_loc_id,
                            "item_id": int(sel_item["id"]),
                            "supplier_id": int(sel_sup["id"]),
                            "batch_id": best_b["batch_id"],
                            "months_requested": float(months_needed),
                            "kits_requested": int(kits_to_req),
                            "tests_requested": int(kits_to_req * tpk),
                            "status": "pending_gm",
                            "requested_by": user["id"]
                        }).execute()
                        log_user_action(
                            user,
                            "إرسال طلب صرف",
                            "أذونات الصرف",
                            f"طلب صرف {kits_to_req} {sel_item['unit_name']} ({kits_to_req * tpk} {sub_u}) من صنف ({sel_item['name']}) شركة ({sel_sup['name']}) تشغيلة ({best_b['batches']['lot_number']})",
                            target_loc_name
                        )
                        st.success("✅ تم إرسال إذن الصرف بنجاح وهو الآن في صفحة '✍️ الموافقات'!")
                else:
                    st.error(f"❌ لا يوجد رصيد متاح في المخزن الرئيسي من ({sel_item['name']}) لشركة ({sel_sup['name']}).")

    with t2:
        st.subheader("أذونات الصرف المعتمدة وجاهزة للطباعة والصرف")
        render_approved_requests_storekeeper_view(key_prefix="tr_tab2_app")

# =========================================================================
# 11. الموافقات
# =========================================================================
elif selected_page == "✍️ الموافقات":
    render_page_header("✍️ الموافقات")
    
    pending_res = supabase.table("transfer_requests").select(
        "*, locations!transfer_requests_to_location_id_fkey(name), items(id, name, variant, unit_name, sub_unit_name), suppliers(name), batches(lot_number, expiry_date)"
    ).eq("status", "pending_gm").execute()
    all_pending = pending_res.data or []
    
    if not all_pending:
        st.info("✅ لا توجد أذونات صرف معلقة بانتظار الموافقة حالياً.")
    else:
        rates_df = get_df("location_consumption_rates")
        all_sub_inv = supabase.table("inventory").select("location_id, kits_available, tests_available, batches(item_id)").neq("location_id", 1).execute().data or []

        rates_lookup = {}
        if not rates_df.empty:
            for _, rr in rates_df.iterrows():
                rates_lookup[(int(rr["location_id"]), int(rr["item_id"]))] = float(rr["monthly_tests_rate"] or 0)

        sub_stock_lookup = {}
        for inv_r in all_sub_inv:
            if inv_r.get("batches"):
                key = (int(inv_r["location_id"]), int(inv_r["batches"]["item_id"]))
                if key not in sub_stock_lookup:
                    sub_stock_lookup[key] = {"kits": 0.0, "tests": 0.0}
                sub_stock_lookup[key]["kits"] += float(inv_r["kits_available"] or 0)
                sub_stock_lookup[key]["tests"] += float(inv_r["tests_available"] or 0)

        af1, af2 = st.columns(2)
        with af1:
            pending_locs = ["الكل"] + sorted(list({r["locations"]["name"] for r in all_pending if r.get("locations")}))
            sel_app_loc = st.selectbox("🏥 تصفية حسب الوحدة / الفرع:", pending_locs, key="app_filter_loc")
        with af2:
            loc_filtered_pending = [
                r for r in all_pending 
                if sel_app_loc == "الكل" or (r.get("locations") and r["locations"]["name"] == sel_app_loc)
            ]
            pending_items = ["الكل"] + sorted(list({r["items"]["name"] for r in loc_filtered_pending if r.get("items")}))
            sel_app_item = st.selectbox("🧪 تصفية حسب الصنف:", pending_items, key="app_filter_item")

        filtered_pending = [
            r for r in loc_filtered_pending 
            if sel_app_item == "الكل" or (r.get("items") and r["items"]["name"] == sel_app_item)
        ]

        if not filtered_pending:
            st.warning("لا توجد طلبات مطابقة للفلاتر المختارة.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)

            col_widths = [1.5, 1.2, 1.0, 1.4, 1.2, 1.4, 1.0, 1.0, 1.3]
            headers = [
                "الجهة الطالبة",
                "الصنف",
                "الشركة",
                "الكمية المطلوبة",
                "تكفي لمدة",
                "الرصيد الحالي",
                "رقم التشغيلة",
                "الصلاحية",
                "الإجراء"
            ]
            hdr_cols = st.columns(col_widths)
            for idx, h_title in enumerate(headers):
                with hdr_cols[idx]:
                    st.markdown(f"<div class='tbl-hdr-cell'>{h_title}</div>", unsafe_allow_html=True)

            for req in filtered_pending:
                to_loc_id = int(req["to_location_id"])
                it_id = int(req["item_id"])
                sub_u = "اختبار" if req["items"].get("sub_unit_name") == "تست" else (req["items"].get("sub_unit_name") or "اختبار")
                
                unit_rate = rates_lookup.get((to_loc_id, it_id), 0.0)
                req_tests = float(req["tests_requested"] or 0)
                req_coverage_txt = format_coverage_duration(req_tests, unit_rate)
                
                cur_sub_stock = sub_stock_lookup.get((to_loc_id, it_id), {"kits": 0.0, "tests": 0.0})
                cur_kits = int(cur_sub_stock["kits"])
                cur_tests = int(cur_sub_stock["tests"])
                cur_stock_txt = f"{cur_kits} {req['items']['unit_name']} ({cur_tests} {sub_u})" if cur_tests > 0 else "صفر"

                qty_txt = f"{req['kits_requested']} {req['items']['unit_name']} ({int(req_tests)} {sub_u})"

                row_cols = st.columns(col_widths)
                with row_cols[0]:
                    st.markdown(f"<div class='tbl-row-cell' style='color:#0e4d92;'>{req['locations']['name']}</div>", unsafe_allow_html=True)
                with row_cols[1]:
                    st.markdown(f"<div class='tbl-row-cell'>{req['items']['name']}</div>", unsafe_allow_html=True)
                with row_cols[2]:
                    st.markdown(f"<div class='tbl-row-cell'>{req['suppliers']['name']}</div>", unsafe_allow_html=True)
                with row_cols[3]:
                    st.markdown(f"<div class='tbl-row-cell' style='color:#0284c7;'>{qty_txt}</div>", unsafe_allow_html=True)
                with row_cols[4]:
                    st.markdown(f"<div class='tbl-row-cell' style='color:#0d9488;'>{req_coverage_txt}</div>", unsafe_allow_html=True)
                with row_cols[5]:
                    st.markdown(f"<div class='tbl-row-cell'>{cur_stock_txt}</div>", unsafe_allow_html=True)
                with row_cols[6]:
                    st.markdown(f"<div class='tbl-row-cell' dir='ltr'>{req['batches']['lot_number']}</div>", unsafe_allow_html=True)
                with row_cols[7]:
                    st.markdown(f"<div class='tbl-row-cell' dir='ltr'>{req['batches']['expiry_date']}</div>", unsafe_allow_html=True)
                
                with row_cols[8]:
                    btn_a, btn_r = st.columns(2)
                    with btn_a:
                        if st.button("✅", key=f"app_{req['id']}", type="primary", help="موافقة واعتماد"):
                            supabase.table("transfer_requests").update({
                                "status": "approved_ready_to_issue",
                                "approved_by": user["id"],
                                "approved_at": datetime.now().isoformat()
                            }).eq("id", req["id"]).execute()
                            log_user_action(
                                user,
                                "موافقة على إذن صرف",
                                "الموافقات",
                                f"اعتماد طلب #{req['id']} لصنف ({req['items']['name']}) كمية ({req['kits_requested']} {req['items']['unit_name']})",
                                req["locations"]["name"]
                            )
                            st.rerun()
                    with btn_r:
                        if st.button("❌", key=f"rej_{req['id']}", help="رفض الطلب"):
                            supabase.table("transfer_requests").update({"status": "rejected"}).eq("id", req["id"]).execute()
                            log_user_action(
                                user,
                                "رفض إذن صرف",
                                "الموافقات",
                                f"رفض طلب #{req['id']} لصنف ({req['items']['name']}) كمية ({req['kits_requested']} {req['items']['unit_name']})",
                                req["locations"]["name"]
                            )
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"✅ موافقة واعتماد All ({len(filtered_pending)} طلب)", type="primary", key="approve_all_filtered_btn"):
                ids_to_approve = [r["id"] for r in filtered_pending]
                supabase.table("transfer_requests").update({
                    "status": "approved_ready_to_issue",
                    "approved_by": user["id"],
                    "approved_at": datetime.now().isoformat()
                }).in_("id", ids_to_approve).execute()
                log_user_action(
                    user,
                    "موافقة جماعية",
                    "الموافقات",
                    f"اعتماد جماعي لعدد {len(ids_to_approve)} طلب صرف",
                    sel_app_loc
                )
                st.success(f"🎉 تم اعتماد والموافقة على {len(ids_to_approve)} طلب دفعة واحدة!")
                st.rerun()

# =========================================================================
# 12. التقارير (يشمل التقرير الكمي والمالي + الاستهلاك + الأسعار + الهدر + سجل تتبع المستخدمين)
# =========================================================================
elif selected_page == "📈 التقارير":
    render_page_header("📈 التقارير")
    
    rep_t1, rep_t2, rep_t3, rep_t4, rep_t5 = st.tabs([
        "💰 التقرير الكمي والمالي (حسب الصنف)",
        "📊 تقرير الاستهلاك الكمي والمالي (بالصنف والشركة)",
        "💲 مقارنة وتطور أسعار الشركات الموردة",
        "📉 تقرير الهدر والفاقد",
        "🕵️ سجل حركات المستخدمين (Audit Log)"
    ])

    with rep_t1:
        st.markdown("<h3 class='section-center-title'>💰 التقرير الكمي والمالي (إجمالي الكمية والتكلفة ومتوسط سعر الاختبار لكل صنف)</h3>", unsafe_allow_html=True)
        fc_d1, fc_d2, fc_d3 = st.columns(3)
        start_fin = fc_d1.date_input("من تاريخ", value=date.today().replace(day=1), key="fin_from_d")
        end_fin = fc_d2.date_input("إلى تاريخ", value=date.today(), key="fin_to_d")

        fin_logs = supabase.table("consumption_logs").select("*, items(id, name, sub_unit_name)").gte("consumed_at", str(start_fin)).lte("consumed_at", str(end_fin) + "T23:59:59").execute().data or []
        all_fin_items = ["الكل"] + sorted(list({l["items"]["name"] for l in fin_logs if l.get("items")}))
        with fc_d3:
            sel_fin_test = st.selectbox("🧪 فلترة بناءً على التيست / الصنف:", all_fin_items, key="fin_test_filter")

        if fin_logs:
            df_fin_raw = pd.DataFrame([{
                "الصنف": l["items"]["name"],
                "الكمية": float(l["tests_consumed"] or 0),
                "التكلفة": float(l["cost_incurred"] or 0)
            } for l in fin_logs if l.get("items")])

            if sel_fin_test != "الكل":
                df_fin_raw = df_fin_raw[df_fin_raw["الصنف"] == sel_fin_test]

            if not df_fin_raw.empty:
                fin_grp = df_fin_raw.groupby("الصنف", as_index=False).agg(
                    إجمالي_الكمية=("الكمية", "sum"),
                    إجمالي_التكلفة_جنيه=("التكلفة", "sum")
                )
                fin_grp["متوسط_سعر_الاختبار"] = fin_grp.apply(
                    lambda x: round(x["إجمالي_التكلفة_جنيه"] / x["إجمالي_الكمية"], 2) if x["إجمالي_الكمية"] > 0 else 0.0,
                    axis=1
                )

                fin_tbl_rows = []
                for _, fr in fin_grp.iterrows():
                    fin_tbl_rows.append([
                        (fr["الصنف"], "color:#0e4d92; font-weight:800;"),
                        (f"{fr['إجمالي_الكمية']:,.0f}", "color:#0284c7; font-weight:800;"),
                        (f"{fr['إجمالي_التكلفة_جنيه']:,.2f} ج.م", "color:#0d9488; font-weight:800;"),
                        (f"{fr['متوسط_سعر_الاختبار']:,.2f} ج.م", "font-weight:800;")
                    ])
                render_styled_table(
                    ["الصنف / التيست", "إجمالي الكمية", "إجمالي التكلفة", "متوسط سعر الاختبار"],
                    fin_tbl_rows
                )

                df_fin_export = fin_grp.rename(columns={
                    "الصنف": "الصنف / التيست",
                    "إجمالي_الكمية": "إجمالي الكمية",
                    "إجمالي_التكلفة_جنيه": "إجمالي التكلفة (ج.م)",
                    "متوسط_سعر_الاختبار": "متوسط سعر الاختبار (ج.م)"
                })
                render_export_buttons(
                    df_fin_export,
                    f"financial_by_item_{start_fin}_{end_fin}",
                    "التقرير الكمي والمالي حسب الصنف",
                    f"الفترة: {start_fin} إلى {end_fin} | الصنف: {sel_fin_test}",
                    key_prefix="fin_item_exp"
                )
            else:
                st.info("لا توجد بيانات مطابقة لفلتر الصنف المحدد.")
        else:
            st.info("لا توجد حركات مسجلة في هذه الفترة.")

    with rep_t2:
        c1, c2 = st.columns(2)
        start_d = c1.date_input("من تاريخ", value=date.today().replace(day=1), key="cons_from_d")
        end_d = c2.date_input("إلى تاريخ", value=date.today(), key="cons_to_d")
        
        logs = supabase.table("consumption_logs").select("*, items(name, variant, sub_unit_name), suppliers(name), locations(name)").gte("consumed_at", str(start_d)).lte("consumed_at", str(end_d) + "T23:59:59").execute()
        
        if logs.data:
            cf1, cf2 = st.columns(2)
            cons_items_opts = ["الكل"] + sorted(list({l["items"]["name"] for l in logs.data if l.get("items")}))
            cons_sups_opts = ["الكل"] + sorted(list({l["suppliers"]["name"] for l in logs.data if l.get("suppliers")}))
            with cf1:
                sel_cons_item = st.selectbox("🧪 فلترة حسب الصنف:", cons_items_opts, key="cons_item_filter")
            with cf2:
                sel_cons_sup = st.selectbox("🏭 فلترة حسب الشركة الموردة:", cons_sups_opts, key="cons_sup_filter")

            df_l = pd.DataFrame([{
                "التاريخ": l["consumed_at"][:10],
                "الوحدة/الفرع": l["locations"]["name"],
                "الصنف": l['items']['name'],
                "الشركة الموردة": l["suppliers"]["name"],
                "الكمية المستهلكة": float(l["tests_consumed"]),
                "التكلفة الإجمالية (ج.م)": float(l["cost_incurred"])
            } for l in logs.data])

            if sel_cons_item != "الكل":
                df_l = df_l[df_l["الصنف"] == sel_cons_item]
            if sel_cons_sup != "الكل":
                df_l = df_l[df_l["الشركة الموردة"] == sel_cons_sup]

            if not df_l.empty:
                st.markdown("<h3 class='section-center-title'>ملخص الاستهلاك مقسماً بالصنف والشركة الموردة</h3>", unsafe_allow_html=True)
                summary = df_l.groupby(["الصنف", "الشركة الموردة"], as_index=False).agg(
                    إجمالي_الكمية=("الكمية المستهلكة", "sum"),
                    إجمالي_التكلفة_جنيه=("التكلفة الإجمالية (ج.م)", "sum")
                )
                summary["متوسط_سعر_الاختبار"] = summary.apply(
                    lambda x: round(x["إجمالي_التكلفة_جنيه"] / x["إجمالي_الكمية"], 2) if x["إجمالي_الكمية"] > 0 else 0.0,
                    axis=1
                )
                
                sum_rows = []
                for _, sr in summary.iterrows():
                    sum_rows.append([
                        (sr["الصنف"], "color:#0e4d92; font-weight:800;"),
                        sr["الشركة الموردة"],
                        (f"{sr['إجمالي_الكمية']:,.0f}", "color:#0284c7; font-weight:800;"),
                        (f"{sr['إجمالي_التكلفة_جنيه']:,.2f} ج.م", "color:#0d9488; font-weight:800;"),
                        f"{sr['متوسط_سعر_الاختبار']:,.2f} ج.م"
                    ])
                render_styled_table(
                    ["الصنف", "الشركة الموردة", "إجمالي الكمية", "إجمالي التكلفة", "متوسط سعر الاختبار"],
                    sum_rows
                )

                render_export_buttons(
                    summary,
                    f"consumption_item_supplier_{start_d}_{end_d}",
                    "تقرير الاستهلاك الكمي والمالي بالصنف والشركة",
                    f"الفترة: {start_d} إلى {end_d} | الصنف: {sel_cons_item} | الشركة: {sel_cons_sup}",
                    key_prefix="cons_sum_exp"
                )
                
                with st.expander("عرض السجل التفصيلي لكل حركة سحب"):
                    df_to_styled_table(df_l)
            else:
                st.info("لا توجد حركات مطابقة للفلاتر المختارة.")
        else:
            st.info("لا توجد حركات استهلاك مسجلة في هذه الفترة.")

    with rep_t3:
        st.markdown("<h3 class='section-center-title'>تتبع ومقارنة أسعار التوريد عبر الزمن بين الشركات</h3>", unsafe_allow_html=True)
        batches_res = supabase.table("batches").select("*, items(name, variant), suppliers(name)").order("received_date").execute()
        if batches_res.data:
            df_b = pd.DataFrame([{
                "تاريخ التوريد": b["received_date"],
                "الصنف": b['items']['name'],
                "الشركة الموردة": b["suppliers"]["name"],
                "رقم التشغيلة": b["lot_number"],
                "سعر الاختبار/القطعة (ج.م)": float(b["unit_price_per_test"]),
                "سعر العلبة (ج.م)": float(b["kit_price"])
            } for b in batches_res.data])
            
            pf1, pf2 = st.columns(2)
            with pf1:
                sel_p_item = st.selectbox("🧪 اختر الصنف لمقارنة أسعار شركاته:", sorted(df_b["الصنف"].unique().tolist()), key="price_item_sel")
            with pf2:
                price_sups = ["الكل"] + sorted(df_b[df_b["الصنف"] == sel_p_item]["الشركة الموردة"].unique().tolist())
                sel_p_sup = st.selectbox("🏭 فلترة حسب الشركة الموردة:", price_sups, key="price_sup_sel")

            sub_b = df_b[df_b["الصنف"] == sel_p_item]
            if sel_p_sup != "الكل":
                sub_b = sub_b[sub_b["الشركة الموردة"] == sel_p_sup]
            
            fig_p = px.line(sub_b, x="تاريخ التوريد", y="سعر الاختبار/القطعة (ج.م)", color="الشركة الموردة", markers=True, title=f"تطور ومقارنة سعر ({sel_p_item}) بين الشركات")
            fig_p.update_layout(font_family="Cairo", title_x=0.5, paper_bgcolor="white", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_p, use_container_width=True)
            df_to_styled_table(sub_b)

            render_export_buttons(
                sub_b,
                f"price_comparison_{sel_p_item}",
                f"مقارنة وتطور أسعار {sel_p_item}",
                f"الصنف: {sel_p_item} | الشركة: {sel_p_sup}",
                key_prefix="price_exp"
            )
        else:
            st.info("لم يتم تسجيل فواتير توريد بعد.")

    with rep_t4:
        st.markdown("<h3 class='section-center-title'>📉 تقرير الهدر والفاقد المسجل</h3>", unsafe_allow_html=True)
        try:
            w_res = supabase.table("wastage_logs").select("*, items(name, sub_unit_name), locations(name)").order("id", desc=True).execute()
            w_data = w_res.data or []
        except Exception:
            w_data = []

        if not w_data:
            st.info("لا توجد سجلات هدر محفوظة بعد. يمكنك تسجيلها من شاشة **📉 حساب الهدر**.")
        else:
            wf1, wf2 = st.columns(2)
            with wf1:
                w_locs_opts = ["الكل"] + sorted(list({
                    (r["locations"]["name"] if r.get("locations") and r["locations"].get("name") else "الكل (إجمالي المعمل)")
                    for r in w_data
                }))
                sel_w_rep_loc = st.selectbox("🏥 فلترة حسب الوحدة / الفرع:", w_locs_opts, key="w_rep_loc_sel")
            with wf2:
                w_items_opts = ["الكل"] + sorted(list({r["items"]["name"] for r in w_data if r.get("items")}))
                sel_w_rep_item = st.selectbox("🧪 فلترة حسب الصنف:", w_items_opts, key="w_rep_item_sel")

            w_rows_disp = []
            w_colors_disp = []
            w_export_list = []

            for wr in w_data:
                it_n = wr["items"]["name"] if wr.get("items") else "-"
                loc_n = wr["locations"]["name"] if wr.get("locations") and wr["locations"].get("name") else "الكل (إجمالي المعمل)"

                if sel_w_rep_loc != "الكل" and loc_n != sel_w_rep_loc:
                    continue
                if sel_w_rep_item != "الكل" and it_n != sel_w_rep_item:
                    continue

                w_qty = float(wr.get("wastage_qty") or 0)
                w_pct = float(wr.get("wastage_pct") or 0)
                w_cost = float(wr.get("wastage_cost") or 0)
                allow_pct = float(wr.get("allowed_wastage_pct") or 0)

                bg = "#fee2e2" if w_pct >= 15 else ("#fef9c3" if w_pct > 5 else "#ffffff")
                w_rows_disp.append([
                    (it_n, "font-weight:800;"),
                    (loc_n, "color:#0e4d92; font-weight:800;"),
                    f"{wr['period_from']} إلى {wr['period_to']}",
                    f"{float(wr.get('issued_qty') or 0):,.0f}",
                    f"{allow_pct:.0f}%",
                    f"{float(wr.get('actual_patient_tests') or 0):,.0f}",
                    (f"{w_qty:,.0f}", "font-weight:800;"),
                    (f"{w_pct:.1f}%", "font-weight:800;"),
                    f"{w_cost:,.2f} ج.م",
                    wr.get("notes") or "-"
                ])
                w_colors_disp.append(bg)
                w_export_list.append({
                    "الصنف": it_n,
                    "الوحدة / الفرع": loc_n,
                    "من تاريخ": wr["period_from"],
                    "إلى تاريخ": wr["period_to"],
                    "المسحوب": float(wr.get("issued_qty") or 0),
                    "المسموح %": allow_pct,
                    "الفعلي بالسيستم": float(wr.get("actual_patient_tests") or 0),
                    "كمية الهدر": w_qty,
                    "نسبة الهدر %": w_pct,
                    "تكلفة الهدر (ج.م)": w_cost,
                    "ملاحظات": wr.get("notes") or "-"
                })

            if w_rows_disp:
                render_styled_table(
                    ["الصنف", "الوحدة / الفرع", "الفترة", "المسحوب", "المسموح %", "الفعلي بالسيستم", "كمية الهدر", "نسبة الهدر", "تكلفة الهدر", "ملاحظات"],
                    w_rows_disp,
                    row_bg_colors=w_colors_disp
                )
                render_export_buttons(
                    pd.DataFrame(w_export_list),
                    "wastage_report",
                    "تقرير الهدر والفاقد",
                    f"الجهة: {sel_w_rep_loc} | الصنف: {sel_w_rep_item}",
                    key_prefix="w_rep_exp"
                )

                st.markdown("<br>", unsafe_allow_html=True)
                confirm_reset_w = st.checkbox("تأكيد رغبتي في مسح جميع سجلات الهدر (ريست أول)", key="confirm_reset_wastage_chk")
                if st.button("🔄 ريسيت أول (مسح كل سجلات الهدر)", key="reset_all_wastage_btn"):
                    if not confirm_reset_w:
                        st.warning("⚠️ برجاء تفعيل مربع التأكيد أولاً قبل تنفيذ (ريست أول).")
                    else:
                        supabase.table("wastage_logs").delete().neq("id", 0).execute()
                        log_user_action(
                            user,
                            "ريست أول للهدر",
                            "تقرير الهدر والفاقد",
                            "مسح جميع سجلات الهدر بالكامل",
                            sel_w_rep_loc
                        )
                        st.success("✅ تم تنفيذ (ريست أول) ومسح جميع سجلات الهدر بنجاح!")
                        st.rerun()
            else:
                st.info("لا توجد سجلات مطابقة للفلاتر المختارة.")

    with rep_t5:
        st.markdown("<h3 class='section-center-title'>🕵️ سجل حركات المستخدمين (من قام بأي أكشن ومتى)</h3>", unsafe_allow_html=True)
        try:
            a_res = supabase.table("audit_logs").select("*").order("id", desc=True).limit(200).execute()
            a_data = a_res.data or []
        except Exception:
            a_data = []

        if not a_data:
            st.info("لا توجد حركات مسجلة في سجل التتبع بعد.")
        else:
            af_u1, af_u2 = st.columns(2)
            u_names_opts = ["الكل"] + sorted(list({r.get("full_name") for r in a_data if r.get("full_name")}))
            act_types_opts = ["الكل"] + sorted(list({r.get("action_type") for r in a_data if r.get("action_type")}))
            with af_u1:
                sel_audit_user = st.selectbox("👤 فلترة حسب المستخدم:", u_names_opts, key="audit_u_flt")
            with af_u2:
                sel_audit_act = st.selectbox("⚡ فلترة حسب نوع الأكشن:", act_types_opts, key="audit_act_flt")

            a_rows_disp = []
            a_export_list = []
            for ar in a_data:
                u_fn = ar.get("full_name") or "-"
                a_tp = ar.get("action_type") or "-"
                if sel_audit_user != "الكل" and u_fn != sel_audit_user:
                    continue
                if sel_audit_act != "الكل" and a_tp != sel_audit_act:
                    continue

                dt_str = str(ar.get("created_at") or "")[:19].replace("T", " ")
                a_rows_disp.append([
                    (u_fn, "color:#0e4d92; font-weight:800;"),
                    ar.get("username") or "-",
                    (a_tp, "color:#0284c7; font-weight:800;"),
                    ar.get("page_name") or "-",
                    ar.get("location_name") or "-",
                    ar.get("details") or "-",
                    dt_str
                ])
                a_export_list.append({
                    "المستخدم": u_fn,
                    "اسم الدخول": ar.get("username") or "-",
                    "نوع الأكشن": a_tp,
                    "الشاشة": ar.get("page_name") or "-",
                    "الوحدة / الفرع": ar.get("location_name") or "-",
                    "التفاصيل": ar.get("details") or "-",
                    "التاريخ والوقت": dt_str
                })

            if a_rows_disp:
                render_styled_table(
                    ["المستخدم", "اسم الدخول", "نوع الأكشن", "الشاشة", "الوحدة / الفرع", "التفاصيل", "التاريخ والوقت"],
                    a_rows_disp
                )
                render_export_buttons(
                    pd.DataFrame(a_export_list),
                    f"audit_log_{date.today()}",
                    "سجل حركات المستخدمين",
                    f"المستخدم: {sel_audit_user} | الأكشن: {sel_audit_act}",
                    key_prefix="audit_log_exp"
                )
            else:
                st.info("لا توجد سجلات مطابقة للفلاتر المختارة.")

# =========================================================================
# 13. التكويد
# =========================================================================
elif selected_page == "⚙️ التكويد":
    render_page_header("⚙️ التكويد")
    
    st1, st2, st3 = st.tabs([
        "🧪 الأصناف ومعدلات استهلاكها لكل فرع/وحدة", 
        "🏢 الشركات الموردة", 
        "🏥 المخازن الفرعية والوحدات"
    ])
    
    with st1:
        locs_df = get_df("locations")
        sub_locs_df = locs_df[locs_df["location_type"] != "main"] if not locs_df.empty else pd.DataFrame()
        sub_loc_names = sub_locs_df["name"].tolist() if not sub_locs_df.empty else []
        ALL_LOCS_OPTION = "🌐 كل المخازن الفرعية والوحدات"

        with st.expander("➕ إضافة صنف جديد وربطه بالمخازن الفرعية والوحدات", expanded=True):
            with st.container(border=True):
                c1, c2 = st.columns(2)
                i_name = c1.text_input("اسم الصنف / التحليل (مثال: ALT أو Gloves أو Syringe)", key="new_i_name")
                i_cat = c2.selectbox("التصنيف", ["reagent", "consumable"], format_func=lambda x: "محاليل وكواشف (Reagent)" if x == "reagent" else "مستهلكات طبية (Consumable)", key="new_i_cat")
                i_unit = c1.text_input("وحدة التوريد الكبرى (مثال: علبة، باكيت، راك)", value="علبة", key="new_i_unit")
                i_sub = c2.text_input("وحدة القياس الصغرى (مثال: اختبار، سرنجة، جوانتي)", value="اختبار", key="new_i_sub")

                selected_targets = st.multiselect(
                    "🏥 المخازن الفرعية والوحدات التي تستخدم هذا الصنف:",
                    options=[ALL_LOCS_OPTION] + sub_loc_names,
                    default=[],
                    key="new_item_locs_multi",
                    help="اختر 'كل المخازن الفرعية والوحدات' أو اختر أكثر من فرع/وحدة محددة"
                )

                if ALL_LOCS_OPTION in selected_targets:
                    effective_locs = sub_loc_names
                else:
                    effective_locs = selected_targets

                unit_rates_input = {}
                if effective_locs:
                    st.markdown(f"#### 📏 حدد معدل الاستهلاك الشهري (بالـ **{i_sub}**) لكل مخزن فرعي / وحدة مختارة:")
                    rate_cols = st.columns(2)
                    for idx, loc_n in enumerate(effective_locs):
                        with rate_cols[idx % 2]:
                            unit_rates_input[loc_n] = st.number_input(
                                f"معدل استهلاك ({loc_n}) شهرياً:",
                                min_value=0.0,
                                step=10.0,
                                key=f"add_rate_{loc_n}"
                            )
                    total_monthly_rate = sum(unit_rates_input.values())
                    st.info(f"📊 إجمالي الاستهلاك الشهري الكلي للمعمل من هذا الصنف: **{total_monthly_rate:,.0f}** {i_sub}/شهر")
                else:
                    total_monthly_rate = 0.0
                    st.caption("اختر مخزناً فرعياً أو وحدة واحدة على الأقل لتحديد معدلات الاستهلاك الشهري.")

                if st.button("💾 حفظ الصنف وربطه بالمخازن المختارة", type="primary", key="save_new_item_btn"):
                    if not i_name.strip():
                        st.error("برجاء إدخال اسم الصنف.")
                    elif not effective_locs:
                        st.error("برجاء اختيار مخزن فرعي أو وحدة واحدة على الأقل.")
                    else:
                        try:
                            ins_res = supabase.table("items").insert({
                                "name": i_name.strip(),
                                "variant": "عام",
                                "category": i_cat,
                                "unit_name": i_unit.strip(),
                                "sub_unit_name": i_sub.strip(),
                                "monthly_consumption_rate": float(total_monthly_rate)
                            }).execute()
                            new_item_id = ins_res.data[0]["id"]

                            rates_payload = []
                            for loc_n, r_val in unit_rates_input.items():
                                l_id = int(sub_locs_df[sub_locs_df["name"] == loc_n].iloc[0]["id"])
                                rates_payload.append({
                                    "location_id": l_id,
                                    "item_id": int(new_item_id),
                                    "monthly_tests_rate": float(r_val)
                                })
                            if rates_payload:
                                supabase.table("location_consumption_rates").insert(rates_payload).execute()

                            log_user_action(user, "إضافة صنف", "التكويد", f"إضافة صنف ({i_name.strip()}) بمعدل شهري {total_monthly_rate:,.0f}", "الكل")
                            st.success(f"🎉 تم حفظ الصنف ({i_name.strip()}) وربطه بـ {len(effective_locs)} موقع بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("هذا الصنف مسجل بالفعل. يمكنك تعديله من القسم بالأسفل.")

        st.divider()
        st.subheader("✏️ تعديل أو حذف صنف مسجل (وتعديل المخازن ومعدلات الاستهلاك)")
        items_df = get_df("items")
        rates_df = get_df("location_consumption_rates")

        if not items_df.empty:
            edit_item_choice = st.selectbox("اختر الصنف المراد تعديله أو حذفه:", items_df["name"].tolist(), key="edit_item_sel")
            cur_item = items_df[items_df["name"] == edit_item_choice].iloc[0]
            cur_item_id = int(cur_item["id"])

            cur_rates_map = {}
            if not rates_df.empty and not sub_locs_df.empty:
                item_rates_rows = rates_df[rates_df["item_id"] == cur_item_id]
                for _, rr in item_rates_rows.iterrows():
                    match_loc = sub_locs_df[sub_locs_df["id"] == rr["location_id"]]
                    if not match_loc.empty:
                        cur_rates_map[match_loc.iloc[0]["name"]] = float(rr["monthly_tests_rate"] or 0)

            with st.container(border=True):
                ec1, ec2 = st.columns(2)
                new_i_name = ec1.text_input("اسم الصنف / التحليل", value=cur_item["name"], key="upd_i_name")
                cat_opts = ["reagent", "consumable"]
                new_i_cat = ec2.selectbox("التصنيف", cat_opts, index=cat_opts.index(cur_item["category"]), format_func=lambda x: "محاليل وكواشف (Reagent)" if x == "reagent" else "مستهلكات طبية (Consumable)", key="upd_i_cat")
                new_i_unit = ec1.text_input("وحدة التوريد الكبرى", value=cur_item["unit_name"], key="upd_i_unit")
                cur_sub_val = "اختبار" if cur_item["sub_unit_name"] == "تست" else cur_item["sub_unit_name"]
                new_i_sub = ec2.text_input("وحدة القياس الصغرى", value=cur_sub_val, key="upd_i_sub")

                default_locs = list(cur_rates_map.keys()) if cur_rates_map else []
                edit_selected_targets = st.multiselect(
                    "🏥 المخازن الفرعية والوحدات المربوطة بهذا الصنف:",
                    options=[ALL_LOCS_OPTION] + sub_loc_names,
                    default=default_locs,
                    key=f"edit_locs_multi_{cur_item_id}"
                )

                if ALL_LOCS_OPTION in edit_selected_targets:
                    edit_effective_locs = sub_loc_names
                else:
                    edit_effective_locs = edit_selected_targets

                edit_unit_rates = {}
                if edit_effective_locs:
                    st.markdown(f"#### 📏 تعديل معدل الاستهلاك الشهري (بالـ **{new_i_sub}**) لكل مخزن / وحدة:")
                    er_cols = st.columns(2)
                    for idx, loc_n in enumerate(edit_effective_locs):
                        with er_cols[idx % 2]:
                            edit_unit_rates[loc_n] = st.number_input(
                                f"معدل ({loc_n}) شهرياً:",
                                min_value=0.0,
                                value=cur_rates_map.get(loc_n, 0.0),
                                step=10.0,
                                key=f"upd_rate_{cur_item_id}_{loc_n}"
                            )
                    upd_total_rate = sum(edit_unit_rates.values())
                    st.info(f"📊 إجمالي الاستهلاك الشهري الكلي المحدّث: **{upd_total_rate:,.0f}** {new_i_sub}/شهر")
                else:
                    upd_total_rate = 0.0

                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    if st.button("💾 حفظ تعديلات الصنف والمعدلات", type="primary", key="btn_upd_item"):
                        if not new_i_name.strip():
                            st.error("برجاء إدخال اسم الصنف.")
                        elif not edit_effective_locs:
                            st.error("برجاء اختيار مخزن فرعي أو وحدة واحدة على الأقل.")
                        else:
                            try:
                                supabase.table("items").update({
                                    "name": new_i_name.strip(),
                                    "category": new_i_cat,
                                    "unit_name": new_i_unit.strip(),
                                    "sub_unit_name": new_i_sub.strip(),
                                    "monthly_consumption_rate": float(upd_total_rate)
                                }).eq("id", cur_item_id).execute()

                                supabase.table("location_consumption_rates").delete().eq("item_id", cur_item_id).execute()
                                new_rates_rows = []
                                for loc_n, r_val in edit_unit_rates.items():
                                    l_id = int(sub_locs_df[sub_locs_df["name"] == loc_n].iloc[0]["id"])
                                    new_rates_rows.append({
                                        "location_id": l_id,
                                        "item_id": cur_item_id,
                                        "monthly_tests_rate": float(r_val)
                                    })
                                if new_rates_rows:
                                    supabase.table("location_consumption_rates").insert(new_rates_rows).execute()

                                log_user_action(user, "تعديل صنف", "التكويد", f"تعديل صنف ({new_i_name.strip()}) بمعدل شهري {upd_total_rate:,.0f}", "الكل")
                                st.success("✅ تم تحديث بيانات الصنف ومعدلات كل وحدة/فرع بنجاح!")
                                st.rerun()
                            except Exception:
                                st.error("تعذر التحديث: يوجد صنف آخر بنفس الاسم.")

                with btn_c2:
                    if st.button("🗑️ حذف الصنف نهائياً", key="btn_del_item"):
                        has_batches = supabase.table("batches").select("id").eq("item_id", cur_item_id).limit(1).execute()
                        if has_batches.data:
                            st.error("❌ لا يمكن حذف هذا الصنف لأنه مرتبط بفواتير توريد أو أرصدة سابقة بالمخزن.")
                        else:
                            supabase.table("items").delete().eq("id", cur_item_id).execute()
                            log_user_action(user, "حذف صنف", "التكويد", f"حذف صنف ({cur_item['name']})", "الكل")
                            st.success("🗑️ تم حذف الصنف بنجاح!")
                            st.rerun()

            st.markdown("#### 📋 قائمة الأصناف والمخازن المرتبطة بها حالياً")
            summary_items_list = []
            for _, it_row in items_df.iterrows():
                iid = int(it_row["id"])
                linked_names = []
                if not rates_df.empty and not sub_locs_df.empty:
                    sub_r = rates_df[rates_df["item_id"] == iid]
                    for _, rr in sub_r.iterrows():
                        m_loc = sub_locs_df[sub_locs_df["id"] == rr["location_id"]]
                        if not m_loc.empty:
                            linked_names.append(f"{m_loc.iloc[0]['name']} ({int(rr['monthly_tests_rate'])})")
                sub_u_lbl = "اختبار" if it_row["sub_unit_name"] == "تست" else it_row["sub_unit_name"]
                summary_items_list.append({
                    "الكود": iid,
                    "اسم الصنف": it_row["name"],
                    "التصنيف": "محاليل وكواشف" if it_row["category"] == "reagent" else "مستهلكات",
                    "الوحدة الكبرى": it_row["unit_name"],
                    "الوحدة الصغرى": sub_u_lbl,
                    "المخازن الفرعية والوحدات (المعدل الشهري)": " | ".join(linked_names) if linked_names else "غير مربوط",
                    "الإجمالي الشهري الكلي": float(it_row["monthly_consumption_rate"] or 0)
                })
            df_to_styled_table(pd.DataFrame(summary_items_list))

    with st2:
        with st.expander("➕ إضافة شركة موردة جديدة", expanded=True):
            with st.container(border=True):
                s_name = st.text_input("اسم الشركة الموردة (مثال: Roche, Abbott, Mindray)", key="add_s_name_inp")
                s_contact = st.text_input("بيانات التواصل / المندوب (اختياري)", key="add_s_contact_inp")
                if st.button("➕ إضافة الشركة", type="primary", key="add_s_submit_btn"):
                    if s_name.strip():
                        try:
                            supabase.table("suppliers").insert({"name": s_name.strip(), "contact_info": s_contact.strip()}).execute()
                            log_user_action(user, "إضافة شركة موردة", "التكويد", f"إضافة شركة ({s_name.strip()})", "")
                            st.success("تم إضافة الشركة بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("هذه الشركة مسجلة بالفعل.")
                    else:
                        st.error("برجاء إدخال اسم الشركة.")

        st.divider()
        st.subheader("✏️ تعديل أو حذف شركة موردة")
        sups_df = get_df("suppliers")
        if not sups_df.empty:
            edit_sup_choice = st.selectbox("اختر الشركة المراد تعديلها أو حذفها:", sups_df["name"].tolist(), key="edit_sup_sel")
            cur_sup = sups_df[sups_df["name"] == edit_sup_choice].iloc[0]
            
            with st.container(border=True):
                new_s_name = st.text_input("اسم الشركة الموردة", value=cur_sup["name"], key=f"upd_s_name_{cur_sup['id']}")
                new_s_contact = st.text_input("بيانات التواصل / المندوب", value=cur_sup["contact_info"] or "", key=f"upd_s_cont_{cur_sup['id']}")
                
                sc1, sc2 = st.columns(2)
                with sc1:
                    if st.button("💾 حفظ تعديل الشركة", type="primary", key=f"upd_s_btn_{cur_sup['id']}"):
                        if new_s_name.strip():
                            try:
                                supabase.table("suppliers").update({
                                    "name": new_s_name.strip(),
                                    "contact_info": new_s_contact.strip()
                                }).eq("id", int(cur_sup["id"])).execute()
                                log_user_action(user, "تعديل شركة موردة", "التكويد", f"تعديل شركة ({new_s_name.strip()})", "")
                                st.success("✅ تم تعديل بيانات الشركة بنجاح!")
                                st.rerun()
                            except Exception:
                                st.error("اسم الشركة مستخدم بالفعل.")
                with sc2:
                    if st.button("🗑️ حذف الشركة", key=f"del_s_btn_{cur_sup['id']}"):
                        has_sup_batches = supabase.table("batches").select("id").eq("supplier_id", int(cur_sup["id"])).limit(1).execute()
                        if has_sup_batches.data:
                            st.error("❌ لا يمكن حذف هذه الشركة لأنها مرتبطة بفواتير توريد سابقة.")
                        else:
                            supabase.table("suppliers").delete().eq("id", int(cur_sup["id"])).execute()
                            log_user_action(user, "حذف شركة موردة", "التكويد", f"حذف شركة ({cur_sup['name']})", "")
                            st.success("🗑️ تم حذف الشركة بنجاح!")
                            st.rerun()

            disp_sups = sups_df[["id", "name", "contact_info"]].copy()
            disp_sups.columns = ["الكود", "اسم الشركة", "بيانات التواصل"]
            df_to_styled_table(disp_sups)

    with st3:
        st.subheader("🏥 إدارة المخازن الفرعية ووحدات المعمل")
        LOC_TYPE_LABELS = {
            "branch": "فرع خارجي (مخزن فرعي)",
            "unit": "وحدة داخلية بالمعمل",
            "main": "المخزن الرئيسي"
        }
        
        with st.expander("➕ إضافة مخزن فرعي أو وحدة جديدة", expanded=True):
            with st.container(border=True):
                lc1, lc2 = st.columns(2)
                loc_name_new = lc1.text_input("اسم الفرع أو الوحدة (مثال: فرع مدينة نصر، وحدة الباثولوجي)", key="new_loc_n_inp")
                loc_type_new = lc2.selectbox("نوع الموقع", ["branch", "unit"], format_func=lambda x: LOC_TYPE_LABELS[x], key="new_loc_t_sel")
                
                if st.button("➕ إضافة المخزن الفرعي / الوحدة", type="primary", key="add_loc_submit_btn"):
                    if loc_name_new.strip():
                        try:
                            supabase.table("locations").insert({
                                "name": loc_name_new.strip(),
                                "location_type": loc_type_new
                            }).execute()
                            log_user_action(user, "إضافة موقع", "التكويد", f"إضافة ({loc_name_new.strip()})", loc_name_new.strip())
                            st.success(f"🎉 تم إضافة ({loc_name_new.strip()}) بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("هذا الاسم مسجل بالفعل.")
                    else:
                        st.error("برجاء كتابة اسم الفرع أو الوحدة.")

        st.divider()
        locs_df = get_df("locations")
        sub_locs_edit = locs_df[locs_df["location_type"] != "main"]
        if not sub_locs_edit.empty:
            st.subheader("✏️ تعديل أو حذف مخزن فرعي / وحدة")
            sel_loc_edit = st.selectbox("اختر الفرع أو الوحدة:", sub_locs_edit["name"].tolist(), key="edit_loc_sel")
            cur_loc = sub_locs_edit[sub_locs_edit["name"] == sel_loc_edit].iloc[0]
            
            with st.container(border=True):
                elc1, elc2 = st.columns(2)
                upd_loc_name = elc1.text_input("اسم الفرع / الوحدة", value=cur_loc["name"], key=f"upd_loc_n_{cur_loc['id']}")
                t_opts = ["branch", "unit"]
                upd_loc_type = elc2.selectbox("النوع", t_opts, index=t_opts.index(cur_loc["location_type"]), format_func=lambda x: LOC_TYPE_LABELS[x], key=f"upd_loc_t_{cur_loc['id']}")
                
                lbc1, lbc2 = st.columns(2)
                with lbc1:
                    if st.button("💾 حفظ التعديل", type="primary", key=f"upd_loc_btn_{cur_loc['id']}"):
                        if upd_loc_name.strip():
                            try:
                                supabase.table("locations").update({
                                    "name": upd_loc_name.strip(),
                                    "location_type": upd_loc_type
                                }).eq("id", int(cur_loc["id"])).execute()
                                log_user_action(user, "تعديل موقع", "التكويد", f"تعديل موقع ({upd_loc_name.strip()})", upd_loc_name.strip())
                                st.success("✅ تم تعديل بيانات الموقع بنجاح!")
                                st.rerun()
                            except Exception:
                                st.error("الاسم مستخدم بالفعل.")
                with lbc2:
                    if st.button("🗑️ حذف الفرع / الوحدة", key=f"del_loc_btn_{cur_loc['id']}"):
                        has_inv = supabase.table("inventory").select("id").eq("location_id", int(cur_loc["id"])).gt("tests_available", 0).limit(1).execute()
                        if has_inv.data:
                            st.error("❌ لا يمكن حذف هذا الفرع لأن لديه أرصدة متاحة حالياً.")
                        else:
                            supabase.table("locations").delete().eq("id", int(cur_loc["id"])).execute()
                            log_user_action(user, "حذف موقع", "التكويد", f"حذف موقع ({cur_loc['name']})", cur_loc["name"])
                            st.success("🗑️ تم حذف الموقع بنجاح!")
                            st.rerun()

        disp_locs = locs_df[["id", "name", "location_type"]].copy()
        disp_locs["location_type"] = disp_locs["location_type"].map(LOC_TYPE_LABELS)
        disp_locs.columns = ["الكود", "اسم المخزن / الوحدة", "النوع"]
        df_to_styled_table(disp_locs)

# =========================================================================
# 14. إدارة المستخدمين والصلاحيات
# =========================================================================
elif selected_page == "👥 إدارة المستخدمين والصلاحيات":
    render_page_header("👥 إدارة المستخدمين والصلاحيات")
    
    locs_df = get_df("locations")
    loc_names_all = locs_df["name"].tolist() if not locs_df.empty else ["المخزن الرئيسي"]

    with st.expander("➕ إنشاء حساب مستخدم جديد", expanded=True):
        with st.container(border=True):
            c1, c2 = st.columns(2)
            f_name = c1.text_input("الاسم الكامل للموظف", key="new_u_fn")
            u_name = c2.text_input("اسم الدخول (Username بالإنجليزية)", key="new_u_un")
            u_pass = c1.text_input("كلمة المرور (Password)", type="password", key="new_u_pw")
            u_role = c2.selectbox("الصلاحية / الدور الوظيفي", list(ROLE_LABELS.keys()), format_func=lambda x: ROLE_LABELS[x], key="new_u_rl")
            u_loc = st.selectbox("الفرع / الوحدة التابع لها", loc_names_all, key="new_u_lc")
            u_custom_pages = st.multiselect(
                "☑️ تحديد الشاشات المسموحة للمستخدم (اتركه فارغاً لاستخدام صلاحيات الدور الافتراضية):",
                options=ALL_SYSTEM_PAGES,
                default=[],
                key="new_u_pages_multi"
            )
            
            if st.button("✅ إنشاء الحساب", type="primary", key="create_u_submit_btn"):
                if f_name and u_name and u_pass:
                    loc_id = int(locs_df[locs_df["name"] == u_loc].iloc[0]["id"]) if not locs_df.empty else 1
                    try:
                        base_u_payload = {
                            "full_name": f_name.strip(),
                            "username": u_name.strip(),
                            "password_hash": hash_password(u_pass),
                            "role": u_role,
                            "location_id": loc_id,
                            "is_active": True
                        }
                        if u_custom_pages:
                            try:
                                supabase.table("users").insert({**base_u_payload, "allowed_pages": json.dumps(u_custom_pages, ensure_ascii=False)}).execute()
                            except Exception:
                                supabase.table("users").insert(base_u_payload).execute()
                        else:
                            supabase.table("users").insert(base_u_payload).execute()

                        log_user_action(
                            user,
                            "إنشاء مستخدم",
                            "إدارة المستخدمين والصلاحيات",
                            f"إنشاء حساب ({u_name.strip()}) باسم ({f_name.strip()}) بصلاحية ({ROLE_LABELS.get(u_role, u_role)})",
                            u_loc
                        )
                        st.success(f"🎉 تم إنشاء الحساب! ابعت للموظف البيانات دي:\n- **اسم الدخول:** `{u_name.strip()}`\n- **كلمة المرور:** `{u_pass}`")
                        st.rerun()
                    except Exception:
                        st.error("اسم المستخدم ده موجود قبل كده، اختار اسم تاني.")
                else:
                    st.error("برجاء ملء جميع الحقول.")

    st.divider()
    st.subheader("✏️ تعديل مستخدم (الاسم، الصلاحية، الحالة Active/Inactive، والشاشات المسموحة)")
    all_users_res = supabase.table("users").select("*").order("id").execute().data or []
    if all_users_res:
        user_choice_labels = [f"{u['full_name']} ({u['username']})" for u in all_users_res]
        sel_u_idx = st.selectbox("اختر المستخدم المراد تعديله:", range(len(all_users_res)), format_func=lambda i: user_choice_labels[i], key="edit_u_selector")
        cur_u = all_users_res[sel_u_idx]
        cur_u_id = int(cur_u["id"])

        cur_u_loc_name = loc_names_all[0]
        if not locs_df.empty:
            m_l = locs_df[locs_df["id"] == cur_u.get("location_id")]
            if not m_l.empty:
                cur_u_loc_name = m_l.iloc[0]["name"]

        active_pages_for_u = [normalize_page_key(p) for p in get_effective_pages_for_user(cur_u) if normalize_page_key(p) in ALL_SYSTEM_PAGES]

        with st.container(border=True):
            ec1, ec2 = st.columns(2)
            upd_full_name = ec1.text_input("الاسم الكامل للموظف", value=cur_u["full_name"], key=f"u_fn_{cur_u_id}")
            role_keys = list(ROLE_LABELS.keys())
            cur_r_idx = role_keys.index(cur_u["role"]) if cur_u["role"] in role_keys else 0
            upd_role = ec2.selectbox("الصلاحية / الدور الوظيفي", role_keys, index=cur_r_idx, format_func=lambda x: ROLE_LABELS[x], key=f"u_rl_{cur_u_id}")

            upd_loc_name = ec1.selectbox("الفرع / الوحدة التابع لها", loc_names_all, index=loc_names_all.index(cur_u_loc_name) if cur_u_loc_name in loc_names_all else 0, key=f"u_lc_{cur_u_id}")
            upd_is_active = ec2.selectbox(
                "حالة الحساب (Active / Inactive)",
                options=[True, False],
                index=0 if cur_u.get("is_active", True) else 1,
                format_func=lambda x: "نشط (Active) ✅" if x else "غير نشط / موقوف (Inactive) ❌",
                key=f"u_act_{cur_u_id}"
            )

            upd_pages = st.multiselect(
                "☑️ الشاشات الظاهرة والمسموحة للمستخدم (يمكنك إضافة أو حذف أي شاشة مباشرة):",
                options=ALL_SYSTEM_PAGES,
                default=active_pages_for_u,
                key=f"u_pgs_{cur_u_id}"
            )

            if active_pages_for_u:
                st.markdown("**الشاشات الحالية للمستخدم (اضغط ➖ لحذف شاشة):**")
                p_cols = st.columns(min(len(active_pages_for_u), 3))
                for idx_p, pg_item in enumerate(active_pages_for_u):
                    with p_cols[idx_p % 3]:
                        c_lbl, c_rem = st.columns([3, 1])
                        with c_lbl:
                            st.write(f"• {pg_item}")
                        with c_rem:
                            if st.button("➖", key=f"rem_pg_{cur_u_id}_{idx_p}", help=f"حذف {pg_item}"):
                                remaining_pages = [x for x in active_pages_for_u if x != pg_item]
                                pages_json_rem = json.dumps(remaining_pages, ensure_ascii=False)
                                try:
                                    supabase.table("users").update({"allowed_pages": pages_json_rem}).eq("id", cur_u_id).execute()
                                    if int(user["id"]) == cur_u_id:
                                        st.session_state.user["allowed_pages"] = pages_json_rem
                                    log_user_action(user, "إزالة صلاحية شاشة", "إدارة المستخدمين والصلاحيات", f"إزالة ({pg_item}) من حساب ({cur_u['username']})", upd_loc_name)
                                    st.rerun()
                                except Exception:
                                    st.error("تعذر تحديث الصلاحيات.")

            reset_pass_val = st.text_input("إعادة تعيين كلمة مرور جديدة للمستخدم (اختياري - اتركه فارغاً للإبقاء على الحالية)", type="password", key=f"u_np_{cur_u_id}")

            if st.button("💾 حفظ التعديلات والصلاحيات", type="primary", key=f"save_u_upd_btn_{cur_u_id}"):
                if not upd_full_name.strip():
                    st.error("❌ برجاء إدخال الاسم الكامل.")
                else:
                    new_loc_id = int(locs_df[locs_df["name"] == upd_loc_name].iloc[0]["id"]) if not locs_df.empty else 1
                    upd_payload = {
                        "full_name": upd_full_name.strip(),
                        "role": upd_role,
                        "location_id": new_loc_id,
                        "is_active": bool(upd_is_active)
                    }
                    if reset_pass_val.strip():
                        upd_payload["password_hash"] = hash_password(reset_pass_val.strip())

                    pages_json_str = json.dumps(upd_pages, ensure_ascii=False)
                    try:
                        supabase.table("users").update({**upd_payload, "allowed_pages": pages_json_str}).eq("id", cur_u_id).execute()
                    except Exception:
                        supabase.table("users").update(upd_payload).eq("id", cur_u_id).execute()

                    if int(user["id"]) == cur_u_id:
                        st.session_state.user = {**st.session_state.user, **upd_payload, "allowed_pages": pages_json_str}

                    log_user_action(
                        user,
                        "تعديل مستخدم/صلاحيات",
                        "إدارة المستخدمين والصلاحيات",
                        f"تحديث حساب ({cur_u['username']}) -> الاسم: ({upd_full_name.strip()}) | الصلاحية: ({ROLE_LABELS.get(upd_role, upd_role)}) | الحالة: ({'Active' if upd_is_active else 'Inactive'})",
                        upd_loc_name
                    )
                    st.success("✅ تم حفظ تعديلات المستخدم والصلاحيات بنجاح!")
                    st.rerun()

    st.subheader("قائمة المستخدمين الحاليين")
    users_df = get_df("users")
    if not users_df.empty:
        loc_map_id = {}
        if not locs_df.empty:
            for _, lr in locs_df.iterrows():
                loc_map_id[int(lr["id"])] = lr["name"]

        disp_u_rows = []
        for _, ur in users_df.iterrows():
            u_pages_list = get_effective_pages_for_user(ur.to_dict())
            pages_summary = "، ".join(u_pages_list) if u_pages_list else "-"
            act_txt = ("نشط (Active) ✅", "color:#166534; font-weight:800;") if ur.get("is_active", True) else ("غير نشط (Inactive) ❌", "color:#991b1b; font-weight:800;")
            disp_u_rows.append([
                str(ur["id"]),
                (str(ur["full_name"]), "color:#0e4d92; font-weight:800;"),
                str(ur["username"]),
                ROLE_LABELS.get(ur["role"], ur["role"]),
                loc_map_id.get(int(ur["location_id"]) if ur.get("location_id") else 1, "-"),
                act_txt,
                pages_summary
            ])
        render_styled_table(
            ["الكود", "الاسم الكامل", "اسم الدخول", "الصلاحية", "الوحدة / الفرع", "الحالة", "الشاشات المسموحة"],
            disp_u_rows
        )
