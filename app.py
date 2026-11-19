import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import hashlib
from datetime import datetime, date, timedelta

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

    .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 17px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 12px rgba(14, 77, 146, 0.22) !important;
    }
    .stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
        background: linear-gradient(90deg, #0b3d75 0%, #0369a1 100%) !important;
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

    /* جدول الموافقات الاحترافي بخط كبير وواضح */
    .approvals-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        margin-bottom: 16px;
        direction: rtl;
        text-align: center;
    }
    .approvals-table th {
        background: linear-gradient(90deg, #0e4d92 0%, #0284c7 100%);
        color: #ffffff;
        font-size: 17px;
        font-weight: 800;
        padding: 14px 10px;
        text-align: center !important;
        border: 1px solid #0e4d92;
    }
    .approvals-table td {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
        padding: 14px 10px;
        text-align: center !important;
        border: 1px solid #cbd5e1;
        vertical-align: middle;
    }
    .approvals-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
    .approvals-table tr:hover {
        background-color: #eff6ff;
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
    st.markdown(f"""
    <div class="page-header-banner">
        <h1>{title_text}</h1>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("""
        <div class="login-header-box">
            <div class="login-header-title">🧬 معامل أ.د/ أسامة عبدالمتعال</div>
        </div>
    """, unsafe_allow_html=True)

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
# القائمة الجانبية ومعلومات المستخدم حسب الصلاحية
# =========================================================================
ROLE_LABELS = {
    "chairman": "رئيس مجلس الإدارة",
    "general_manager": "المدير العام",
    "main_storekeeper": "أمين المخزن الرئيسي",
    "unit_supervisor": "مشرف وحدة / فرع"
}

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

    menu_options = []
    if role == "main_storekeeper":
        menu_options = [
            "🏢 المخزن الرئيسي",
            "🛒 الطلبيات",
            "📥 إضافة فاتورة",
            f"📦 أذونات الصرف المعتمدة{approved_badge}",
            "⚙️ التكويد"
        ]
    elif role in ["chairman", "general_manager"]:
        menu_options = [
            "📊 الرئيسية",
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
        menu_options = [
            "🧪 المخازن الفرعية",
            "🔄 أذونات الصرف"
        ]

    selected_page = st.radio("القائمة الرئيسية", menu_options, label_visibility="collapsed")
    st.divider()
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# دوال مساعدة لجلب البيانات
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
    
    expiring_soon = []
    today = date.today()
    for r in filtered_inv:
        if r["tests_available"] > 0 and r.get("batches"):
            exp_d = datetime.strptime(r["batches"]["expiry_date"], "%Y-%m-%d").date()
            days_left = (exp_d - today).days
            if days_left <= 60:
                expiring_soon.append({
                    "الصنف": r['batches']['items']['name'],
                    "الشركة": r["batches"]["suppliers"]["name"],
                    "المخزن": r["locations"]["name"],
                    "رقم التشغيلة": r["batches"]["lot_number"],
                    "تاريخ الصلاحية": r["batches"]["expiry_date"],
                    "الأيام المتبقية": days_left,
                    "الرصيد (اختبار/قطعة)": r["tests_available"]
                })

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid #0e4d92;">
            <div class="kpi-title">💰 إجمالي قيمة المخزون الحالي</div>
            <div class="kpi-value" style="color: #0e4d92;">{total_stock_value:,.2f} ج.م</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid #0284c7;">
            <div class="kpi-title">📉 تكلفة استهلاك آخر {period_days} يوم</div>
            <div class="kpi-value" style="color: #0284c7;">{monthly_cost:,.2f} ج.م</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid #0d9488;">
            <div class="kpi-title">🧪 إجمالي السحب ({period_days} يوم)</div>
            <div class="kpi-value" style="color: #0d9488;">{monthly_tests:,.0f} اختبار/قطعة</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        alert_color = "#dc2626" if len(expiring_soon) > 0 else "#16a34a"
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 5px solid {alert_color};">
            <div class="kpi-title">⚠️ تشغيلات قريبة الانتهاء (≤60 يوم)</div>
            <div class="kpi-value" style="color: {alert_color};">{len(expiring_soon)} تشغيلة</div>
        </div>
        """, unsafe_allow_html=True)

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

    st.divider()
    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        st.markdown("<h3 class='section-center-title'>⏳ تنبيهات الصلاحيات</h3>", unsafe_allow_html=True)
        if expiring_soon:
            st.dataframe(pd.DataFrame(expiring_soon).sort_values("الأيام المتبقية"), use_container_width=True, hide_index=True)
        else:
            st.success("✅ جميع التشغيلات بالمخازن صلاحيتها آمنة (أكثر من 60 يوماً).")
            
    with ai_col2:
        st.markdown("<h3 class='section-center-title'>🔮 التنبؤ بكفاية المخزون الرئيسي</h3>", unsafe_allow_html=True)
        main_inv = [r for r in inv_data if r["location_id"] == 1 and r["tests_available"] > 0 and r.get("batches")]
        if main_inv:
            summary_map = {}
            for r in main_inv:
                it = r["batches"]["items"]
                key = it['name']
                if key not in summary_map:
                    summary_map[key] = {"total": 0, "rate": float(it["monthly_consumption_rate"] or 0)}
                summary_map[key]["total"] += float(r["tests_available"])
            
            ai_alerts = []
            for k, v in summary_map.items():
                if v["rate"] > 0:
                    months_left = v["total"] / v["rate"]
                    status = "🔴 حرج (اطلب فوراً)" if months_left < 1 else ("🟡 تنبيه (أقل من شهرين)" if months_left < 2 else "🟢 آمن")
                    ai_alerts.append({
                        "الصنف": k,
                        "الرصيد الكلي": v["total"],
                        "الاستهلاك الشهري الكلي": v["rate"],
                        "يكفي لمدة (شهر)": round(months_left, 1),
                        "الحالة": status
                    })
            if ai_alerts:
                st.dataframe(pd.DataFrame(ai_alerts).sort_values("يكفي لمدة (شهر)"), use_container_width=True, hide_index=True)
            else:
                st.info("قم بإدخال معدلات الاستهلاك الشهري للأصناف في التكويد لتفعيل التنبؤ التلقائي.")
        else:
            st.info("لا توجد أرصدة في المخزن الرئيسي حالياً.")

# =========================================================================
# 2. المخزن الرئيسي
# =========================================================================
elif selected_page == "🏢 المخزن الرئيسي":
    render_page_header("🏢 المخزن الرئيسي")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(id, name, variant, category, unit_name, sub_unit_name, monthly_consumption_rate), suppliers(name))").eq("location_id", 1).gt("tests_available", 0).execute()
    rows = inv_res.data or []
    
    if not rows:
        st.warning("المخزن الرئيسي فارغ حالياً. اذهب إلى '📥 إضافة فاتورة' لإضافة الأرصدة.")
    else:
        tab1, tab2 = st.tabs(["📊 العرض التجميعي الذكي (كل الشركات معاً + مدة الكفاية)", "🏢 العرض التفصيلي (مفصول حسب الشركة ورقم التشغيلة)"])
        
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
                agg_list.append({
                    "الصنف": k[1],
                    "التصنيف": "محاليل وكواشف" if k[2] == "reagent" else "مستهلكات",
                    "الشركات المتوفرة": " + ".join(v["companies"]),
                    "إجمالي العلب/الباكيت": v["kits"],
                    "إجمالي الرصيد": v["tests"],
                    "الوحدة": k[3],
                    "الاستهلاك الشهري الكلي": rate,
                    "يكفي لمدة (شهور)": f"{months_cov} شهر" if rate > 0 else "غير محدد",
                    "القيمة المالية (ج.م)": round(v["value"], 2)
                })
            st.dataframe(pd.DataFrame(agg_list), use_container_width=True, hide_index=True)

        with tab2:
            st.markdown("<h3 class='section-center-title'>تفاصيل الأرصدة حسب الشركة الموردة ورقم التشغيلة</h3>", unsafe_allow_html=True)
            det_list = []
            for r in rows:
                b = r["batches"]
                it = b["items"]
                sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
                det_list.append({
                    "الصنف": it['name'],
                    "الشركة الموردة": b["suppliers"]["name"],
                    "رقم التشغيلة": b["lot_number"],
                    "تاريخ الصلاحية": b["expiry_date"],
                    "العلب المتاحة": float(r["kits_available"]),
                    "الكمية المتاحة": float(r["tests_available"]),
                    "الوحدة": sub_u,
                    "سعر الوحدة": float(b["unit_price_per_test"]),
                    "إجمالي القيمة": round(float(r["tests_available"]) * float(b["unit_price_per_test"]), 2)
                })
            df_det = pd.DataFrame(det_list).sort_values(["الصنف", "تاريخ الصلاحية"])
            
            filter_item = st.selectbox("فلترة باسم الصنف (اختياري):", ["الكل"] + sorted(df_det["الصنف"].unique().tolist()))
            if filter_item != "الكل":
                df_det = df_det[df_det["الصنف"] == filter_item]
            st.dataframe(df_det, use_container_width=True, hide_index=True)

# =========================================================================
# 3. الطلبيات
# =========================================================================
elif selected_page == "🛒 الطلبيات":
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
    else:
        target_loc_id = int(sub_locs[sub_locs["name"] == sel_order_loc].iloc[0]["id"])
        inv_res = supabase.table("inventory").select("tests_available, batches(item_id)").eq("location_id", target_loc_id).execute()
    
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
            stock_col_title = "الرصيد الحالي بالمخزن الرئيسي"
        else:
            if not rates_df.empty:
                match_r = rates_df[(rates_df["location_id"] == target_loc_id) & (rates_df["item_id"] == iid)]
                rate = float(match_r.iloc[0]["monthly_tests_rate"]) if not match_r.empty else 0.0
            else:
                rate = 0.0
            stock_col_title = f"الرصيد الحالي في ({sel_order_loc})"

        if rate > 0:
            needed_total = rate * months_cover
            current_stock = stock_by_item.get(iid, 0)
            deficit = max(0, needed_total - current_stock)
            unit_label = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
            
            if deficit > 0:
                order_rows.append({
                    "الصنف": it["name"],
                    "التصنيف": it_cat_ar,
                    "الاستهلاك الشهري": rate,
                    f"الاحتياج لـ {months_cover} شهور": needed_total,
                    stock_col_title: current_stock,
                    "العجز المطلوب شراؤه": deficit,
                    "الوحدة": unit_label
                })
    
    if order_rows:
        df_ord = pd.DataFrame(order_rows)
        st.dataframe(df_ord, use_container_width=True, hide_index=True)
        csv = df_ord.to_csv(index=False).encode("utf-8-sig")
        file_tag = "all_lab" if sel_order_loc == "الكل (إجمالي المعمل)" else sel_order_loc
        st.download_button(
            "📥 تحميل الطلبية (Excel / CSV)", 
            data=csv, 
            file_name=f"order_{file_tag}_{months_cover}_months.csv", 
            mime="text/csv", 
            type="primary"
        )
    else:
        st.success("✅ لا يوجد عجز مطلوب شراؤه بناءً على الفلاتر والمدة المحددة!")

# =========================================================================
# 4. المخازن الفرعية
# =========================================================================
elif selected_page == "🧪 المخازن الفرعية":
    render_page_header("🧪 المخازن الفرعية")
    
    locs_df = get_df("locations")
    sub_locs = locs_df[locs_df["location_type"] != "main"]
    
    if role in ["chairman", "general_manager"]:
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            loc_name = st.selectbox("🏥 الوحدة / الفرع:", sub_locs["name"].tolist(), key="sub_loc_gm")
            sel_loc_id = int(sub_locs[sub_locs["name"] == loc_name].iloc[0]["id"])
        with fc2:
            sub_cat_filter = st.selectbox("📂 التصنيف (محاليل / مستهلكات):", ["الكل", "محاليل وكواشف", "مستهلكات"], key="sub_cat_gm")
    else:
        sel_loc_id = user_loc_id
        st.markdown(f"<h3 class='section-center-title'>🏥 مخزن: {user_loc_name}</h3>", unsafe_allow_html=True)
        fc2, fc3 = st.columns(2)
        with fc2:
            sub_cat_filter = st.selectbox("📂 التصنيف (محاليل / مستهلكات):", ["الكل", "محاليل وكواشف", "مستهلكات"], key="sub_cat_sup")

    sub_inv = supabase.table("inventory").select("*, batches(*, items(id, name, category, unit_name, sub_unit_name), suppliers(id, name))").eq("location_id", sel_loc_id).gt("kits_available", 0).execute()
    raw_rows = sub_inv.data or []

    cat_filtered_rows = []
    for r in raw_rows:
        it_cat = "محاليل وكواشف" if r["batches"]["items"]["category"] == "reagent" else "مستهلكات"
        if sub_cat_filter == "الكل" or it_cat == sub_cat_filter:
            cat_filtered_rows.append(r)

    available_item_names = sorted(list({r["batches"]["items"]["name"] for r in cat_filtered_rows}))
    with fc3:
        item_label_title = "🧪 اسم المحلول:" if sub_cat_filter == "محاليل وكواشف" else ("🧤 اسم المستهلك:" if sub_cat_filter == "مستهلكات" else "🔍 اسم المحلول / المستهلك:")
        sel_sub_item = st.selectbox(item_label_title, ["الكل"] + available_item_names, key="sub_item_filter")

    final_sub_rows = [
        r for r in cat_filtered_rows 
        if sel_sub_item == "الكل" or r["batches"]["items"]["name"] == sel_sub_item
    ]

    if not final_sub_rows:
        st.info("لا توجد أرصدة مطابقة للفلاتر المختارة في هذه الوحدة حالياً.")
    else:
        for row in final_sub_rows:
            b = row["batches"]
            it = b["items"]
            sup = b["suppliers"]
            sub_u = "اختبار" if it["sub_unit_name"] == "تست" else it["sub_unit_name"]
            cat_badge = "محاليل وكواشف" if it["category"] == "reagent" else "مستهلكات"
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"### {it['name']} ({cat_badge}) — شركة **{sup['name']}**")
                    st.write(f"**الرصيد المتاح بالوحدة:** `{int(row['kits_available'])}` {it['unit_name']} ({int(row['tests_available'])} {sub_u}) | **رقم التشغيلة:** `{b['lot_number']}` | **الصلاحية:** `{b['expiry_date']}`")
                with c2:
                    kits_pull = st.number_input(f"سحب ({it['unit_name']})", min_value=1, max_value=int(row["kits_available"]), value=1, key=f"pull_qty_{row['id']}")
                with c3:
                    st.write("")
                    st.write("")
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
                        st.success(f"تم سحب {kits_pull} {it['unit_name']} ({tests_pulled} {sub_u}) وخصمها من رصيد الوحدة.")
                        st.rerun()

