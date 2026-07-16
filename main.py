from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"
DB_FILE = "database.db"

# --- HTML Templates ---
HOME_HTML = "<h1>السيرفر يعمل!</h1>"
ADMIN_LOGIN_HTML = "<h2>دخول الإدارة</h2><form method='POST' action='/admin/login'><input name='username'><input type='password' name='password'><button>دخول</button></form>"

# --- Routes ---

# 1. واجهة اللعبة (للـ API)
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

# 2. لوحة تحكم الإدارة (Admin)
@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/admin', methods=['GET'])
def admin_page():
    if session.get('logged_in'):
        return "أهلاً بك في لوحة التحكم!" # يمكنك إعادة وضع كود الـ Dashboard هنا
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('username') == "admin" and request.form.get('password') == "12345":
        session['logged_in'] = True
        return redirect(url_for('admin_page'))
    return "خطأ في الدخول"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
