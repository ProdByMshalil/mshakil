from flask import Flask, request, jsonify, redirect, session, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_secret_key_2026"
DB_FILE = "database.db"

# --- 1. قاعدة البيانات والتهيئة ---
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

# --- 2. واجهات اللعبة (الرئيسية) ---
@app.route('/')
def home():
    return "<h1>سيرفر اللعبة الإمبراطور عزو يعمل!</h1>"

@app.route('/register', methods=['POST'])
def game_register():
    data = request.get_json()
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", 
                     (data['username'], data['email'], data['password']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "موجود مسبقاً"}), 400

@app.route('/login', methods=['POST'])
def game_login():
    data = request.get_json()
    conn = sqlite3.connect(DB_FILE)
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (data['email'], data['password'])).fetchone()
    conn.close()
    if user: return jsonify({"status": "success", "username": user[0]})
    return jsonify({"status": "error"}), 400

# --- 3. لوحة الأدمن (الكاملة) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('password') == "12345":
            session['logged_in'] = True
    
    if not session.get('logged_in'):
        return "<form method='POST'>كلمة السر: <input type='password' name='password'><button>دخول</button></form>"

    conn = sqlite3.connect(DB_FILE)
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    html = "<style>body{background:#000; color:#0f0; font-family:monospace;}</style><h1>لوحة تحكم الإمبراطور عزو</h1><table border='1'><tr><th>اللاعب</th><th>الفلوس</th><th>الحالة</th><th>تحكم</th></tr>"
    for u in users:
        html += f"<tr><td>{u[0]}</td><td>{u[2]}</td><td>{'🔴 محظور' if u[4] else '🟢 نشط'}</td><td>"
        html += f"<a href='/admin/action?act=ban&u={u[0]}'>[حظر]</a> "
        html += f"<a href='/admin/action?act=money&u={u[0]}'>[+100]</a> "
        html += f"<a href='/admin/action?act=del&u={u[0]}'>[حذف]</a></td></tr>"
    return html + "</table><br><a href='/admin/logout'>تسجيل الخروج</a>"

@app.route('/admin/action')
def admin_action():
    if not session.get('logged_in'): return redirect('/admin')
    act, user = request.args.get('act'), request.args.get('u')
    conn = sqlite3.connect(DB_FILE)
    if act == 'ban': conn.execute("UPDATE users SET is_banned=1 WHERE username=?", (user,))
    elif act == 'money': conn.execute("UPDATE users SET money=money+100 WHERE username=?", (user,))
    elif act == 'del': conn.execute("DELETE FROM users WHERE username=?", (user,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
