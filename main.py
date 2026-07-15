from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "database.db"

# إنشاء قاعدة البيانات وجدول المستخدمين إذا لم يكن موجوداً
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar_id INTEGER DEFAULT 1,
            money INTEGER DEFAULT 600
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 🎨 واجهات الـ HTML بتصميم ألعاب احترافي
# ==========================================

# 1️⃣ تصميم الصفحة الرئيسية (تحت التطوير)
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
            overflow: hidden;
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
            animation: fadeIn 1.5s ease-out;
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
            line-height: 1.6;
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
            transition: transform 0.2s, box-shadow 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.8);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 اللعبة تحت التطوير 🎮</h1>
        <p>مرحباً بك في سيرفر لعبة عزو الخاص! نحن نعمل بجد خلف الكواليس لبناء عالم ألعاب مذهل ومليء بالمغامرات.</p>
        <a href="#" class="btn">اللعبة قريباً 🚀</a>
    </div>
</body>
</html>
"""

# 2️⃣ تصميم صفحة تسجيل دخول الإدارة (/admin)
ADMIN_HTML = """
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }
        h2 {
            text-align: center;
            margin-bottom: 30px;
            color: #ff007f;
            text-shadow: 0 0 10px rgba(255, 0, 127, 0.3);
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 0.9rem;
        }
        .input-group input {
            width: 100%;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
            box-sizing: border-box;
        }
        .input-group input:focus {
            border-color: #7f00ff;
            box-shadow: 0 0 8px rgba(127, 0, 255, 0.3);
        }
        .submit-btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(45deg, #7f00ff, #ff007f);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 0, 127, 0.4);
        }
        .back-home {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #888;
            text-decoration: none;
            font-size: 0.9rem;
            transition: color 0.3s;
        }
        .back-home:hover {
            color: #ff007f;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>تسجيل دخول الإدارة 🔐</h2>
        <form action="/admin/login" method="POST">
            <div class="input-group">
                <label for="username">اسم المستخدم الإداري</label>
                <input type="text" id="username" name="username" required placeholder="أدخل اسم المستخدم">
            </div>
            <div class="input-group">
                <label for="password">كلمة المرور</label>
                <input type="password" id="password" name="password" required placeholder="أدخل كلمة المرور">
            </div>
            <button type="submit" class="submit-btn">تسجيل الدخول</button>
        </form>
        <a href="/" class="back-home">⬅️ العودة للرئيسية</a>
    </div>
</body>
</html>
"""

# ==========================================
# 🌐 روابط التطبيق (Routes)
# ==========================================

# الصفحة الرئيسية للسيرفر
@app.route('/')
def home():
    return render_template_string(HOME_HTML)

# صفحة تسجيل دخول الإدارة
@app.route('/admin')
def admin():
    return render_template_string(ADMIN_HTML)

# استقبال بيانات تسجيل دخول الآدمن
@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # هنا يمكنك تعيين باسوورد الآدمن الخاص بك (مثلاً: admin و 12345)
    if username == "admin" and password == "12345":
        return "<h1>👋 أهلاً بك يا عزو في لوحة تحكم السيرفر! (قيد التطوير)</h1>"
    else:
        return "<h1>❌ خطأ في اسم المستخدم أو الباسوورد الخاص بالإدارة!</h1><a href='/admin'>حاول مجدداً</a>"

# --- تسجيل حساب جديد من اللعبة (Godot) ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    avatar_id = data.get('avatar_id', 1)

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "الرجاء تعبئة جميع الحقول المطلوبة!"}), 400

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
        return jsonify({"status": "error", "message": "اسم المستخدم هذا مستخدم بالفعل!"}), 400

# --- تسجيل الدخول من اللعبة (Godot) ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password, email, avatar_id, money FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == password:
        return jsonify({
            "status": "success",
            "message": f"أهلاً بك يا {username}!",
            "email": row[1],
            "avatar_id": row[2],
            "money": row[3]
        }), 200
    else:
        return jsonify({"status": "error", "message": "اسم المستخدم أو كلمة المرور خاطئة!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
