from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_secret_key"
DB_FILE = "database.db"

# دالة لتهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT,
            money INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    # تسجيل الدخول
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "12345":
            session['logged_in'] = True
    
    if not session.get('logged_in'):
        return """
        <body style='background:#1a1a2e; color:white; text-align:center;'>
            <h2>دخول الإدارة</h2>
            <form method='POST'>
                <input name='username' placeholder='اسم المستخدم'><br>
                <input type='password' name='password' placeholder='كلمة المرور'><br>
                <button>دخول</button>
            </form>
        </body>
        """

    # جلب البيانات
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, money, is_banned FROM users")
    users = cursor.fetchall()
    conn.close()

    # إنشاء التنسيق الجمالي للوحة
    html = """
    <body style='background:#1a1a2e; color:white; text-align:center;'>
        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
        <table border='1' style='margin:auto; width:80%; border-collapse:collapse;'>
            <tr style='background:#0f3460;'>
                <th>اللاعب</th><th>البريد</th><th>الفلوس</th><th>الحالة</th><th>تحكم</th>
            </tr>
    """
    for u in users:
        status = "🟢 نشط" if not u[3] else "🔴 محظور"
        html += f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>💰 {u[2]}</td><td>{status}</td><td>...</td></tr>"
    
    html += "</table><br><a href='/admin/logout' style='color:red;'>تسجيل الخروج</a></body>"
    return html

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
