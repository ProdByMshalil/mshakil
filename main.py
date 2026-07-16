from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "database.db"

# المسار الرئيسي (اختياري)
@app.route('/')
def home():
    return "السيرفر يعمل الآن!"

# مسار تسجيل الدخول - هذا هو الأهم
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400
        
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # تأكد أن عمود البريد اسمه 'email' في قاعدة بياناتك
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row and row[1] == password:
        return jsonify({"status": "success", "username": row[0]}), 200
    else:
        return jsonify({"status": "error", "message": "بيانات الدخول خاطئة"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
