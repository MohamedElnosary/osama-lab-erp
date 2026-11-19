import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import hashlib
from datetime import datetime, date, timedelta

# =========================================================================
# إعدادات الصفحة والتنسيق العام (واجهة عربية احترافية)
# =========================================================================
st.set_page_config(
    page_title="معامل د. أسامة عبدالمتعال",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0e4d92;
        color: white;
    }
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* =====================================================================
       تنسيق القائمة الجانبية الاحترافي (كروت تنقل عريضة وخط كبير)
       ===================================================================== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #eff6ff 100%) !important;
        border-left: 2px solid #cbd5e1 !important;
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
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        border-color: #0284c7 !important;
        background-color: #f0f9ff !important;
        transform: translateX(-3px);
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        font-size: 17px !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        line-height: 1.4 !important;
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
# نظام تسجيل الدخول (تصميم عصري جذاب ومضغوط في المنتصف)
# =========================================================================
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown("""
    <style>
        .stApp {
            background: radial-gradient(circle at top right, #bae6fd 0%, #f0f9ff 45%, #e0e7ff 100%);
        }
        [data-testid="stForm"] {
            max-width: 410px !important;
            margin: 0 auto !important;
            background: rgba(255, 255, 255, 0.96) !important;
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

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
        <h1 style='text-align: center;
                   background: linear-gradient(90deg, #0e4d92, #0284c7);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   font-size: 38px;
                   font-weight: 800;
                   margin-bottom: 18px;'>
            🧬 معامل د. أسامة عبدالمتعال
        </h1>
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
# القائمة الجانبية ومعلومات المستخدم (مرتبة بالمسميات المطلوبة)
# =========================================================================
ROLE_LABELS = {
    "chairman": "رئيس مجلس الإدارة",
    "general_manager": "المدير العام",
    "main_storekeeper": "أمين المخزن الرئيسي",
    "unit_supervisor": "مشرف وحدة / فرع"
}

with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #0e4d92; font-weight: 800; margin-bottom: 12px;'>🧬 معامل د. أسامة عبدالمتعال</h2>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #0e4d92 0%, #0284c7 100%);
                color: white;
                padding: 14px 16px;
                border-radius: 14px;
                text-align: center;
                font-size: 20px;
                font-weight: 700;
                box-shadow: 0 4px 10px rgba(14, 77, 146, 0.2);
                margin-bottom: 18px;'>
        👤 {user['full_name']}
    </div>
    """, unsafe_allow_html=True)
    
    menu_options = []
    if role in ["chairman", "general_manager"]:
        menu_options.append("📊 الرئيسية")
    if role in ["chairman", "general_manager", "main_storekeeper"]:
        menu_options.append("🏢 المخزن الرئيسي")
        menu_options.append("🛒 الطلبيات")
    menu_options.append("🧪 المخازن الفرعية")
    if role in ["chairman", "general_manager", "main_storekeeper"]:
        menu_options.append("📥 إضافة فاتورة")
    menu_options.append("🔄 أذونات الصرف")
    if role in ["chairman", "general_manager"]:
        menu_options.append("✍️ الموافقات")
    if role in ["chairman", "general_manager", "main_storekeeper"]:
        menu_options.append("📈 التقارير")
        menu_options.append("⚙️ التكويد")
    if role in ["chairman", "general_manager"]:
        menu_options.append("👥 إدارة المستخدمين والصلاحيات")

    selected_page = st.radio("القائمة الرئيسية", menu_options, label_visibility="collapsed")
    st.divider()
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# دوال مساعدة لجلب البيانات
def get_df(table_name, select_query="*"):
    res = supabase.table(table_name).select(select_query).order("id").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

