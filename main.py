from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

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
    cursor.execute('''
        INSERT OR IGNORE INTO players (username, money, is_banned, admin_message)
        VALUES ('ghgh', 600, 0, '')
    ''')
    conn.commit()
    conn.close()

init_db()

# الثيم القديم البسيط للرئيسية
@app.route('/')
def home():
    return "السيرفر يعمل بنجاح وجاهز لاستقبال طلبات لعبة جودوت!"

# دالة لوحة التحكم (Admin Panel) القديمة حقتك للتحكم في الحظر والبيانات
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # استقبال البيانات من الفورم حقك
        username = request.form.get('username')
        money = request.form.get('money')
        is_banned = request.form.get('is_banned')
        admin_msg = request.form.get('admin_message')
        
        cursor.execute('''
            INSERT INTO players (username, money, is_banned, admin_message)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                money=excluded.money,
                is_banned=excluded.is_banned,
                admin_message=excluded.admin_message
        ''', (username, money, is_banned, admin_msg))
        conn.commit()
    
    # جلب كل اللاعبين لعرضهم في اللوحة القديمة
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    conn.close()
    
    # الثيم القديم للوحة التحكم HTML اللي يخليك تتحكم في الكل
    html = '''
    <h1>لوحة تحكم المسؤولين - Admin Panel</h1>
    <form method="POST">
        تعديل لاعب: <input type="text" name="username" placeholder="اسم اللاعب" required><br><br>
        الفلوس: <input type="number" name="money" value="600"><br><br>
        الحظر (0 أو 1): <input type="number" name="is_banned" value="0" min="0" max="1"><br><br>
        رسالة الإدارة: <input type="text" name="admin_message"><br><br>
        <input type="submit" value="تحديث البيانات">
    </form>
    <h2>قائمة اللاعبين الحالية:</h2>
    <table border="1">
        <tr><th>الاسم</th><th>الفلوس</th><th>محظور؟</th><th>الرسالة</th></tr>
    '''
    for p in players:
        html += f"<tr><td>{p[0]}</td><td>{p[1]}</td><td>{p[2]}</td><td>{p[3]}</td></tr>"
    html += "</table>"
    return html

# المسار الخاص بجودوت لطلب البيانات
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
        cursor.execute('INSERT INTO players (username, money, is_banned, admin_message) VALUES (?, 600, 0, "")', (username,))
        conn.commit()
        conn.close()
        return jsonify({
            "money": 600,
            "is_banned": 0,
            "admin_message": ""
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
