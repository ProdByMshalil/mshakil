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
            email TEXT DEFAULT '888',
            money INTEGER DEFAULT 600,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT ''
        )
    ''')
    # إضافة اللاعب التجريبي ghgh بنفس بيانات صورتك إذا لم يكن موجوداً
    cursor.execute('''
        INSERT OR IGNORE INTO players (username, email, money, is_banned, admin_message)
        VALUES ('ghgh', '888', 500, 0, 'لا يوجد')
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return "السيرفر يعمل بنجاح وجاهز لاستقبال طلبات لعبة جودوت!"

# 👑 لوحة تحكم الإمبراطور عزو بالثيم البنفسجي والأزرار السريعة
@app.route('/admin', methods=['GET'])
def admin_panel():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT username, email, money, is_banned, admin_message FROM players')
    players = cursor.fetchall()
    conn.close()

    # تصميم الـ CSS المطابق تماماً لصورتك (خلفية سوداء، إطار بنفسجي مضيء، نيون)
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
                text-shadow: 0 0 10px #00ffcc, 0 0 20px #00ffcc;
                font-size: 24px;
                margin-bottom: 30px;
            }
            .panel-container {
                border: 3px solid #ff00ff;
                border-radius: 15px;
                padding: 20px;
                max-width: 95%;
                margin: 0 auto;
                background-color: #120124;
                box-shadow: 0 0 15px #ff00ff, inset 0 0 15px #120124;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th {
                color: #00ffff;
                padding: 12px;
                font-size: 14px;
                border-bottom: 2px solid #ff00ff;
            }
            td {
                padding: 15px;
                border-bottom: 1px solid #333;
                font-size: 14px;
                vertical-align: middle;
            }
            .status-active { color: #00ff00; font-weight: bold; }
            .status-banned { color: #ff0055; font-weight: bold; }
            .msg-text { color: #ff00ff; }
            
            /* أشكال عناصر التحكم الداعمة داخل الجدول */
            .control-box {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-items: center;
                justify-content: center;
                background: #1a0236;
                padding: 10px;
                border-radius: 8px;
            }
            .input-val {
                background: #2d0b5a;
                border: 1px solid #ff00ff;
                color: #fff;
                padding: 6px;
                border-radius: 4px;
                width: 110px;
                text-align: center;
            }
            .btn {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                color: white;
                cursor: pointer;
                font-weight: bold;
                font-size: 12px;
            }
            .btn-ban { background-color: #ff0055; }
            .btn-unban { background-color: #00cc66; }
            .btn-minus { background-color: #ff9900; }
            .btn-plus { background-color: #00cccc; }
            .btn-msg { background-color: #007bff; }
            .btn-del { background-color: #555; }
            
            .logout-btn {
                display: inline-block;
                margin-top: 25px;
                color: #ff3366;
                text-decoration: none;
                font-size: 14px;
            }
        </style>
    </head>
    <body>

        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>

        <div class="panel-container">
            <table>
                <thead>
                    <tr>
                        <th>اللاعب</th>
                        <th>البريد الإلكتروني</th>
                        <th>الفلوس الحالية</th>
                        <th>حالة الحساب</th>
                        <th>رسالة الإدارة له</th>
                        <th>خيارات التحكم السريعة</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for p in players:
        username, email, money, is_banned, admin_message = p
        status_str = '<span class="status-active">🟢 نشط</span>' if is_banned == 0 else '<span class="status-banned">🔴 محظور</span>'
        ban_btn_label = 'حظر' if is_banned == 0 else 'فك الحظر'
        ban_btn_class = 'btn-ban' if is_banned == 0 else 'btn-unban'
        
        html += f'''
                    <tr>
                        <td>{username}</td>
                        <td>{email}</td>
                        <td>{money} 💰</td>
                        <td>{status_str}</td>
                        <td class="msg-text">{admin_message}</td>
                        <td>
                            <div class="control-box">
                                <button class="btn {ban_btn_class}" onclick="location.href='/quick_action?action=toggle_ban&username={username}'">{ban_btn_label}</button>
                                
                                <form action="/quick_action" method="GET" style="display:inline; margin:0;">
                                    <input type="hidden" name="action" value="update_money">
                                    <input type="hidden" name="username" value="{username}">
                                    <input type="number" name="amount" class="input-val" placeholder="المبلغ أو الرسالة" required>
                                    <button type="submit" name="sub_action" value="plus" class="btn btn-plus">+ زيادة</button>
                                    <button type="submit" name="sub_action" value="minus" class="btn btn-minus">- نقصان</button>
                                </form>

                                <form action="/quick_action" method="GET" style="display:inline; margin:0;">
                                    <input type="hidden" name="action" value="send_message">
                                    <input type="hidden" name="username" value="{username}">
                                    <input type="text" name="message" class="input-val" placeholder="اكتب الرسالة هنا" required>
                                    <button type="submit" class="btn btn-msg">📧 إرسال رسالة</button>
                                </form>

                                <button class="btn btn-del" onclick="if(confirm('هل أنت متأكد؟')) location.href='/quick_action?action=delete&username={username}'">❌ حذف</button>
                            </div>
                        </td>
                    </tr>
        '''
        
    html += '''
                </tbody>
            </table>
        </div>

        <a href="#" class="logout-btn">🚪 تسجيل الخروج</a>

    </body>
    </html>
    '''
    return html

# 🛠️ معالج العمليات السريعة بضغطة زر واحدة بدون تعقيد
@app.route('/quick_action', methods=['GET'])
def quick_action():
    action = request.args.get('action')
    username = request.args.get('username')
    
    if not username:
        return redirect(url_for('admin_panel'))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if action == 'toggle_ban':
        cursor.execute('UPDATE players SET is_banned = 1 - is_banned WHERE username = ?', (username,))
        
    elif action == 'update_money':
        amount = request.args.get('amount', type=int, default=0)
        sub_action = request.args.get('sub_action')
        if sub_action == 'plus':
            cursor.execute('UPDATE players SET money = money + ? WHERE username = ?', (amount, username))
        elif sub_action == 'minus':
            cursor.execute('UPDATE players SET money = money - ? WHERE username = ?', (amount, username))
            
    elif action == 'send_message':
        msg = request.args.get('message', default='')
        cursor.execute('UPDATE players SET admin_message = ? WHERE username = ?', (msg, username))
        
    elif action == 'delete':
        cursor.execute('DELETE FROM players WHERE username = ?', (username,))
        
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

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
        cursor.execute('INSERT INTO players (username, money, is_banned, admin_message) VALUES (?, 600, 0, "لا يوجد")', (username,))
        conn.commit()
        conn.close()
        return jsonify({
            "money": 600,
            "is_banned": 0,
            "admin_message": "لا يوجد"
        })

# 🆕 مسار التسجيل الجديد لحل مشكلة الـ 404 في جودوت
@app.route('/register', methods=['POST', 'GET'])
def register():
    data = request.get_json(silent=True) or request.form
    username = data.get('username')
    
    if not username:
        return jsonify({"status": "error", "message": "اسم المستخدم مفقود"}), 400
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT username FROM players WHERE username = ?', (username,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return jsonify({"status": "error", "message": "اسم المستخدم مستخدم مسبقاً"})
    
    cursor.execute('''
        INSERT INTO players (username, money, is_banned, admin_message)
        VALUES (?, 600, 0, 'لا يوجد')
    ''', (username,))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح!"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
