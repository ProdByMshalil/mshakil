from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import sqlite3
import os

# --- 1. تعريف التطبيق أولاً (ضروري جداً قبل أي app.route) ---
app = Flask(__name__)
app.secret_key = "ezzo_secret_key"
DB_FILE = "database.db"

# --- 2. تهيئة قاعدة البيانات ---
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

# --- 3. المسارات (Routes) ---
@app.route('/')
def home():
    return "سيرفر اللعبة يعمل!"

@app.route('/register', methods=['POST'])
def game_register():
    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
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

@app.route('/login', methods=['POST'])
def game_login():
    data = request.get_json() if request.is_json else request.form
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[1] == password:
        return jsonify({"status": "success", "username": row[0]}), 200
    return jsonify({"status": "error", "message": "خطأ"}), 400

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "12345":
            session['logged_in'] = True
            return "<h1>أهلاً بك في لوحة تحكم عزو</h1>"
    
    if session.get('logged_in'):
        return "<h1>أهلاً بك في لوحة تحكم عزو</h1>"
    
    return "<h2>دخول الإدارة</h2><form method='POST'><input name='username'><input type='password' name='password'><button>دخول</button></form>"

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect('/admin')

# --- 4. تشغيل السيرفر ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
