from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

# --- 1. تهيئة التطبيق وقاعدة البيانات ---
app = Flask(__name__)
app.secret_key = "ezzo_emperor_secret_2026"
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

# --- 2. مسارات اللعبة الأساسية (لربط Godot وحل الـ 404) ---
@app.route('/')
def home():
    return "<h1>سيرفر الإمبراطور عزو يعمل بنجاح!</h1>"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "بيانات فارغة"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_FILE)
    user = conn.execute("SELECT username, is_banned FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    conn.close()
    
    if user:
        if user[1] == 1: # إذا كان محظوراً
            return jsonify({"status": "error", "message": "الحساب محظور"}), 403
        return jsonify({"status": "success", "username": user[0]})
    return jsonify({"status": "error", "message": "البيانات خاطئة"}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error"}), 400
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", 
                     (data.get('username'), data.get('email'), data.get('password')))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "المستخدم موجود مسبقاً"}), 400


# --- 3. لوحة الأدمن الاحترافية (تصميم نيون بنفسجي وسيان) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        if request.form.get('password') == "12345":
            session['logged_in'] = True
            
    if not session.get('logged_in'):
        return """
        <body style='background:#0a0512; color:#00ffff; text-align:center; font-family:sans-serif; padding-top:100px;'>
            <h2 style='text-shadow: 0 0 10px #00ffff;'>🔒 تسجيل دخول الإدارة</h2>
            <form method='POST' style='background:#130b24; padding:20px; display:inline-block; border-radius:8px; border:1px solid #ff00ff; box-shadow: 0 0 15px #ff00ff;'>
                كلمة السر: <input type='password' name='password' style='background:#22143b; color:#fff; border:1px solid #00ffff; padding:5px;'><br><br>
                <button type='submit' style='background:#ff00ff; color:#fff; border:none; padding:8px 15px; cursor:pointer; font-weight:bold; border-radius:4px;'>دخول</button>
            </form>
        </body>
        """

    conn = sqlite3.connect(DB_FILE)
    users = conn.execute("SELECT username, email, money, is_banned, admin_message FROM users").fetchall()
    conn.close()
    
    # بناء واجهة النيون المطلوبة
    html = """
    <style>
        body { background: #0a0512; color: #fff; font-family: Arial, sans-serif; text-align: center; direction: rtl; padding: 20px; }
        h1 { color: #00ffff; text-shadow: 0 0 15px #00ffff; margin-bottom: 30px; }
        table { width: 95%; margin: auto; border-collapse: collapse; background: #130b24; box-shadow: 0 0 20px #ff00ff; border-radius: 8px; overflow: hidden; }
        th { background: #1a0f33; color: #00ffff; padding: 15px; border-bottom: 2px solid #ff00ff; }
        td { padding: 12px; border-bottom: 1px solid #22143b; color: #e0d5f5; }
        input[type='text'] { background: #22143b; color: #fff; border: 1px solid #00ffff; padding: 6px; border-radius: 4px; text-align: center; }
        button { padding: 6px 12px; margin: 2px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; color: white; }
        .btn-add { background: #00ffcc; color: #000; }
        .btn-sub { background: #ffaa00; color: #000; }
        .btn-ban { background: #ff0055; }
        .btn-unban { background: #00ff55; color: #000; }
        .btn-msg { background: #0099ff; }
        .btn-del { background: #555555; }
        .logout { display: inline-block; margin-top: 20px; color: #ff00ff; text-decoration: none; font-weight: bold; text-shadow: 0 0 5px #ff00ff; }
    </style>
    <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
    <table>
        <tr>
            <th>اللاعب</th>
            <th>البريد الإلكتروني</th>
            <th>الفلوس الحالية</th>
            <th>حالة الحساب</th>
            <th>رسالة الإدارة له</th>
            <th>خيارات التحكم السريعة</th>
        </tr>
    """
    for u in users:
        status_text = "<span style='color:#ff0055; text-shadow:0 0 5px #ff0055;'>🔴 محظور</span>" if u[3] else "<span style='color:#00ff55; text-shadow:0 0 5px #00ff55;'>🟢 نشط</span>"
        ban_btn = f"<button name='act' value='unban' class='btn-unban'>فك الحظر</button>" if u[3] else f"<button name='act' value='ban' class='btn-ban'>حظر</button>"
        
        html += f"""
        <tr>
            <td><b>{u[0]}</b></td>
            <td>{u[1]}</td>
            <td style='color:#00ffcc;'>💰 {u[2]}</td>
            <td>{status_text}</td>
            <td style='color:#ff00ff;'>{u[4] if u[4] else 'لا يوجد'}</td>
            <td>
                <form action='/admin/action' method='POST' style='display:inline;'>
                    <input type='hidden' name='u' value='{u[0]}'>
                    <input type='text' name='val' placeholder='المبلغ أو الرسالة' size='15'>
                    <button name='act' value='add' class='btn-add'>+ زيادة</button>
                    <button name='act' value='sub' class='btn-sub'>- نقصان</button>
                    {ban_btn}
                    <button name='act' value='msg' class='btn-msg'>💬 إرسال رسالة</button>
                    <button name='act' value='del' class='btn-del' onclick="return confirm('هل أنت متأكد من حذف الحساب نهائياً؟')">❌ حذف</button>
                </form>
            </td>
        </tr>
        """
    return html + "</table><br><a href='/admin/logout' class='logout'>🚪 تسجيل الخروج</a>"

# --- 4. معالجة الإجراءات (تعديل فلوس، رسائل، حظر، حذف) ---
@app.route('/admin/action', methods=['POST'])
def admin_action():
    if not session.get('logged_in'): 
        return redirect('/admin')
        
    act = request.form.get('act')
    user = request.form.get('u')
    val = request.form.get('val', '')
    
    conn = sqlite3.connect(DB_FILE)
    
    if act == 'add' and val.isdigit():
        conn.execute("UPDATE users SET money = money + ? WHERE username = ?", (int(val), user))
    elif act == 'sub' and val.isdigit():
        conn.execute("UPDATE users SET money = money - ? WHERE username = ?", (int(val), user))
    elif act == 'ban':
        conn.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (user,))
    elif act == 'unban':
        conn.execute("UPDATE users SET is_banned = 0 WHERE username = ?", (user,))
    elif act == 'msg':
        conn.execute("UPDATE users SET admin_message = ? WHERE username = ?", (val, user))
    elif act == 'del':
        conn.execute("DELETE FROM users WHERE username = ?", (user,))
        
    conn.commit()
    conn.close()
    return redirect('/admin')

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
