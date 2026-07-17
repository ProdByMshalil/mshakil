from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database.db"

# دالة لإنشاء قاعدة البيانات وجدول اللاعبين تلقائياً إذا لم يكن موجوداً
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            money INTEGER DEFAULT 600,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT ''
        )
    ''')
    # إضافة لاعب تجريبي "ghgh" إذا كانت قاعدة البيانات جديدة تماماً
    cursor.execute('''
        INSERT OR IGNORE INTO players (username, money, is_banned, admin_message)
        VALUES ('ghgh', 7500, 0, 'مرحباً بك يا عزو! السيرفر متصل الآن بنجاح 🚀')
    ''')
    conn.commit()
    conn.close()

# تشغيل إنشاء قاعدة البيانات فوراً عند إقلاع السيرفر
init_db()

@app.route('/')
def home():
    return "السيرفر يعمل بكفاءة عالية مع قاعدة بيانات SQLite دائمية!"

# 🌐 المسار الخاص بجودوت لجلب حالة اللاعب ومزامنتها
@app.route('/get_player_status', methods=['GET'])
def get_player_status():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "اسم اللاعب مفقود"}), 400
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT money, is_banned, admin_message FROM players WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    if row:
        money, is_banned, admin_message = row
        conn.close()
        return jsonify({
            "money": money,
            "is_banned": is_banned,
            "admin_message": admin_message
        })
    else:
        # إذا اللاعب جديد، نسجله في قاعدة البيانات بالقيم الافتراضية فوراً
        cursor.execute('INSERT INTO players (username, money, is_banned, admin_message) VALUES (?, 600, 0, "")', (username,))
        conn.commit()
        conn.close()
        return jsonify({
            "money": 600,
            "is_banned": 0,
            "admin_message": "تم تسجيل لاعب جديد تلقائياً"
        })

# 🛠️ مسارات إضافية تتيح لك التحكم باللاعب (تغيير فلوسه أو حظره) عبر المتصفح مباشرة!
@app.route('/admin/set_money', methods=['GET'])
def set_money():
    username = request.args.get('username')
    amount = request.args.get('amount', type=int)
    if not username or amount is None:
        return "خطأ: يجب تحديد اسم اللاعب والمبلغ", 400
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE players SET money = ? WHERE username = ?', (amount, username))
    conn.commit()
    conn.close()
    return f"تم تعديل فلوس اللاعب {username} إلى {amount} بنجاح!"

@app.route('/admin/ban', methods=['GET'])
def ban_player():
    username = request.args.get('username')
    status = request.args.get('status', type=int, default=1) # 1 للحظر، 0 لإلغاء الحظر
    if not username:
        return "خطأ: يجب تحديد اسم اللاعب", 400
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE players SET is_banned = ? WHERE username = ?', (status, username))
    conn.commit()
    conn.close()
    return f"تم تغيير حالة حظر اللاعب {username} إلى {status}!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
