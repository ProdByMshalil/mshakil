from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_secret_key_final"
DB_FILE = "database.db"

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

# --- 1. الموقع الرئيسي (للعبة) ---
@app.route('/')
def home():
    return "سيرفر اللعبة الإمبراطور عزو يعمل!"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", (data['username'], data['email'], data['password']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except: return jsonify({"status": "error"}), 400

# --- 2. لوحة تحكم الأدمن (التصميم النيون) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == "12345": session['logged_in'] = True
    
    if not session.get('logged_in'):
        return "<body style='background:#0d0d0d; color:#0f0; text-align:center;'><h2>دخول الإدارة</h2><form method='POST'>كلمة السر: <input type='password' name='password'><button>دخول</button></form></body>"

    conn = sqlite3.connect(DB_FILE)
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    
    html = "<style>body{background:#0d0d0d; color:#0f0; font-family:monospace;} table{width:100%; border:1px solid #0f0;} th,td{padding:10px; border:1px solid #0f0;}</style><h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>"
    html += "<table><tr><th>اللاعب</th><th>البريد</th><th>الفلوس</th><th>الحالة</th><th>الرسالة</th><th>تحكم</th></tr>"
    for u in users:
        html += f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[3]}</td><td>{'🔴' if u[4] else '🟢'}</td><td>{u[5]}</td>"
        html += f"<td><form action='/admin/action' method='POST'><input type='hidden' name='u' value='{u[0]}'>"
        html += "<input name='val' placeholder='قيمة/رسالة' size='8'> <button name='act' value='add'>+فلوس</button> <button name='act' value='sub'>-فلوس</button> <button name='act' value='ban'>حظر</button> <button name='act' value='msg'>رسالة</button> <button name='act' value='del'>حذف</button></form></td></tr>"
    return html + "</table><br><a href='/admin/logout'>تسجيل الخروج</a>"

@app.route('/admin/action', methods=['POST'])
def action():
    if not session.get('logged_in'): return redirect('/admin')
    act, user, val = request.form['act'], request.form['u'], request.form.get('val', '')
    conn = sqlite3.connect(DB_FILE)
    if act == 'add': conn.execute("UPDATE users SET money=money+? WHERE username=?", (val, user))
    elif act == 'sub': conn.execute("UPDATE users SET money=money-? WHERE username=?", (val, user))
    elif act == 'ban': conn.execute("UPDATE users SET is_banned=1 WHERE username=?", (user,))
    elif act == 'msg': conn.execute("UPDATE users SET admin_message=? WHERE username=?", (val, user))
    elif act == 'del': conn.execute("DELETE FROM users WHERE username=?", (user,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
