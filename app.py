# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# --- 1. الإعدادات الهندسية الأساسية ---
st.set_page_config(page_title="Civil Engineering Hub", layout="centered")

# --- 2. محرك قاعدة البيانات (DB Engine) ---
def get_db_connection():
    conn = sqlite3.connect("Engineering_Library.db")
    conn.row_factory = sqlite3.Row  # لجلب البيانات كأسماء أعمدة
    return conn

# --- 3. نظام التحقق المطور (Privacy System) ---
def verify_student(full_name, serial):
    conn = get_db_connection()
    cursor = conn.cursor()
    # التحقق من وجود الطالب ورقمه الجامعي
    cursor.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (full_name, serial))
    student = cursor.fetchone()
    conn.close()
    return student

# --- 4. إدارة حالة التطبيق (State Management) ---
if 'step' not in st.session_state:
    st.session_state.step = 'welcome'
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

# --- 5. واجهة المستخدم (User Interface) ---

# [أ] صفحة الترحيب (Welcome)
if st.session_state.step == 'welcome':
    st.title("🏗️ Civil Engineering Hub")
    st.subheader("المنصة الرقمية لكلية الهندسة المدنية")
    st.divider()
    if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
        st.session_state.step = 'verify'
        st.rerun()

# [ب] صفحة التحقق الأولية (Identity Check)
elif st.session_state.step == 'verify':
    st.header("🔑 التحقق من الهوية الجامعية")
    name_input = st.text_input("الاسم الثلاثي")
    serial_input = st.text_input("الرقم الجامعي")
    
    if st.button("التحقق من البيانات", use_container_width=True, type="primary"):
        res = verify_student(name_input, serial_input)
        if res:
            st.session_state.user_data = res
            st.session_state.step = 'password_entry'
            st.rerun()
        else:
            st.error("بيانات الطالب غير موجودة. يرجى مراجعة الإدارة.")
    
    if st.button("عودة"):
        st.session_state.step = 'welcome'
        st.rerun()

# [ج] صفحة كلمة المرور الخاصة (Privacy Password)
elif st.session_state.step == 'password_entry':
    st.header(f"🔒 مرحباً مهندس {st.session_state.user_data['full_name']}")
    st.write("يرجى إدخال كلمة المرور الخاصة بالطالب للمتابعة:")
    
    # جلب كلمة المرور المخزنة في قاعدة البيانات (حقل password)
    # ملاحظة: يجب التأكد من وجود عمود باسم password في جدول access_gate
    student_pass = st.text_input("كلمة المرور", type="password")
    
    if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
        # نقارن كلمة المرور المدخلة بما هو موجود في قاعدة البيانات
        if student_pass == str(st.session_state.user_data['password']):
            st.session_state.step = 'main_archive'
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة.")
            
    if st.button("إلغاء"):
        st.session_state.step = 'welcome'
        st.rerun()

# [د] صفحة الأرشيف والمواد (The Archive)
elif st.session_state.step == 'main_archive':
    st.title("📚 أرشيف المواد الدراسية")
    years_list = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
    selected_year = st.sidebar.selectbox("اختر السنة الدراسية:", years_list)
    
    # جلب المواد
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (selected_year,))
    subjects = [row['subject_name'] for row in cursor.fetchall()]
    conn.close()
    
    if subjects:
        selected_subject = st.selectbox("اختر المادة:", subjects)
        st.divider()
        
        # جلب المحاضرات
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT lecture_title, file_url FROM university_archive WHERE academic_year=? AND subject_name=?", (selected_year, selected_subject))
        lectures = cursor.fetchall()
        conn.close()
        
        if lectures:
            for lec in lectures:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📄 {lec['lecture_title']}")
                c2.link_button("تحميل", lec['file_url'], use_container_width=True)
        else:
            st.info("لم يتم رفع محاضرات لهذه المادة بعد.")
            
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.step = 'welcome'
        st.session_state.user_data = None
        st.rerun()

# --- نهاية الكود الأساسي ---
# يمكنك إضافة أي تعديلات مستقبلية ابتداءً من السطر القادم:
