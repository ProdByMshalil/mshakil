from flask import Flask, request, jsonify, redirect, url_for
import os
import random
import psycopg2
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        return conn, 'pg'
    else:
        conn = sqlite3.connect("database.db")
        return conn, 'sqlite'

def init_db():
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == 'pg':
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                username VARCHAR(100) PRIMARY KEY,
                password TEXT DEFAULT '',
                email TEXT DEFAULT '',
                money INTEGER DEFAULT 600,
                is_banned INTEGER DEFAULT 0,
                admin_message TEXT DEFAULT '',
                avatar TEXT DEFAULT ''
            );
        ''')
        for col, col_type in [('avatar', 'TEXT DEFAULT \'\''), ('admin_message', 'TEXT DEFAULT \'\''), ('is_banned', 'INTEGER DEFAULT 0'), ('money', 'INTEGER DEFAULT 600'), ('email', 'TEXT DEFAULT \'\''), ('password', 'TEXT DEFAULT \'\'')]:
            try:
                cursor.execute(f'ALTER TABLE players ADD COLUMN IF NOT EXISTS {col} {col_type}')
            except:
                conn.rollback()
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                password TEXT DEFAULT '',
                email TEXT DEFAULT '',
                money INTEGER DEFAULT 600,
                is_banned INTEGER DEFAULT 0,
                admin_message TEXT DEFAULT '',
                avatar TEXT DEFAULT ''
            );
        ''')
    
    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>عالم Relic Curse</title>
        <style>
            body { background: #0b0c10; color: #fff; font-family: Tahoma; text-align: center; padding: 50px; }
            h1 { color: #00ffcc; }
        </style>
    </head>
    <body>
        <h1>🎮 خوادم Relic Curse تعمل بكفاءة!</h1>
        <p>السيرفر متصل وقاعدة البيانات تعمل بنجاح.</p>
    </body>
    </html>
    '''

# مسار إرسال رمز التحقق (يستقبل من اللعبة أو الموقع ويتحقق من إعدادات البريد)
@app.route('/send-code', methods=['POST', 'GET'])
def send_code():
    try:
        data = request.get_json(silent=True) or request.form or request.args
        email = str(data.get('email', '')).strip()
        
        if not email or "@" not in email:
            return jsonify({"status": "error", "message": "البريد الإلكتروني غير صالح"}), 400
            
        otp_code = str(random.randint(1000, 9999))
        
        sender_email = os.environ.get('MAIL_USERNAME', '')
        sender_password = os.environ.get('MAIL_PASSWORD', '')
        
        if not sender_email or not sender_password:
            # لو بيانات البريد مش محددة في البيئة، نرجع الرمز كاستجابة تجريبية عشان اللعبة ما تتعطلش
            return jsonify({
                "status": "success",
                "message": "تم إنشاء الرمز بنجاح",
                "code": otp_code 
            })
        
        subject = "رمز التحقق - Relic Curse"
        body = f"أهلاً بك يا بطل!\n\nرمز التحقق الخاص بك في لعبة Relic Curse هو: {otp_code}\n\nلا تقم بمشاركته مع أحد."
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()

        return jsonify({
            "status": "success",
            "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني بنجاح!"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ بالسرفر: {str(e)}"}), 500

# لوحة التحكم الخاصة بالإمبراطور عزو
@app.route('/admin', methods=['GET'])
def admin_panel():
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT username, password, email, money, is_banned, admin_message, avatar FROM players')
        players = cursor.fetchall()
    except Exception as e:
        cursor.close()
        conn.close()
        return f"خطأ في قاعدة البيانات: {str(e)}"
        
    cursor.close()
    conn.close()

    html = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>لوحة تحكم الإمبراطور عزو</title>
        <style>
            body { background-color: #0b0c10; color: #fff; font-family: Tahoma; text-align: center; padding: 20px; }
            h1 { color: #00ffcc; text-shadow: 0 0 10px #00ffcc; }
            .panel-container { border: 2px solid #ff00ff; border-radius: 15px; padding: 20px; max-width: 98%; margin: 0 auto; background-color: #120124; box-shadow: 0 0 15px #ff00ff; overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { color: #00ffff; padding: 12px; font-size: 13px; border-bottom: 2px solid #ff00ff; }
            td { padding: 12px 8px; border-bottom: 1px solid #333; font-size: 13px; vertical-align: middle; }
            .status-active { color: #00ff00; font-weight: bold; }
            .status-banned { color: #ff0055; font-weight: bold; }
            .msg-text { color: #ff00ff; }
            .pass-text { color: #ffcc00; font-family: monospace; }
            .control-box { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; justify-content: center; background: #1a0236; padding: 8px; border-radius: 8px; }
            .input-val { background: #2d0b5a; border: 1px solid #ff00ff; color: #fff; padding: 5px; border-radius: 4px; width: 95px; text-align: center; font-size: 11px; }
            .btn { padding: 5px 10px; border: none; border-radius: 4px; color: white; cursor: pointer; font-weight: bold; font-size: 11px; }
            .btn-ban { background-color: #ff0055; }
            .btn-unban { background-color: #00cc66; }
            .btn-minus { background-color: #ff9900; }
            .btn-plus { background-color: #00cccc; }
            .btn-msg { background-color: #007bff; }
            .btn-edit { background-color: #9900ff; }
            .btn-del { background-color: #555; }
            .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #00ffcc; background: #222; }
        </style>
    </head>
    <body>
        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
        <div class="panel-container">
            <table>
                <thead>
                    <tr>
                        <th>الصورة</th>
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
        username, password, email, money, is_banned, admin_message, avatar = p
        status_str = '<span class="status-active">🟢 نشط</span>' if is_banned == 0 else '<span class="status-banned">🔴 محظور</span>'
        ban_btn_label = 'حظر' if is_banned == 0 else 'فك الحظر'
        ban_btn_class = 'btn-ban' if is_banned == 0 else 'btn-unban'
        
        if avatar and avatar.strip() != '':
            avatar_display = f'<img src="{avatar}" class="avatar-img" onerror="this.onerror=null; this.src=\'https://cdn-icons-png.flaticon.com/512/149/149071.png\';">'
        else:
            avatar_display = '<img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" class="avatar-img">'
        
        html += f'''
                    <tr>
                        <td>{avatar_display}</td>
                        <td><b>{username}</b></td>
                        <td class="pass-text">{password}</td>
                        <td>{email}</td>
                        <td>{money} 💰</td>
                        <td>{status_str}</td>
                        <td class="msg-text">{admin_message}</td>
                        
                        <td>
                            <form action="/quick_action" method="GET" style="display:flex; gap:4px; flex-direction:column;">
                                <input type="hidden" name="action" value="update_profile">
                                <input type="hidden" name="old_username" value="{username}">
                                <input type="text" name="new_username" class="input-val" value="{username}" placeholder="الاسم الجديد" required>
                                <input type="text" name="new_email" class="input-val" value="{email}" placeholder="البريد الجديد">
                                <input type="text" name="new_password" class="input-val" value="{password}" placeholder="كلمة السر">
                                <input type="text" name="new_avatar" class="input-val" value="{avatar}" placeholder="رابط الصورة">
                                <button type="submit" class="btn btn-edit">✏️ حفظ التعديل</button>
                            </form>
                        </td>

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

@app.route('/quick_action', methods=['GET'])
def quick_action():
    action = request.args.get('action')
    username = request.args.get('username')
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if action == 'toggle_ban' and username:
        if db_type == 'pg':
            cursor.execute('UPDATE players SET is_banned = 1 - is_banned WHERE username = %s', (username,))
        else:
            cursor.execute('UPDATE players SET is_banned = 1 - is_banned WHERE username = ?', (username,))
    
    elif action == 'update_money' and username:
        amount = request.args.get('amount', type=int, default=0)
        sub_action = request.args.get('sub_action')
        if sub_action == 'plus':
            if db_type == 'pg':
                cursor.execute('UPDATE players SET money = money + %s WHERE username = %s', (amount, username))
            else:
                cursor.execute('UPDATE players SET money = money + ? WHERE username = ?', (amount, username))
        elif sub_action == 'minus':
            if db_type == 'pg':
                cursor.execute('UPDATE players SET money = money - %s WHERE username = %s', (amount, username))
            else:
                cursor.execute('UPDATE players SET money = money - ? WHERE username = ?', (amount, username))
            
    elif action == 'send_message' and username:
        msg = request.args.get('message', default='')
        if db_type == 'pg':
            cursor.execute('UPDATE players SET admin_message = %s WHERE username = %s', (msg, username))
        else:
            cursor.execute('UPDATE players SET admin_message = ? WHERE username = ?', (msg, username))
        
    elif action == 'delete' and username:
        if db_type == 'pg':
            cursor.execute('DELETE FROM players WHERE username = %s', (username,))
        else:
            cursor.execute('DELETE FROM players WHERE username = ?', (username,))
        
    elif action == 'update_profile':
        old_username = request.args.get('old_username')
        new_username = request.args.get('new_username')
        new_email = request.args.get('new_email', '')
        new_password = request.args.get('new_password', '')
        new_avatar = request.args.get('new_avatar', '')
        
        if old_username and new_username:
            if db_type == 'pg':
                cursor.execute('UPDATE players SET username = %s, email = %s, password = %s, avatar = %s WHERE username = %s', (new_username, new_email, new_password, new_avatar, old_username))
            else:
                cursor.execute('UPDATE players SET username = ?, email = ?, password = ?, avatar = ? WHERE username = ?', (new_username, new_email, new_password, new_avatar, old_username))
        
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_panel'))

# مسار مزامنة وتحديث الفلوس من داخل اللعبة (يعود بالفلوس الجديدة مباشرة)
@app.route('/update_money_sync', methods=['POST', 'GET'])
def update_money_sync():
    data = request.get_json(silent=True) or request.form or request.args
    username = data.get('username')
    amount = data.get('amount', type=int, default=0)
    operation = data.get('operation', 'deduct')

    if not username:
        return jsonify({"status": "error", "message": "اسم المستخدم مطلوب"}), 400

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == 'pg':
        cursor.execute('SELECT money FROM players WHERE username = %s', (username,))
    else:
        cursor.execute('SELECT money FROM players WHERE username = ?', (username,))
        
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({"status": "error", "message": "اللاعب غير موجود"}), 404
        
    current_money = row[0]
    
    if operation == 'deduct':
        if current_money < amount:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "الرصيد غير كافٍ!"}), 400
        new_money = current_money - amount
    else:
        new_money = current_money + amount

    if db_type == 'pg':
        cursor.execute('UPDATE players SET money = %s WHERE username = %s', (new_money, username))
    else:
        cursor.execute('UPDATE players SET money = ? WHERE username = ?', (new_money, username))
        
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success", "message": "تم تحديث الفلوس بنجاح", "money": new_money})

