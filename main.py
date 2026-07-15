from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "database.db"

# تحديث قاعدة البيانات لتشمل الإيميل والصورة الرمزية
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

@app.route('/')
def home():
    return "🔥 سيرفر عزو المطور جاهز لاستقبال البيانات الكاملة! 🔥"

# --- تسجيل حساب جديد بالإيميل والصورة ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    avatar_id = data.get('avatar_id', 1)  # القيمة الافتراضية 1 إذا لم يختر

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

# --- تسجيل الدخول واسترجاع البيانات كاملة ---
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
