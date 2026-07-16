from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_secret_key"
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

@app.route('/')
def home():
    return "السيرفر يعمل!"

@app.route('/register', methods=['POST'])
def game_register():
    data = request.get_json() if request.is_json else request.form
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400
    
    username, email, password = data['username'], data['email'], data['password']
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", (username, email, password))
        conn.commit()
        return jsonify({"status": "success"}), 200
    except:
        return jsonify({"status": "error", "message": "موجود مسبقاً"}), 400
    finally:
        conn.close()

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "12345":
            session['logged_in'] = True
    
    if not session.get('logged_in'):
        return "<h2>دخول الإدارة</h2><form method='POST'><input name='username'><input type='password' name='password'><button>دخول</button></form>"

    # معالجة الأوامر من اللوحة (حظر، فك حظر، زيادة فلوس)
    action = request.args.get('action')
    target_user = request.args.get('user')
    if action and target_user:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        if action == 'ban': cursor.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (target_user,))
        elif action == 'unban': cursor.execute("UPDATE users SET is_banned = 0 WHERE username = ?", (target_user,))
        elif action == 'add_money': cursor.execute("UPDATE users SET money = money + 100 WHERE username = ?", (target_user,))
        conn.commit()
        conn.close()
        return redirect('/admin')

    # عرض اللوحة
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, money, is_banned FROM users")
    users = cursor.fetchall()
    conn.close()
    
    html = "<h1>لوحة تحكم عزو</h1><table border='1'><tr><th>اللاعب</th><th>الفلوس</th><th>الحالة</th><th>تحكم</th></tr>"
    for u in users:
        status = "محظور" if u[2] else "نشط"
        html += f"<tr><td>{u[0]}</td><td>{u[1]}</td><td>{status}</td><td><a href='/admin?action=ban&user={u[0]}'>حظر</a> | <a href='/admin?action=unban&user={u[0]}'>فك</a> | <a href='/admin?action=add_money&user={u[0]}'>+100</a></td></tr>"
    html += "</table><br><a href='/admin/logout'>تسجيل الخروج</a>"
    return html

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
