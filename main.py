from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"
app.url_map.strict_slashes = False

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

# --- الصفحات ---
HOME_HTML = "<h1>سيرفر اللعبة يعمل!</h1>"
ADMIN_LOGIN_HTML = "<h2>دخول الإدارة</h2><form method='POST'><input name='username'><input type='password' name='password'><button>دخول</button></form>"

@app.route('/')
def home():
    return HOME_HTML

# --- مسار التسجيل (تم تصحيح الشروط برمجياً) ---
@app.route('/register', methods=['POST'])
def game_register():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400
        
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # التحقق المكتمل مع النقطتين الرأسيتين
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "الرجاء تعبئة جميع الحقول"}), 400

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

# --- مسار الدخول ---
@app.route('/login', methods=['POST'])
def game_login():
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[1] == password:
        return jsonify({"status": "success", "username": row[0]}), 200
    return jsonify({"status": "error", "message": "خطأ في البيانات"}), 400

# --- لوحة التحكم ---
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return ADMIN_LOGIN_HTML
    return "<h1>لوحة تحكم عزو</h1>"

@app.route('/admin/login', methods=['POST'])
def admin_login():
    if request.form.get('username') == "admin" and request.form.get('password') == "12345":
        session['logged_in'] = True
        return redirect('/admin')
    return "خطأ"

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
