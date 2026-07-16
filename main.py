from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"
DB_FILE = "database.db"

# هنا تضع كامل أكواد الـ HTML القديمة الخاصة بك (HOME_HTML, ADMIN_LOGIN_HTML, ADMIN_DASHBOARD_HTML)
# (نفس الأكواد التي أرسلتها لي في البداية)

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

# المسار الخاص باللعبة (API)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, money, is_banned, admin_message FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row and row[1] == password:
        if row[3] == 1: return jsonify({"status": "error", "message": "محظور"}), 403
        return jsonify({"status": "success", "username": row[0], "money": row[2], "msg": row[4]}), 200
    return jsonify({"status": "error", "message": "خطأ"}), 400

# مسارات الإدارة (بكامل وظائفها القديمة)
@app.route('/admin')
def admin():
    if session.get('logged_in'): return redirect(url_for('admin_dashboard'))
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('username') == "admin" and request.form.get('password') == "12345":
        session['logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    return "خطأ"

@app.route('/admin/dashboard')
def admin_dashboard():
    # هنا ضع الكود الخاص بـ استخراج بيانات اللاعبين وعرضها في الجدول
    return render_template_string(ADMIN_DASHBOARD_HTML)

# (أضف هنا باقي الدوال: ban, unban, add_money, send_message كما كانت عندك بالضبط)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
