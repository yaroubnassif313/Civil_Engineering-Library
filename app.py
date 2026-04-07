# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import math

# --- 1. الإعدادات الهندسية وجمالية الواجهة ---
st.set_page_config(page_title="Civil Engineering Hub", layout="wide")

# دالة الاتصال بقاعدة البيانات
def get_db():
    conn = sqlite3.connect("Engineering_Library.db")
    conn.row_factory = sqlite3.Row
    return conn

# دالة حساب الإحصائيات تلقائياً
def get_auto_stats():
    try:
        db = get_db()
        subj = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        stud = db.execute("SELECT COUNT(*) FROM access_gate").fetchone()[0]
        lecs = db.execute("SELECT COUNT(*) FROM university_archive").fetchone()[0]
        db.close()
        return subj, stud, lecs
    except: return 0, 0, 0

# --- 2. إدارة حالة التطبيق (Session State) ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'user_data' not in st.session_state: st.session_state.user_data = None
if 'calc_val' not in st.session_state: st.session_state.calc_val = ""

# --- 3. القائمة الجانبية (الأدوات الدائمة - Sidebar) ---
with st.sidebar:
    st.title("🛠️ أدوات المهندس")
    
    # [أ] الآلة الحاسبة العلمية (بدون تسجيل دخول - مباشرة)
    st.subheader("📟 الحاسبة العلمية الذكية")
    with st.container(border=True):
        # خانة إدخال النص للحسابات المعقدة
        calc_exp = st.text_input("اكتب العملية هنا:", value=st.session_state.calc_val, placeholder="مثلاً: sin(30) + sqrt(16)")
        
        col_c1, col_c2, col_c3 = st.columns(3)
        if col_c1.button("sin"): st.session_state.calc_val += "math.sin(math.radians())"
        if col_c2.button("cos"): st.session_state.calc_val += "math.cos(math.radians())"
        if col_c3.button("tan"): st.session_state.calc_val += "math.tan(math.radians())"
        
        col_c4, col_c5, col_c6 = st.columns(3)
        if col_c4.button("√ الجذر"): st.session_state.calc_val += "math.sqrt()"
        if col_c5.button("^ الأس"): st.session_state.calc_val += "**"
        if col_c6.button("log"): st.session_state.calc_val += "math.log10()"

        if st.button("🟰 احسب النتيجة", use_container_width=True, type="primary"):
            try:
                # حساب النتيجة باستخدام مكتبة math
                allowed_names = {"math": math, "sin": math.sin, "cos": math.cos, "tan": math.tan, "sqrt": math.sqrt, "pi": math.pi, "log": math.log10}
                result = eval(calc_exp, {"__builtins__": None}, allowed_names)
                st.success(f"النتيجة: {result:.4f}")
            except:
                st.error("خطأ في الصيغة")
        if st.button("مسح 🧹", use_container_width=True):
            st.session_state.calc_val = ""
            st.rerun()

    st.divider()

    # [ب] محول الوحدات الشامل
    with st.expander("⚖️ محول الوحدات الهندسي"):
        val = st.number_input("القيمة", value=1.0)
        u_type = st.selectbox("نوع التحويل", ["متر ➔ إنش", "إنش ➔ متر", "كغ ➔ طن", "نيوتن ➔ كغ.ق"])
        if u_type == "متر ➔ إنش": st.write(f"النتيجة: {val * 39.37:.2f} in")
        elif u_type == "إنش ➔ متر": st.write(f"النتيجة: {val / 39.37:.2f} m")

    st.divider()
    
    # [ج] الدعم الفني (من قاعدة البيانات)
    st.subheader("📞 الدعم الفني")
    try:
        db = get_db()
        admins = db.execute("SELECT * FROM support_info").fetchall()
        db.close()
        for admin in admins:
            with st.expander(f"👤 {admin['admin_name']}"):
                st.link_button("تليجرام", admin['telegram_url'], use_container_width=True)
                st.link_button("واتساب", admin['whatsapp_url'], use_container_width=True)
    except: st.info("إعداد روابط الدعم...")