# =========================================================================
# 1. الرئيسية (لوحة القيادة التنفيذية والذكاء الاصطناعي)
# =========================================================================
if selected_page == "📊 الرئيسية":
    st.title("📊 الرئيسية — لوحة القيادة والتحليلات الذكية")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(name, variant, category, monthly_consumption_rate), suppliers(name)), locations(name, location_type)").execute()
    cons_res = supabase.table("consumption_logs").select("*, items(name, variant), suppliers(name), locations(name)").execute()
    
    inv_data = inv_res.data or []
    cons_data = cons_res.data or []
    
    total_stock_value = sum(r["tests_available"] * r["batches"]["unit_price_per_test"] for r in inv_data if r.get("batches"))
    
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    recent_cons = [c for c in cons_data if c["consumed_at"] >= thirty_days_ago]
    monthly_cost = sum(c["cost_incurred"] for c in recent_cons)
    monthly_tests = sum(c["tests_consumed"] for c in recent_cons)
    
    expiring_soon = []
    today = date.today()
    for r in inv_data:
        if r["tests_available"] > 0 and r.get("batches"):
            exp_d = datetime.strptime(r["batches"]["expiry_date"], "%Y-%m-%d").date()
            days_left = (exp_d - today).days
            if days_left <= 60:
                expiring_soon.append({
                    "الصنف": f"{r['batches']['items']['name']} ({r['batches']['items']['variant']})",
                    "الشركة": r["batches"]["suppliers"]["name"],
                    "المخزن": r["locations"]["name"],
                    "Lot": r["batches"]["lot_number"],
                    "تاريخ الصلاحية": r["batches"]["expiry_date"],
                    "الأيام المتبقية": days_left,
                    "الرصيد (تست/قطعة)": r["tests_available"]
                })

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 إجمالي قيمة المخزون الحالي", f"{total_stock_value:,.2f} ج.م")
    c2.metric("📉 تكلفة استهلاك آخر 30 يوم", f"{monthly_cost:,.2f} ج.م")
    c3.metric("🧪 إجمالي السحب (30 يوم)", f"{monthly_tests:,.0f} تست/قطعة")
    c4.metric("⚠️ تشغيلات قريبة الانتهاء (≤60 يوم)", f"{len(expiring_soon)} تشغيلة")

    st.divider()
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🔥 أكثر الأصناف سحباً (حسب التكلفة المالية)")
        if recent_cons:
            df_c = pd.DataFrame([{
                "الصنف": f"{c['items']['name']} ({c['items']['variant']})",
                "التكلفة": c["cost_incurred"],
                "الكمية": c["tests_consumed"]
            } for c in recent_cons])
            top_cost = df_c.groupby("الصنف")["التكلفة"].sum().reset_index().sort_values("التكلفة", ascending=False).head(10)
            fig1 = px.bar(top_cost, x="الصنف", y="التكلفة", color="التكلفة", color_continuous_scale="Blues", text_auto='.0f')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("لا توجد حركات سحب مسجلة خلال آخر 30 يوم لعرض الرسم البياني.")

    with col_b:
        st.subheader("🏭 توزيع قيمة المخزون حسب الشركات الموردة")
        if inv_data:
            df_s = pd.DataFrame([{
                "الشركة": r["batches"]["suppliers"]["name"],
                "القيمة": r["tests_available"] * r["batches"]["unit_price_per_test"]
            } for r in inv_data if r["tests_available"] > 0 and r.get("batches")])
            if not df_s.empty:
                sup_val = df_s.groupby("الشركة")["القيمة"].sum().reset_index()
                fig2 = px.pie(sup_val, names="الشركة", values="القيمة", hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("المخزون الحالي فارغ.")
        else:
            st.info("لا توجد أرصدة مسجلة بعد.")

    st.subheader("🤖 مساعد الذكاء الاصطناعي: التنبؤ بالاستهلاك وتنبيهات الهدر")
    ai_col1, ai_col2 = st.columns(2)
    with ai_col1:
        st.markdown("#### ⏳ تنبيهات انتهاء الصلاحية (FEFO Priority)")
        if expiring_soon:
            st.dataframe(pd.DataFrame(expiring_soon).sort_values("الأيام المتبقية"), use_container_width=True, hide_index=True)
        else:
            st.success("✅ جميع التشغيلات بالمخازن صلاحيتها آمنة (أكثر من 60 يوماً).")
            
    with ai_col2:
        st.markdown("#### 🔮 التنبؤ الذكي بكفاية المخزون الرئيسي")
        main_inv = [r for r in inv_data if r["location_id"] == 1 and r["tests_available"] > 0 and r.get("batches")]
        if main_inv:
            summary_map = {}
            for r in main_inv:
                it = r["batches"]["items"]
                key = f"{it['name']} ({it['variant']})"
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
                        "الاستهلاك الشهري": v["rate"],
                        "يكفي لمدة (شهر)": round(months_left, 1),
                        "الحالة": status
                    })
            if ai_alerts:
                st.dataframe(pd.DataFrame(ai_alerts).sort_values("يكفي لمدة (شهر)"), use_container_width=True, hide_index=True)
            else:
                st.info("قم بإدخال معدلات الاستهلاك الشهري للأصناف لتفعيل التنبؤ التلقائي.")
        else:
            st.info("لا توجد أرصدة في المخزن الرئيسي حالياً.")

# =========================================================================
# 2. المخزن الرئيسي (عرض مزدوج: حسب الشركة + تجميعي بالكفاية الشهرية)
# =========================================================================
elif selected_page == "🏢 المخزن الرئيسي":
    st.title("🏢 أرصدة المخزن الرئيسي")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(id, name, variant, category, unit_name, sub_unit_name, monthly_consumption_rate), suppliers(name))").eq("location_id", 1).gt("tests_available", 0).execute()
    rows = inv_res.data or []
    
    if not rows:
        st.warning("المخزن الرئيسي فارغ حالياً. اذهب إلى '📥 إضافة فاتورة' لإضافة الأرصدة.")
    else:
        tab1, tab2 = st.tabs(["📊 العرض التجميعي الذكي (كل الشركات معاً + مدة الكفاية)", "🏢 العرض التفصيلي (مفصول حسب الشركة والـ Lot)"])
        
        with tab1:
            st.subheader("إجمالي الرصيد الكلي لكل تحليل/صنف ومدة كفايته")
            agg = {}
            for r in rows:
                it = r["batches"]["items"]
                key = (it["id"], it["name"], it["variant"], it["category"], it["sub_unit_name"], float(it["monthly_consumption_rate"] or 0))
                if key not in agg:
                    agg[key] = {"kits": 0.0, "tests": 0.0, "value": 0.0, "companies": set()}
                agg[key]["kits"] += float(r["kits_available"])
                agg[key]["tests"] += float(r["tests_available"])
                agg[key]["value"] += float(r["tests_available"]) * float(r["batches"]["unit_price_per_test"])
                agg[key]["companies"].add(r["batches"]["suppliers"]["name"])
            
            agg_list = []
            for k, v in agg.items():
                rate = k[5]
                months_cov = round(v["tests"] / rate, 2) if rate > 0 else 0
                agg_list.append({
                    "الصنف": k[1],
                    "النوع/المقاس": k[2],
                    "التصنيف": "محاليل وكواشف" if k[3] == "reagent" else "مستهلكات",
                    "الشركات المتوفرة": " + ".join(v["companies"]),
                    "إجمالي العلب/الباكيت": v["kits"],
                    f"إجمالي الرصيد ({k[4]})": v["tests"],
                    "الاستهلاك الشهري": rate,
                    "يكفي لمدة (شهور)": f"{months_cov} شهر" if rate > 0 else "غير محدد",
                    "القيمة المالية (ج.م)": round(v["value"], 2)
                })
            st.dataframe(pd.DataFrame(agg_list), use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("تفاصيل الأرصدة حسب الشركة الموردة ورقم التشغيلة (Lot)")
            det_list = []
            for r in rows:
                b = r["batches"]
                it = b["items"]
                det_list.append({
                    "الصنف": f"{it['name']} ({it['variant']})",
                    "الشركة الموردة": b["suppliers"]["name"],
                    "Lot Number": b["lot_number"],
                    "تاريخ الصلاحية": b["expiry_date"],
                    "العلب المتاحة": float(r["kits_available"]),
                    "التستات/القطع المتاحة": float(r["tests_available"]),
                    "سعر التست/القطعة": float(b["unit_price_per_test"]),
                    "إجمالي القيمة": round(float(r["tests_available"]) * float(b["unit_price_per_test"]), 2)
                })
            df_det = pd.DataFrame(det_list).sort_values(["الصنف", "تاريخ الصلاحية"])
            
            filter_item = st.selectbox("فلترة باسم الصنف (اختياري):", ["الكل"] + sorted(df_det["الصنف"].unique().tolist()))
            if filter_item != "الكل":
                df_det = df_det[df_det["الصنف"] == filter_item]
            st.dataframe(df_det, use_container_width=True, hide_index=True)

# =========================================================================
# 3. الطلبيات (طلبيات الشراء من الشركات للمخزن الرئيسي)
# =========================================================================
elif selected_page == "🛒 الطلبيات":
    st.title("🛒 حساب طلبيات الشراء الذكية من الشركات الموردة")
    
    months_cover = st.slider("حدد عدد الشهور المطلوب تغطيتها في طلبية الشراء:", min_value=1, max_value=12, value=3)
    
    items_df = get_df("items")
    inv_res = supabase.table("inventory").select("tests_available, batches(item_id)").eq("location_id", 1).execute()
    
    stock_by_item = {}
    for r in (inv_res.data or []):
        if r.get("batches"):
            iid = r["batches"]["item_id"]
            stock_by_item[iid] = stock_by_item.get(iid, 0) + float(r["tests_available"])
    
    order_rows = []
    for _, it in items_df.iterrows():
        rate = float(it["monthly_consumption_rate"] or 0)
        if rate > 0:
            needed_total = rate * months_cover
            current_stock = stock_by_item.get(it["id"], 0)
            deficit = max(0, needed_total - current_stock)
            if deficit > 0:
                order_rows.append({
                    "الصنف": f"{it['name']} ({it['variant']})",
                    "الاستهلاك الشهري الكلي": rate,
                    f"الاحتياج لـ {months_cover} شهور": needed_total,
                    "الرصيد الحالي بالمخزن الرئيسي": current_stock,
                    f"العجز المطلوب شراؤه ({it['sub_unit_name']})": deficit
                })
    
    if order_rows:
        df_ord = pd.DataFrame(order_rows)
        st.dataframe(df_ord, use_container_width=True, hide_index=True)
        csv = df_ord.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل طلبية الشراء (Excel / CSV)", data=csv, file_name=f"purchase_order_{months_cover}_months.csv", mime="text/csv", type="primary")
    else:
        st.success("✅ الأرصدة الحالية في المخزن الرئيسي تغطي الفترة المحددة بالكامل بناءً على معدلات الاستهلاك المسجلة!")

# =========================================================================
# 4. المخازن الفرعية والسحب اليومي على الأجهزة
# =========================================================================
elif selected_page == "🧪 المخازن الفرعية":
    st.title("🧪 أرصدة المخازن الفرعية والوحدات وتسجيل السحب للأجهزة")
    
    locs_df = get_df("locations")
    sub_locs = locs_df[locs_df["location_type"] != "main"]
    
    if role == "unit_supervisor" and user_loc_id != 1:
        sel_loc_id = user_loc_id
        st.subheader(f"مخزن: {user_loc_name}")
    else:
        loc_name = st.selectbox("اختر الوحدة / الفرع لعرض رصيده وتسجيل السحب:", sub_locs["name"].tolist())
        sel_loc_id = int(sub_locs[sub_locs["name"] == loc_name].iloc[0]["id"])
    
    sub_inv = supabase.table("inventory").select("*, batches(*, items(id, name, variant, unit_name, sub_unit_name), suppliers(id, name))").eq("location_id", sel_loc_id).gt("kits_available", 0).execute()
    
    if not sub_inv.data:
        st.info("لا توجد أرصدة حالياً في هذه الوحدة. يمكنك طلب صرفية من صفحة '🔄 أذونات الصرف'.")
    else:
        for row in sub_inv.data:
            b = row["batches"]
            it = b["items"]
            sup = b["suppliers"]
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"### {it['name']} ({it['variant']}) — شركة **{sup['name']}**")
                    st.write(f"**الرصيد المتاح بالوحدة:** `{int(row['kits_available'])}` {it['unit_name']} ({int(row['tests_available'])} {it['sub_unit_name']}) | **Lot:** `{b['lot_number']}` | **الصلاحية:** `{b['expiry_date']}`")
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
                        st.success(f"تم سحب {kits_pull} {it['unit_name']} ({tests_pulled} {it['sub_unit_name']}) وخصمها من رصيد الوحدة.")
                        st.rerun()

