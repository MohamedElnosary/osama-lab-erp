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
    page_title="نظام إدارة مخازن معامل د. أسامة عبد المتعال",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
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
# نظام تسجيل الدخول
# =========================================================================
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #0e4d92;'>🧬 معامل د. أسامة عبد المتعال</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #475569;'>نظام إدارة المخازن والكواشف الذكي (ERP / LIMS)</h4>", unsafe_allow_html=True)
        st.divider()
        with st.form("login_form"):
            username = st.text_input("اسم المستخدم (Username)")
            password = st.text_input("كلمة المرور (Password)", type="password")
            submit = st.form_submit_button("تسجيل الدخول", use_container_width=True, type="primary")
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
# القائمة الجانبية ومعلومات المستخدم
# =========================================================================
ROLE_LABELS = {
    "chairman": "رئيس مجلس الإدارة",
    "general_manager": "المدير العام",
    "main_storekeeper": "أمين المخزن الرئيسي",
    "unit_supervisor": "مشرف وحدة / فرع"
}

with st.sidebar:
    st.markdown("### 🧬 معامل د. أسامة عبد المتعال")
    st.info(f"**المستخدم:** {user['full_name']}\n\n**الصلاحية:** {ROLE_LABELS.get(role, role)}\n\n**الموقع:** {user_loc_name}")
    
    menu_options = []
    if role in ["chairman", "general_manager"]:
        menu_options.append("📊 لوحة القيادة والذكاء الاصطناعي")
    if role in ["chairman", "general_manager", "main_storekeeper"]:
        menu_options.append("🏢 المخزن الرئيسي (عرض مزدوج)")
        menu_options.append("📥 توريد فاتورة / إضافة رصيد")
    menu_options.append("🔄 طلبات الصرف والموافقات")
    menu_options.append("🧪 المخازن الفرعية والسحب للأجهزة")
    if role in ["chairman", "general_manager", "main_storekeeper"]:
        menu_options.append("🛒 طلبيات الشراء من الشركات")
        menu_options.append("📈 التقارير المالية ومقارنة الأسعار")
        menu_options.append("⚙️ تكويد الأصناف والشركات والفروع")
    if role in ["chairman", "general_manager"]:
        menu_options.append("👥 إدارة المستخدمين والصلاحيات")

    selected_page = st.radio("القائمة الرئيسية", menu_options)
    st.divider()
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.user = None
        st.rerun()

# دوال مساعدة لجلب البيانات
def get_df(table_name, select_query="*"):
    res = supabase.table(table_name).select(select_query).order("id").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

