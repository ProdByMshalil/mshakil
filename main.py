from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"
DB_FILE = "database.db"

# --- تصميماتك الأسطورية (النيون والشكل الحلو) ---
HOME_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><style>
body { background: linear-gradient(135deg, #0f0c1b, #201335); color: #ffffff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
h1 { font-size: 2.5rem; background: linear-gradient(45deg, #ff007f, #7f00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 20px rgba(127, 0, 255, 0.5); }
</style></head><body><h1>🎮 اللعبة تحت التطوير 🎮</h1></body></html>
"""

ADMIN_LOGIN_HTML = """
<!DOCTYPE html><html lang="ar" dir="rtl"><head><style>
body { background: #0f0c1b; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; }
.login-card { background: rgba(255, 255, 255, 0.03); padding: 40px; border-radius: 15px; border: 1px solid #ff007f; }
input { width: 100%; padding: 10px; margin: 10px 0; background: #222; color: white; border: 1px solid #7f00ff; border-radius: 5px; }
button { width: 100%; padding: 10px; background: linear-gradient(45deg, #7f00ff, #ff007f); border: none; color: white; cursor: pointer; }
</style></head><body><div class="login-card"><h2>تسجيل دخول الإدارة 🔐</h2>
<form method="POST" action="/admin/login">
<input name="username" placeholder="اسم المستخدم" required>
<input type="password" name="password" placeholder="كلمة المرور" required>
<button type="submit">دخول</button></form></div></body></html>
"""

ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html><html lang="ar" dir="rtl"><head><style>
body { background: #0b0813; color: #fff; padding: 20px; }
h1 { color: #00f0ff; text-shadow: 0 0 10px #00f0ff; }
.logout-btn { background: #ff3333; padding: 10px; color: white; text-decoration: none; border-radius: 8px; }
</style></head><body>
<h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
<a href="/admin/logout" class="logout-btn">تسجيل الخروج 🚪</a>
</body></html>
"""

# --- 1. مسار اللعبة (API) ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[1] == password:
        return jsonify({"status": "success", "username": row[0]}), 200
    return jsonify({"status": "error", "message": "بيانات خاطئة"}), 400

# --- 2. مسارات لوحة التحكم (Admin) ---
@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/admin')
def admin():
    if session.get('logged_in'):
        return render_template_string(ADMIN_DASHBOARD_HTML)
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('username') == "admin" and request.form.get('password') == "12345":
        session['logged_in'] = True
        return redirect('/admin')
    return "خطأ في الدخول"

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
