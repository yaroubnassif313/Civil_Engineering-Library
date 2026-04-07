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

# دالة حساب الإحصائيات تلقائياً (تحديث حي)
def get_auto_stats():
    try:
        db = get_db()
        subj = db.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        stud = db.execute("SELECT COUNT(*) FROM access_gate").fetchone()[0]
        lecs = db.execute("SELECT COUNT(*) FROM university_archive").fetchone()[0]
        db.close()
        return subj, stud, lecs
    except:
        return 0, 0, 0

# --- 2. إدارة حالة التطبيق (Session State) ---
if 'step' not in st.session_state: st.session_state.step = 'welcome'
if 'user_data' not in st.session_state: st.session_state.user_data = None
if 'temp_user' not in st.session_state: st.session_state.temp_user = None

# التحقق من الوضع السري للمسؤول (Admin Mode)
query_params = st.query_params
is_admin_mode = query_params.get("role") == "admin"

# --- 3. القائمة الجانبية (الأدوات الدائمة - Sidebar) ---
with st.sidebar:
    st.title("🛠️ أدوات المهندس الشاملة")
    
    # [أ] الحاسبة العلمية المتطورة (Casio FX Style)
    st.subheader("📟 الحاسبة العلمية")
    with st.expander("فتح الحاسبة الهندسية", expanded=False):
        # دمج محاكي علمي عالمي يدعم (sin, cos, tan, log, التكاملات)
        st.components.v1.iframe("https://desmos.com", height=500, scrolling=False)
        st.caption("تحتوي على كافة العمليات الهندسية المعقدة")

    st.divider()

    # [ب] حاسبة تحويل الوحدات الشاملة
    st.subheader("⚖️ محول الوحدات")
    with st.expander("إجراء تحويل سريع", expanded=False):
        val = st.number_input("أدخل القيمة:", value=1.0)
        u_type = st.selectbox("نوع التحويل:", [
            "متر ➔ إنش", "إنش ➔ متر", 
            "كيلو غرام ➔ طن", "طن ➔ كيلو غرام",
            "نيوتن ➔ كيلو غرام قوة", "بايت ➔ ميجابايت"
        ])
        if u_type == "متر ➔ إنش": st.success(f"النتيجة: {val * 39.37:.2f} in")
        elif u_type == "إنش ➔ متر": st.success(f"النتيجة: {val / 39.37:.2f} m")
        elif u_type == "كيلو غرام ➔ طن": st.success(f"النتيجة: {val / 1000:.4f} Ton")
        elif u_type == "طن ➔ كيلو غرام": st.success(f"النتيجة: {val * 1000:.0f} kg")

    st.divider()

    # [ج] نظام الدعم الفني (يقرأ من قاعدة البيانات)
    st.subheader("📞 الدعم الفني والإدارة")
    try:
        db = get_db()
        admins = db.execute("SELECT * FROM support_info").fetchall()
        db.close()
        for admin in admins:
            with st.expander(f"👤 {admin['admin_name']}"):
                st.link_button("تليجرام", admin['telegram_url'], use_container_width=True)
                st.link_button("واتساب", admin['whatsapp_url'], use_container_width=True)
    except:
        st.info("جاري تحميل بيانات المشرفين...")

# --- 4. الواجهة الرئيسية (تظهر لجميع الزوار) ---
st.title("🏗️ Civil Engineering Hub")
st.write("مرحباً بك في المنصة الرقمية الأكاديمية - كلية الهندسة المدنية")

# [1] عداد حالة الموقع التلقائي
s_c, st_c, l_c = get_auto_stats()
col1, col2, col3 = st.columns(3)
col1.metric("📚 المواد المرفوعة", f"{s_c}")
col2.metric("👥 الطلاب المسجلين", f"{st_c}")
col3.metric("📄 المحاضرات والملفات", f"{l_c}")

# [2] لوحة إعلانات الكلية (تدعم النص والصور والفيديو والـ PDF)
try:
    db = get_db()
    news = db.execute("SELECT * FROM college_news ORDER BY id DESC LIMIT 1").fetchone()
    db.close()
    if news:
        with st.expander(f"📢 آخر الأخبار: {news['news_title']}", expanded=True):
            st.write(news['news_text'])
            if news['media_type'] == 'image': st.image(news['media_url'], caption="إعلان مصور")
            elif news['media_type'] == 'video': st.video(news['media_url'])
            elif news['media_type'] == 'pdf': st.link_button("💾 تحميل التعميم (PDF)", news['media_url'], use_container_width=True)
except:
    st.info("📢 لا يوجد إعلانات جديدة حالياً.")

