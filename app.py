# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import math

# --- 1. الإعدادات الهندسية الفائقة والجمالية ---
st.set_page_config(page_title="Civil Engineering Hub", layout="wide", initial_sidebar_state="expanded")

# تنسيق CSS احترافي للواجهة وللحاسبة الكاسيو (The UI Matrix)
st.markdown("""
    <style>
    /* شاشة الحاسبة الكاسيو */
    .calc-screen {
        background-color: #9eb19e;
        color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 28px;
        text-align: right;
        border: 4px solid #333;
        margin-bottom: 10px;
        box-shadow: inset 0 0 10px #000;
        min-height: 80px;
    }
    /* تنسيق أزرار الحاسبة */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 3em;
    }
    /* أزرار العمليات والمسح */
    div[data-testid="stHorizontalBlock"] .del-btn button { background-color: #ff9800 !important; color: white !important; }
    div[data-testid="stHorizontalBlock"] .ac-btn button { background-color: #f44336 !important; color: white !important; }
    /* تحسين شكل القوائم */
    .stSelectbox label, .stRadio label { font-weight: bold; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك قاعدة البيانات والعمليات التلقائية ---
def get_db():
    conn = sqlite3.connect("Engineering_Library.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_auto_stats():
    try:
        db = get_db()
        subj = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        stud = db.execute("SELECT COUNT(*) FROM access_gate").fetchone()[0]
        lecs = db.execute("SELECT COUNT(*) FROM university_archive").fetchone()[0]
        db.close()
        return subj, stud, lecs
    except: return 0, 0, 0

# --- 3. إدارة حالة التطبيق (State Management) ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'user_data' not in st.session_state: st.session_state.user_data = None
if 'temp_user' not in st.session_state: st.session_state.temp_user = None
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""

# الرابط السري للإدارة
is_admin_link = st.query_params.get("role") == "admin"

# --- 4. القائمة الجانبية (Sidebar): الحاسبة + التحويل + الدعم ---
with st.sidebar:
    st.title("🛠️ أدوات المهندس الذكية")
    
    # [أ] الآلة الحاسبة العلمية (Casio UI Matrix)
    with st.container(border=True):
        st.subheader("📟 Casio FX-991 Mode")
        st.markdown(f'<div class="calc-screen">{st.session_state.calc_expr if st.session_state.calc_expr != "" else "0"}</div>', unsafe_allow_html=True)
        
        # مصفوفة الأزرار (Matrix)
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        if r1_c1.button("sin"): st.session_state.calc_expr += "math.sin(math.radians("
        if r1_c2.button("cos"): st.session_state.calc_expr += "math.cos(math.radians("
        if r1_c3.button("tan"): st.session_state.calc_expr += "math.tan(math.radians("
        if r1_c4.button("√"): st.session_state.calc_expr += "math.sqrt("

        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        if r2_c1.button("7"): st.session_state.calc_expr += "7"
        if r2_c2.button("8"): st.session_state.calc_expr += "8"
        if r2_c3.button("9"): st.session_state.calc_expr += "9"
        if r2_c4.button("log"): st.session_state.calc_expr += "math.log10("

        r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
        if r3_c1.button("4"): st.session_state.calc_expr += "4"
        if r3_c2.button("5"): st.session_state.calc_expr += "5"
        if r3_c3.button("6"): st.session_state.calc_expr += "6"
        if r3_c4.button("×"): st.session_state.calc_expr += "*"

        r4_c1, r4_c2, r4_c3, r4_c4 = st.columns(4)
        if r4_c1.button("1"): st.session_state.calc_expr += "1"
        if r4_c2.button("2"): st.session_state.calc_expr += "2"
        if r4_c3.button("3"): st.session_state.calc_expr += "3"
        if r4_c4.button("÷"): st.session_state.calc_expr += "/"

        r5_c1, r5_c2, r5_c3, r5_c4 = st.columns(4)
        if r5_c1.button("0"): st.session_state.calc_expr += "0"
        if r5_c2.button("."): st.session_state.calc_expr += "."
        if r5_c3.button("+"): st.session_state.calc_expr += "+"
        if r5_c4.button("-"): st.session_state.calc_expr += "-"

        r6_c1, r6_c2 = st.columns(2)
        with r6_c1: st.markdown('<div class="ac-btn">', unsafe_allow_html=True)
        if r6_c1.button("AC"): st.session_state.calc_expr = ""; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        if r6_c2.button("🟰", type="primary"):
            try:
                res = eval(st.session_state.calc_expr, {"math": math, "__builtins__": None})
                st.session_state.calc_expr = str(round(res, 6))
                st.rerun()
            except: st.error("خطأ")

    st.divider()
    
    # [ب] محول الوحدات الشامل
    with st.expander("⚖️ محول الوحدات الهندسي"):
        val = st.number_input("القيمة", value=1.0)
        u_type = st.selectbox("نوع التحويل", ["متر ➔ إنش", "إنش ➔ متر", "كغ ➔ طن", "نيوتن ➔ كغ.ق"])
        if u_type == "متر ➔ إنش": st.success(f"{val*39.37:.2f} in")
        elif u_type == "إنش ➔ متر": st.success(f"{val/39.37:.2f} m")
        elif u_type == "كغ ➔ طن": st.success(f"{val/1000:.4f} Ton")

    st.divider()
    
    # [ج] الدعم الفني (يُقرأ من قاعدة البيانات)
    st.subheader("📞 الدعم الفني والإدارة")
    try:
        db = get_db(); admins = db.execute("SELECT * FROM support_info").fetchall(); db.close()
        for admin in admins:
            with st.expander(f"👤 {admin['admin_name']}"):
                st.link_button("تليجرام", admin['telegram_url'], use_container_width=True)
                st.link_button("واتساب", admin['whatsapp_url'], use_container_width=True)
    except: st.info("تواصل مع المهندس يعرب.")

# --- 5. الواجهة الرئيسية للمنصة (Front-end) ---
st.title("🏗️ Civil Engineering Hub")
st.write("المنصة الرقمية المتكاملة لطلاب كلية الهندسة المدنية")

# عداد حالة الموقع التلقائي (Live Stats)
s_c, st_c, l_c = get_auto_stats()
col_s1, col_s2, col_s3 = st.columns(3)
col_s1.metric("📚 المواد المرفوعة", s_c)
col_s2.metric("👥 الطلاب المسجلين", st_c)
col_s3.metric("📄 المحاضرات والملفات", l_c)

# شريط الأخبار والإعلانات (يظهر للجميع)
try:
    db = get_db(); news = db.execute("SELECT * FROM college_news ORDER BY id DESC LIMIT 1").fetchone(); db.close()
    if news:
        with st.expander(f"📢 آخر الأخبار: {news['news_title']}", expanded=True):
            st.write(news['news_text'])
            if news['media_type'] == 'image': st.image(news['media_url'])
            elif news['media_type'] == 'video': st.video(news['media_url'])
            elif news['media_type'] == 'pdf': st.link_button("💾 تحميل الإعلان (PDF)", news['media_url'], use_container_width=True)
except: st.info("📢 أهلاً بكم في المنصة الرقمية للهندسة المدنية.")

st.divider()

# --- 6. منطق التنقل والخصوصية ---

# [صفحة الترحيب]
if st.session_state.step == 'welcome':
    if st.session_state.user_data:
        st.success(f"مرحباً بك مهندس {st.session_state.user_data['full_name']}")
        if st.button("الذهاب إلى محاضراتي", use_container_width=True, type="primary"):
            st.session_state.step = 'archive'; st.rerun()
    else:
        if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
            st.session_state.step = 'login'; st.rerun()
    
    if is_admin_link:
        st.warning("⚠️ وضع الإدارة مفعل (للمسؤولين فقط)")
        st.info("يمكنك تعديل البيانات عبر DB Browser ورفع الملف.")

# [صفحة تسجيل الدخول - التحقق من الهوية]
elif st.session_state.step == 'login':
    st.header("🔑 التحقق من الهوية الجامعية")
    u_n = st.text_input("الاسم الثلاثي")
    u_s = st.text_input("الرقم الجامعي")
    if st.button("تحقق", use_container_width=True, type="primary"):
        if u_n and u_s:
            db = get_db(); user = db.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (u_n, u_s)).fetchone(); db.close()
            if user:
                st.session_state.temp_user = user; st.session_state.step = 'password'; st.rerun()
            else: st.error("⚠️ البيانات غير موجودة. يرجى مراجعة الدعم الفني.")
    if st.button("رجوع"): st.session_state.step = 'welcome'; st.rerun()

# [صفحة كلمة المرور - الخصوصية]
elif st.session_state.step == 'password':
    st.header(f"🔒 خصوصية المهندس {st.session_state.temp_user['full_name']}")
    u_p = st.text_input("أدخل كلمة المرور الخاصة بك", type="password")
    if st.button("تسجيل دخول آمن", use_container_width=True, type="primary"):
        if u_p == str(st.session_state.temp_user['password']):
            st.session_state.user_data = st.session_state.temp_user; st.session_state.step = 'archive'; st.rerun()
        else: st.error("❌ كلمة المرور خاطئة")
    if st.button("إلغاء"): st.session_state.step = 'welcome'; st.rerun()

# [صفحة المكتبة والأرشيف والنتائج]
elif st.session_state.step == 'archive':
    st.header(f"📚 المكتبة الرقمية")
    menu = st.selectbox("انتقل إلى القسم المطلوب:", ["المحاضرات الدراسية", "إعلانات عامة للكلية", "نتائج الامتحانات (PDF)"])
    
    if menu == "المحاضرات الدراسية":
        year = st.radio("اختر السنة الدراسية:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"], horizontal=True)
        db = get_db(); subs = [r['subject_name'] for r in db.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (year,)).fetchall()]; db.close()
        if subs:
            s_s = st.selectbox("اختر المادة العلمية:", subs)
            db = get_db(); lecs = db.execute("SELECT * FROM university_archive WHERE academic_year=? AND subject_name=?", (year, s_s)).fetchall(); db.close()
            if lecs:
                for l in lecs:
                    col_l1, col_l2 = st.columns([3, 1])
                    col_l1.write(f"📄 {l['lecture_title']}")
                    col_l2.link_button("تحميل", l['file_url'], use_container_width=True)
            else: st.info("لا توجد محاضرات مرفوعة لهذه المادة حالياً.")
        else: st.warning("جاري ترتيب مواد هذه السنة.")

    elif menu == "إعلانات عامة للكلية":
        st.subheader("📌 جداول الدوام وتوزيع الفئات")
        st.info("تجد هنا كافة التعاميم الخاصة بالدوام الرسمي.")

    elif menu == "نتائج الامتحانات (PDF)":
        st.subheader("📊 نتائج الامتحانات الرسمية")
        y_r = st.selectbox("عرض نتائج سنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"])
        db = get_db(); results = db.execute("SELECT * FROM exam_results WHERE academic_year=?", (y_r,)).fetchall(); db.close()
        if results:
            for r in results:
                col_r1, col_r2 = st.columns([3, 1])
                col_r1.write(f"📊 {r['result_title']}")
                col_r2.link_button("فتح PDF", r['pdf_url'], use_container_width=True)
        else: st.info("لا توجد نتائج مرفوعة حالياً.")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_data = None; st.session_state.step = 'welcome'; st.rerun()