# مسار تسجيل الدخول (يرسل حالة الحظر والفلوس والبيانات كاملة للعبة بدقة)
@app.route('/login', methods=['POST', 'GET'])
def login():
    try:
        data = request.get_json(silent=True) or request.form or request.args
        login_id = str(data.get('email') or data.get('username') or '').strip()
        password = str(data.get('password', '')).strip()

        conn, db_type = get_db_connection()
        cursor = conn.cursor()

        if db_type == 'pg':
            cursor.execute('SELECT username, email, money, is_banned, admin_message, avatar FROM players WHERE (email = %s OR username = %s) AND password = %s', (login_id, login_id, password))
        else:
            cursor.execute('SELECT username, email, money, is_banned, admin_message, avatar FROM players WHERE (email = ? OR username = ?) AND password = ?', (login_id, login_id, password))
        
        player = cursor.fetchone()
        cursor.close()
        conn.close()

        if player:
            username, email, money, is_banned, admin_message, avatar = player
            
            # إرسال حالة الحظر بوضوح تام للعبة
            if is_banned == 1:
                return jsonify({
                    "status": "error", 
                    "message": "هذا الحساب محظور من الإدارة!", 
                    "is_banned": 1
                })

            return jsonify({
                "status": "success",
                "message": "تم تسجيل الدخول بنجاح!",
                "username": username,
                "email": email,
                "money": money,
                "admin_message": admin_message,
                "avatar": avatar,
                "is_banned": 0
            })
        else:
            return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ بالسرفر: {str(e)}"}), 500

