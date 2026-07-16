from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key"
DB_FILE = "database.db"

# --- دالة عرض اللوحة بتنسيق النيون ---
def get_admin_html(users):
    html = """
    <style>
        body { background: #0d0d0d; color: #00ffcc; font-family: sans-serif; text-align: center; }
        table { margin: 20px auto; width: 90%; border-collapse: collapse; box-shadow: 0 0 10px #00ffcc; }
        th, td { padding: 15px; border: 1px solid #00ffcc; }
        button { background: transparent; color: #ff00ff; border: 1px solid #ff00ff; cursor: pointer; padding: 5px; }
        button:hover { background: #ff00ff; color: white; }
    </style>
    <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
    <table>
        <tr><th>اللاعب</th><th>البريد</th><th>الفلوس</th><th>الحالة</th><th>تحكم</th></tr>
    """
    for u in users:
        status = "🟢 نشط" if not u[3] else "🔴 محظور"
        html += f"""<tr>
            <td>{u[0]}</td><td>{u[1]}</td><td>💰 {u[2]}</td><td>{status}</td>
            <td>
                <a href='/admin/action?act=ban&user={u[0]}'><button>حظر</button></a>
                <a href='/admin/action?act=add&user={u[0]}'><button>+100</button></a>
                <a href='/admin/action?act=del&user={u[0]}'><button>حذف</button></a>
            </td>
        </tr>"""
    return html + "</table><a href='/admin/logout'>تسجيل الخروج</a>"

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('password') == "12345": session['logged_in'] = True
    if not session.get('logged_in'):
        return "<body style='background:#0d0d0d; color:white;'><form method='POST'>كلمة السر: <input type='password' name='password'><button>دخول</button></form></body>"
    
    conn = sqlite3.connect(DB_FILE)
    users = conn.execute("SELECT username, email, money, is_banned FROM users").fetchall()
    conn.close()
    return get_admin_html(users)

@app.route('/admin/action')
def admin_action():
    if not session.get('logged_in'): return redirect('/admin')
    act, user = request.args.get('act'), request.args.get('user')
    conn = sqlite3.connect(DB_FILE)
    if act == 'ban': conn.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (user,))
    elif act == 'add': conn.execute("UPDATE users SET money = money + 100 WHERE username = ?", (user,))
    elif act == 'del': conn.execute("DELETE FROM users WHERE username = ?", (user,))
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
