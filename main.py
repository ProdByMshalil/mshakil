import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template_string, redirect, url_for

app = Flask(__name__)

DB_FILE = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# إنشاء الجداول محلياً
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT,
            money INTEGER DEFAULT 1000,
            score INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT '',
            unlocked_weapons TEXT DEFAULT '["PISTOL"]'
        );
        
        CREATE TABLE IF NOT EXISTS shop (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image TEXT DEFAULT ''
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ══════════════════════════════════════════════════
# ⚡ الـ APIs الخاصة بـ Godot
# ══════════════════════════════════════════════════

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    email = str(data.get('email', '')).strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "اسم المستخدم وكلمة السر مطلوبان"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT username FROM players WHERE LOWER(username) = LOWER(?) OR (email != '' AND LOWER(email) = LOWER(?))", (username, email))
    existing = cur.fetchone()

    if existing:
        conn.close()
        return jsonify({"status": "error", "message": "اسم المستخدم أو البريد مستخدم بالفعل"}), 400

    cur.execute("""
        INSERT INTO players (username, password, email, money, score, is_banned, admin_message, unlocked_weapons)
        VALUES (?, ?, ?, 1000, 0, 0, '', '["PISTOL"]')
    """, (username, password, email))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    user_input = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', '')).strip()

    if not user_input or not password:
        return jsonify({"status": "error", "message": "يرجى إدخال اسم المستخدم وكلمة السر"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username) = ? OR LOWER(email) = ?", (user_input, user_input))
    player = cur.fetchone()
    conn.close()

    if not player or str(player['password']).strip() != password:
        return jsonify({"status": "error", "message": "اسم المستخدم أو كلمة السر غير صحيحة"}), 401

    if player['is_banned'] == 1:
        msg = player['admin_message'] or "تم حظر حسابك من قبل الإدارة"
        return jsonify({"status": "error", "message": msg, "is_banned": 1}), 403

    weapons = json.loads(player['unlocked_weapons'] or '["PISTOL"]')

    return jsonify({
        "status": "success",
        "username": player['username'],
        "email": player['email'] or "",
        "money": player['money'],
        "score": player['score'],
        "is_banned": 0,
        "unlocked_weapons": weapons
    }), 200


@app.route('/get_shop', methods=['GET'])
def get_shop():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop")
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"status": "success", "shop": items}), 200


@app.route('/buy_item', methods=['POST'])
def buy_item():
    data = request.json or {}
    username = str(data.get('username', '')).strip()
    item_id = str(data.get('item_id', '')).strip()

    if not username or not item_id:
        return jsonify({"status": "error", "message": "بيانات غير مكتملة"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM players WHERE LOWER(username) = LOWER(?)", (username,))
    player = cur.fetchone()

    if not player:
        conn.close()
        return jsonify({"status": "error", "message": "اللاعب غير موجود"}), 404

    cur.execute("SELECT * FROM shop WHERE id = ?", (item_id,))
    item = cur.fetchone()

    if not item:
        conn.close()
        return jsonify({"status": "error", "message": "العنصر غير موجود في المتجر"}), 404

    price = item['price']
    current_money = player['money']

    if current_money < price:
        conn.close()
        return jsonify({"status": "error", "message": "رصيدك غير كافٍ"}), 400

    new_money = current_money - price
    weapons = json.loads(player['unlocked_weapons'] or '["PISTOL"]')

    if item_id not in weapons:
        weapons.append(item_id)

    cur.execute("""
        UPDATE players 
        SET money = ?, unlocked_weapons = ? 
        WHERE LOWER(username) = LOWER(?)
    """, (new_money, json.dumps(weapons), username))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "تم الشراء بنجاح",
        "new_money": new_money,
        "unlocked_weapons": weapons
    }), 200

