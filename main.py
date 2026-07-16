from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"

# حماية إضافية: تمنع حدوث خطأ 404 إذا أرسل جودو شرطة مائلة زائدة في نهاية الرابط (مثل /login/)
app.url_map.strict_slashes = False

DB_FILE = "database.db"

# ==========================================
# 0. دالة الإصلاح والإنشاء التلقائي لقاعدة البيانات
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # إنشاء جدول المستخدمين إذا لم يكن موجوداً
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
    
    # فحص الأعمدة الحالية وإضافة أي عمود ناقص تلقائياً (حماية من الانهيار)
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = {
        "password": "TEXT DEFAULT ''",
        "money": "INTEGER DEFAULT 0",
        "is_banned": "INTEGER DEFAULT 0",
        "admin_message": "TEXT DEFAULT ''"
    }
    
    for col_name, col_type in required_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"🔧 تم إصلاح وإضافة العمود الناقص: {col_name}")
            except Exception as e:
                print(f"⚠️ خطأ أثناء تحديث العمود {col_name}: {e}")
                
    conn.commit()
    conn.close()

# تشغيل الفحص التلقائي بمجرد إقلاع السيرفر
init_db()

# ==========================================
# 1. تصاميم HTML (واجهات الموقع)
# ==========================================

HOME_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سيرفر اللعبة</title>
    <style>
        body { background: radial-gradient(circle, #2a1b4d 0%, #0b0813 100%); color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; }
        .hero { background: rgba(0, 0, 0, 0.6); padding: 50px; border-radius: 20px; border: 2px solid #ff007f; box-shadow: 0 0 30px rgba(255, 0, 127, 0.5); }
        h1 { font-size: 3rem; margin-bottom: 10px; color: #00f0ff; text-shadow: 0 0 10px #00f0ff; }
        p { font-size: 1.5rem; color: #cccccc; margin-bottom: 30px; }
        .status { background: #ff007f; padding: 10px 20px; border-radius: 50px; font-weight: bold; font-size: 1.2rem; display: inline-block; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🎯 سيرفر اللعبة 🎯</h1>
        <p>استعد لأقوى المعارك... السيرفر يعمل بنجاح!</p>
        <div class="status">⚠️ اللعبة تحت التطوير ⚠️</div>
    </div>
</body>
</html>
"""

ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>دخول الإدارة</title>
    <style>
        body { background: #0b0813; color: white; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; }
        form { background: #1a0b2e; padding: 40px; border-radius: 15px; border: 1px solid #00f0ff; box-shadow: 0 0 15px rgba(0, 240, 255, 0.3); text-align: center; width: 300px; }
        input { width: 90%; padding: 12px; margin: 10px 0; background: #0b0813; color: white; border: 1px solid #ff007f; border-radius: 8px; outline: none; }
        button { width: 100%; padding: 12px; background: linear-gradient(45deg, #00f0ff, #ff007f); border: none; color: white; font-size: 1.1rem; font-weight: bold; border-radius: 8px; cursor: pointer; margin-top: 15px; }
    </style>
</head>
<body>
    <form method="POST" action="/admin/login">
        <h2>👑 دخول الإمبراطور 👑</h2>
        <input name="username" placeholder="اسم المستخدم" required>
        <input type="password" name="password" placeholder="كلمة المرور" required>
        <button type="submit">تسجيل الدخول</button>
    </form>
</body>
</html>
"""

ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم الإمبراطور</title>
    <style>
        body { background-color: #0d0a14; color: white; font-family: sans-serif; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #ff007f; padding-bottom: 10px; }
        .header h1 { color: #ff007f; margin: 0; font-size: 2.2rem; text-shadow: 0 0 10px rgba(255,0,127,0.5); }
        .logout-btn { background-color: #ff3333; color: white; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; }
        .flash-message { background-color: #28a745; color: white; padding: 15px; text-align: center; border-radius: 8px; margin-bottom: 20px; font-weight: bold; }
        
        table { width: 100%; border-collapse: collapse; background-color: #150e24; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        th { background-color: #210b38; color: #00f0ff; padding: 15px; text-align: center; font-size: 1.1rem; border-bottom: 1px solid #3d2366; }
        td { padding: 15px; text-align: center; border-bottom: 1px solid #2a1b4d; vertical-align: middle; }
        
        .banned { color: #ff3333; font-weight: bold; background: rgba(255,51,51,0.1); padding: 5px 10px; border-radius: 50px; }
        .active { color: #28a745; font-weight: bold; background: rgba(40,167,69,0.1); padding: 5px 10px; border-radius: 50px; }
        .money { color: #ffd700; font-weight: bold; font-size: 1.1rem; }
        .password-box { background: #000; padding: 5px 10px; border-radius: 5px; color: #ff007f; font-family: monospace; }
        
        .actions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
        .input-sm { padding: 8px; background: #0d0a14; border: 1px solid #3d2366; color: white; border-radius: 5px; width: 100px; text-align: center; outline: none; }
        .btn { padding: 8px 15px; border: none; border-radius: 5px; color: white; font-weight: bold; cursor: pointer; text-decoration: none; }
        
        .btn-add { background-color: #8a2be2; }
        .btn-sub { background-color: #dc143c; }
        .btn-send { background-color: #00e5ff; color: black; }
        .btn-ban { background-color: #ff3333; }
        .btn-unban { background-color: #28a745; }
        .btn-delete { background-color: #8b0000; border: 1px solid #ff0000; margin-top: 10px; width: 100%; }
        
        .action-group { background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body>
    <div class="header">
        <a href="/admin/logout" class="logout-btn">تسجيل الخروج 🚪</a>
        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
    </div>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div class="flash-message">💬 {{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <table>
        <thead>
            <tr>
                <th>اللاعب 👤</th>
                <th>البريد الإلكتروني 📧</th>
                <th>الباسورد 🔑</th>
                <th>الفلوس الحالية 💰</th>
                <th>حالة الحساب 🚦</th>
                <th>رسالة الإدارة 💬</th>
                <th>خيارات التحكم السريعة 🛠️</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td style="color: #ff007f; font-weight: bold;">{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td><span class="password-box">{{ user.password }}</span></td>
                <td class="money">${{ user.money }}</td>
                <td>
                    {% if user.is_banned == 1 %}
                        <span class="banned">محظور 🔴</span>
                    {% else %}
                        <span class="active">نشط 🟢</span>
                    {% endif %}
                </td>
                <td style="color: #ccc;">{{ user.admin_message or 'لا توجد رسالة' }}</td>
                <td>
                    <div class="actions">
                        <form method="POST" action="/admin/action/{{ user.username }}" class="action-group" style="display: flex; gap: 5px;">
                            <input type="number" name="amount" class="input-sm" placeholder="المبلغ" required>
                            <button type="submit" name="action_type" value="add_money" class="btn btn-add">زيادة ➕</button>
                            <button type="submit" name="action_type" value="sub_money" class="btn btn-sub">خصم ➖</button>
                        </form>
                        
                        <form method="POST" action="/admin/action/{{ user.username }}" class="action-group" style="display: flex; gap: 5px;">
                            <input type="text" name="message" class="input-sm" style="width: 150px;" placeholder="اكتب رسالة..." required>
                            <button type="submit" name="action_type" value="send_msg" class="btn btn-send">إرسال 💬</button>
                        </form>
                        
                        <form method="POST" action="/admin/action/{{ user.username }}" class="action-group">
                            {% if user.is_banned == 1 %}
                                <button type="submit" name="action_type" value="unban" class="btn btn-unban">فك الحظر ✅</button>
                            {% else %}
                                <button type="submit" name="action_type" value="ban" class="btn btn-ban">حظر 🚫</button>
                            {% endif %}
                        </form>
                    </div>
                    
                    <form method="POST" action="/admin/action/{{ user.username }}" onsubmit="return confirm('⚠️ هل أنت متأكد من حذف حساب ({{ user.username }}) نهائياً؟');">
                        <button type="submit" name="action_type" value="delete" class="btn btn-delete">حذف الحساب نهائياً 🗑️</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# ==========================================
# 2. مسارات اللعبة (API)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

# دالة تسجيل الدخول (Login)
@app.route('/login', methods=['POST'])
def game_login():
    # دعم استقبال البيانات سواء كـ JSON أو كـ Form البيانات المرسلة من جودو
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    if not data:
        return jsonify({"status": "error", "message": "لم يتم إرسال أي بيانات!"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"status": "error", "message": "الرجاء إدخال البريد الإلكتروني وكلمة المرور"}), 400
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, money, is_banned, admin_message FROM users WHERE email = ?", (email.strip(),))
    row = cursor.fetchone()
    conn.close()
        
    if row and row[1] == password.strip():
        if row[3] == 1: 
            return jsonify({"status": "error", "message": "حسابك محظور من قبل الإدارة!"}), 403
        return jsonify({"status": "success", "username": row[0], "money": row[2], "msg": row[4]}), 200
        
    return jsonify({"status": "error", "message": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}), 400

# دالة إنشاء حساب جديد (Register)
@app.route('/register', methods=['POST'])
def game_register():
    # دعم استقبال البيانات سواء كـ JSON أو كـ Form البيانات المرسلة من جودو
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400
        
    username = data.get('username').strip()
    email = data.get('email').strip()
    password = data.get('password').strip()
    
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "الرجاء تعبئة جميع الحقول"}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # التحقق من عدم تكرار الإيميل أو اسم المستخدم
    cursor.execute("SELECT username, email FROM users WHERE username = ? OR email = ?", (username, email))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"status": "error", "message": "اسم المستخدم أو البريد الإلكتروني مسجل مسبقاً!"}), 400
        
    # تسجيل الحساب الجديد في قاعدة البيانات بنجاح
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, money, is_banned, admin_message) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, password, 500, 0, "") # يحصل اللاعب على 500 دولار هدية تسجيل
        )
        conn.commit()
        success = True
    except Exception as e:
        success = False
        error_msg = str(e)
    finally:
        conn.close()
        
    if success:
        return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح!"}), 200
    else:
        return jsonify({"status": "error", "message": f"خطأ في السيرفر: {error_msg}"}), 500

# ==========================================
# 3. لوحة التحكم (Admin)
# ==========================================

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return render_template_string(ADMIN_LOGIN_HTML)
        
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # جلب البيانات بشكل آمن ومحمي
    try:
        cursor.execute("SELECT username, email, password, money, is_banned, admin_message FROM users")
        users = cursor.fetchall()
    except sqlite3.OperationalError:
        users = []
        flash("تنبيه: تم إعادة ضبط قاعدة البيانات بنجاح.")
    finally:
        conn.close()
        
    return render_template_string(ADMIN_DASHBOARD_HTML, users=users)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('username') == "admin" and request.form.get('password') == "12345":
        session['logged_in'] = True
        return redirect('/admin')
    return "<h2 style='color:red; text-align:center;'>بيانات الدخول خاطئة!</h2>"

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return
