# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

st.set_page_config(page_title="Civil Engineering Hub", layout="wide")

def get_db():
    conn = sqlite3.connect("Engineering_Library.db")
    conn.row_factory = sqlite3.Row
    return conn

# --- حساب الإحصائيات تلقائياً من الجداول ---
def get_auto_stats():
    db = get_db()
    subj_count = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
    stud_count = db.execute("SELECT COUNT(*) FROM access_gate").fetchone()[0]
    lec_count = db.execute("SELECT COUNT(*) FROM university_archive").fetchone()[0]
    db.close()
    return subj_count, stud_count, lec_count

if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'user_data' not in st.session_state: st.session_state.user_data = None

# --- القائمة الجانبية (الأدوات والدعم) ---
with st.sidebar:
    st.title("🔢 أدوات المهندس")
    # (هنا توضع الحاسبة ومحول الوحدات كما في الكود السابق)
    st.divider()
    st.title("📞 الدعم الفني")
    db = get_db()
    admins = db.execute("SELECT * FROM support_info").fetchall()
    db.close()
    for admin in admins:
        with st.expander(f"👤 {admin['admin_name']}"):
            st.link_button("تليجرام", admin['telegram_url'], use_container_width=True)
            st.link_button("واتساب", admin['whatsapp_url'], use_container_width=True)

# --- الواجهة الرئيسية ---
st.title("🏗️ Civil Engineering Hub")

# 1. عرض الإحصائيات (تلقائية)
s_count, st_count, l_count = get_auto_stats()
c1, c2, c3 = st.columns(3)
c1.metric("📚 المواد", s_count)
c2.metric("👥 الطلاب", st_count)
c3.metric("📄 المحاضرات", l_count)

# 2. عرض الإعلانات (يدعم PDF، صور، فيديو)
db = get_db()
news = db.execute("SELECT * FROM college_news ORDER BY id DESC LIMIT 1").fetchone()
db.close()
if news:
    with st.expander(f"📢 {news['news_title']}", expanded=True):
        st.write(news['news_text'])
        if news['media_type'] == 'image': st.image(news['media_url'])
        elif news['media_type'] == 'video': st.video(news['media_url'])
        elif news['media_type'] == 'pdf': st.link_button("تحميل الإعلان (PDF)", news['media_url'])

st.divider()

# --- منطق الصفحات ---
if st.session_state.step == 'welcome':
    if st.button("دخول الطلاب", use_container_width=True, type="primary"):
        st.session_state.step = 'login'
        st.rerun()

elif st.session_state.step == 'login':
    # (كود تسجيل الدخول بالاسم والرقم والباسورد كما في الكود الصخري)
    pass

elif st.session_state.step == 'archive':
    menu = st.selectbox("انتقل إلى:", ["المحاضرات", "نتائج الامتحانات (PDF)"])
    
    if menu == "نتائج الامتحانات (PDF)":
        year = st.selectbox("السنة", ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة"])
        db = get_db()
        results = db.execute("SELECT * FROM exam_results WHERE academic_year=?", (year,)).fetchall()
        db.close()
        for res in results:
            col1, col2 = st.columns([3, 1])
            col1.write(f"📊 {res['result_title']}")
            col2.link_button("فتح PDF", res['pdf_url'])