# --- 4. الواجهة الرئيسية ---
st.title("🏗️ Civil Engineering Hub")

# عرض الإحصائيات التلقائية
s_c, st_c, l_c = get_auto_stats()
col1, col2, col3 = st.columns(3)
col1.metric("📚 المواد", s_c)
col2.metric("👥 الطلاب", st_c)
col3.metric("📄 المحاضرات", l_c)

# لوحة الإعلانات العامة (تظهر للجميع)
try:
    db = get_db()
    news = db.execute("SELECT * FROM college_news ORDER BY id DESC LIMIT 1").fetchone()
    db.close()
    if news:
        with st.expander(f"📢 {news['news_title']}", expanded=True):
            st.write(news['news_text'])
            if news['media_type'] == 'image': st.image(news['media_url'])
            elif news['media_type'] == 'video': st.video(news['media_url'])
            elif news['media_type'] == 'pdf': st.link_button("تحميل الملف (PDF)", news['media_url'])
except: st.info("مرحباً بكم في المنصة الرقمية.")

st.divider()

# --- 5. منطق التنقل (Navigation) ---

if st.session_state.step == 'welcome':
    if st.session_state.user_data:
        st.success(f"مرحباً بعودتك مهندس {st.session_state.user_data['full_name']}")
        if st.button("الدخول للمحاضرات", use_container_width=True, type="primary"):
            st.session_state.step = 'archive'
            st.rerun()
    else:
        if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
            st.session_state.step = 'login'
            st.rerun()

elif st.session_state.step == 'login':
    st.header("🔑 التحقق من الهوية")
    u_name = st.text_input("الاسم الثلاثي")
    u_serial = st.text_input("الرقم الجامعي")
    if st.button("تحقق", use_container_width=True, type="primary"):
        db = get_db()
        user = db.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (u_name, u_serial)).fetchone()
        db.close()
        if user:
            st.session_state.temp_user = user
            st.session_state.step = 'password'
            st.rerun()
        else: st.error("⚠️ البيانات غير موجودة.")
    if st.button("عودة"):
        st.session_state.step = 'welcome'
        st.rerun()

elif st.session_state.step == 'password':
    st.header(f"🔒 خصوصية المهندس {st.session_state.temp_user['full_name']}")
    u_pass = st.text_input("كلمة المرور", type="password")
    if st.button("دخول", use_container_width=True, type="primary"):
        if u_pass == str(st.session_state.temp_user['password']):
            st.session_state.user_data = st.session_state.temp_user
            st.session_state.step = 'archive'
            st.rerun()
        else: st.error("❌ كلمة المرور خاطئة.")

elif st.session_state.step == 'archive':
    menu = st.selectbox("انتقل إلى:", ["المحاضرات الدراسية", "إعلانات عامة للكلية", "نتائج الامتحانات (PDF)"])
    
    if menu == "المحاضرات الدراسية":
        year = st.radio("السنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"], horizontal=True)
        db = get_db()
        subs = [r['subject_name'] for r in db.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (year,)).fetchall()]
        db.close()
        if subs:
            s_s = st.selectbox("المادة:", subs)
            db = get_db()
            ls = db.execute("SELECT * FROM university_archive WHERE academic_year=? AND subject_name=?", (year, s_s)).fetchall()
            db.close()
            for l in ls:
                c1, c2 = st.columns(); c1.write(f"📄 {l['lecture_title']}"); c2.link_button("فتح", l['file_url'])

    elif menu == "نتائج الامتحانات (PDF)":
        y_r = st.selectbox("السنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"])
        db = get_db()
        rs = db.execute("SELECT * FROM exam_results WHERE academic_year=?", (y_r,)).fetchall()
        db.close()
        if rs:
            for r in rs:
                c1, c2 = st.columns(); c1.write(f"📊 {r['result_title']}"); c2.link_button("فتح PDF", r['pdf_url'])
        else: st.info("لا توجد نتائج مرفوعة.")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_data = None
        st.session_state.step = 'welcome'
        st.rerun()