st.divider()

# --- 5. منطق التنقل والخصوصية (Navigation) ---

# [صفحة الترحيب]
if st.session_state.step == 'welcome':
    if st.session_state.user_data:
        st.success(f"مرحباً بعودتك مهندس {st.session_state.user_data['full_name']}")
        if st.button("الانتقال إلى أرشيف محاضراتي", use_container_width=True, type="primary"):
            st.session_state.step = 'archive'
            st.rerun()
    else:
        if st.button("دخول الطلاب | Student Access", use_container_width=True, type="primary"):
            st.session_state.step = 'login'
            st.rerun()
    
    # الوضع السري للمسؤول (يظهر فقط بالرابط السري)
    if is_admin_mode:
        st.warning("تم اكتشاف رابط الإدارة السري")
        if st.button("الدخول إلى لوحة التحكم (Admin)"):
            st.info("هذا القسم يتم إدارته عبر قاعدة البيانات حالياً.")

# [صفحة تسجيل الدخول - المرحلة 1]
elif st.session_state.step == 'login':
    st.header("🔑 التحقق من الهوية الجامعية")
    u_name = st.text_input("الاسم الثلاثي المعتمد")
    u_serial = st.text_input("الرقم التسلسلي (الجامعي)")
    
    if st.button("تحقق من البيانات", use_container_width=True, type="primary"):
        db = get_db()
        user = db.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (u_name, u_serial)).fetchone()
        db.close()
        if user:
            st.session_state.temp_user = user
            st.session_state.step = 'password'
            st.rerun()
        else:
            st.error("⚠️ البيانات غير موجودة. يرجى التأكد من الكتابة بدقة أو مراسلة الدعم الفني.")
    
    if st.button("عودة للرئيسية"):
        st.session_state.step = 'welcome'
        st.rerun()

# [صفحة كلمة المرور - المرحلة 2]
elif st.session_state.step == 'password':
    st.header(f"🔒 خصوصية المهندس {st.session_state.temp_user['full_name']}")
    u_pass = st.text_input("أدخل كلمة المرور الخاصة بك:", type="password")
    
    if st.button("تسجيل الدخول الآمن", use_container_width=True, type="primary"):
        if u_pass == str(st.session_state.temp_user['password']):
            st.session_state.user_data = st.session_state.temp_user
            st.session_state.step = 'archive'
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة. حاول مجدداً.")
            
    if st.button("إلغاء"):
        st.session_state.step = 'welcome'
        st.rerun()

# [صفحة الأرشيف والنتائج]
elif st.session_state.step == 'archive':
    st.header(f"📚 المكتبة الرقمية")
    menu = st.selectbox("انتقل إلى القسم المطلوب:", ["المحاضرات الدراسية", "نتائج الامتحانات الأكاديمية (PDF)"])
    
    if menu == "المحاضرات الدراسية":
        year = st.radio("اختر السنة الدراسية:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"], horizontal=True)
        
        db = get_db()
        subjects = [r['subject_name'] for r in db.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (year,)).fetchall()]
        db.close()
        
        if subjects:
            sel_sub = st.selectbox("اختر المادة العلمية:", subjects)
            st.divider()
            
            db = get_db()
            lectures = db.execute("SELECT * FROM university_archive WHERE academic_year=? AND subject_name=?", (year, sel_sub)).fetchall()
            db.close()
            
            if lectures:
                for lec in lectures:
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"📄 {lec['lecture_title']}")
                    c2.link_button("تحميل / عرض", lec['file_url'], use_container_width=True)
            else:
                st.info("لم يتم رفع محاضرات لهذه المادة بعد. ترقبوا التحديثات.")
        else:
            st.warning("جاري ترتيب مواد هذه السنة الدراسية.")

    elif menu == "نتائج الامتحانات الأكاديمية (PDF)":
        st.subheader("📊 نتائج الامتحانات الرسمية")
        y_res = st.selectbox("نتائج امتحانات سنة:", ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"])
        
        db = get_db()
        results = db.execute("SELECT * FROM exam_results WHERE academic_year=?", (y_res,)).fetchall()
        db.close()
        
        if results:
            for res in results:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📈 {res['result_title']}")
                col2.link_button("فتح الملف (PDF)", res['pdf_url'], use_container_width=True)
        else:
            st.info("لا توجد نتائج مرفوعة لهذه السنة حالياً.")

    if st.sidebar.button("تسجيل الخروج الآمن"):
        st.session_state.user_data = None
        st.session_state.step = 'welcome'
        st.rerun()

# --- نهاية الكود الأساسي للمنصة ---
