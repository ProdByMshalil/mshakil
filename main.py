from flask import Flask, request, jsonify, redirect, session, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"

DB_FILE = "database.db"

# تهيئة قاعدة البيانات
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

# --- واجهة الأدمن (بشكل النيون الأصلي) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('password') == "12345":
            session['logged_in'] = True
    
    if not session.get('logged_in'):
        return "<body style='background:#0d0d0d; color:#0f0; text-align:center;'><h2>دخول الإدارة</h2><form method='POST'>كلمة السر: <input type='password' name='password'><button>دخول</button></form></body>"

    conn = sqlite3.connect(DB_FILE)
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    # الشكل الجمالي (النيون)
    html = """
    <style>
        body { background: #1a1a2e; color: #fff; font-family: Arial; text-align: center; }
        table { margin: 20px auto; width: 90%; border-collapse: collapse; background: #0f3460; }
        th, td { padding: 15px; border: 1px solid #444; }
        button { background: #e94560; color: white; border: none; padding: 5px 10px; cursor: pointer; }
    </style>
    <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
    <table>
        <tr><th>اللاعب</th><th>البريد</th><th>الفلوس</th><th>الحالة</th><th>تحكم</th></tr>
    """
    for u in users:
        status = "🔴 محظور" if u[4] else "🟢 نشط"
        html += f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>💰 {u[2]}</td><td>{status}</td><td>"
        html += f"<a href='/admin/action?act=ban&u={u[0]}'><button>حظر</button></a> "
        html += f"<a href='/admin/action?act=money&u={u[0]}'><button>+100</button></a> "
        html += f"<a href='/admin/action?act=del&u={u[0]}'><button>حذف</button></a></td></tr>"
    return html + "</table><a href='/admin/logout' style='color:#e94560;'>تسجيل الخروج</a>"

# --- معالجة الأزرار (حل مشكلة 404) ---
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

# --- باقي المسارات ---
@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

# مسارات اللعبة للاتصال (تأكد أنها تظل كما كانت)
@app.route('/register', methods=['POST'])
def game_register():
    data = request.get_json()
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", (data['username'], data['email'], data['password']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except: return jsonify({"status": "error"}), 400

@app.route('/login', methods=['POST'])
def game_login():
    data = request.get_json()
    conn = sqlite3.connect(DB_FILE)
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (data['email'], data['password'])).fetchone()
    conn.close()
    if user: return jsonify({"status": "success", "username": user[0]})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
