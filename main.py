from flask import Flask, request, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            password TEXT DEFAULT '',
            email TEXT DEFAULT '',
            money INTEGER DEFAULT 600,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT ''
        )
    ''')
    
    cursor.execute("PRAGMA table_info(players)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'password' not in columns:
        cursor.execute("ALTER TABLE players ADD COLUMN password TEXT DEFAULT ''")
    if 'email' not in columns:
        cursor.execute("ALTER TABLE players ADD COLUMN email TEXT DEFAULT ''")

    conn.commit()
    conn.close()

init_db()

# 🏠 الصفحة الرئيسية (مقدمة اللعبة وزر التحميل)
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>عالم Relic Curse</title>
        <style>
            body {
                background: linear-gradient(135deg, #0b0c10, #1a0236);
                color: #fff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center;
                padding: 50px 20px;
                margin: 0;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .hero-card {
                background: rgba(18, 1, 36, 0.85);
                border: 2px solid #00ffcc;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                box-shadow: 0 0 25px rgba(0, 255, 204, 0.3);
            }
            h1 {
                color: #00ffcc;
                font-size: 32px;
                margin-bottom: 15px;
                text-shadow: 0 0 10px #00ffcc;
            }
            p {
                font-size: 18px;
                line-height: 1.6;
                color: #ddd;
                margin-bottom: 30px;
            }
            .btn-download {
                display: inline-block;
                padding: 15px 35px;
                background: linear-gradient(45deg, #ff00ff, #00ffff);
                color: #000;
                font-weight: bold;
                font-size: 18px;
                border-radius: 30px;
                text-decoration: none;
                box-shadow: 0 0 15px #ff00ff;
                transition: transform 0.2s;
            }
            .btn-download:hover {
                transform: scale(1.05);
            }
            .badge {
                display: block;
                margin-top: 15px;
                font-size: 13px;
                color: #ff00ff;
            }
        </style>
    </head>
    <body>
        <div class="hero-card">
            <h1>🎮 مرحباً بك في خوادم اللعبة</h1>
            <p>استعد لتجربة قتال وحماس لا مثيل لهما. السيرفرات تعمل بكفاءة وجاهزة لاستقبال اللاعبين والربط مع المحرك.</p>
            <a href="#" class="btn-download" onclick="alert('تنزيل اللعبة سيكون متاحاً قريباً جداً!'); return false;">📥 تحميل اللعبة (قريباً...)</a>
            <span class="badge">الإصدار التجريبي تحت التطوير</span>
        </div>
    </body>
    </html>
    '''

