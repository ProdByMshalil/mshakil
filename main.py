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
            unlocked_weapons TEXT DEFAULT '["PISTOL"]',
            avatar TEXT DEFAULT ''
        );
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image TEXT DEFAULT ''
        );
    """)

    default_items = [
        ("AK47", "AK-47", 100, "https://i.imgur.com/7k1287B.png"),
        ("DESEART EAGLE", "Desert Eagle", 350, "https://i.imgur.com/384384Q.png"),
        ("UMP", "UMP", 500, "https://i.imgur.com/5656565.png")
    ]
    for item_id, name, price, img in default_items:
        cur.execute("INSERT OR IGNORE INTO shop (id, name, price, image) VALUES (?, ?, ?, ?)", (item_id, name, price, img))
    
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
    cur.execute("SELECT username FROM players WHERE LOWER(username) = LOWER(?)", (username,))
    if cur.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "اسم المستخدم مستخدم بالفعل"}), 400

    cur.execute("""
        INSERT INTO players (username, password, email, money, score, is_banned, admin_message, unlocked_weapons, avatar)
        VALUES (?, ?, ?, 1000, 0, 0, '', '["PISTOL"]', '')
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

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE LOWER(username) = ? OR LOWER(email) = ?", (user_input, user_input))
    player = cur.fetchone()
    conn.close()

    if not player or str(player['password']).strip() != password:
        return jsonify({"status": "error", "message": "بيانات الدخول غير صحيحة"}), 401

    if player['is_banned'] == 1:
        return jsonify({"status": "error", "message": player['admin_message'] or "الحساب محظور", "is_banned": 1}), 403

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
        return jsonify({"status": "error", "message": f"العنصر {item_id} غير موجود في المتجر"}), 404

    price = item['price']
    current_money = player['money']

    if current_money < price:
        conn.close()
        return jsonify({"status": "error", "message": "رصيدك غير كافٍ"}), 400

    new_money = current_money - price
    weapons = json.loads(player['unlocked_weapons'] or '["PISTOL"]')

    if item_id not in weapons:
        weapons.append(item_id)

    cur.execute("UPDATE players SET money = ?, unlocked_weapons = ? WHERE LOWER(username) = LOWER(?)", 
                (new_money, json.dumps(weapons), username))
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
# 🖥️ لوحة التحكم الأصلية الاحترافية مع توقيت حي
# ══════════════════════════════════════════════════

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة إدارة السيرفر - EZ9</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-main: #090c15;
            --bg-card: #111827;
            --bg-input: #1f2937;
            --border: #374151;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Tahoma, sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-main); display: flex; flex-direction: column; min-height: 100vh; padding: 15px; }
        header { display: flex; justify-content: space-between; align-items: center; background: var(--bg-card); border: 1px solid var(--border); padding: 15px 25px; border-radius: 10px; margin-bottom: 20px; }
        header h1 { font-size: 20px; color: var(--success); }
        .stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: var(--bg-card); border: 1px solid var(--border); padding: 15px; border-radius: 10px; text-align: center; }
        .stat-card h3 { font-size: 14px; color: var(--text-muted); margin-bottom: 5px; }
        .stat-card p { font-size: 22px; font-weight: bold; color: var(--primary); }
        
        .main-layout { display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
        @media(max-width: 900px) { .main-layout { grid-template-columns: 1fr; } }

        .sidebar { display: flex; flex-direction: column; gap: 20px; }
        .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 15px; }
        .card h2 { font-size: 16px; margin-bottom: 12px; border-bottom: 1px solid var(--border); padding-bottom: 8px; color: var(--success); }
        
        form { display: flex; flex-direction: column; gap: 10px; }
        label { font-size: 12px; color: var(--text-muted); }
        input, select { background: var(--bg-input); border: 1px solid var(--border); color: var(--text-main); padding: 8px; border-radius: 6px; font-size: 13px; width: 100%; }
        button { background: var(--success); color: white; border: none; padding: 9px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { opacity: 0.9; }

        .table-container { background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 15px; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; min-width: 800px; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid var(--border); font-size: 13px; }
        th { color: var(--success); background: rgba(16, 185, 129, 0.05); }
        
        .btn-action { padding: 5px 10px; border-radius: 4px; border: none; cursor: pointer; color: white; font-size: 12px; }
        .btn-edit { background: var(--primary); }
        .btn-delete { background: var(--danger); }
        .btn-save { background: var(--success); }
        
        .shop-item-box { display: flex; flex-direction: column; background: var(--bg-input); border: 1px solid var(--border); padding: 10px; border-radius: 8px; margin-bottom: 10px; gap: 8px; }
        .shop-item-header { display: flex; justify-content: space-between; align-items: center; }
        .shop-item-body { display: grid; grid-template-columns: 1fr 1fr 70px; gap: 5px; }
        .shop-img-preview { width: 35px; height: 35px; border-radius: 4px; object-fit: cover; background: #000; }
    </style>
</head>
<body>

    <header>
        <h1>لوحة إدارة السيرفر (EZ9)</h1>
        <div style="text-align: left;">
            <div id="live-clock" style="font-size: 15px; font-weight: bold; color: var(--success);">جاري تحميل الوقت...</div>
            <div id="live-date" style="font-size: 12px; color: var(--text-muted);"></div>
        </div>
    </header>

    <div class="stats-container">
        <div class="stat-card">
            <h3>إجمالي اللاعبين</h3>
            <p>{{ players|length }}</p>
        </div>
        <div class="stat-card">
            <h3>إجمالي أموال اللعبة</h3>
            <p>${{ players|sum(attribute='money') }}</p>
        </div>
        <div class="stat-card">
            <h3>عدد عناصر المتجر</h3>
            <p>{{ shop|length }}</p>
        </div>
    </div>

    <div class="main-layout">
        <!-- القائمة الجانبية لإضافة الأسلحة وتعديل المتجر -->
        <div class="sidebar">
            <div class="card">
                <h2>إضافة سلاح جديد للمتجر</h2>
                <form action="/admin/add_shop" method="POST">
                    <label>معرف السلاح في اللعبة (ID مثل: DESEART EAGLE)</label>
                    <input type="text" name="shop_id" placeholder="DESEART EAGLE" required>
                    
                    <label>اسم السلاح الظاهر</label>
                    <input type="text" name="shop_name" placeholder="نصر صحراء" required>
                    
                    <label>رابط الصورة (URL)</label>
                    <input type="text" name="shop_image" placeholder="https://example.com/gun.png">
                    
                    <label>السعر ($)</label>
                    <input type="number" name="shop_price" placeholder="350" required>
                    
                    <button type="submit">إضافة للسيرفر</button>
                </form>
            </div>

            <!-- قائمة تعديل وحذف عناصر المتجر نهائياً -->
            <div class="card">
                <h2>عناصر المتجر الحاليّة</h2>
                {% for item in shop %}
                <form action="/admin/edit_shop" method="POST" class="shop-item-box">
                    <input type="hidden" name="old_id" value="{{ item.id }}">
                    <div class="shop-item-header">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <img src="{{ item.image if item.image else 'https://via.placeholder.com/35' }}" class="shop-img-preview" onerror="this.src='https://via.placeholder.com/35'">
                            <b style="font-size: 12px; color: var(--warning);">ID: {{ item.id }}</b>
                        </div>
                        <div style="display: flex; gap: 4px;">
                            <button type="submit" name="action" value="edit" class="btn-action btn-save" title="حفظ التعديل"><i class="fas fa-save"></i></button>
                            <button type="submit" name="action" value="delete" class="btn-action btn-delete" title="حذف تام من المتجر واللعبة"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                    <div class="shop-item-body">
                        <input type="text" name="new_id" value="{{ item.id }}" placeholder="ID" title="معرف السلاح في اللعبة" required>
                        <input type="text" name="new_name" value="{{ item.name }}" placeholder="الاسم" title="الاسم الظاهر" required>
                        <input type="number" name="new_price" value="{{ item.price }}" placeholder="السعر" title="السعر" required>
                    </div>
                    <input type="text" name="new_image" value="{{ item.image }}" placeholder="رابط الصورة URL" title="رابط الصورة">
                </form>
                {% endfor %}
            </div>
        </div>

        <!-- جدول إدارة اللاعبين الكامل -->
        <div class="table-container">
            <h2 style="font-size: 16px; color: var(--success); margin-bottom: 15px;">قائمة الحسابات والتحكم الكامل</h2>
            <table>
                <tr>
                    <th>اسم المستخدم</th>
                    <th>البريد الإلكتروني</th>
                    <th>كلمة السر</th>
                    <th>الرصيد الحالي</th>
                    <th>تعديل الفلوس</th>
                    <th>رسالة الإدارة</th>
                    <th>حالة الحظر</th>
                    <th>إجراءات الحفظ والحذف</th>
                </tr>
                {% for p in players %}
                <tr>
                    <form action="/admin/update_user_full" method="POST">
                        <input type="hidden" name="target_username" value="{{ p.username }}">
                        <td><input type="text" name="new_username" value="{{ p.username }}" required></td>
                        <td><input type="text" name="new_email" value="{{ p.email }}"></td>
                        <td><input type="text" name="new_password" value="{{ p.password }}" required></td>
                        <td><b style="color: var(--success);">${{ p.money }}</b></td>
                        <td>
                            <div style="display: flex; gap: 4px; align-items: center;">
                                <button type="submit" name="action" value="add_money" class="btn-action" style="background:var(--success); padding: 5px 8px;">+</button>
                                <input type="number" name="money_change" value="100" style="width: 60px; text-align: center;">
                                <button type="submit" name="action" value="sub_money" class="btn-action" style="background:var(--danger); padding: 5px 8px;">-</button>
                            </div>
                        </td>
                        <td><input type="text" name="admin_message" value="{{ p.admin_message }}" placeholder="رسالة عند الحظر..."></td>
                        <td>
                            <select name="is_banned" style="padding: 5px;">
                                <option value="0" {% if p.is_banned == 0 %}selected{% endif %}>نشط</option>
                                <option value="1" {% if p.is_banned == 1 %}selected{% endif %}>محظور</option>
                            </select>
                        </td>
                        <td>
                            <div style="display: flex; gap: 5px; justify-content: center;">
                                <button type="submit" name="action" value="save_profile" class="btn-action btn-edit" title="حفظ التعديلات"><i class="fas fa-edit"></i></button>
                                <button type="submit" name="action" value="delete_account" class="btn-action btn-delete" title="حذف الحساب نهائياً"><i class="fas fa-trash"></i></button>
                            </div>
                        </td>
                    </form>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            // عرض الوقت بالساعات الدقائق والثواني
            document.getElementById('live-clock').innerText = now.toLocaleTimeString('ar-EG');
            // عرض التاريخ اليومي
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('live-date').innerText = now.toLocaleDateString('ar-EG', options);
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
</body>
</html>
"""

@app.route('/admin', methods=['GET'])
def admin_panel():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players")
    players = [dict(row) for row in cur.fetchall()]
    cur.execute("SELECT * FROM shop")
    shop = [dict(row) for row in cur.fetchall()]
    conn.close()
    return render_template_string(ADMIN_HTML, players=players, shop=shop)

@app.route('/admin/add_shop', methods=['POST'])
def add_shop():
    s_id = request.form.get('shop_id').strip()
    s_name = request.form.get('shop_name').strip()
    s_image = request.form.get('shop_image', '').strip()
    s_price = request.form.get('shop_price')
    if s_id and s_name and s_price:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO shop (id, name, price, image) VALUES (?, ?, ?, ?)",
                    (s_id, s_name, int(s_price), s_image))
        conn.commit()
        conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit_shop', methods=['POST'])
def edit_shop():
    old_id = request.form.get('old_id').strip()
    action = request.form.get('action')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    if action == "delete":
        cur.execute("DELETE FROM shop WHERE id = ?", (old_id,))
    elif action == "edit":
        new_id = request.form.get('new_id').strip()
        new_name = request.form.get('new_name').strip()
        new_price = int(request.form.get('new_price', 0))
        new_image = request.form.get('new_image', '').strip()
        
        if old_id != new_id:
            cur.execute("DELETE FROM shop WHERE id = ?", (old_id,))
            cur.execute("INSERT OR REPLACE INTO shop (id, name, price, image) VALUES (?, ?, ?, ?)",
                        (new_id, new_name, new_price, new_image))
        else:
            cur.execute("UPDATE shop SET name = ?, price = ?, image = ? WHERE id = ?",
                        (new_name, new_price, new_image, old_id))
            
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_user_full', methods=['POST'])
def admin_update_user_full():
    target = request.form.get('target_username').strip()
    action = request.form.get('action')
    
    conn = get_db_connection()
    cur = conn.cursor()

    if action == "add_money":
        money_change = int(request.form.get('money_change', 0))
        cur.execute("UPDATE players SET money = money + ? WHERE LOWER(username) = LOWER(?)", (money_change, target))
    elif action == "sub_money":
        money_change = int(request.form.get('money_change', 0))
        cur.execute("UPDATE players SET money = MAX(0, money - ?) WHERE LOWER(username) = LOWER(?)", (money_change, target))
    elif action == "delete_account":
        cur.execute("DELETE FROM players WHERE LOWER(username) = LOWER(?)", (target,))
    elif action == "save_profile":
        new_username = request.form.get('new_username').strip()
        new_email = request.form.get('new_email').strip()
        new_password = request.form.get('new_password').strip()
        admin_message = request.form.get('admin_message', '').strip()
        is_banned = int(request.form.get('is_banned', 0))

        cur.execute("""
            UPDATE players 
            SET username = ?, email = ?, password = ?, admin_message = ?, is_banned = ? 
            WHERE LOWER(username) = LOWER(?)
        """, (new_username, new_email, new_password, admin_message, is_banned, target))

    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
