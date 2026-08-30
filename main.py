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

    # العناصر الافتراضية
    default_items = [
        ("AK47", "AK-47", 100, ""),
        ("DESEART EAGLE", "Desert Eagle", 350, ""),
        ("UMP", "UMP", 500, "")
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
# 🖥️ لوحة الأدمن المحدثة (تعديل وحذف تام للمتجر)
# ══════════════════════════════════════════════════

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم السيرفر - EZ9</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root { --bg-body: #090c15; --bg-card: #111827; --border: #1f2937; --text: #e2e8f0; --green: #10b981; }
        body { background: var(--bg-body); color: var(--text); font-family: Tahoma, sans-serif; display: flex; padding: 15px; gap: 15px; min-height: 100vh; }
        .main { flex: 1; display: flex; flex-direction: column; gap: 15px; }
        .side { width: 340px; display: flex; flex-direction: column; gap: 15px; }
        .box { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 15px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: center; border-bottom: 1px solid var(--border); font-size: 13px; }
        th { color: var(--green); }
        input, button { background: #0b0f19; border: 1px solid var(--border); color: var(--text); padding: 6px; border-radius: 4px; font-size: 12px; }
        .btn { background: var(--green); color: #fff; border: none; cursor: pointer; font-weight: bold; }
        .btn-del { background: #7f1d1d; color: #fff; border: none; cursor: pointer; padding: 4px 8px; border-radius: 4px; }
        .btn-edit { background: #2563eb; color: #fff; border: none; cursor: pointer; padding: 4px 8px; border-radius: 4px; }
        .shop-row { display: flex; flex-direction: column; background: #0b0f19; padding: 10px; border-radius: 6px; margin-bottom: 8px; border: 1px solid var(--border); gap: 6px; }
        .shop-row-top { display: flex; justify-content: space-between; align-items: center; }
        .shop-row-inputs { display: flex; gap: 4px; }
        .shop-row-inputs input { width: 100%; }
    </style>
</head>
<body>
    <div class="main">
        <h2>لوحة تحكم السيرفر (EZ9)</h2>
        <div class="box" style="overflow-x:auto;">
            <h3>اللاعبين المسجلين</h3>
            <table>
                <tr><th>اسم المستخدم</th><th>البريد</th><th>الرصيد</th><th>التحكم بالفلوس</th><th>حذف</th></tr>
                {% for p in players %}
                <tr>
                    <form action="/admin/update_user" method="POST">
                        <input type="hidden" name="target_username" value="{{ p.username }}">
                        <td>{{ p.username }}</td>
                        <td>{{ p.email }}</td>
                        <td>${{ p.money }}</td>
                        <td>
                            <button type="submit" name="action" value="add_money" class="btn">+</button>
                            <input type="number" name="money_change" value="100" style="width:50px; text-align:center;">
                            <button type="submit" name="action" value="sub_money" class="btn" style="background:#dc2626;">-</button>
                        </td>
                        <td><button type="submit" name="action" value="delete" class="btn-del"><i class="fas fa-trash"></i></button></td>
                    </form>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
    <div class="side">
        <div class="box">
            <h3>إضافة عنصر للمتجر</h3>
            <form action="/admin/add_shop" method="POST" style="display:flex; flex-direction:column; gap:8px;">
                <label>معرف السلاح (ID مثل: DESEART EAGLE)</label>
                <input type="text" name="shop_id" placeholder="DESEART EAGLE" required>
                <label>اسم السلاح الظاهر</label>
                <input type="text" name="shop_name" placeholder="نصر صحراء" required>
                <label>السعر ($)</label>
                <input type="number" name="shop_price" placeholder="350" required>
                <button type="submit" class="btn" style="padding:8px;">إضافة للسيرفر</button>
            </form>
        </div>
        <div class="box" style="flex:1;">
            <h3>عناصر المتجر (تعديل أو حذف تام)</h3>
            {% for item in shop %}
            <form action="/admin/edit_shop" method="POST" class="shop-row">
                <input type="hidden" name="old_id" value="{{ item.id }}">
                <div class="shop-row-top">
                    <span><b>ID:</b> {{ item.id }}</span>
                    <div style="display:flex; gap:4px;">
                        <button type="submit" name="action" value="edit" class="btn-edit" title="حفظ التعديل"><i class="fas fa-save"></i></button>
                        <button type="submit" name="action" value="delete" class="btn-del" title="حذف تام من اللعبة والموقع"><i class="fas fa-trash"></i></button>
                    </div>
                </div>
                <div class="shop-row-inputs">
                    <input type="text" name="new_id" value="{{ item.id }}" placeholder="ID" title="تعديل معرف السلاح" required>
                    <input type="text" name="new_name" value="{{ item.name }}" placeholder="الاسم" title="تعديل اسم السلاح" required>
                    <input type="number" name="new_price" value="{{ item.price }}" placeholder="السعر" title="تعديل السعر" style="width:70px;" required>
                </div>
            </form>
            {% endfor %}
        </div>
    </div>
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
    s_price = request.form.get('shop_price')
    if s_id and s_name and s_price:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO shop (id, name, price, image) VALUES (?, ?, ?, '')",
                    (s_id, s_name, int(s_price)))
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
        # حذف تام من قاعدة البيانات ومن اللعبة
        cur.execute("DELETE FROM shop WHERE id = ?", (old_id,))
    elif action == "edit":
        new_id = request.form.get('new_id').strip()
        new_name = request.form.get('new_name').strip()
        new_price = int(request.form.get('new_price', 0))
        
        if old_id != new_id:
            cur.execute("DELETE FROM shop WHERE id = ?", (old_id,))
            cur.execute("INSERT OR REPLACE INTO shop (id, name, price, image) VALUES (?, ?, ?, '')",
                        (new_id, new_name, new_price))
        else:
            cur.execute("UPDATE shop SET name = ?, price = ? WHERE id = ?",
                        (new_name, new_price, old_id))
            
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_user', methods=['POST'])
def admin_update_user():
    target = request.form.get('target_username')
    action = request.form.get('action')
    money_change = int(request.form.get('money_change', 0))

    conn = get_db_connection()
    cur = conn.cursor()
    if action == "add_money":
        cur.execute("UPDATE players SET money = money + ? WHERE LOWER(username) = LOWER(?)", (money_change, target))
    elif action == "sub_money":
        cur.execute("UPDATE players SET money = MAX(0, money - ?) WHERE LOWER(username) = LOWER(?)", (money_change, target))
    elif action == "delete":
        cur.execute("DELETE FROM players WHERE LOWER(username) = LOWER(?)", (target,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