# 👑 لوحة تحكم الإمبراطور عزو
@app.route('/admin', methods=['GET'])
def admin_panel():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, password, email, money, is_banned, admin_message FROM players')
    players = cursor.fetchall()
    conn.close()

    html = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة تحكم الإمبراطور عزو</title>
        <style>
            body {
                background-color: #0b0c10;
                color: #fff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                text-align: center;
                padding: 20px;
                margin: 0;
            }
            h1 {
                color: #00ffcc;
                text-shadow: 0 0 10px #00ffcc;
                font-size: 24px;
                margin-bottom: 30px;
            }
            .panel-container {
                border: 2px solid #ff00ff;
                border-radius: 15px;
                padding: 20px;
                max-width: 98%;
                margin: 0 auto;
                background-color: #120124;
                box-shadow: 0 0 15px #ff00ff;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th {
                color: #00ffff;
                padding: 12px;
                font-size: 13px;
                border-bottom: 2px solid #ff00ff;
            }
            td {
                padding: 12px 8px;
                border-bottom: 1px solid #333;
                font-size: 13px;
                vertical-align: middle;
            }
            .status-active { color: #00ff00; font-weight: bold; }
            .status-banned { color: #ff0055; font-weight: bold; }
            .msg-text { color: #ff00ff; }
            .pass-text { color: #ffcc00; font-family: monospace; }
            .control-box {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                align-items: center;
                justify-content: center;
                background: #1a0236;
                padding: 8px;
                border-radius: 8px;
            }
            .input-val {
                background: #2d0b5a;
                border: 1px solid #ff00ff;
                color: #fff;
                padding: 5px;
                border-radius: 4px;
                width: 95px;
                text-align: center;
                font-size: 11px;
            }
            .btn {
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                color: white;
                cursor: pointer;
                font-weight: bold;
                font-size: 11px;
            }
            .btn-ban { background-color: #ff0055; }
            .btn-unban { background-color: #00cc66; }
            .btn-minus { background-color: #ff9900; }
            .btn-plus { background-color: #00cccc; }
            .btn-msg { background-color: #007bff; }
            .btn-edit { background-color: #9900ff; }
            .btn-del { background-color: #555; }
        </style>
    </head>
    <body>
        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
        <div class="panel-container">
            <table>
                <thead>
                    <tr>
                        <th>اللاعب</th>
                        <th>كلمة المرور</th>
                        <th>البريد الإلكتروني</th>
                        <th>الفلوس الحالية</th>
                        <th>حالة الحساب</th>
                        <th>رسالة الإدارة</th>
                        <th>تعديل البيانات السريع</th>
                        <th>التحكم بالنظام</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for p in players:
        username, password, email, money, is_banned, admin_message = p
        status_str = '<span class="status-active">🟢 نشط</span>' if is_banned == 0 else '<span class="status-banned">🔴 محظور</span>'
        ban_btn_label = 'حظر' if is_banned == 0 else 'فك الحظر'
        ban_btn_class = 'btn-ban' if is_banned == 0 else 'btn-unban'
        
        html += f'''
                    <tr>
                        <td><b>{username}</b></td>
                        <td class="pass-text">{password}</td>
                        <td>{email}</td>
                        <td>{money} 💰</td>
                        <td>{status_str}</td>
                        <td class="msg-text">{admin_message}</td>
                        
                        <!-- 📝 نموذج تعديل (الاسم، البريد، كلمة السر) -->
                        <td>
                            <form action="/quick_action" method="GET" style="display:flex; gap:4px; flex-direction:column;">
                                <input type="hidden" name="action" value="update_profile">
                                <input type="hidden" name="old_username" value="{username}">
                                <input type="text" name="new_username" class="input-val" value="{username}" placeholder="الاسم الجديد" required>
                                <input type="text" name="new_email" class="input-val" value="{email}" placeholder="البريد الجديد">
                                <input type="text" name="new_password" class="input-val" value="{password}" placeholder="كلمة السر">
                                <button type="submit" class="btn btn-edit">✏️ حفظ التعديل</button>
                            </form>
                        </td>

                        <!-- ⚙️ أدوات التحكم بالسيرفر -->
                        <td>
                            <div class="control-box">
                                <button class="btn {ban_btn_class}" onclick="location.href='/quick_action?action=toggle_ban&username={username}'">{ban_btn_label}</button>
                                
                                <form action="/quick_action" method="GET" style="display:inline; margin:0;">
                                    <input type="hidden" name="action" value="update_money">
                                    <input type="hidden" name="username" value="{username}">
                                    <input type="number" name="amount" class="input-val" placeholder="المبلغ" required>
                                    <button type="submit" name="sub_action" value="plus" class="btn btn-plus">+ زيادة</button>
                                    <button type="submit" name="sub_action" value="minus" class="btn btn-minus">- نقصان</button>
                                </form>

                                <form action="/quick_action" method="GET" style="display:inline; margin:0;">
                                    <input type="hidden" name="action" value="send_message">
                                    <input type="hidden" name="username" value="{username}">
                                    <input type="text" name="message" class="input-val" placeholder="اكتب الرسالة" required>
                                    <button type="submit" class="btn btn-msg">📧 إرسال</button>
                                </form>

                                <button class="btn btn-del" onclick="if(confirm('هل أنت متأكد من الحذف؟')) location.href='/quick_action?action=delete&username={username}'">❌ حذف</button>
                            </div>
                        </td>
                    </tr>
        '''
        
    html += '''
                </tbody>
            </table>
        </div>
    </body>
    </html>
    '''
    return html

# 🛠️ التحكم السريع
@app.route('/quick_action', methods=['GET'])
def quick_action():
    action = request.args.get('action')
    username = request.args.get('username')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if action == 'toggle_ban' and username:
        cursor.execute('UPDATE players SET is_banned = 1 - is_banned WHERE username = ?', (username,))
    
    elif action == 'update_money' and username:
        amount = request.args.get('amount', type=int, default=0)
        sub_action = request.args.get('sub_action')
        if sub_action == 'plus':
            cursor.execute('UPDATE players SET money = money + ? WHERE username = ?', (amount, username))
        elif sub_action == 'minus':
            cursor.execute('UPDATE players SET money = money - ? WHERE username = ?', (amount, username))
            
    elif action == 'send_message' and username:
        msg = request.args.get('message', default='')
        cursor.execute('UPDATE players SET admin_message = ? WHERE username = ?', (msg, username))
        
    elif action == 'delete' and username:
        cursor.execute('DELETE FROM players WHERE username = ?', (username,))
        
    elif action == 'update_profile':
        old_username = request.args.get('old_username')
        new_username = request.args.get('new_username')
        new_email = request.args.get('new_email', '')
        new_password = request.args.get('new_password', '')
        
        if old_username and new_username:
            cursor.execute('''
                UPDATE players 
                SET username = ?, email = ?, password = ? 
                WHERE username = ?
            ''', (new_username, new_email, new_password, old_username))
        
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

# 💳 خصم الفلوس الحقيقي من السيرفر
@app.route('/deduct_money', methods=['POST'])
def deduct_money():
    data = request.get_json(silent=True) or request.form
    username = data.get('username')
    amount = data.get('amount', type=int, default=0)

    if not username or amount <= 0:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT money FROM players WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "اللاعب غير موجود"}), 404
        
    current_money = row[0]
    if current_money < amount:
        conn.close()
        return jsonify({"status": "error", "message": "الرصيد غير كافٍ!"}), 400

    new_money = current_money - amount
    cursor.execute('UPDATE players SET money = ? WHERE username = ?', (new_money, username))
    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "تم الخصم بنجاح",
        "new_money": new_money
    })

# 🌐 تسجيل الدخول
@app.route('/login', methods=['POST', 'GET'])
def login():
    data = request.get_json(silent=True) or request.form or request.args
    login_id = str(data.get('email') or data.get('username') or '').strip()
    password = str(data.get('password', '')).strip()

    if not login_id:
        return jsonify({"status": "error", "message": "بيانات مفقودة"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT username, email, money, is_banned, admin_message 
        FROM players 
        WHERE (email = ? OR username = ?) AND password = ?
    ''', (login_id, login_id, password))
    
    player = cursor.fetchone()
    conn.close()

    if player:
        username, email, money, is_banned, admin_message = player
        if is_banned == 1:
            return jsonify({"status": "error", "message": "هذا الحساب محظور من الإدارة!"})

        return jsonify({
            "status": "success",
            "message": "تم تسجيل الدخول بنجاح!",
            "username": username,
            "email": email,
            "money": money,
            "admin_message": admin_message
        })
    else:
        return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة!"})

# 🌐 إنشاء حساب
@app.route('/register', methods=['POST', 'GET'])
def register():
    data = request.get_json(silent=True) or request.form or request.args
    email = str(data.get('email', '')).strip()
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()

    if not username and email: username = email
    if not email and username: email = username

    if not username:
        return jsonify({"status": "error", "message": "بيانات الحساب غير كاملة"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT username FROM players WHERE username = ? OR (email != "" AND email = ?)', (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "الحساب أو البريد مستخدم مسبقاً!"})

    cursor.execute('''
        INSERT INTO players (username, password, email, money, is_banned, admin_message)
        VALUES (?, ?, ?, 600, 0, 'لا يوجد')
    ''', (username, password, email))
    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح!"})

# 🌐 جلب حالة اللاعب
@app.route('/get_player_status', methods=['GET'])
def get_player_status():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "اسم اللاعب مفقود"}), 400
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT money, is_banned, admin_message FROM players WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()

    if row:
        money, is_banned, admin_message = row
        return jsonify({
            "money": money,
            "is_banned": is_banned,
            "admin_message": admin_message
        })
    else:
        return jsonify({"error": "اللاعب غير موجود"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