# =========================================================================
# 5. إضافة فاتورة (توريد رصيد جديد للمخزن الرئيسي)
# =========================================================================
elif selected_page == "📥 إضافة فاتورة":
    st.title("📥 إضافة فاتورة توريد إلى المخزن الرئيسي")
    
    items_df = get_df("items")
    suppliers_df = get_df("suppliers")
    
    if items_df.empty or suppliers_df.empty:
        st.warning("⚠️ برجاء إضافة الأصناف والشركات أولاً من صفحة '⚙️ التكويد'.")
    else:
        with st.form("receive_batch_form"):
            col1, col2 = st.columns(2)
            with col1:
                items_df["label"] = items_df["name"] + " - (" + items_df["variant"] + ")"
                item_choice = st.selectbox("اختر الصنف / التحليل", items_df["label"].tolist())
                selected_item = items_df[items_df["label"] == item_choice].iloc[0]
                
                sup_choice = st.selectbox("الشركة الموردة", suppliers_df["name"].tolist())
                selected_sup = suppliers_df[suppliers_df["name"] == sup_choice].iloc[0]
                
                lot_number = st.text_input("رقم التشغيلة (Lot Number)")
                expiry_date = st.date_input("تاريخ الصلاحية (Expiry Date)", min_value=date.today())

            with col2:
                kits_qty = st.number_input(f"الكمية الواردة (عدد الـ {selected_item['unit_name']})", min_value=1, step=1)
                tests_per_kit = st.number_input(f"عدد الـ ({selected_item['sub_unit_name']}) داخل كل {selected_item['unit_name']}", min_value=1, value=100, step=1)
                unit_price = st.number_input(f"سعر الـ ({selected_item['sub_unit_name']}) الواحد بالجنيه", min_value=0.0, step=0.1, format="%.2f")
                rec_date = st.date_input("تاريخ التوريد", value=date.today())

            total_tests = kits_qty * tests_per_kit
            kit_price = unit_price * tests_per_kit
            st.info(f"📌 ملخص الإضافة: **{kits_qty}** {selected_item['unit_name']} × **{tests_per_kit}** = **{total_tests}** {selected_item['sub_unit_name']} | سعر العلبة: **{kit_price:,.2f} ج.م** | إجمالي الفاتورة: **{total_tests * unit_price:,.2f} ج.م**")
            
            submitted = st.form_submit_button("✅ تأكيد إضافة الفاتورة للمخزن الرئيسي", type="primary", use_container_width=True)
            if submitted:
                if not lot_number.strip():
                    st.error("برجاء إدخال رقم التشغيلة (Lot Number).")
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
                    st.success(f"🎉 تم إضافة {kits_qty} {selected_item['unit_name']} ({total_tests} {selected_item['sub_unit_name']}) بنجاح إلى المخزن الرئيسي!")

