from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key"
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

# --- المسارات الرئيسية ---
@app.route('/')
def home():
    return "السيرفر يعمل بكامل طاقته!"

# مسار التسجيل
@app.route('/register', methods=['POST'])
def game_register():
    data = request.get_json() if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "لا يوجد بيانات"}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # تصحيح النقطتين الرأسيتين هنا
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", (username, email, password))
        conn.commit()
        return jsonify({"status": "success", "message": "تم التسجيل"}), 200
    except:
        return jsonify({"status": "error", "message": "موجود مسبقاً"}), 400
    finally:
        conn.close()

# مسار لوحة تحكم الأدمن (التي طلبتها في صورتك)
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "12345":
            session['logged_in'] = True
    
    if not session.get('logged_in'):
        return """
        <h2>دخول الإدارة</h2>
        <form method='POST'>
            <input name='username' placeholder='اسم المستخدم'>
            <input type='password' name='password' placeholder='كلمة المرور'>
            <button>دخول</button>
        </form>
        """
    
    # هنا يجب أن تضع كود عرض اللوحة (الجدول والبيانات) كما كان في مشروعك
    return "<h1>مرحباً بك في لوحة تحكم عزو - الإدارة تعمل!</h1>"

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