# ══════════════════════════════════════════════════
# 🖥️ لوحة الأدمن
# ══════════════════════════════════════════════════

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة إدارة السيرفر</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg-body: #090c15; --bg-card: #111827; --border-color: #1f2937; --text-color: #e2e8f0; --text-muted: #9ca3af; --bg-input: #0b0f19; --accent-green: #10b981; }
        body.light-mode { --bg-body: #f1f5f9; --bg-card: #ffffff; --border-color: #cbd5e1; --text-color: #0f172a; --text-muted: #64748b; --bg-input: #f8fafc; --accent-green: #059669; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; transition: background 0.2s, color 0.2s; }
        body { background-color: var(--bg-body); color: var(--text-color); display: flex; min-height: 100vh; padding: 15px; gap: 15px; }
        .main-content { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        .sidebar-left { width: 320px; display: flex; flex-direction: column; gap: 15px; }
        .card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; }
        .time-box { text-align: center; border-color: #064e3b; }
        .time-title { color: var(--accent-green); font-size: 13px; font-weight: bold; margin-bottom: 5px; }
        .time-val { font-size: 20px; font-weight: bold; color: var(--accent-green); }
        .date-val { font-size: 12px; color: var(--text-muted); margin-top: 3px; }
        .form-title { color: var(--accent-green); font-size: 14px; font-weight: bold; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .inp-group { margin-bottom: 10px; }
        .inp-label { font-size: 11px; color: var(--text-muted); margin-bottom: 4px; display: block; }
        .sidebar-left input { width: 100%; background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-color); padding: 8px 10px; border-radius: 6px; font-size: 12px; }
        .btn-add-shop { width: 100%; background: var(--accent-green); color: #fff; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 5px; }
        .shop-list-title { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; }
        .shop-item { display: flex; justify-content: space-between; align-items: center; background: var(--bg-input); padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; border: 1px solid var(--border-color); }
        .shop-item-left { display: flex; align-items: center; gap: 8px; }
        .shop-img { width: 30px; height: 30px; border-radius: 4px; object-fit: cover; background: var(--border-color); }
        .shop-badge { background: #064e3b; color: #10b981; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .btn-del-shop { background: #7f1d1d; color: #fff; border: none; width: 24px; height: 24px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; }
        .main-title { font-size: 22px; font-weight: bold; color: var(--text-color); display: flex; align-items: center; gap: 10px; }
        .main-title span { color: var(--accent-green); }
        .top-btns { display: flex; gap: 8px; }
        .btn-top { background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-color); padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; }
        .btn-exit { background: #991b1b; color: #fff; border: none; }
        .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
        .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; text-align: center; }
        .stat-label { font-size: 12px; color: var(--text-muted); margin-bottom: 8px; }
        .stat-num { font-size: 24px; font-weight: bold; color: var(--accent-green); }
        .stat-num.red { color: #ef4444; }
        .search-box input { width: 100%; background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-color); padding: 10px 15px; border-radius: 8px; font-size: 13px; }
        .table-card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; flex: 1; overflow-x: auto; }
        .table-header { color: var(--accent-green); font-size: 15px; font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
        table { width: 100%; border-collapse: collapse; min-width: 950px; }
        th { color: var(--accent-green); font-size: 12px; padding: 10px; text-align: center; border-bottom: 1px solid var(--border-color); }
        td { padding: 10px; text-align: center; border-bottom: 1px solid var(--border-color); font-size: 13px; }
        .user-avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--border-color); display: inline-flex; align-items: center; justify-content: center; color: var(--accent-green); }
        .money-badge { background: #fbbf24; color: #000; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; }
        .weapons-text { font-size: 10px; color: var(--text-muted); display: block; margin-top: 2px; }
        .actions { display: flex; justify-content: center; gap: 4px; }
        .btn-act { width: 28px; height: 28px; border: none; border-radius: 4px; cursor: pointer; color: white; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; }
        .btn-act.status-active { background: #059669; }
        .btn-act.status-banned { background: #dc2626; }
        .btn-act.delete { background: #7f1d1d; }
        .btn-act.save-pass { background: #2563eb; }
        .inp-tbl { background: var(--bg-input); border: 1px solid var(--border-color); color: var(--text-color); padding: 4px 6px; border-radius: 4px; text-align: center; font-size: 12px; }
        .inp-money { width: 50px; }
        .inp-pass { width: 90px; }
        .inp-msg { width: 100px; }
    </style>
</head>
<body>
    <div class="main-content">
        <div class="top-bar">
            <div class="main-title"><i class="fas fa-gamepad"></i> لوحة إدارة السيرفر</div>
            <div class="top-btns">
                <button class="btn-top" onclick="toggleTheme()"><i class="fas fa-adjust"></i> <span id="theme-text">الوضع الفاتح</span></button>
                <button class="btn-top btn-exit"><i class="fas fa-sign-out-alt"></i> خروج</button>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">إجمالي اللاعبين</div><div class="stat-num">{{ total_players }}</div></div>
            <div class="stat-card"><div class="stat-label">إجمالي أموال اللعبة</div><div class="stat-num">${{ total_money }}</div></div>
            <div class="stat-card"><div class="stat-label">الحسابات المحظورة</div><div class="stat-num red">{{ banned_count }}</div></div>
        </div>
        <div class="search-box">
            <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="🔍 ابحث عن لاعب بالاسم أو البريد...">
        </div>
        <div class="table-card">
            <div class="table-header"><i class="fas fa-users-cog"></i> قائمة الحسابات والتعديل</div>
            <table id="playersTable">
                <thead>
                    <tr>
                        <th>الصورة</th><th>اسم المستخدم</th><th>البريد الإلكتروني</th><th>كلمة السر</th><th>الرصيد الحالي</th><th>تعديل الفلوس</th><th>رسالة الإدارة</th><th>إجراءات</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in players %}
                    <tr>
                        <form action="/admin/update_user" method="POST">
                            <input type="hidden" name="target_username" value="{{ p.username }}">
                            <td><div class="user-avatar"><i class="fas fa-user"></i></div></td>
                            <td><strong>{{ p.username }}</strong></td>
                            <td>{{ p.email or 'غ/م' }}</td>
                            <td><input type="text" name="new_password" value="{{ p.password }}" class="inp-tbl inp-pass"></td>
                            <td>
                                <div class="money-badge">${{ p.money }}</div>
                                <span class="weapons-text">الأسلحة: {{ p.unlocked_weapons_list | join(',') }}</span>
                            </td>
                            <td>
                                <button type="submit" name="action" value="add_money" class="btn-act status-active">+</button>
                                <input type="number" name="money_change" value="0" class="inp-tbl inp-money">
                                <button type="submit" name="action" value="sub_money" class="btn-act status-banned">-</button>
                            </td>
                            <td><input type="text" name="admin_message" value="{{ p.admin_message or '' }}" placeholder="رسالة تنبيه..." class="inp-tbl inp-msg"></td>
                            <td>
                                <div class="actions">
                                    <button type="submit" name="action" value="save_all" class="btn-act save-pass" title="حفظ التعديلات"><i class="fas fa-save"></i></button>
                                    {% if p.is_banned %}
                                        <button type="submit" name="action" value="unban" class="btn-act status-banned">محظور</button>
                                    {% else %}
                                        <button type="submit" name="action" value="ban" class="btn-act status-active">نشط</button>
                                    {% endif %}
                                    <button type="submit" name="action" value="delete" class="btn-act delete" title="حذف الحساب"><i class="fas fa-trash"></i></button>
                                </div>
                            </td>
                        </form>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    <div class="sidebar-left">
        <div class="card time-box">
            <div class="time-title"><i class="far fa-calendar-alt"></i> التاريخ والوقت</div>
            <div class="time-val" id="clock">--:--:--</div>
            <div class="date-val" id="date">--</div>
        </div>
        <div class="card">
            <div class="form-title"><i class="fas fa-cart-plus"></i> إضافة شيء للمتجر عن بُعد</div>
            <form action="/admin/add_shop" method="POST">
                <div class="inp-group"><label class="inp-label">معرف العنصر (ID)</label><input type="text" name="shop_id" placeholder="مثال: M416" required></div>
                <div class="inp-group"><label class="inp-label">اسم السلاح</label><input type="text" name="shop_name" placeholder="مثال: سلاح M416" required></div>
                <div class="inp-group"><label class="inp-label">رابط الصورة (URL)</label><input type="text" name="shop_image" placeholder="https://example.com/gun.png"></div>
                <div class="inp-group"><label class="inp-label">السعر ($)</label><input type="number" name="shop_price" placeholder="400" required></div>
                <button type="submit" class="btn-add-shop">+ إضافة للمتجر</button>
            </form>
        </div>
        <div class="card" style="flex:1;">
            <div class="shop-list-title"><span><i class="fas fa-store"></i> المتجر الحالي</span></div>
            {% for item in shop %}
            <div class="shop-item">
                <div class="shop-item-left">
                    {% if item.image %}<img src="{{ item.image }}" class="shop-img" alt="weapon">{% else %}<div class="shop-img" style="display:flex;align-items:center;justify-content:center;"><i class="fas fa-crosshairs" style="font-size:10px;"></i></div>{% endif %}
                    <span>{{ item.name }}</span>
                </div>
                <div style="display:flex; align-items:center; gap:6px;">
                    <span class="shop-badge">${{ item.price }}</span>
                    <form action="/admin/delete_shop" method="POST" style="margin:0;">
                        <input type="hidden" name="shop_id" value="{{ item.id }}">
                        <button type="submit" class="btn-del-shop" title="حذف العنصر"><i class="fas fa-trash"></i></button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function toggleTheme() { document.body.classList.toggle('light-mode'); document.getElementById('theme-text').textContent = document.body.classList.contains('light-mode') ? 'الوضع الداكن' : 'الوضع الفاتح'; }
        function updateClock() {
            const now = new Date();
            const hours = String(now.getHours() % 12 || 12).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const ampm = now.getHours() >= 12 ? 'ص' : 'م';
            document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
            document.getElementById('date').textContent = now.toLocaleDateString('ar-SA', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        }
        setInterval(updateClock, 1000); updateClock();
        function filterTable() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('#playersTable tbody tr').forEach(row => { row.style.display = row.textContent.toLowerCase().includes(input) ? '' : 'none'; });
        }
    </script>
</body>
</html>
"""

@app.route('/admin', methods=['GET'])
def admin_panel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    raw_players = cur.fetchall()
    
    players = []
    for p in raw_players:
        p_dict = dict(p)
        try:
            p_dict['unlocked_weapons_list'] = json.loads(p_dict['unlocked_weapons'] or '["PISTOL"]')
        except:
            p_dict['unlocked_weapons_list'] = ["PISTOL"]
        players.append(p_dict)

    cur.execute("SELECT * FROM shop")
    shop = [dict(row) for row in cur.fetchall()]
    conn.close()

    total_players = len(players)
    total_money = sum(p['money'] for p in players)
    banned_count = sum(1 for p in players if p['is_banned'] == 1)

    return render_template_string(ADMIN_HTML, players=players, shop=shop, total_players=total_players, total_money=total_money, banned_count=banned_count)

@app.route('/admin/add_shop', methods=['POST'])
def add_shop():
    s_id = request.form.get('shop_id')
    s_name = request.form.get('shop_name')
    s_price = request.form.get('shop_price')
    s_image = request.form.get('shop_image', '')

    if s_id and s_name and s_price:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO shop (id, name, price, image) VALUES (?, ?, ?, ?)",
                    (s_id, s_name, int(s_price), s_image))
        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_shop', methods=['POST'])
def delete_shop():
    s_id = request.form.get('shop_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM shop WHERE id = ?", (s_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_user', methods=['POST'])
def admin_update_user():
    target = request.form.get('target_username')
    action = request.form.get('action')
    money_change = int(request.form.get('money_change', 0))
    admin_msg = request.form.get('admin_message', '')
    new_pass = request.form.get('new_password', '').strip()

    conn = get_db_connection()
    cur = conn.cursor()

    if new_pass:
        cur.execute("UPDATE players SET password = ? WHERE LOWER(username) = LOWER(?)", (new_pass, target))

    cur.execute("UPDATE players SET admin_message = ? WHERE LOWER(username) = LOWER(?)", (admin_msg, target))

    if action == "add_money":
        cur.execute("UPDATE players SET money = money + ? WHERE LOWER(username) = LOWER(?)", (money_change, target))
    elif action == "sub_money":
        cur.execute("UPDATE players SET money = MAX(0, money - ?) WHERE LOWER(username) = LOWER(?)", (money_change, target))
    elif action == "ban":
        cur.execute("UPDATE players SET is_banned = 1 WHERE LOWER(username) = LOWER(?)", (target,))
    elif action == "unban":
        cur.execute("UPDATE players SET is_banned = 0 WHERE LOWER(username) = LOWER(?)", (target,))
    elif action == "delete":
        cur.execute("DELETE FROM players WHERE LOWER(username) = LOWER(?)", (target,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
