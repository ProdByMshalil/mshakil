from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"  # مفتاح أمان الجلسات
DB_FILE = "database.db"

# إنشاء وتحديث قاعدة البيانات لتشمل الحظر والرسائل الإدارية
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar_id INTEGER DEFAULT 1,
            money INTEGER DEFAULT 600,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT ""
        )
    ''')
    # صيانة للتأكد من وجود الأعمدة الجديدة لو كانت القاعدة قديمة
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN admin_message TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 🎨 واجهات الـ HTML (التصميم الاحترافي)
# ==========================================

# 1️⃣ الصفحة الرئيسية (اللعبة تحت التطوير)
HOME_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سيرفر لعبة عزو | تحت التطوير</title>
    <style>
        body {
            background: linear-gradient(135deg, #0f0c1b, #201335);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.05);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 500px;
            width: 90%;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(127, 0, 255, 0.5);
        }
        p {
            font-size: 1.2rem;
            color: #ccc;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(45deg, #7f00ff, #ff007f);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
            transition: 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.8);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 اللعبة تحت التطوير 🎮</h1>
        <p>مرحباً بك في سيرفر لعبة عزو المطور! نحن نعمل على بناء عالم ألعاب أسطوري.</p>
        <a href="#" class="btn">اللعبة قريباً 🚀</a>
    </div>
</body>
</html>
"""

# 2️⃣ صفحة تسجيل دخول الإدارة
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم | تسجيل الدخول</title>
    <style>
        body {
            background: linear-gradient(135deg, #0f0c1b, #150d22);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.03);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }
        h2 { text-align: center; color: #ff007f; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 8px; color: #aaa; }
        .input-group input {
            width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px;
            color: white; outline: none; box-sizing: border-box;
        }
        .submit-btn {
            width: 100%; padding: 12px; background: linear-gradient(45deg, #7f00ff, #ff007f);
            border: none; border-radius: 8px; color: white; font-size: 1.1rem; font-weight: bold; cursor: pointer;
        }
        .alert { background: #ff3333; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>تسجيل دخول الإدارة 🔐</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        <form action="/admin/login" method="POST">
            <div class="input-group">
                <label>اسم المستخدم الإداري</label>
                <input type="text" name="username" required>
            </div>
            <div class="input-group">
                <label>كلمة المرور</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="submit-btn">دخول</button>
        </form>
    </div>
</body>
</html>
"""

# 3️⃣ لوحة التحكم الاحترافية للمشرف (اللاعبين، الفلوس، الحظر، الرسائل)
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم عزو الأسطورية 👑</title>
    <style>
        body {
            background: #0b0813;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #ff007f;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        h1 {
            background: linear-gradient(45deg, #00f0ff, #ff007f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .logout-btn {
            background: #ff3333; color: white; padding: 10px 20px; text-decoration: none;
            border-radius: 8px; font-weight: bold; transition: 0.2s;
        }
        .logout-btn:hover { background: #cc0000; box-shadow: 0 0 10px #ff3333; }
        
        .alert-success { background: #22c55e; color: white; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: bold;}

        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        th, td {
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        th {
            background: rgba(127, 0, 255, 0.2);
            color: #00f0ff;
            font-size: 1.1rem;
        }
        tr:hover { background: rgba(255, 255, 255, 0.03); }
        
        .badge { padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; }
        .badge-active { background: #22c55e; color: #fff; }
        .badge-banned { background: #ef4444; color: #fff; }

        .btn {
            padding: 8px 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s;
        }
        .btn-ban { background: #ef4444; color: white; text-decoration: none; display: inline-block; }
        .btn-ban:hover { background: #dc2626; }
        .btn-unban { background: #10b981; color: white; text-decoration: none; display: inline-block; }
        .btn-unban:hover { background: #059669; }
        
        .action-form { display: inline-flex; gap: 5px; margin: 0; }
        .input-style {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            padding: 6px;
            border-radius: 6px;
            outline: none;
        }
        .input-money { width: 70px; text-align: center; }
        .input-msg { width: 150px; }
        .btn-add { background: #7f00ff; color: white; }
        .btn-add:hover { background: #6b00d6; }
        .btn-msg { background: #00f0ff; color: #0b0813; }
        .btn-msg:hover { background: #00c8d6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
        <a href="/admin/logout" class="logout-btn">تسجيل الخروج 🚪</a>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert-success">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <table>
        <thead>
            <tr>
                <th>اللاعب 👤</th>
                <th>البريد الإلكتروني 📧</th>
                <th>الفلوس الحاليّة 💰</th>
                <th>حالة الحساب 🚦</th>
                <th>رسالة الإدارة له 💬</th>
                <th>خيارات التحكم السريعة 🛠️</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td style="font-weight: bold; color: #ff007f;">{{ user[0] }}</td>
                <td>{{ user[1] }}</td>
                <td style="color: #ffd700; font-weight: bold;">${{ user[4] }}</td>
                <td>
                    {% if user[5] == 1 %}
                    <span class="badge badge-banned">محظور 🔴</span>
                    {% else %}
                    <span class="badge badge-active">نشط 🟢</span>
                    {% endif %}
                </td>
                <td style="color: #aaa; font-style: italic;">
                    {{ user[6] if user[6] != "" else "لا توجد رسالة مبعوثة" }}
                </td>
                <td>
                    {% if user[5] == 1 %}
                    <a href="/admin/unban/{{ user[0] }}" class="btn btn-unban">فك الحظر ✅</a>
                    {% else %}
                    <a href="/admin/ban/{{ user[0] }}" class="btn btn-ban">حظر اللاعب 🚫</a>
                    {% endif %}

                    <form action="/admin/add_money/{{ user[0] }}" method="POST" class="action-form">
                        <input type="number" name="amount" class="input-style input-money" placeholder="المبلغ" required min="1">
                        <button type="submit" class="btn btn-add">زيادة 💰</button>
                    </form>

                    <form action="/admin/send_message/{{ user[0] }}" method="POST" class="action-form">
                        <input type="text" name="message" class="input-style input-msg" placeholder="اكتب رسالة للاعب..." required>
                        <button type="submit" class="btn btn-msg">إرسال 💬</button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="6" style="text-align: center; color: #888;">لا يوجد لاعبون مسجلون في السيرفر حالياً!</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# ==========================================
# 🌐 التحكم بالصفحات والمشرفين (Routes)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/admin')
def admin():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # يمكنك تغيير بيانات الدخول السرية الخاصة بك من هنا
    if username == "admin" and password == "12345":
        session['logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash("خطأ في اسم المستخدم أو الباسوورد!")
        return redirect(url_for('admin'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin'))

# لوحة التحكم الحقيقية بعد الدخول
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, password, avatar_id, money, is_banned, admin_message FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return render_template_string(ADMIN_DASHBOARD_HTML, users=users)


# ==========================================
# 🛠️ عمليات لوحة التحكم (Actions)
# ==========================================

# حظر لاعب
@app.route('/admin/ban/<username>')
def ban_player(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    flash(f"تم حظر اللاعب {username} بنجاح! 🚫")
    return redirect(url_for('admin_dashboard'))

# فك حظر لاعب
@app.route('/admin/unban/<username>')
def unban_player(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    flash(f"تم إلغاء الحظر عن اللاعب {username} بنجاح! ✅")
    return redirect(url_for('admin_dashboard'))

# زيادة الفلوس للاعب
@app.route('/admin/add_money/<username>', methods=['POST'])
def add_money(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    amount = int(request.form.get('amount', 0))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET money = money + ? WHERE username = ?", (amount, username))
    conn.commit()
    conn.close()
    flash(f"تم إضافة {amount}$ إلى حساب اللاعب {username}! 💰")
    return redirect(url_for('admin_dashboard'))

# إرسال كلمة/رسالة مخصصة للاعب تظهر له في اللعبة
@app.route('/admin/send_message/<username>', methods=['POST'])
def send_message(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    msg = request.form.get('message', '')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET admin_message = ? WHERE username = ?", (msg, username))
    conn.commit()
    conn.close()
    flash(f"تم إرسال الرسالة إلى {username} بنجاح! 💬")
    return redirect(url_for('admin_dashboard'))


# ==========================================
# 🎮 واجهة الـ API للعبة (Godot)
# ==========================================

# عند التسجيل
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    avatar_id = data.get('avatar_id', 1)

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "الرجاء تعبئة جميع الحقول!"}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, avatar_id) VALUES (?, ?, ?, ?)",
            (username, email, password, avatar_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "تم إنشاء حسابك بنجاح!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "اسم المستخدم مستخدم بالفعل!"}), 400

# عند تسجيل الدخول من اللعبة
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password, email, avatar_id, money, is_banned, admin_message FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == password:
        # التحقق إذا كان اللاعب محظوراً
        if row[4] == 1:
            return jsonify({
                "status": "error", 
                "message": "🚫 تم حظر حسابك من قبل الإدارة! يرجى مراجعة المسؤول عزو."
            }), 403
            
        return jsonify({
            "status": "success",
            "message": f"أهلاً بك يا {username}!",
            "email": row[1],
            "avatar_id": row[2],
            "money": row[3],
            "admin_message": row[5] # هنا نرسل الكلمة التي كتبها الآدمن للاعب ليقرأها في جادوت!
        }), 200
    else:
        return jsonify({"status": "error", "message": "اسم المستخدم أو كلمة المرور خاطئة!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
