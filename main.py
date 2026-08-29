from flask import Flask, request, jsonify, redirect, url_for, session
import os
import random
import psycopg2
import sqlite3

app = Flask(__name__)
app.secret_key = 'relic_curse_secret_key_ez9'

ADMIN_CODE = "Prod_By_77"
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn, 'pg'
        except Exception as e:
            print(f"⚠️ تعذر الاتصال بـ PostgreSQL: {e}. سيتم استخدام SQLite بدلاً عنها.")
    
    conn = sqlite3.connect("database.db", check_same_thread=False)
    return conn, 'sqlite'

def init_db():
    try:
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
                    admin_message TEXT DEFAULT 'لا يوجد',
                    avatar TEXT DEFAULT ''
                );
            ''')
            for col, col_type in [('avatar', 'TEXT DEFAULT \'\''), ('admin_message', 'TEXT DEFAULT \'لا يوجد\''), ('is_banned', 'INTEGER DEFAULT 0'), ('money', 'INTEGER DEFAULT 600'), ('email', 'TEXT DEFAULT \'\''), ('password', 'TEXT DEFAULT \'\'')]:
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
                    admin_message TEXT DEFAULT 'لا يوجد',
                    avatar TEXT DEFAULT ''
                );
            ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ خطأ أثناء تهيئة قاعدة البيانات: {e}")

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
            body { background: #0b0c10; color: #fff; font-family: Tahoma, sans-serif; text-align: center; padding: 50px; }
            h1 { color: #00ffcc; }
            a { color: #ff00ff; font-size: 20px; text-decoration: none; border: 2px solid #ff00ff; padding: 10px 20px; border-radius: 8px; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>🎮 خوادم Relic Curse تعمل بكفاءة!</h1>
        <p>السيرفر متصل وقاعدة البيانات تعمل بنجاح.</p>
        <a href="/admin">الذهاب إلى لوحة تحكم الإمبراطور 👑</a>
    </body>
    </html>
    '''

