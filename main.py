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
        ("AK47", "AK47", 30000, "https://i.imgur.com/7k1287B.png"),
        ("DESERT_EAGLE", "نصر صحراء", 30000, "https://i.imgur.com/384384Q.png")
    ]
    for item_id, name, price, img in default_items:
        cur.execute("INSERT OR IGNORE INTO shop (id, name, price, image) VALUES (?, ?, ?, ?)", (item_id, name, price, img))
    
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ══════════════════════════════════════════════════
# ⚡ الـ APIs الخاصة بالربط مع لعبة Godot
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
# 🖥️ لوحة التحكم بالتصميم الأسطوري الأصلي 100%
# ══════════════════════════════════════════════════

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة إدارة السيرفر - EZ9</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0b111a;
            --card-bg: #111a28;
            --input-bg: #0b1018;
            --border-color: #1e2d42;
            --text-color: #d1d5db;
            --accent-green: #00d285;
            --btn-red: #d9534f;
            --btn-blue: #0275d8;
            --gold: #f59e0b;
        }

        .light-theme {
            --bg-color: #f3f4f6;
            --card-bg: #ffffff;
            --input-bg: #e5e7eb;
            --border-color: #d1d5db;
            --text-color: #1f2937;
            --accent-green: #059669;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); padding: 12px; transition: 0.3s; }

        /* Top Header Layout */
        .top-header { display: flex; justify-content: space-between; align-items: stretch; gap: 15px; margin-bottom: 12px; }
        
        .header-left { display: flex; align-items: center; gap: 10px; }
        .time-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 8px 15px; min-width: 150px; }
        .time-card-title { font-size: 11px; color: var(--accent-green); display: flex; align-items: center; gap: 5px; }
        .time-clock { font-size: 16px; font-weight: bold; color: var(--accent-green); margin-top: 2px; }
        .time-date { font-size: 10px; color: #888; }

        .btn-top { border: none; padding: 8px 14px; border-radius: 5px; font-size: 12px; font-weight: bold; cursor: pointer; color: white; display: flex; align-items: center; gap: 6px; }
        .btn-logout { background: #d9383a; }
        .btn-mode { background: #233146; color: #fff; }

        .header-right h1 { font-size: 22px; color: var(--accent-green); font-weight: bold; display: flex; align-items: center; gap: 8px; }

        /* Stats Section */
        .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px; }
        .stat-box { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 12px; text-align: center; }
        .stat-box .title { font-size: 12px; color: #88a; margin-bottom: 4px; }
        .stat-box .value { font-size: 20px; font-weight: bold; }

        /* Main Container */
        .main-container { display: grid; grid-template-columns: 280px 1fr; gap: 12px; }
        @media(max-width: 900px) { .main-container { grid-template-columns: 1fr; } }

        /* Sidebar Styles */
        .sidebar-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 12px; margin-bottom: 12px; }
        .sidebar-card h3 { font-size: 13px; color: var(--accent-green); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
        
        form label { font-size: 11px; color: #aaa; display: block; margin-top: 6px; margin-bottom: 2px; }
        input[type="text"], input[type="number"] { width: 100%; background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-color); padding: 7px 10px; border-radius: 4px; font-size: 12px; }
        
        .btn-add-store { width: 100%; background: var(--accent-green); color: #000; border: none; padding: 8px; border-radius: 4px; font-weight: bold; margin-top: 10px; cursor: pointer; font-size: 12px; }
        
        /* Store Items List */
        .shop-list-item { display: flex; align-items: center; justify-content: space-between; background: var(--input-bg); border: 1px solid var(--border-color); padding: 6px 10px; border-radius: 5px; margin-bottom: 6px; }
        .shop-item-info { display: flex; align-items: center; gap: 8px; }
        .shop-item-badge { background: var(--accent-green); color: #000; font-size: 11px; font-weight: bold; padding: 2px 6px; border-radius: 3px; }
        .shop-item-img { width: 28px; height: 28px; object-fit: contain; }

        /* Main Content Area */
        .search-box { margin-bottom: 10px; position: relative; }
        .search-box input { padding-right: 30px; }
        .search-box i { position: absolute; right: 10px; top: 10px; color: #666; font-size: 12px; }

        .table-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 6px; padding: 12px; }
        .table-card h3 { font-size: 13px; color: var(--accent-green); margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }

        table { width: 100%; border-collapse: collapse; text-align: center; font-size: 12px; }
        th { color: var(--accent-green); padding: 8px; font-weight: normal; border-bottom: 1px solid var(--border-color); }
        td { padding: 8px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }

        .user-avatar { width: 26px; height: 26px; background: #1c2b3e; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; color: var(--accent-green); }
        .balance-badge { background: var(--gold); color: #000; font-weight: bold; padding: 3px 8px; border-radius: 4px; display: inline-block; }
        .weapons-subtext { font-size: 10px; color: #778; margin-top: 3px; display: block; }

        .btn-icon { border: none; width: 26px; height: 26px; border-radius: 4px; color: white; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; }
        .btn-danger { background: var(--btn-red); }
        .btn-success { background: var(--accent-green); color: #000; }
        .btn-primary { background: var(--btn-blue); }

        .money-control { display: flex; align-items: center; justify-content: center; gap: 4px; }
        .money-control input { width: 45px; text-align: center; padding: 4px; }
        .money-btn { border: none; width: 20px; height: 20px; border-radius: 3px; font-weight: bold; cursor: pointer; color: white; }
    </style>
</head>
<body>

    <!-- Upper Control Bar -->
    <div class="top-header">
        <div class="header-left">
            <div class="time-card">
                <div class="time-card-title"><i class="far fa-calendar-alt"></i> التاريخ والوقت</div>
                <div class="time-clock" id="live-clock">03:37:18 ص</div>
                <div class="time-date" id="live-date">الأحد، ٣٠ أغسطس ٢٠٢٦</div>
            </div>
            <button class="btn-top btn-logout"><i class="fas fa-sign-out-alt"></i> خروج</button>
            <button class="btn-top btn-mode" onclick="toggleTheme()"><i class="fas fa-moon"></i> الوضع الفاتح</button>
        </div>
        <div class="header-right">
            <h1><i class="fas fa-gamepad"></i> لوحة إدارة السيرفر EZ9</h1>
        </div>
    </div>

    <!-- Stats Bar -->
    <div class="stats-row">
        <div class="stat-box">
            <div class="title">إجمالي اللاعبين</div>
            <div class="value" style="color: var(--accent-green);">{{ players|length }}</div>
        </div>
        <div class="stat-box">
            <div class="title">إجمالي أموال اللعبة</div>
            <div class="value" style="color: var(--accent-green);">${{ players|sum(attribute='money') }}</div>
        </div>
        <div class="stat-box">
            <div class="title">الحسابات المحظورة</div>
            <div class="value" style="color: var(--btn-red);">{{ players|selectattr('is_banned', 'equalto', 1)|list|length }}</div>
        </div>
    </div>

    <!-- Main Grid -->
    <div class="main-container">
        
        <!-- Left Sidebar -->
        <div>
            <!-- Add Item Box -->
            <div class="sidebar-card">
                <h3><i class="fas fa-shopping-cart"></i> إضافة عنصر للمتجر عن بعد</h3>
                <form action="/admin/add_shop" method="POST">
                    <label>معرف العنصر (ID)</label>
                    <input type="text" name="shop_id" placeholder="مثال: DESERT_EAGLE" required>

                    <label>اسم السلاح</label>
                    <input type="text" name="shop_name" placeholder="مثال: نصر صحراء" required>

                    <label>رابط الصورة (URL)</label>
                    <input type="text" name="shop_image" value="https://example.com/gun.png">

                    <label>السعر ($)</label>
                    <input type="number" name="shop_price" value="400" required>

                    <button type="submit" class="btn-add-store">+ إضافة للمتجر</button>
                </form>
            </div>

            <!-- Current Store Box -->
            <div class="sidebar-card">
                <h3><i class="fas fa-store"></i> المتجر الحالي</h3>
                {% for item in shop %}
                <div class="shop-list-item">
                    <form action="/admin/delete_shop" method="POST" style="margin:0;">
                        <input type="hidden" name="shop_id" value="{{ item.id }}">
                        <button type="submit" class="btn-icon btn-danger" title="حذف العنصر"><i class="fas fa-trash"></i></button>
                    </form>
                    <div class="shop-item-info">
                        <span class="shop-item-badge">${{ item.price }}</span>
                        <span style="font-size: 12px; font-weight: bold;">{{ item.name }}</span>
                        {% if item.image %}
                        <img src="{{ item.image }}" class="shop-item-img" onerror="this.style.display='none'">
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Right Main Table Area -->
        <div>
            <!-- Search Input -->
            <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" id="search-input" onkeyup="filterUsers()" placeholder="ابحث عن لاعب بالاسم، البريد، أو تفاصيل السلاح...">
            </div>

            <!-- Table Card -->
            <div class="table-card">
                <h3><i class="fas fa-users"></i> قائمة الحسابات والتحكم الشامل</h3>
                <table id="users-table">
                    <thead>
                        <tr>
                            <th>الصورة</th>
                            <th>اسم المستخدم</th>
                            <th>البريد الإلكتروني</th>
                            <th>كلمة السر</th>
                            <th>الرصيد الحالي</th>
                            <th>تعديل الفلوس</th>
                            <th>رسالة الإدارة</th>
                            <th>إجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in players %}
                        <tr class="user-row">
                            <form action="/admin/update_user_full" method="POST">
                                <input type="hidden" name="target_username" value="{{ p.username }}">
                                
                                <td>
                                    <div class="user-avatar"><i class="fas fa-user"></i></div>
                                </td>
                                <td>
                                    <input type="text" name="new_username" value="{{ p.username }}" style="width: 80px; text-align: center;">
                                </td>
                                <td>
                                    <input type="text" name="new_email" value="{{ p.email or '0' }}" style="width: 70px; text-align: center;">
                                </td>
                                <td>
                                    <input type="text" name="new_password" value="{{ p.password }}" style="width: 60px; text-align: center;">
                                </td>
                                <td>
                                    <div class="balance-badge">${{ p.money }}</div>
                                    <span class="weapons-subtext">الأسلحة: {{ p.unlocked_weapons|replace('"', '')|replace('[', '')|replace(']', '') }}</span>
                                </td>
                                <td>
                                    <div class="money-control">
                                        <button type="submit" name="action" value="sub_money" class="money-btn" style="background:#d9383a;">-</button>
                                        <input type="number" name="money_change" value="0">
                                        <button type="submit" name="action" value="add_money" class="money-btn" style="background:var(--accent-green); color:#000;">+</button>
                                    </div>
                                </td>
                                <td>
                                    <input type="text" name="admin_message" value="{{ p.admin_message }}" placeholder="رسالة تنبيه..." style="width: 90px;">
                                </td>
                                <td>
                                    <div style="display: flex; gap: 4px; justify-content: center;">
                                        <button type="submit" name="action" value="delete_account" class="btn-icon btn-danger" title="حذف الحساب"><i class="fas fa-trash"></i></button>
                                        
                                        {% if p.is_banned == 1 %}
                                        <button type="submit" name="action" value="unban" class="btn-icon btn-primary" title="فك الحظر"><i class="fas fa-unlock"></i></button>
                                        {% else %}
                                        <button type="submit" name="action" value="save_and_ban" class="btn-icon btn-primary" title="حظر وتعديل"><i class="fas fa-lock"></i></button>
                                        {% endif %}
                                        
                                        <button type="submit" name="action" value="save_profile" class="btn-icon btn-success" title="حفظ"><i class="fas fa-check"></i></button>
                                    </div>
                                </td>
                            </form>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('live-clock').innerText = now.toLocaleTimeString('ar-EG');
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            document.getElementById('live-date').innerText = now.toLocaleDateString('ar-EG', options);
        }
        setInterval(updateClock, 1000);
        updateClock();

        function filterUsers() {
            let input = document.getElementById('search-input').value.toLowerCase();
            let rows = document.querySelectorAll('.user-row');
            rows.forEach(row => {
                let text = row.innerText.toLowerCase();
                let inputs = row.querySelectorAll('input');
                inputs.forEach(i => text += ' ' + i.value.toLowerCase());
                row.style.display = text.includes(input) ? '' : 'none';
            });
        }

        function toggleTheme() {
            document.body.classList.toggle('light-theme');
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

@app.route('/admin/delete_shop', methods=['POST'])
def delete_shop():
    s_id = request.form.get('shop_id').strip()
    if s_id:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM shop WHERE id = ?", (s_id,))
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
    elif action in ["save_profile", "save_and_ban", "unban"]:
        new_username = request.form.get('new_username').strip()
        new_email = request.form.get('new_email').strip()
        new_password = request.form.get('new_password').strip()
        admin_message = request.form.get('admin_message', '').strip()
        
        is_banned = 1 if action == "save_and_ban" else (0 if action == "unban" else None)

        if is_banned is not None:
            cur.execute("""
                UPDATE players 
                SET username = ?, email = ?, password = ?, admin_message = ?, is_banned = ? 
                WHERE LOWER(username) = LOWER(?)
            """, (new_username, new_email, new_password, admin_message, is_banned, target))
        else:
            cur.execute("""
                UPDATE players 
                SET username = ?, email = ?, password = ?, admin_message = ? 
                WHERE LOWER(username) = LOWER(?)
            """, (new_username, new_email, new_password, admin_message, target))

    conn.commit()
    conn.close()
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
