# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# --- 1. إعدادات الصفحة الرسمية ---
st.set_page_config(page_title="Civil Engineering Hub", layout="centered")

# --- 2. محرك قاعدة البيانات ---
def get_db_connection():
    conn = sqlite3.connect("Engineering_Library.db")
    conn.row_factory = sqlite3.Row
    return conn

def verify_student(full_name, serial):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (full_name, serial))
    student = cursor.fetchone()
    conn.close()
    return student

# --- 3. نظام "تذكر الدخول" والدعم الفني ---
if 'step' not in st.session_state:
    st.session_state.step = 'welcome'
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# إضافة زر الدعم الفني في القائمة الجانبية (Sidebar) ليظهر في كل الصفحات
with st.sidebar:
    st.title("🛠️ الدعم الفني")
    st.write("إذا واجهت مشكلة في الدخول أو لم تجد اسمك، تواصل معنا:")
    
    # روابط التواصل (يمكنك تعديلها من هنا مستقبلاً)
    telegram_url = "https://t.me" # استبدل your_username بمعرفك
    whatsapp_url = "https://wa.me" # استبدل الـ X برقمك مع مفتاح الدولة
    
    st.link_button("💬 تليجرام الإدارة", telegram_url, use_container_width=True)
    st.link_button("🟢 واتساب الإدارة", whatsapp_url, use_container_width=True)
    st.divider()

# --- 4. واجهة المستخدم المحدثة ---

# [أ] صفحة الترحيب
if st.session_state.step == 'welcome':
    st.title("🏗️ Civil Engineering Hub")
    st.subheader("المنصة الرقمية لكلية الهندسة المدنية")
    st.divider()
    
    # ميزة حفظ الجلسة: إذا كان مسجل دخول سابقاً نرسله للأرشيف فوراً
    if st.session_state.user_data:
        if st.button("العودة إلى محاضراتي", use_container_width=True, type="primary"):
            st.session_state.step = 'main_archive'
            st.rerun()
    else:
        if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
            st.session_state.step = 'verify'
            st.rerun()

# [ب] صفحة التحقق مع زر إعادة المحاولة
elif st.session_state.step == 'verify':
    st.header("🔑 التحقق من الهوية")
    name_input = st.text_input("الاسم الثلاثي")
    serial_input = st.text_input("الرقم الجامعي")
    
    if st.button("تحقق", use_container_width=True, type="primary"):
        res = verify_student(name_input, serial_input)
        if res:
            st.session_state.user_data = res
            st.session_state.step = 'password_entry'
            st.rerun()
        else:
            st.error("⚠️ البيانات غير صحيحة أو غير مسجلة.")
            if st.button("إعادة المحاولة وتحديث الصفحة"):
                st.rerun()

# [ج] صفحة كلمة المرور
elif st.session_state.step == 'password_entry':
    st.header(f"🔒 المهندس {st.session_state.user_data['full_name']}")
    student_pass = st.text_input("أدخل كلمة المرور الخاصة بك", type="password")
    
    if st.button("دخول", use_container_width=True, type="primary"):
        if student_pass == str(st.session_state.user_data['password']):
            st.session_state.step = 'main_archive'
            st.rerun()
        else:
            st.error("❌ كلمة المرور خاطئة.")

# [د] صفحة الأرشيف (كما هي مع الاحتفاظ بالدخول)
elif st.session_state.step == 'main_archive':
    st.title("📚 أرشيف المواد")
    years_list = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
    selected_year = st.sidebar.selectbox("اختر السنة:", years_list)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (selected_year,))
    subjects = [row['subject_name'] for row in cursor.fetchall()]
    conn.close()
    
    if subjects:
        selected_subject = st.selectbox("المادة:", subjects)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT lecture_title, file_url FROM university_archive WHERE academic_year=? AND subject_name=?", (selected_year, selected_subject))
        lectures = cursor.fetchall()
        conn.close()
        
        for lec in lectures:
            c1, c2 = st.columns([3, 1])
            c1.write(f"📄 {lec['lecture_title']}")
            c2.link_button("فتح", lec['file_url'])
            
    if st.sidebar.button("تسجيل الخروج ونسح البيانات"):
        st.session_state.step = 'welcome'
        st.session_state.user_data = None
        st.rerun()