# =========================================================================
# 5. إضافة فاتورة
# =========================================================================
elif selected_page == "📥 إضافة فاتورة":
    render_page_header("📥 إضافة فاتورة")
    
    items_df = get_df("items")
    suppliers_df = get_df("suppliers")
    
    if items_df.empty or suppliers_df.empty:
        st.warning("⚠️ برجاء إضافة الأصناف والشركات أولاً من صفحة '⚙️ التكويد'.")
    else:
        with st.form("receive_batch_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_choice = st.selectbox("اختر الصنف / التحليل", items_df["name"].tolist())
                selected_item = items_df[items_df["name"] == item_choice].iloc[0]
                sub_u = "اختبار" if selected_item["sub_unit_name"] == "تست" else selected_item["sub_unit_name"]
                
                sup_choice = st.selectbox("الشركة الموردة", suppliers_df["name"].tolist())
                selected_sup = suppliers_df[suppliers_df["name"] == sup_choice].iloc[0]
                
                lot_number = st.text_input("رقم التشغيلة (Lot Number)")
                expiry_date = st.date_input("تاريخ الصلاحية", min_value=date.today())

            with col2:
                kits_qty = st.number_input(f"الكمية الواردة (عدد الـ {selected_item['unit_name']})", min_value=1, step=1)
                tests_per_kit = st.number_input(f"عدد الـ ({sub_u}) داخل كل {selected_item['unit_name']}", min_value=1, value=100, step=1)
                unit_price = st.number_input(f"سعر الـ ({sub_u}) الواحد بالجنيه", min_value=0.0, step=0.1, format="%.2f")
                rec_date = st.date_input("تاريخ التوريد", value=date.today())

            total_tests = kits_qty * tests_per_kit
            kit_price = unit_price * tests_per_kit
            st.info(f"📌 ملخص الإضافة: **{kits_qty}** {selected_item['unit_name']} × **{tests_per_kit}** = **{total_tests}** {sub_u} | سعر العلبة: **{kit_price:,.2f} ج.م** | إجمالي الفاتورة: **{total_tests * unit_price:,.2f} ج.م**")
            
            submitted = st.form_submit_button("✅ تأكيد إضافة الفاتورة للمخزن الرئيسي", type="primary", use_container_width=True)
            if submitted:
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
                    st.success(f"🎉 تم إضافة {kits_qty} {selected_item['unit_name']} ({total_tests} {sub_u}) بنجاح إلى المخزن الرئيسي!")

# =========================================================================
# 6. أذونات الصرف المعتمدة (شاشة أمين المخزن لتنفيذ الصرف بعد موافقة المدير العام)
# =========================================================================
elif selected_page.startswith("📦 أذونات الصرف المعتمدة"):
    render_page_header("📦 أذونات الصرف المعتمدة من المدير العام")
    
    approved = supabase.table("transfer_requests").select("*, locations!transfer_requests_to_location_id_fkey(name), items(name, variant, unit_name), suppliers(name), batches(lot_number, expiry_date, tests_per_kit)").eq("status", "approved_ready_to_issue").execute()
    if not approved.data:
        st.info("✅ لا توجد أذونات صرف معتمدة من المدير العام بانتظار الصرف حالياً.")
    else:
        st.success(f"🔔 لديك **{len(approved.data)}** إذن صرف معتمد من المدير العام وجاهز للتسليم للمخازن الفرعية/الوحدات:")
        for req in approved.data:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**صرف إلى:** {req['locations']['name']} | **الصنف:** {req['items']['name']} - **{req['suppliers']['name']}**")
                    st.caption(f"الكمية المعتمدة: **{req['kits_requested']}** {req['items']['unit_name']} ({req['tests_requested']} اختبار/قطعة) | رقم التشغيلة: `{req['batches']['lot_number']}` | الصلاحية: `{req['batches']['expiry_date']}`")
                with c2:
                    if st.button("📦 تنفيذ الصرف الآن", key=f"iss_store_{req['id']}", type="primary", use_container_width=True):
                        m_inv = supabase.table("inventory").select("*").eq("location_id", 1).eq("batch_id", req["batch_id"]).execute().data[0]
                        new_m_kits = float(m_inv["kits_available"]) - req["kits_requested"]
                        new_m_tests = float(m_inv["tests_available"]) - req["tests_requested"]
                        supabase.table("inventory").update({"kits_available": max(0, new_m_kits), "tests_available": max(0, new_m_tests)}).eq("id", m_inv["id"]).execute()
                        
                        sub_inv_res = supabase.table("inventory").select("*").eq("location_id", req["to_location_id"]).eq("batch_id", req["batch_id"]).execute()
                        if sub_inv_res.data:
                            s_inv = sub_inv_res.data[0]
                            supabase.table("inventory").update({
                                "kits_available": float(s_inv["kits_available"]) + req["kits_requested"],
                                "tests_available": float(s_inv["tests_available"]) + req["tests_requested"]
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
                            "issued_by": user["id"],
                            "issued_at": datetime.now().isoformat()
                        }).eq("id", req["id"]).execute()
                        st.success("🎉 تم الصرف والتحويل للمخزن الفرعي بنجاح!")
                        st.rerun()

# =========================================================================
# 7. أذونات الصرف
# =========================================================================
elif selected_page == "🔄 أذونات الصرف":
    render_page_header("🔄 أذونات الصرف")
    
    t1, t2 = st.tabs(["📝 إنشاء إذن صرف جديد (للوحدات والفروع)", "📦 أذونات الصرف المعتمدة (تنفيذ الصرف)"])
    
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
                if role == "unit_supervisor" and user_loc_id != 1:
                    target_loc_id = user_loc_id
                    st.text_input("الوحدة / الفرع الطالب", value=user_loc_name, disabled=True)
                else:
                    loc_choice = st.selectbox("اختر الوحدة / الفرع الطالب", sub_locs["name"].tolist())
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
                        st.success("✅ تم إرسال إذن الصرف بنجاح وهو الآن في صفحة '✍️ الموافقات'!")
                else:
                    st.error(f"❌ لا يوجد رصيد متاح في المخزن الرئيسي من ({sel_item['name']}) لشركة ({sel_sup['name']}).")

    with t2:
        st.subheader("أذونات الصرف المعتمدة وجاهزة للتحويل للمخازن الفرعية")
        approved = supabase.table("transfer_requests").select("*, locations!transfer_requests_to_location_id_fkey(name), items(name, variant, unit_name), suppliers(name), batches(lot_number, expiry_date, tests_per_kit)").eq("status", "approved_ready_to_issue").execute()
        if not approved.data:
            st.info("لا توجد أذونات صرف معتمدة بانتظار التنفيذ.")
        else:
            for req in approved.data:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**صرف إلى:** {req['locations']['name']} | **الصنف:** {req['items']['name']} - **{req['suppliers']['name']}**")
                        st.caption(f"الكمية المعتمدة: **{req['kits_requested']}** {req['items']['unit_name']} | رقم التشغيلة: `{req['batches']['lot_number']}`")
                    with c2:
                        if role in ["main_storekeeper", "general_manager", "chairman"]:
                            if st.button("📦 تنفيذ الصرف الآن", key=f"iss_{req['id']}", type="primary"):
                                m_inv = supabase.table("inventory").select("*").eq("location_id", 1).eq("batch_id", req["batch_id"]).execute().data[0]
                                new_m_kits = float(m_inv["kits_available"]) - req["kits_requested"]
                                new_m_tests = float(m_inv["tests_available"]) - req["tests_requested"]
                                supabase.table("inventory").update({"kits_available": max(0, new_m_kits), "tests_available": max(0, new_m_tests)}).eq("id", m_inv["id"]).execute()
                                
                                sub_inv_res = supabase.table("inventory").select("*").eq("location_id", req["to_location_id"]).eq("batch_id", req["batch_id"]).execute()
                                if sub_inv_res.data:
                                    s_inv = sub_inv_res.data[0]
                                    supabase.table("inventory").update({
                                        "kits_available": float(s_inv["kits_available"]) + req["kits_requested"],
                                        "tests_available": float(s_inv["tests_available"]) + req["tests_requested"]
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
                                    "issued_by": user["id"],
                                    "issued_at": datetime.now().isoformat()
                                }).eq("id", req["id"]).execute()
                                st.success("تم الصرف والتحويل بنجاح!")
                                st.rerun()

# =========================================================================
# 8. الموافقات (عرض جدولي كبير وواضح للعين المجردة + اعتماد فردي وجماعي)
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
            if st.button(f"✅ موافقة واعتماد All ({len(filtered_pending)} طلب)", type="primary", use_container_width=True, key="approve_all_filtered_btn"):
                ids_to_approve = [r["id"] for r in filtered_pending]
                supabase.table("transfer_requests").update({
                    "status": "approved_ready_to_issue",
                    "approved_by": user["id"],
                    "approved_at": datetime.now().isoformat()
                }).in_("id", ids_to_approve).execute()
                st.success(f"🎉 تم اعتماد والموافقة على {len(ids_to_approve)} طلب دفعة واحدة!")
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # بناء صفوف الجدول الكامل الواضح
            table_rows_html = ""
            enriched_requests = []

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
                
                enriched_requests.append({
                    "req": req,
                    "qty_txt": qty_txt,
                    "req_coverage_txt": req_coverage_txt,
                    "cur_stock_txt": cur_stock_txt
                })

                table_rows_html += f"""
                <tr>
                    <td style="color:#0e4d92; font-weight:800;">{req['locations']['name']}</td>
                    <td style="font-weight:800;">{req['items']['name']}</td>
                    <td>{req['suppliers']['name']}</td>
                    <td style="color:#0284c7; font-weight:800;">{qty_txt}</td>
                    <td style="color:#0d9488; font-weight:800;">{req_coverage_txt}</td>
                    <td>{cur_stock_txt}</td>
                    <td dir="ltr">{req['batches']['lot_number']}</td>
                    <td dir="ltr">{req['batches']['expiry_date']}</td>
                </tr>
                """

            st.markdown(f"""
            <table class="approvals-table">
                <thead>
                    <tr>
                        <th>الجهة الطالبة</th>
                        <th>الصنف</th>
                        <th>الشركة</th>
                        <th>الكمية المطلوبة</th>
                        <th>تكفي لمدة</th>
                        <th>الرصيد الحالي بالوحدة</th>
                        <th>رقم التشغيلة</th>
                        <th>الصلاحية</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            st.markdown("<h3 class='section-center-title'>⚡ اعتماد أو رفض الطلبات</h3>", unsafe_allow_html=True)
            for item_info in enriched_requests:
                req = item_info["req"]
                with st.container(border=True):
                    c_info, c_app, c_rej = st.columns([3.5, 0.85, 0.65])
                    with c_info:
                        st.markdown(
                            f"<div style='font-size:18px; font-weight:800; color:#0f172a;'>"
                            f"🏥 <span style='color:#0e4d92;'>{req['locations']['name']}</span> &nbsp;|&nbsp; "
                            f"🧪 {req['items']['name']} ({req['suppliers']['name']}) &nbsp;|&nbsp; "
                            f"📦 <span style='color:#0284c7;'>{item_info['qty_txt']}</span> &nbsp;|&nbsp; "
                            f"⏳ تكفي: <span style='color:#0d9488;'>{item_info['req_coverage_txt']}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with c_app:
                        if st.button("✅ موافقة واعتماد", key=f"app_{req['id']}", type="primary", use_container_width=True):
                            supabase.table("transfer_requests").update({
                                "status": "approved_ready_to_issue",
                                "approved_by": user["id"],
                                "approved_at": datetime.now().isoformat()
                            }).eq("id", req["id"]).execute()
                            st.rerun()
                    with c_rej:
                        if st.button("❌ رفض", key=f"rej_{req['id']}", use_container_width=True):
                            supabase.table("transfer_requests").update({"status": "rejected"}).eq("id", req["id"]).execute()
                            st.rerun()

# =========================================================================
# 9. التقارير
# =========================================================================
elif selected_page == "📈 التقارير":
    render_page_header("📈 التقارير")
    
    rep_t1, rep_t2 = st.tabs(["📊 تقرير الاستهلاك الكمي والمالي (حسب الفترة والشركة)", "💲 مقارنة وتطور أسعار الشركات الموردة"])
    
    with rep_t1:
        c1, c2 = st.columns(2)
        start_d = c1.date_input("من تاريخ", value=date.today().replace(day=1))
        end_d = c2.date_input("إلى تاريخ", value=date.today())
        
        logs = supabase.table("consumption_logs").select("*, items(name, variant, sub_unit_name), suppliers(name), locations(name)").gte("consumed_at", str(start_d)).lte("consumed_at", str(end_d) + "T23:59:59").execute()
        
        if logs.data:
            df_l = pd.DataFrame([{
                "التاريخ": l["consumed_at"][:10],
                "الوحدة/الفرع": l["locations"]["name"],
                "الصنف": l['items']['name'],
                "الشركة الموردة": l["suppliers"]["name"],
                "الكمية المستهلكة": float(l["tests_consumed"]),
                "التكلفة الإجمالية (ج.م)": float(l["cost_incurred"])
            } for l in logs.data])
            
            st.markdown("<h3 class='section-center-title'>ملخص الاستهلاك مقسماً بالصنف والشركة الموردة</h3>", unsafe_allow_html=True)
            summary = df_l.groupby(["الصنف", "الشركة الموردة"]).agg(
                إجمالي_الكمية=("الكمية المستهلكة", "sum"),
                إجمالي_التكلفة_جنيه=("التكلفة الإجمالية (ج.م)", "sum")
            ).reset_index()
            summary["متوسط_سعر_الاختبار"] = (summary["إجمالي_التكلفة_جنيه"] / summary["إجمالي_الكمية"]).round(2)
            st.dataframe(summary, use_container_width=True, hide_index=True)
            
            with st.expander("عرض السجل التفصيلي لكل حركة سحب"):
                st.dataframe(df_l, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد حركات استهلاك مسجلة في هذه الفترة.")

    with rep_t2:
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
            
            sel_p_item = st.selectbox("اختر الصنف لمقارنة أسعار شركاته:", sorted(df_b["الصنف"].unique().tolist()))
            sub_b = df_b[df_b["الصنف"] == sel_p_item]
            
            fig_p = px.line(sub_b, x="تاريخ التوريد", y="سعر الاختبار/القطعة (ج.م)", color="الشركة الموردة", markers=True, title=f"تطور ومقارنة سعر ({sel_p_item}) بين الشركات")
            fig_p.update_layout(font_family="Cairo", title_x=0.5, paper_bgcolor="white", plot_bgcolor="#f8fafc")
            st.plotly_chart(fig_p, use_container_width=True)
            st.dataframe(sub_b, use_container_width=True, hide_index=True)
        else:
            st.info("لم يتم تسجيل فواتير توريد بعد.")

# =========================================================================
# 10. التكويد
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

            if st.button("💾 حفظ الصنف وربطه بالمخازن المختارة", type="primary", use_container_width=True, key="save_new_item_btn"):
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
                if st.button("💾 حفظ تعديلات الصنف والمعدلات", type="primary", use_container_width=True, key="btn_upd_item"):
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

                            st.success("✅ تم تحديث بيانات الصنف ومعدلات كل وحدة/فرع بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("تعذر التحديث: يوجد صنف آخر بنفس الاسم.")

            with btn_c2:
                if st.button("🗑️ حذف الصنف نهائياً", use_container_width=True, key="btn_del_item"):
                    has_batches = supabase.table("batches").select("id").eq("item_id", cur_item_id).limit(1).execute()
                    if has_batches.data:
                        st.error("❌ لا يمكن حذف هذا الصنف لأنه مرتبط بفواتير توريد أو أرصدة سابقة بالمخزن.")
                    else:
                        supabase.table("items").delete().eq("id", cur_item_id).execute()
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
            st.dataframe(pd.DataFrame(summary_items_list), use_container_width=True, hide_index=True)

    with st2:
        with st.expander("➕ إضافة شركة موردة جديدة", expanded=True):
            with st.form("add_sup_form"):
                s_name = st.text_input("اسم الشركة الموردة (مثال: Roche, Abbott, Mindray)")
                s_contact = st.text_input("بيانات التواصل / المندوب (اختياري)")
                if st.form_submit_button("➕ إضافة الشركة", type="primary"):
                    if s_name.strip():
                        try:
                            supabase.table("suppliers").insert({"name": s_name.strip(), "contact_info": s_contact.strip()}).execute()
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
            
            with st.form("edit_sup_form"):
                new_s_name = st.text_input("اسم الشركة الموردة", value=cur_sup["name"])
                new_s_contact = st.text_input("بيانات التواصل / المندوب", value=cur_sup["contact_info"] or "")
                
                sc1, sc2 = st.columns(2)
                upd_sup_btn = sc1.form_submit_button("💾 حفظ تعديل الشركة", type="primary", use_container_width=True)
                del_sup_btn = sc2.form_submit_button("🗑️ حذف الشركة", use_container_width=True)
                
                if upd_sup_btn:
                    if new_s_name.strip():
                        try:
                            supabase.table("suppliers").update({
                                "name": new_s_name.strip(),
                                "contact_info": new_s_contact.strip()
                            }).eq("id", int(cur_sup["id"])).execute()
                            st.success("✅ تم تعديل بيانات الشركة بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("اسم الشركة مستخدم بالفعل.")
                            
                if del_sup_btn:
                    has_sup_batches = supabase.table("batches").select("id").eq("supplier_id", int(cur_sup["id"])).limit(1).execute()
                    if has_sup_batches.data:
                        st.error("❌ لا يمكن حذف هذه الشركة لأنها مرتبطة بفواتير توريد سابقة.")
                    else:
                        supabase.table("suppliers").delete().eq("id", int(cur_sup["id"])).execute()
                        st.success("🗑️ تم حذف الشركة بنجاح!")
                        st.rerun()

            disp_sups = sups_df[["id", "name", "contact_info"]].copy()
            disp_sups.columns = ["الكود", "اسم الشركة", "بيانات التواصل"]
            st.dataframe(disp_sups, use_container_width=True, hide_index=True)

    with st3:
        st.subheader("🏥 إدارة المخازن الفرعية ووحدات المعمل")
        LOC_TYPE_LABELS = {
            "branch": "فرع خارجي (مخزن فرعي)",
            "unit": "وحدة داخلية بالمعمل",
            "main": "المخزن الرئيسي"
        }
        
        with st.expander("➕ إضافة مخزن فرعي أو وحدة جديدة", expanded=True):
            with st.form("add_loc_form"):
                lc1, lc2 = st.columns(2)
                loc_name_new = lc1.text_input("اسم الفرع أو الوحدة (مثال: فرع مدينة نصر، وحدة الباثولوجي)")
                loc_type_new = lc2.selectbox("نوع الموقع", ["branch", "unit"], format_func=lambda x: LOC_TYPE_LABELS[x])
                
                if st.form_submit_button("➕ إضافة المخزن الفرعي / الوحدة", type="primary"):
                    if loc_name_new.strip():
                        try:
                            supabase.table("locations").insert({
                                "name": loc_name_new.strip(),
                                "location_type": loc_type_new
                            }).execute()
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
            
            with st.form("edit_loc_form"):
                elc1, elc2 = st.columns(2)
                upd_loc_name = elc1.text_input("اسم الفرع / الوحدة", value=cur_loc["name"])
                t_opts = ["branch", "unit"]
                upd_loc_type = elc2.selectbox("النوع", t_opts, index=t_opts.index(cur_loc["location_type"]), format_func=lambda x: LOC_TYPE_LABELS[x])
                
                lbc1, lbc2 = st.columns(2)
                upd_loc_btn = lbc1.form_submit_button("💾 حفظ التعديل", type="primary", use_container_width=True)
                del_loc_btn = lbc2.form_submit_button("🗑️ حذف الفرع / الوحدة", use_container_width=True)
                
                if upd_loc_btn and upd_loc_name.strip():
                    try:
                        supabase.table("locations").update({
                            "name": upd_loc_name.strip(),
                            "location_type": upd_loc_type
                        }).eq("id", int(cur_loc["id"])).execute()
                        st.success("✅ تم تعديل بيانات الموقع بنجاح!")
                        st.rerun()
                    except Exception:
                        st.error("الاسم مستخدم بالفعل.")
                        
                if del_loc_btn:
                    has_inv = supabase.table("inventory").select("id").eq("location_id", int(cur_loc["id"])).gt("tests_available", 0).limit(1).execute()
                    if has_inv.data:
                        st.error("❌ لا يمكن حذف هذا الفرع لأن لديه أرصدة متاحة حالياً.")
                    else:
                        supabase.table("locations").delete().eq("id", int(cur_loc["id"])).execute()
                        st.success("🗑️ تم حذف الموقع بنجاح!")
                        st.rerun()

        disp_locs = locs_df[["id", "name", "location_type"]].copy()
        disp_locs["location_type"] = disp_locs["location_type"].map(LOC_TYPE_LABELS)
        disp_locs.columns = ["الكود", "اسم المخزن / الوحدة", "النوع"]
        st.dataframe(disp_locs, use_container_width=True, hide_index=True)

# =========================================================================
# 11. إدارة المستخدمين والصلاحيات
# =========================================================================
elif selected_page == "👥 إدارة المستخدمين والصلاحيات":
    render_page_header("👥 إدارة المستخدمين والصلاحيات")
    
    locs_df = get_df("locations")
    with st.form("create_user_form"):
        c1, c2 = st.columns(2)
        f_name = c1.text_input("الاسم الكامل للموظف")
        u_name = c2.text_input("اسم الدخول (Username بالإنجليزية)")
        u_pass = c1.text_input("كلمة المرور (Password)", type="password")
        u_role = c2.selectbox("الصلاحية / الدور الوظيفي", list(ROLE_LABELS.keys()), format_func=lambda x: ROLE_LABELS[x])
        u_loc = st.selectbox("الفرع / الوحدة التابع لها", locs_df["name"].tolist())
        
        if st.form_submit_button("✅ إنشاء الحساب", type="primary"):
            if f_name and u_name and u_pass:
                loc_id = int(locs_df[locs_df["name"] == u_loc].iloc[0]["id"])
                try:
                    supabase.table("users").insert({
                        "full_name": f_name.strip(),
                        "username": u_name.strip(),
                        "password_hash": hash_password(u_pass),
                        "role": u_role,
                        "location_id": loc_id
                    }).execute()
                    st.success(f"🎉 تم إنشاء الحساب! ابعت للموظف البيانات دي:\n- **اسم الدخول:** `{u_name.strip()}`\n- **كلمة المرور:** `{u_pass}`")
                except Exception:
                    st.error("اسم المستخدم ده موجود قبل كده، اختار اسم تاني.")
            else:
                st.error("برجاء ملء جميع الحقول.")
                
    st.subheader("قائمة المستخدمين الحاليين")
    users_df = get_df("users", "id, full_name, username, role, is_active")
    if not users_df.empty:
        users_df["role"] = users_df["role"].map(ROLE_LABELS)
        users_df.columns = ["الكود", "الاسم الكامل", "اسم الدخول", "الصلاحية", "نشط"]
        st.dataframe(users_df, use_container_width=True, hide_index=True)
