from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"
DB_FILE = "database.db"

# --- المتغيرات التي تحتوي على تصميماتك القديمة (ضع أكوادك هنا) ---
# سأضع لك مثالاً بسيطاً، انسخ أنت أكواد الـ HTML الأصلية التي كانت عندك وضعها هنا:
HOME_HTML = "<h1>مرحباً بك في سيرفر عزو الأسطوري</h1>"
ADMIN_LOGIN_HTML = "<h2>دخول الإدارة</h2><form method='POST' action='/admin/login'><input name='username' placeholder='الاسم'><input type='password' name='password' placeholder='الباسوورد'><button>دخول</button></form>"
ADMIN_DASHBOARD_HTML = "<h1>لوحة التحكم تعمل!</h1><a href='/admin/logout'>خروج</a>"

# --- 1. مسارات اللعبة (API) ---
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
