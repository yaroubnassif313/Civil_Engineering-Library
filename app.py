# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# --- 1. إعدادات الصفحة والواجهة ---
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

# --- 2. إدارة حالة التطبيق ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'user_data' not in st.session_state: st.session_state.user_data = None

# --- 3. القائمة الجانبية (الدعم الفني فقط) ---
with st.sidebar:
    st.title("📞 الدعم الفني")
    try:
        db = get_db()
        admins = db.execute("SELECT * FROM support_info").fetchall()
        db.close()
        for admin in admins:
            with st.expander(f"👤 {admin['admin_name']}"):
                st.link_button("تليجرام", admin['telegram_url'], use_container_width=True)
                st.link_button("واتساب", admin['whatsapp_url'], use_container_width=True)
    except:
        st.info("تواصل مع المهندس يعرب ناصيف للإدارة.")

# --- 4. الواجهة الرئيسية للمنصة ---
st.title("🏗️ Civil Engineering Hub")
st.write("المكتبة الرقمية والأرشيف الأكاديمي الشامل لطلاب الهندسة المدنية")

# عرض الإحصائيات التلقائية (Live Stats)
s_c, st_c, l_c = get_auto_stats()
col1, col2, col3 = st.columns(3)
col1.metric("📚 المواد المرفوعة", s_c)
col2.metric("👥 الطلاب المسجلين", st_c)
col3.metric("📄 المحاضرات والملفات", l_c)

# لوحة الإعلانات العامة (تظهر للجميع)
try:
    db = get_db()
    news = db.execute("SELECT * FROM college_news ORDER BY id DESC LIMIT 1").fetchone()
    db.close()
    if news:
        with st.expander(f"📢 آخر الأخبار: {news['news_title']}", expanded=True):
            st.write(news['news_text'])
            if news['media_type'] == 'image': st.image(news['media_url'])
            elif news['media_type'] == 'video': st.video(news['media_url'])
            elif news['media_type'] == 'pdf': st.link_button("💾 تحميل الملف (PDF)", news['media_url'], use_container_width=True)
except:
    st.info("📢 أهلاً بكم في المنصة الرقمية الرسمية.")

st.divider()

# --- 5. منطق التنقل والخصوصية ---

# [صفحة الترحيب]
if st.session_state.step == 'welcome':
    if st.session_state.user_data:
        st.success(f"مرحباً بعودتك مهندس {st.session_state.user_data['full_name']}")
        if st.button("الانتقال إلى محاضراتي", use_container_width=True, type="primary"):
            st.session_state.step = 'archive'
            st.rerun()
    else:
        if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
            st.session_state.step = 'login'
            st.rerun()

# [صفحة تسجيل الدخول - التحقق الأول]
elif st.session_state.step == 'login':
    st.header("🔑 التحقق من الهوية")
    u_name = st.text_input("الاسم الثلاثي المعتمد")
    u_serial = st.text_input("الرقم الجامعي")
    
    if st.button("تحقق", use_container_width=True, type="primary"):
        db = get_db()
        user = db.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (u_name, u_serial)).fetchone()
        db.close()
        if user:
            st.session_state.temp_user = user
            st.session_state.step = 'password'
            st.rerun()
        else:
            st.error("⚠️ البيانات غير موجودة. يرجى التواصل مع الإدارة.")
    
    if st.button("رجوع"):
        st.session_state.step = 'welcome'
        st.rerun()

# [صفحة كلمة المرور - الخصوصية]
elif st.session_state.step == 'password':
    st.header(f"🔒 خصوصية المهندس {st.session_state.temp_user['full_name']}")
    u_pass = st.text_input("أدخل كلمة المرور الخاصة بك", type="password")
    
    if st.button("تسجيل دخول آمن", use_container_width=True, type="primary"):
        if u_pass == str(st.session_state.temp_user['password']):
            st.session_state.user_data = st.session_state.temp_user
            st.session_state.step = 'archive'
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة.")
            
    if st.button("إلغاء"):
        st.session_state.step = 'welcome'
        st.rerun()

# [صفحة الأرشيف والنتائج]
elif st.session_state.step == 'archive':
    st.header("📚 المكتبة الرقمية")
    menu = st.selectbox("انتقل إلى:", ["المحاضرات الدراسية", "إعلانات عامة للكلية", "نتائج الامتحانات (PDF)"])
    
    if menu == "المحاضرات الدراسية":
        year = st.radio("اختر السنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"], horizontal=True)
        db = get_db()
        subjects = [r['subject_name'] for r in db.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (year,)).fetchall()]
        db.close()
        
        if subjects:
            sel_sub = st.selectbox("المادة:", subjects)
            st.divider()
            db = get_db()
            lecs = db.execute("SELECT * FROM university_archive WHERE academic_year=? AND subject_name=?", (year, sel_sub)).fetchall()
            db.close()
            if lecs:
                for l in lecs:
                    c1, c2 = st.columns()
                    c1.write(f"📄 {l['lecture_title']}")
                    c2.link_button("فتح", l['file_url'], use_container_width=True)
            else: st.info("لا توجد ملفات مرفوعة لهذه المادة.")
        else: st.warning("جاري ترتيب مواد هذه السنة.")

    elif menu == "نتائج الامتحانات (PDF)":
        st.subheader("📊 نتائج الامتحانات الرسمية")
        y_res = st.selectbox("نتائج سنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"])
        db = get_db()
        results = db.execute("SELECT * FROM exam_results WHERE academic_year=?", (y_res,)).fetchall()
        db.close()
        if results:
            for r in results:
                c1, c2 = st.columns()
                c1.write(f"📈 {r['result_title']}")
                c2.link_button("فتح PDF", r['pdf_url'], use_container_width=True)
        else: st.info("لا توجد نتائج مرفوعة حالياً.")

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.user_data = None
        st.session_state.step = 'welcome'
        st.rerun()