# مسار التسجيل (يدعم الحقلين avatar و avatar_path لعدم حدوث أي خطأ)
@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        data = request.get_json(silent=True) or request.form or request.args
        username = str(data.get('username', '')).strip()
        email = str(data.get('email', '')).strip()
        password = str(data.get('password', '')).strip()
        avatar = str(data.get('avatar') or data.get('avatar_path') or '').strip()

        if not username or not email or not password:
            return jsonify({"status": "error", "message": "بيانات الحساب غير كاملة"}), 400

        conn, db_type = get_db_connection()
        cursor = conn.cursor()

        if db_type == 'pg':
            cursor.execute('SELECT username FROM players WHERE username = %s OR email = %s', (username, email))
        else:
            cursor.execute('SELECT username FROM players WHERE username = ? OR email = ?', (username, email))
            
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "اسم المستخدم أو البريد مستخدم مسبقاً!"})

        if db_type == 'pg':
            cursor.execute('INSERT INTO players (username, password, email, money, is_banned, admin_message, avatar) VALUES (%s, %s, %s, 600, 0, \'لا يوجد\', %s)', (username, password, email, avatar))
        else:
            cursor.execute('INSERT INTO players (username, password, email, money, is_banned, admin_message, avatar) VALUES (?, ?, ?, 600, 0, "لا يوجد", ?)', (username, password, email, avatar))
            
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ بالسرفر: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
