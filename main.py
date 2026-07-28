from flask import Flask, request, jsonify, redirect, url_for
import os
import psycopg2
import sqlite3

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
        # التأكد من إضافة الأعمدة لو الجدول كان قديم
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
            h1 { color: #00ffcc; }
            .panel-container { border: 2px solid #ff00ff; border-radius: 15px; padding: 20px; max-width: 98%; margin: 0 auto; background-color: #120124; overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { color: #00ffff; padding: 12px; border-bottom: 2px solid #ff00ff; }
            td { padding: 12px 8px; border-bottom: 1px solid #333; }
            .status-active { color: #00ff00; font-weight: bold; }
            .status-banned { color: #ff0055; font-weight: bold; }
            .btn { padding: 5px 10px; border: none; border-radius: 4px; color: white; cursor: pointer; font-weight: bold; }
            .btn-ban { background-color: #ff0055; }
            .btn-unban { background-color: #00cc66; }
            .avatar-img { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 1px solid #00ffcc; }
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
                        <th>الفلوس</th>
                        <th>الحالة</th>
                        <th>رسالة الإدارة</th>
                        <th>الإجراءات</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for p in players:
        username, password, email, money, is_banned, admin_message, avatar = p
        status_str = '<span class="status-active">🟢 نشط</span>' if is_banned == 0 else '<span class="status-banned">🔴 محظور</span>'
        ban_btn_label = 'حظر' if is_banned == 0 else 'فك الحظر'
        ban_btn_class = 'btn-ban' if is_banned == 0 else 'btn-unban'
        avatar_display = f'<img src="{avatar}" class="avatar-img">' if avatar else '<span>👤</span>'
        
        html += f'''
                    <tr>
                        <td>{avatar_display}</td>
                        <td><b>{username}</b></td>
                        <td>{password}</td>
                        <td>{email}</td>
                        <td>{money} 💰</td>
                        <td>{status_str}</td>
                        <td>{admin_message}</td>
                        <td>
                            <button class="btn {ban_btn_class}" onclick="location.href='/quick_action?action=toggle_ban&username={username}'">{ban_btn_label}</button>
                            <button class="btn" style="background:#555;" onclick="if(confirm('حذف؟')) location.href='/quick_action?action=delete&username={username}'">❌ حذف</button>
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
        if is_banned == 1:
            return jsonify({"status": "error", "message": "الحساب محظور!"})
        return jsonify({"status": "success", "username": username, "money": money, "avatar": avatar})
    return jsonify({"status": "error", "message": "خطأ في البيانات!"})

@app.route('/register', methods=['POST', 'GET'])
def register():
    data = request.get_json(silent=True) or request.form or request.args
    email = str(data.get('email', '')).strip()
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    avatar = str(data.get('avatar', '')).strip()

    if not username and email: username = email
    if not email and username: email = username

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    if db_type == 'pg':
        cursor.execute('INSERT INTO players (username, password, email, money, is_banned, admin_message, avatar) VALUES (%s, %s, %s, 600, 0, \'لا يوجد\', %s)', (username, password, email, avatar))
    else:
        cursor.execute('INSERT INTO players (username, password, email, money, is_banned, admin_message, avatar) VALUES (?, ?, ?, 600, 0, "لا يوجد", ?)', (username, password, email, avatar))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success", "message": "تم التسجيل بنجاح!"})

if __name__ == '__main__':
    app.run(debug=True)