# =========================================================================
# 6. أذونات الصرف (إنشاء طلب صرف + تنفيذ الصرف لأمين المخزن)
# =========================================================================
elif selected_page == "🔄 أذونات الصرف":
    st.title("🔄 أذونات الصرف من المخزن الرئيسي")
    
    t1, t2 = st.tabs(["📝 إنشاء إذن صرف جديد (للوحدات والفروع)", "📦 أذونات الصرف المعتمدة (تنفيذ الصرف)"])
    
    with t1:
        st.subheader("طلب صرف من المخزن الرئيسي")
        locs_df = get_df("locations")
        sub_locs = locs_df[locs_df["location_type"] != "main"]
        items_df = get_df("items")
        suppliers_df = get_df("suppliers")
        
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
                
                items_df["label"] = items_df["name"] + " - (" + items_df["variant"] + ")"
                item_choice = st.selectbox("اختر الصنف المطلوب", items_df["label"].tolist(), key="req_item")
                sel_item = items_df[items_df["label"] == item_choice].iloc[0]
                
                sup_choice = st.selectbox("اختر الشركة الموردة", suppliers_df["name"].tolist(), key="req_sup")
                sel_sup = suppliers_df[suppliers_df["name"] == sup_choice].iloc[0]

            with c2:
                rate_res = supabase.table("location_consumption_rates").select("monthly_tests_rate").eq("location_id", target_loc_id).eq("item_id", int(sel_item["id"])).execute()
                unit_monthly_rate = float(rate_res.data[0]["monthly_tests_rate"]) if rate_res.data else float(sel_item["monthly_consumption_rate"] or 0)
                
                months_needed = st.number_input("المدة المطلوب تغطيتها (بالشهور)", min_value=0.5, max_value=12.0, value=1.0, step=0.5)
                
                avail_batches = supabase.table("inventory").select("*, batches!inner(*)").eq("location_id", 1).eq("batches.item_id", int(sel_item["id"])).eq("batches.supplier_id", int(sel_sup["id"])).gt("kits_available", 0).execute()
                
                if avail_batches.data:
                    sorted_b = sorted(avail_batches.data, key=lambda x: x["batches"]["expiry_date"])
                    best_b = sorted_b[0]
                    tpk = best_b["batches"]["tests_per_kit"]
                    suggested_kits = max(1, round((unit_monthly_rate * months_needed) / tpk)) if unit_monthly_rate > 0 else 1
                    
                    st.success(f"💡 ترشيح النظام (FEFO): **Lot {best_b['batches']['lot_number']}** (ينتهي في `{best_b['batches']['expiry_date']}`) | المتاح بالمخزن الرئيسي: **{int(best_b['kits_available'])}** {sel_item['unit_name']}")
                    if unit_monthly_rate > 0:
                        st.caption(f"بناءً على استهلاك الوحدة ({unit_monthly_rate} {sel_item['sub_unit_name']}/شهر)، الكمية المقترحة لـ {months_needed} شهر هي **{suggested_kits}** {sel_item['unit_name']}.")
                    
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
                        st.markdown(f"**صرف إلى:** {req['locations']['name']} | **الصنف:** {req['items']['name']} ({req['items']['variant']}) - **{req['suppliers']['name']}**")
                        st.caption(f"الكمية المعتمدة: **{req['kits_requested']}** {req['items']['unit_name']} | Lot: `{req['batches']['lot_number']}`")
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
# 7. الموافقات (قائمة مستقلة لاعتماد أذونات الصرف)
# =========================================================================
elif selected_page == "✍️ الموافقات":
    st.title("✍️ الموافقات — اعتماد أذونات الصرف")
    
    pending = supabase.table("transfer_requests").select("*, locations!transfer_requests_to_location_id_fkey(name), items(name, variant, unit_name), suppliers(name), batches(lot_number, expiry_date)").eq("status", "pending_gm").execute()
    if not pending.data:
        st.info("✅ لا توجد أذونات صرف معلقة بانتظار الموافقة حالياً.")
    else:
        for req in pending.data:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**الجهة الطالبة:** {req['locations']['name']} | **الصنف:** {req['items']['name']} ({req['items']['variant']}) - شركة **{req['suppliers']['name']}**")
                    st.caption(f"الكمية: **{req['kits_requested']}** {req['items']['unit_name']} ({req['tests_requested']} تست/قطعة) | Lot: `{req['batches']['lot_number']}` | الصلاحية: `{req['batches']['expiry_date']}`")
                with col2:
                    if st.button("✅ موافقة واعتماد", key=f"app_{req['id']}", type="primary", use_container_width=True):
                        supabase.table("transfer_requests").update({
                            "status": "approved_ready_to_issue",
                            "approved_by": user["id"],
                            "approved_at": datetime.now().isoformat()
                        }).eq("id", req["id"]).execute()
                        st.rerun()
                with col3:
                    if st.button("❌ رفض", key=f"rej_{req['id']}", use_container_width=True):
                        supabase.table("transfer_requests").update({"status": "rejected"}).eq("id", req["id"]).execute()
                        st.rerun()