# =========================================================================
# 1. لوحة القيادة التنفيذية والذكاء الاصطناعي (رئيس مجلس الإدارة والمدير العام)
# =========================================================================
if selected_page == "📊 لوحة القيادة والذكاء الاصطناعي":
    st.title("📊 لوحة القيادة التنفيذية وتحليلات الذكاء الاصطناعي")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(name, variant, category, monthly_consumption_rate), suppliers(name)), locations(name, location_type)").execute()
    cons_res = supabase.table("consumption_logs").select("*, items(name, variant), suppliers(name), locations(name)").execute()
    
    inv_data = inv_res.data or []
    cons_data = cons_res.data or []
    
    total_stock_value = sum(r["tests_available"] * r["batches"]["unit_price_per_test"] for r in inv_data if r.get("batches"))
    
    # استهلاك آخر 30 يوم
    thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
    recent_cons = [c for c in cons_data if c["consumed_at"] >= thirty_days_ago]
    monthly_cost = sum(c["cost_incurred"] for c in recent_cons)
    monthly_tests = sum(c["tests_consumed"] for c in recent_cons)
    
    # تنبيهات الصلاحية (أقل من 60 يوم)
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
elif selected_page == "🏢 المخزن الرئيسي (عرض مزدوج)":
    st.title("🏢 أرصدة المخزن الرئيسي")
    
    inv_res = supabase.table("inventory").select("*, batches(*, items(id, name, variant, category, unit_name, sub_unit_name, monthly_consumption_rate), suppliers(name))").eq("location_id", 1).gt("tests_available", 0).execute()
    rows = inv_res.data or []
    
    if not rows:
        st.warning("المخزن الرئيسي فارغ حالياً. اذهب إلى '📥 توريد فاتورة' لإضافة الأرصدة.")
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
# 3. توريد فاتورة / إضافة رصيد للمخزن الرئيسي
# =========================================================================
elif selected_page == "📥 توريد فاتورة / إضافة رصيد":
    st.title("📥 تسجيل وارد جديد إلى المخزن الرئيسي")
    
    items_df = get_df("items")
    suppliers_df = get_df("suppliers")
    
    if items_df.empty or suppliers_df.empty:
        st.warning("⚠️ برجاء إضافة الأصناف والشركات أولاً من صفحة '⚙️ تكويد الأصناف والشركات والفروع'.")
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
            
            submitted = st.form_submit_button("✅ تأكيد الإضافة للمخزن الرئيسي", type="primary", use_container_width=True)
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
# 4. طلبات الصرف الذكية وموافقات المدير العام وصرف أمين المخزن
# =========================================================================
elif selected_page == "🔄 طلبات الصرف والموافقات":
    st.title("🔄 دورة طلب وصرف الكواشف والمستلزمات")
    
    t1, t2, t3 = st.tabs(["📝 إنشاء طلبية صرف جديدة (للوحدات والفروع)", "✍️ اعتماد المدير العام", "📦 شاشة الصرف (أمين المخزن الرئيسي)"])
    
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
                    
                    if st.button("🚀 إرسال الطلبية لاعتماد المدير العام", type="primary"):
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
                        st.success("✅ تم إرسال الطلبية بنجاح وهي الآن بانتظار موافقة المدير العام!")
                else:
                    st.error(f"❌ لا يوجد رصيد متاح في المخزن الرئيسي من ({sel_item['name']}) لشركة ({sel_sup['name']}).")

    with t2:
        st.subheader("طلبات الصرف المعلقة بانتظار موافقة المدير العام")
        pending = supabase.table("transfer_requests").select("*, locations!transfer_requests_to_location_id_fkey(name), items(name, variant, unit_name), suppliers(name), batches(lot_number, expiry_date)").eq("status", "pending_gm").execute()
        if not pending.data:
            st.info("لا توجد طلبات معلقة حالياً.")
        else:
            for req in pending.data:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**الجهة الطالبة:** {req['locations']['name']} | **الصنف:** {req['items']['name']} ({req['items']['variant']}) - شركة **{req['suppliers']['name']}**")
                        st.caption(f"الكمية: **{req['kits_requested']}** {req['items']['unit_name']} ({req['tests_requested']} تست/قطعة) | Lot: `{req['batches']['lot_number']}` | الصلاحية: `{req['batches']['expiry_date']}`")
                    with col2:
                        if role in ["general_manager", "chairman"]:
                            if st.button("✅ موافقة واعتماد", key=f"app_{req['id']}", type="primary"):
                                supabase.table("transfer_requests").update({
                                    "status": "approved_ready_to_issue",
                                    "approved_by": user["id"],
                                    "approved_at": datetime.now().isoformat()
                                }).eq("id", req["id"]).execute()
                                st.rerun()
                    with col3:
                        if role in ["general_manager", "chairman"]:
                            if st.button("❌ رفض", key=f"rej_{req['id']}"):
                                supabase.table("transfer_requests").update({"status": "rejected"}).eq("id", req["id"]).execute()
                                st.rerun()

    with t3:
        st.subheader("أذون الصرف المعتمدة وجاهزة للتحويل للمخازن الفرعية")
        approved = supabase.table("transfer_requests").select("*, locations!transfer_requests_to_location_id_fkey(name), items(name, variant, unit_name), suppliers(name), batches(lot_number, expiry_date, tests_per_kit)").eq("status", "approved_ready_to_issue").execute()
        if not approved.data:
            st.info("لا توجد أذون صرف معتمدة بانتظار التنفيذ.")
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
                                        "tests_available": float(s_inv["tests_available"])