@app.route('/send-code', methods=['POST', 'GET'])
def send_code():
    try:
        data = request.get_json(silent=True) or request.form or request.args
        email = str(data.get('email', '')).strip()
        
        if not email:
            return jsonify({"status": "error", "message": "البريد الإلكتروني مطلوب"}), 400
            
        otp_code = str(random.randint(1000, 9999))
        
        print(f"\n================================")
        print(f"🔑 [رمز التحقق OTP] للإيميل ({email}) هو: {otp_code}")
        print(f"================================\n")

        return jsonify({
            "status": "success",
            "message": "تم إرسال رمز التحقق بنجاح!",
            "debug_code": otp_code
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ بالسرفر: {str(e)}"}), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if code == ADMIN_CODE:
            session['admin_logged'] = True
            return redirect(url_for('admin_panel'))
        else:
            return '''
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <style>
                    body { background: #0b0c10; color: #ff0055; font-family: Tahoma; text-align: center; padding-top: 100px; }
                    a { color: #00ffcc; text-decoration: none; font-size: 18px; display: block; margin-top: 20px; }
                </style>
            </head>
            <body>
                <h2>❌ رمز الدخول غير صحيح!</h2>
                <a href="/admin">إعادة المحاولة</a>
            </body>
            </html>
            '''

    if not session.get('admin_logged'):
        return '''
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تأكيد الهوية - الإمبراطور</title>
            <style>
                body { background-color: #0b0c10; color: #fff; font-family: Tahoma; text-align: center; padding-top: 120px; }
                .box { border: 2px solid #ff00ff; border-radius: 12px; padding: 30px; display: inline-block; background: #120124; box-shadow: 0 0 20px #ff00ff; }
                input { padding: 10px; border-radius: 6px; border: 1px solid #00ffcc; background: #1a0236; color: #fff; text-align: center; font-size: 16px; margin-bottom: 15px; }
                button { padding: 10px 25px; border: none; border-radius: 6px; background: #ff00ff; color: #fff; font-weight: bold; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="box">
                <h2 style="color: #00ffcc;">👑 أدخل رمز الحماية للوحة التحكم</h2>
                <form method="POST">
                    <input type="password" name="code" placeholder="رمز الحماية" required><br>
                    <button type="submit">دخول</button>
                </form>
            </div>
        </body>
        </html>
        '''

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
            body { background-color: #05020a; color: #fff; font-family: Tahoma, sans-serif; text-align: center; padding: 20px; margin: 0; }
            h1 { color: #00e5ff; text-shadow: 0 0 10px #00e5ff; margin-bottom: 25px; font-size: 24px; }
            .panel-container { border: 2px solid #a800ff; border-radius: 15px; padding: 15px; max-width: 98%; margin: 0 auto; background-color: #0a0118; box-shadow: 0 0 20px rgba(168, 0, 255, 0.4); overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; }
            th { color: #a800ff; padding: 12px 6px; font-size: 13px; border-bottom: 2px solid #a800ff; white-space: nowrap; }
            td { padding: 10px 6px; border-bottom: 1px solid #1f083a; font-size: 12px; vertical-align: middle; }
            
            .player-cell { display: flex; align-items: center; justify-content: center; gap: 10px; }
            .avatar-img { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid #00e5ff; background: #111; }
            
            .status-active { color: #00ff66; font-weight: bold; }
            .status-banned { color: #ff0055; font-weight: bold; }
            .msg-text { color: #d870ff; }
            .pass-text { color: #ffcc00; font-family: monospace; }
            
            .ctrl-flex { display: flex; align-items: center; justify-content: center; gap: 4px; flex-wrap: nowrap; }
            .input-val { background: #180530; border: 1px solid #7700cc; color: #fff; padding: 6px; border-radius: 4px; width: 110px; text-align: center; font-size: 11px; }
            
            .btn { padding: 6px 10px; border: none; border-radius: 4px; color: white; cursor: pointer; font-weight: bold; font-size: 11px; white-space: nowrap; }
            .btn-ban { background-color: #e6005c; }
            .btn-unban { background-color: #00b359; }
            .btn-minus { background-color: #ff8800; }
            .btn-plus { background-color: #00c8c8; }
            .btn-msg { background-color: #0066ff; }
            .btn-del { background-color: #333344; border: 1px solid #555; }
            .logout-btn { color: #ff3377; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 20px; font-size: 14px; }
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
                        <th>كلمة المرور</th>
                        <th>الفلوس الحالية</th>
                        <th>حالة الحساب</th>
                        <th>رسالة الإدارة له</th>
                        <th>خيارات التحكم السريعة</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for p in players:
        username, password, email, money, is_banned, admin_message, avatar = p
        status_str = '<span class="status-active">🟢 نشط</span>' if is_banned == 0 else '<span class="status-banned">🔴 محظور</span>'
        ban_btn_label = 'حظر' if is_banned == 0 else 'فك الحظر'
        ban_btn_class = 'btn-ban' if is_banned == 0 else 'btn-unban'
        
        avatar_url = avatar if avatar and avatar.strip() != '' else 'https://cdn-icons-png.flaticon.com/512/149/149071.png'
        
        html += f'''
                    <tr>
                        <td>
                            <div class="player-cell">
                                <img src="{avatar_url}" class="avatar-img" onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';">
                                <b>{username}</b>
                            </div>
                        </td>
                        <td>{email}</td>
                        <td class="pass-text">{password}</td>
                        <td>{money} 💰</td>
                        <td>{status_str}</td>
                        <td class="msg-text">{admin_message}</td>
                        
                        <td>
                            <div class="ctrl-flex">
                                <button class="btn {ban_btn_class}" onclick="location.href='/quick_action?action=toggle_ban&username={username}'">{ban_btn_label}</button>
                                
                                <form action="/quick_action" method="GET" style="display:flex; gap:3px; margin:0;">
                                    <input type="hidden" name="username" value="{username}">
                                    <input type="text" name="val_input" class="input-val" placeholder="المبلغ أو الرسالة">
                                    <button type="submit" name="action" value="add_money" class="btn btn-plus">+ زيادة</button>
                                    <button type="submit" name="action" value="sub_money" class="btn btn-minus">- نقصان</button>
                                    <button type="submit" name="action" value="send_message" class="btn btn-msg">📧 إرسال رسالة</button>
                                </form>

                                <button class="btn btn-del" onclick="if(confirm('هل أنت متأكد من حذف الحساب؟')) location.href='/quick_action?action=delete&username={username}'">❌ حذف</button>
                            </div>
                        </td>
                    </tr>
        '''
        
    html += '''
                </tbody>
            </table>
        </div>
        <a href="/admin_logout" class="logout-btn">🚪 تسجيل الخروج</a>
    </body>
    </html>
    '''
    return html

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('admin_panel'))

@app.route('/quick_action', methods=['GET'])
def quick_action():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_panel'))

    action = request.args.get('action')
    username = request.args.get('username')
    val_input = request.args.get('val_input', '').strip()
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if action == 'toggle_ban' and username:
        if db_type == 'pg':
            cursor.execute('UPDATE players SET is_banned = 1 - is_banned WHERE username = %s', (username,))
        else:
            cursor.execute('UPDATE players SET is_banned = 1 - is_banned WHERE username = ?', (username,))
    
    elif action == 'add_money' and username:
        amount = int(val_input) if val_input.isdigit() else 0
        if db_type == 'pg':
            cursor.execute('UPDATE players SET money = money + %s WHERE username = %s', (amount, username))
        else:
            cursor.execute('UPDATE players SET money = money + ? WHERE username = ?', (amount, username))

    elif action == 'sub_money' and username:
        amount = int(val_input) if val_input.isdigit() else 0
        if db_type == 'pg':
            cursor.execute('UPDATE players SET money = money - %s WHERE username = %s', (amount, username))
        else:
            cursor.execute('UPDATE players SET money = money - ? WHERE username = ?', (amount, username))
            
    elif action == 'send_message' and username:
        if db_type == 'pg':
            cursor.execute('UPDATE players SET admin_message = %s WHERE username = %s', (val_input, username))
        else:
            cursor.execute('UPDATE players SET admin_message = ? WHERE username = ?', (val_input, username))
        
    elif action == 'delete' and username:
        if db_type == 'pg':
            cursor.execute('DELETE FROM players WHERE username = %s', (username,))
        else:
            cursor.execute('DELETE FROM players WHERE username = ?', (username,))
        
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('admin_panel'))

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
            
            return jsonify({
                "status": "success",
                "message": "تم التحديث بنجاح!",
                "username": username,
                "email": email,
                "money": money,
                "admin_message": admin_message,
                "avatar": avatar,
                "is_banned": is_banned
            })
        else:
            return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"خطأ بالسرفر: {str(e)}"}), 500

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