# =========================================================================
# 8. التقارير (التقارير المالية ومقارنة الأسعار بين الشركات)
# =========================================================================
elif selected_page == "📈 التقارير":
    st.title("📈 التقارير المالية وتحليل أسعار الشركات")
    
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
                "الصنف": f"{l['items']['name']} ({l['items']['variant']})",
                "الشركة الموردة": l["suppliers"]["name"],
                "الكمية المستهلكة": float(l["tests_consumed"]),
                "التكلفة الإجمالية (ج.م)": float(l["cost_incurred"])
            } for l in logs.data])
            
            st.subheader("ملخص الاستهلاك مقسماً بالصنف والشركة الموردة")
            summary = df_l.groupby(["الصنف", "الشركة الموردة"]).agg(
                إجمالي_الكمية=("الكمية المستهلكة", "sum"),
                إجمالي_التكلفة_جنيه=("التكلفة الإجمالية (ج.م)", "sum")
            ).reset_index()
            summary["متوسط_سعر_التست"] = (summary["إجمالي_التكلفة_جنيه"] / summary["إجمالي_الكمية"]).round(2)
            st.dataframe(summary, use_container_width=True, hide_index=True)
            
            with st.expander("عرض السجل التفصيلي لكل حركة سحب"):
                st.dataframe(df_l, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد حركات استهلاك مسجلة في هذه الفترة.")

    with rep_t2:
        st.subheader("تتبع ومقارنة أسعار التوريد عبر الزمن بين الشركات")
        batches_res = supabase.table("batches").select("*, items(name, variant), suppliers(name)").order("received_date").execute()
        if batches_res.data:
            df_b = pd.DataFrame([{
                "تاريخ التوريد": b["received_date"],
                "الصنف": f"{b['items']['name']} ({b['items']['variant']})",
                "الشركة الموردة": b["suppliers"]["name"],
                "Lot": b["lot_number"],
                "سعر التست/القطعة (ج.م)": float(b["unit_price_per_test"]),
                "سعر العلبة (ج.م)": float(b["kit_price"])
            } for b in batches_res.data])
            
            sel_p_item = st.selectbox("اختر الصنف لمقارنة أسعار شركاته:", sorted(df_b["الصنف"].unique().tolist()))
            sub_b = df_b[df_b["الصنف"] == sel_p_item]
            
            fig_p = px.line(sub_b, x="تاريخ التوريد", y="سعر التست/القطعة (ج.م)", color="الشركة الموردة", markers=True, title=f"تطور ومقارنة سعر ({sel_p_item}) بين الشركات")
            st.plotly_chart(fig_p, use_container_width=True)
            st.dataframe(sub_b, use_container_width=True, hide_index=True)
        else:
            st.info("لم يتم تسجيل فواتير توريد بعد.")

# =========================================================================
# 9. التكويد (تكويد وتعديل وحذف الأصناف والشركات والفروع ومعدلات الاستهلاك)
# =========================================================================
elif selected_page == "⚙️ التكويد":
    st.title("⚙️ التكويد — إدارة الأصناف والشركات والمخازن الفرعية")
    
    st1, st2, st3, st4 = st.tabs([
        "🧪 الأصناف (إضافة / تعديل / حذف)", 
        "🏢 الشركات الموردة (إضافة / تعديل / حذف)", 
        "🏥 المخازن الفرعية والوحدات",
        "📏 معدلات الاستهلاك الشهري"
    ])
    
    with st1:
        with st.expander("➕ إضافة صنف جديد (محلول / مستهلك)", expanded=True):
            with st.form("add_item_form"):
                c1, c2 = st.columns(2)
                i_name = c1.text_input("اسم الصنف / التحليل (مثال: ALT أو Gloves أو Syringe)")
                i_var = c2.text_input("المقاس أو النوع (مثال: قياسي، S، M، L، 5ml، EDTA)", value="قياسي")
                i_cat = c1.selectbox("التصنيف", ["reagent", "consumable"], format_func=lambda x: "محاليل وكواشف (Reagent)" if x == "reagent" else "مستهلكات طبية (Consumable)")
                i_unit = c2.text_input("وحدة التوريد الكبرى (مثال: علبة أو باكيت)", value="علبة")
                i_sub = c1.text_input("وحدة القياس الصغرى (مثال: تست أو قطعة)", value="تست")
                i_rate = c2.number_input("معدل الاستهلاك الشهري الكلي للمعمل (بالتست أو القطعة)", min_value=0.0, step=50.0)
                
                if st.form_submit_button("💾 حفظ الصنف الجديد", type="primary"):
                    if i_name.strip():
                        try:
                            supabase.table("items").insert({
                                "name": i_name.strip(),
                                "variant": i_var.strip() or "قياسي",
                                "category": i_cat,
                                "unit_name": i_unit.strip(),
                                "sub_unit_name": i_sub.strip(),
                                "monthly_consumption_rate": float(i_rate)
                            }).execute()
                            st.success(f"تم إضافة الصنف ({i_name} - {i_var}) بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("هذا الصنف بنفس المقاس مسجل بالفعل.")
                    else:
                        st.error("برجاء إدخال اسم الصنف.")

        st.divider()
        st.subheader("✏️ تعديل أو حذف صنف مسجل")
        items_df = get_df("items")
        if not items_df.empty:
            items_df["label"] = items_df["name"] + " - (" + items_df["variant"] + ")"
            edit_item_choice = st.selectbox("اختر الصنف المراد تعديله أو حذفه:", items_df["label"].tolist(), key="edit_item_sel")
            cur_item = items_df[items_df["label"] == edit_item_choice].iloc[0]
            
            with st.form("edit_item_form"):
                ec1, ec2 = st.columns(2)
                new_i_name = ec1.text_input("اسم الصنف / التحليل", value=cur_item["name"])
                new_i_var = ec2.text_input("المقاس أو النوع", value=cur_item["variant"])
                cat_opts = ["reagent", "consumable"]
                new_i_cat = ec1.selectbox("التصنيف", cat_opts, index=cat_opts.index(cur_item["category"]), format_func=lambda x: "محاليل وكواشف (Reagent)" if x == "reagent" else "مستهلكات طبية (Consumable)")
                new_i_unit = ec2.text_input("وحدة التوريد الكبرى", value=cur_item["unit_name"])
                new_i_sub = ec1.text_input("وحدة القياس الصغرى", value=cur_item["sub_unit_name"])
                new_i_rate = ec2.number_input("معدل الاستهلاك الشهري الكلي", min_value=0.0, value=float(cur_item["monthly_consumption_rate"] or 0), step=50.0)
                
                btn_c1, btn_c2 = st.columns(2)
                update_item_btn = btn_c1.form_submit_button("💾 حفظ التعديلات", type="primary", use_container_width=True)
                delete_item_btn = btn_c2.form_submit_button("🗑️ حذف الصنف نهائياً", use_container_width=True)
                
                if update_item_btn:
                    if new_i_name.strip():
                        try:
                            supabase.table("items").update({
                                "name": new_i_name.strip(),
                                "variant": new_i_var.strip() or "قياسي",
                                "category": new_i_cat,
                                "unit_name": new_i_unit.strip(),
                                "sub_unit_name": new_i_sub.strip(),
                                "monthly_consumption_rate": float(new_i_rate)
                            }).eq("id", int(cur_item["id"])).execute()
                            st.success("✅ تم تحديث بيانات الصنف بنجاح!")
                            st.rerun()
                        except Exception:
                            st.error("تعذر التحديث: يوجد صنف آخر بنفس الاسم والمقاس.")
                            
                if delete_item_btn:
                    has_batches = supabase.table("batches").select("id").eq("item_id", int(cur_item["id"])).limit(1).execute()
                    if has_batches.data:
                        st.error("❌ لا يمكن حذف هذا الصنف لأنه مرتبط بفواتير توريد أو أرصدة سابقة بالمخزن.")
                    else:
                        supabase.table("items").delete().eq("id", int(cur_item["id"])).execute()
                        st.success("🗑️ تم حذف الصنف بنجاح!")
                        st.rerun()

            st.markdown("#### 📋 قائمة الأصناف المسجلة حالياً")
            disp_items = items_df[["id", "name", "variant", "category", "unit_name", "sub_unit_name", "monthly_consumption_rate"]].copy()
            disp_items.columns = ["الكود", "الاسم", "النوع/المقاس", "التصنيف", "الوحدة الكبرى", "الوحدة الصغرى", "الاستهلاك الشهري"]
            disp_items["التصنيف"] = disp_items["التصنيف"].map({"reagent": "محاليل وكواشف", "consumable": "مستهلكات"})
            st.dataframe(disp_items, use_container_width=True, hide_index=True)

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

    with st4:
        st.subheader("📏 ضبط معدلات الاستهلاك الشهري")
        items_df = get_df("items")
        locs_df = get_df("locations")
        sub_locs = locs_df[locs_df["location_type"] != "main"]
        
        if not items_df.empty:
            items_df["label"] = items_df["name"] + " (" + items_df["variant"] + ")"
            
            c_tot, c_unit = st.columns(2)
            with c_tot:
                st.markdown("#### 1️⃣ المعدل الشهري الكلي للمعمل (لحساب الطلبيات)")
                sel_u_item = st.selectbox("اختر الصنف:", items_df["label"].tolist(), key="rate_tot_item")
                row_it = items_df[items_df["label"] == sel_u_item].iloc[0]
                new_r = st.number_input("معدل الاستهلاك الشهري الكلي الجديد (تست/قطعة):", min_value=0.0, value=float(row_it["monthly_consumption_rate"] or 0), step=50.0, key="rate_tot_val")
                if st.button("💾 تحديث المعدل الكلي", type="primary"):
                    supabase.table("items").update({"monthly_consumption_rate": float(new_r)}).eq("id", int(row_it["id"])).execute()
                    st.success("✅ تم تحديث المعدل الكلي بنجاح!")
                    st.rerun()

            with c_unit:
                st.markdown("#### 2️⃣ المعدل الشهري الخاص بكل وحدة/فرع (لأذونات الصرف)")
                if not sub_locs.empty:
                    sel_r_loc = st.selectbox("اختر الوحدة / الفرع:", sub_locs["name"].tolist(), key="rate_loc_sel")
                    r_loc_id = int(sub_locs[sub_locs["name"] == sel_r_loc].iloc[0]["id"])
                    sel_r_item = st.selectbox("اختر الصنف:", items_df["label"].tolist(), key="rate_loc_item")
                    r_item_id = int(items_df[items_df["label"] == sel_r_item].iloc[0]["id"])
                    
                    existing_r = supabase.table("location_consumption_rates").select("monthly_tests_rate").eq("location_id", r_loc_id).eq("item_id", r_item_id).execute()
                    cur_u_rate = float(existing_r.data[0]["monthly_tests_rate"]) if existing_r.data else 0.0
                    
                    new_u_rate = st.number_input("الاستهلاك الشهري لهذه الوحدة (تست/قطعة):", min_value=0.0, value=cur_u_rate, step=25.0, key="rate_loc_val")
                    if st.button("💾 حفظ معدل الوحدة"):
                        supabase.table("location_consumption_rates").upsert({
                            "location_id": r_loc_id,
                            "item_id": r_item_id,
                            "monthly_tests_rate": float(new_u_rate)
                        }, on_conflict="location_id,item_id").execute()
                        st.success(f"✅ تم حفظ معدل استهلاك ({sel_r_loc}) بنجاح!")

# =========================================================================
# 10. إدارة المستخدمين والصلاحيات
# =========================================================================
elif selected_page == "👥 إدارة المستخدمين والصلاحيات":
    st.title("👥 إدارة حسابات الموظفين والصلاحيات")
    
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
                    st.success(f"🎉 تم إنشاء الحساب! ابعت للموظف البيانات دي:\n- **Username:** `{u_name.strip()}`\n- **Password:** `{u_pass}`")
                except Exception:
                    st.error("اسم المستخدم ده موجود قبل كده، اختار اسم تاني.")
            else:
                st.error("برجاء ملء جميع الحقول.")
                
    st.subheader("قائمة المستخدمين الحاليين")
    users_df = get_df("users", "id, full_name, username, role, is_active")
    if not users_df.empty:
        users_df["role"] = users_df["role"].map(ROLE_LABELS)
        st.dataframe(users_df, use_container_width=True, hide_index=True)
