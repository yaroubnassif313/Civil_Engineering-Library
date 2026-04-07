# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import math

# --- 1. إعدادات الصفحة والجمالية ---
st.set_page_config(page_title="Civil Engineering Hub", layout="wide")

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

# --- 2. إدارة حالة التطبيق ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'user_data' not in st.session_state: st.session_state.user_data = None

# --- 3. القائمة الجانبية (الأدوات الدائمة) ---
with st.sidebar:
    st.title("🛠️ أدوات المهندس")
    # الحاسبة العلمية
    with st.expander("🔢 آلة حاسبة علمية", expanded=False):
        calc_input = st.text_input("أدخل العملية (مثال: 5*math.pi)", "0")
        if st.button("احسب"):
            try: st.success(f"النتيجة: {eval(calc_input, {'math': math, '__builtins__': None})}")
            except: st.error("خطأ في الصيغة")
    
    # محول الوحدات
    with st.expander("⚖️ محول الوحدات", expanded=False):
        val = st.number_input("القيمة", value=1.0)
        u_type = st.selectbox("النوع", ["متر إلى إنش", "إنش إلى متر", "كغ إلى طن", "طن إلى كغ"])
        if u_type == "متر إلى إنش": st.write(f"النتيجة: {val * 39.37:.2f} إنش")
        elif u_type == "إنش إلى متر": st.write(f"النتيجة: {val / 39.37:.2f} متر")
    
    st.divider()
    st.title("📞 الدعم الفني")
    try:
        db = get_db()
        admins = db.execute("SELECT * FROM support_info").fetchall()
        db.close()
        for admin in admins:
            with st.expander(f"👤 {admin['admin_name']}"):
                st.link_button("تليجرام", admin['telegram_url'], use_container_width=True)
                st.link_button("واتساب", admin['whatsapp_url'], use_container_width=True)
    except: st.info("إعداد الدعم...")

# --- 4. الواجهة الرئيسية (تظهر للجميع) ---
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
except: st.info("أهلاً بكم في المنصة الرقمية.")

st.divider()

# --- 5. منطق الصفحات (التنقل) ---

# [صفحة الترحيب]
if st.session_state.step == 'welcome':
    if st.session_state.user_data:
        st.success(f"مرحباً بعودتك مهندس {st.session_state.user_data['full_name']}")
        if st.button("الدخول للأرشيف", use_container_width=True, type="primary"):
            st.session_state.step = 'archive'
            st.rerun()
    else:
        if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
            st.session_state.step = 'login'
            st.rerun()

# [صفحة تسجيل الدخول والخصوصية]
elif st.session_state.step == 'login':
    st.header("🔑 تسجيل الدخول")
    u_name = st.text_input("الاسم الثلاثي")
    u_serial = st.text_input("الرقم الجامعي")
    if st.button("تحقق من الهوية", use_container_width=True, type="primary"):
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
    st.header(f"🔒 كلمة مرور المهندس {st.session_state.temp_user['full_name']}")
    u_pass = st.text_input("أدخل كلمة المرور", type="password")
    if st.button("دخول", use_container_width=True, type="primary"):
        if u_pass == str(st.session_state.temp_user['password']):
            st.session_state.user_data = st.session_state.temp_user
            st.session_state.step = 'archive'
            st.rerun()
        else: st.error("❌ كلمة المرور خاطئة.")

# [صفحة الأرشيف والنتائج]
elif st.session_state.step == 'archive':
    menu = st.selectbox("انتقل إلى:", ["المحاضرات الدراسية", "إعلانات عامة للكلية", "نتائج الامتحانات (PDF)"])
    
    if menu == "المحاضرات الدراسية":
        year = st.radio("اختر السنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"], horizontal=True)
        db = get_db()
        subjects = [r['subject_name'] for r in db.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (year,)).fetchall()]
        db.close()
        if subjects:
            sel_sub = st.selectbox("اختر المادة:", subjects)
            db = get_db()
            lecs = db.execute("SELECT * FROM university_archive WHERE academic_year=? AND subject_name=?", (year, sel_sub)).fetchall()
            db.close()
            for l in lecs:
                c1, c2 = st.columns([3,1])
                c1.write(f"📄 {l['lecture_title']}")
                c2.link_button("فتح", l['file_url'])
        else: st.info("لا يوجد مواد مرفوعة.")

    elif menu == "نتائج الامتحانات (PDF)":
        y_res = st.selectbox("نتائج سنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"])
        db = get_db()
        results = db.execute("SELECT * FROM exam_results WHERE academic_year=?", (y_res,)).fetchall()
        db.close()
        if results:
            for r in results:
                c1, c2 = st.columns([3,1])
                c1.write(f"📊 {r['result_title']}")
                c2.link_button("فتح PDF", r['pdf_url'])
        else: st.info("لا توجد نتائج مرفوعة حالياً.")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_data = None
        st.session_state.step = 'welcome'
        st.rerun()
