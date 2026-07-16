from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"
DB_FILE = "database.db"

# --- استدعاء الأشكال القديمة ---
HOME_HTML = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><style>
body { background: linear-gradient(135deg, #0f0c1b, #201335); color: #ffffff; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; }
.container { background: rgba(255, 255, 255, 0.05); padding: 40px; border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; }
h1 { background: linear-gradient(45deg, #ff007f, #7f00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style></head><body><div class="container"><h1>🎮 اللعبة تحت التطوير 🎮</h1><p>سيرفر عزو الأسطوري</p></div></body></html>"""

ADMIN_LOGIN_HTML = """<div style="background:#0f0c1b; color:white; height:100vh; display:flex; align-items:center; justify-content:center;">
<form method="POST" action="/admin/login" style="padding:40px; border:1px solid #ff007f; border-radius:15px;">
<h2>دخول الإدارة 🔐</h2><input name="username" placeholder="الاسم" required><br><br>
<input type="password" name="password" placeholder="الباسورد" required><br><br>
<button type="submit">دخول</button></form></div>"""

# --- دوال العمليات (التي طلبتها) ---
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
        return jsonify({"status": "success", "username": row[0], "money": row[2]}), 200
    return jsonify({"status": "error", "message": "خطأ"}), 400

@app.route('/')
def home(): return render_template_string(HOME_HTML)

@app.route('/admin')
def admin():
    if session.get('logged_in'): return "لوحة التحكم تعمل!"
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('username') == "admin" and request.form.get('password') == "12345":
        session['logged_in'] = True
        return redirect('/admin')
    return "خطأ"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
