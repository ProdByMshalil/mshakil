from flask import Flask, request, jsonify, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_secret_key"
DB_FILE = "database.db"

# دالة لتهيئة قاعدة البيانات
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
    return "سيرفر اللعبة يعمل!"

@app.route('/register', methods=['POST'])
def game_register():
    data = request.get_json() if request.is_json else request.form
    if not data:
        return jsonify({"status": "error", "message": "لا توجد بيانات"}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # هنا التأكد من الشكل الصحيح (النقطتين والمسافات البادئة)
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "الرجاء تعبئة جميع الحقول"}), 400
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password, money) VALUES (?, ?, ?, 500)", (username, email, password))
        conn.commit()
        return jsonify({"status": "success", "message": "تم التسجيل"}), 200
    except:
        return jsonify({"status": "error", "message": "خطأ في التسجيل"}), 400
    finally:
        conn.close()

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

@app.route('/admin/logout')
def admin_logout():
    # هذا الشكل يضمن تسجيل الخروج بشكل سليم
    session.pop('logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
