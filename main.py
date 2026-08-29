from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "ez9_super_secret_admin_key"

# كلمة سر لوحة التحكم
ADMIN_PASSWORD = "admin"

# ملف التخزين المحلي للبانات
DATA_FILE = "players_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "players": {},
        "store_items": [
            {"id": "AK47", "name": "AK-47", "price": 500, "icon": "🔫"},
            {"id": "DESERT", "name": "Desert Eagle", "price": 300, "icon": "💥"}
        ]
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==================== API GAME ENDPOINTS ====================

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    avatar = data.get('avatar', '')

    if not username or not password:
        return jsonify({"status": "error", "message": "اسم المستخدم وكلمة السر مطلوبان"}), 400

    db = load_data()
    if username in db["players"]:
        return jsonify({"status": "error", "message": "اسم المستخدم مستخدم بالفعل"}), 400

    db["players"][username] = {
        "username": username,
        "email": email,
        "password": password,
        "money": 1000,
        "avatar": avatar,
        "is_banned": 0,
        "admin_message": "",
        "unlocked_weapons": ["PISTOL"],
        "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_data(db)
    return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    db = load_data()
    player = db["players"].get(username)

    if not player or player.get("password") != password:
        return jsonify({"status": "error", "message": "اسم المستخدم أو كلمة السر غير صحيحة"}), 401

    return jsonify({
        "status": "success",
        "username": player["username"],
        "email": player.get("email", ""),
        "money": player.get("money", 0),
        "is_banned": player.get("is_banned", 0),
        "admin_message": player.get("admin_message", ""),
        "unlocked_weapons": player.get("unlocked_weapons", [])
    }), 200

# 🛒 API شراء سلاح من داخل جودوت (يخصم الفلوس فوراً)
@app.route('/buy_weapon', methods=['POST'])
def buy_weapon():
    data = request.json or {}
    username = data.get('username', '').strip()
    item_id = data.get('item_id', '').strip()
    price = int(data.get('price', 0))

    db = load_data()
    player = db["players"].get(username)

    if not player:
        return jsonify({"status": "error", "message": "اللاعب غير موجود"}), 404

    current_money = player.get("money", 0)
    if current_money < price:
        return jsonify({"status": "error", "message": "الرصيد غير كافي"}), 400

    player["money"] = current_money - price
    if "unlocked_weapons" not in player:
        player["unlocked_weapons"] = []
    
    if item_id not in player["unlocked_weapons"]:
        player["unlocked_weapons"].append(item_id)

    save_data(db)
    return jsonify({
        "status": "success",
        "message": "تم الشراء بنجاح!",
        "new_money": player["money"],
        "unlocked_weapons": player["unlocked_weapons"]
    }), 200

# ==================== ADMIN DASHBOARD ====================

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم السيرفر - EZ9 Gaming</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e14; color: #e1e6ed; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .sidebar { background: #121721; min-height: 100vh; border-left: 1px solid #1f293d; padding: 20px; }
        .card-custom { background: #151c28; border: 1px solid #222d42; border-radius: 12px; }
        .neon-text { color: #00ffaa; text-shadow: 0 0 10px rgba(0,255,170,0.3); }
        .btn-neon { background: #00ffaa; color: #000; font-weight: bold; border: none; }
        .btn-neon:hover { background: #00cc88; color: #000; }
        .table-dark-custom { background: #151c28; color: #fff; }
        .table-dark-custom th { background: #1c2536; color: #00ffaa; border-bottom: 2px solid #2a374e; }
        .table-dark-custom td { border-bottom: 1px solid #222d42; vertical-align: middle; }
        .input-dark { background: #0b0e14; border: 1px solid #2a374e; color: #fff; }
        .input-dark:focus { background: #0f141f; color: #fff; border-color: #00ffaa; box-shadow: none; }
        .avatar-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #00ffaa; }
    </style>
</head>
<body>
<div class="container-fluid">
    <div class="row">
        <!-- Dashboard Main Content -->
        <div class="col-md-9 col-lg-9 p-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2><i class="fa-solid fa-gamepad neon-text me-2"></i> لوحة إدارة السيرفر وحسابات اللاعبين</h2>
                <a href="/admin/logout" class="btn btn-outline-danger btn-sm"><i class="fa-solid fa-right-from-bracket"></i> خروج</a>
            </div>

            <!-- Stats Row -->
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="card-custom p-3 text-center">
                        <small class="text-muted">إجمالي اللاعبين</small>
                        <h3 class="neon-text mt-1">{{ total_players }}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card-custom p-3 text-center">
                        <small class="text-muted">إجمالي أموال اللعبة</small>
                        <h3 class="text-warning mt-1">${{ total_money }}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card-custom p-3 text-center">
                        <small class="text-muted">الحسابات المحظورة</small>
                        <h3 class="text-danger mt-1">{{ banned_players }}</h3>
                    </div>
                </div>
            </div>

            <!-- Search Bar -->
            <div class="mb-3">
                <input type="text" id="search-input" onkeyup="filterPlayers()" placeholder="🔍 ابحث عن لاعب بالاسم أو البريد..." class="form-control input-dark">
            </div>

            <!-- Players Management Table -->
            <div class="card-custom p-3">
                <h5 class="mb-3 neon-text"><i class="fa-solid fa-users-gear me-2"></i> قائمة حسابات اللاعبين والتعديل</h5>
                <div class="table-responsive">
                    <table class="table table-dark-custom align-middle" id="players-table">
                        <thead>
                            <tr>
                                <th>الصورة</th>
                                <th>اسم المستخدم</th>
                                <th>البريد الإلكتروني</th>
                                <th>الرصيد الحالي</th>
                                <th>تعديل الفلوس (مبلغ + نوع)</th>
                                <th>رسالة الإدارة</th>
                                <th>الحالة / إجراءات</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for uname, p in players.items() %}
                            <tr>
                                <form action="/admin/update_player" method="POST">
                                    <input type="hidden" name="original_username" value="{{ uname }}">
                                    <td>
                                        {% if p.avatar %}
                                            <img src="{{ p.avatar }}" class="avatar-img">
                                        {% else %}
                                            <div class="avatar-img bg-secondary text-center lh-lg">👤</div>
                                        {% endif %}
                                    </td>
                                    <td>
                                        <input type="text" name="username" value="{{ p.username }}" class="form-control form-control-sm input-dark" style="min-width: 110px;">
                                    </td>
                                    <td>
                                        <input type="email" name="email" value="{{ p.get('email', '') }}" class="form-control form-control-sm input-dark" style="min-width: 130px;">
                                    </td>
                                    <td>
                                        <span class="badge bg-warning text-dark fs-6">${{ p.get('money', 0) }}</span>
                                        <br><small class="text-muted" style="font-size: 10px;">الأسلحة: {{ p.get('unlocked_weapons', [])|join(', ') }}</small>
                                    </td>
                                    <td>
                                        <div class="d-flex gap-1">
                                            <input type="number" name="money_amount" value="0" min="0" class="form-control form-control-sm input-dark" style="width: 80px;" placeholder="المبلغ">
                                            <select name="money_action" class="form-select form-select-sm input-dark" style="width: 95px;">
                                                <option value="add">➕ إضافة</option>
                                                <option value="subtract">➖ خصم</option>
                                                <option value="set">🎯 تعيين</option>
                                            </select>
                                        </div>
                                    </td>
                                    <td>
                                        <input type="text" name="admin_message" value="{{ p.get('admin_message', '') }}" placeholder="إرسال رسالة للاعب..." class="form-control form-control-sm input-dark" style="min-width: 130px;">
                                    </td>
                                    <td>
                                        <div class="d-flex align-items-center gap-1">
                                            {% if p.get('is_banned') == 1 %}
                                                <span class="badge bg-danger">محظور</span>
                                            {% else %}
                                                <span class="badge bg-success">نشط</span>
                                            {% endif %}
                                            <button type="submit" class="btn btn-neon btn-sm" title="حفظ"><i class="fa-solid fa-floppy-disk"></i></button>
                                            <a href="/admin/toggle_ban/{{ uname }}" class="btn btn-outline-warning btn-sm" title="حظر/فك حظر"><i class="fa-solid fa-ban"></i></a>
                                            <a href="/admin/delete_player/{{ uname }}" class="btn btn-outline-danger btn-sm" onclick="return confirm('حذف الحساب نهائياً؟')" title="حذف"><i class="fa-solid fa-trash"></i></a>
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

        <!-- Sidebar Right -->
        <div class="col-md-3 col-lg-3 sidebar">
            <!-- Date & Time Widget -->
            <div class="card-custom p-3 mb-4 text-center">
                <h6 class="text-muted mb-2"><i class="fa-regular fa-calendar-days text-info me-1"></i> التاريخ والوقت</h6>
                <div id="live-clock" class="fs-5 fw-bold neon-text">--:--:--</div>
                <small id="live-date" class="text-muted"></small>
            </div>

            <!-- Remote Store Management Widget -->
            <div class="card-custom p-3 mb-4">
                <h6 class="neon-text mb-3"><i class="fa-solid fa-cart-plus me-1"></i> إضافة عنصر للمتجر عن بُعد</h6>
                <form action="/admin/add_store_item" method="POST">
                    <div class="mb-2">
                        <label class="form-label small text-muted">معرّف العنصر (ID)</label>
                        <input type="text" name="item_id" placeholder="مثال: M416" class="form-control form-control-sm input-dark" required>
                    </div>
                    <div class="mb-2">
                        <label class="form-label small text-muted">اسم العنصر/السلاح</label>
                        <input type="text" name="item_name" placeholder="مثال: سلاح M416" class="form-control form-control-sm input-dark" required>
                    </div>
                    <div class="mb-2">
                        <label class="form-label small text-muted">السعر ($)</label>
                        <input type="number" name="price" placeholder="400" class="form-control form-control-sm input-dark" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label small text-muted">الأيقونة (Emoji)</label>
                        <input type="text" name="icon" value="🔫" class="form-control form-control-sm input-dark">
                    </div>
                    <button type="submit" class="btn btn-neon w-100 btn-sm"><i class="fa-solid fa-plus"></i> إضافة للمتجر فوراً</button>
                </form>
            </div>

            <!-- Current Store Items -->
            <div class="card-custom p-3">
                <h6 class="text-muted mb-3"><i class="fa-solid fa-store me-1"></i> عناصر المتجر الحالية</h6>
                <ul class="list-group list-group-flush bg-transparent">
                    {% for item in store_items %}
                    <li class="list-group-item bg-transparent border-bottom border-secondary d-flex justify-content-between align-items-center py-2 text-white">
                        <span>{{ item.icon }} {{ item.name }}</span>
                        <span class="badge bg-success">${{ item.price }}</span>
                    </li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </div>
</div>

<script>
    function updateClock() {
        const now = new Date();
        document.getElementById('live-clock').innerText = now.toLocaleTimeString('ar-EG');
        document.getElementById('live-date').innerText = now.toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }
    setInterval(updateClock, 1000);
    updateClock();

    function filterPlayers() {
        let input = document.getElementById('search-input').value.toLowerCase();
        let rows = document.querySelectorAll('#players-table tbody tr');
        rows.forEach(row => {
            let text = row.innerText.toLowerCase();
            row.style.display = text.includes(input) ? '' : 'none';
        });
    }
</script>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول - الإدارة</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <style>
        body { background-color: #0b0e14; color: #fff; height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { background: #151c28; border: 1px solid #222d42; border-radius: 16px; padding: 30px; width: 100%; max-width: 380px; }
        .neon-text { color: #00ffaa; }
        .input-dark { background: #0b0e14; border: 1px solid #2a374e; color: #fff; }
    </style>
</head>
<body>
<div class="login-card text-center">
    <h3 class="neon-text mb-4">🔐 دخول لوحة الإدارة</h3>
    {% if error %}<div class="alert alert-danger py-2 small">{{ error }}</div>{% endif %}
    <form method="POST">
        <div class="mb-3">
            <input type="password" name="password" placeholder="كلمة المرور" class="form-control input-dark" required>
        </div>
        <button type="submit" class="btn btn-success w-100 fw-bold" style="background: #00ffaa; color: #000; border: none;">دخول</button>
    </form>
</div>
</body>
</html>
"""

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template_string(LOGIN_HTML, error="كلمة المرور غير صحيحة!")
    return render_template_string(LOGIN_HTML)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    db = load_data()
    players = db.get("players", {})
    store_items = db.get("store_items", [])

    total_players = len(players)
    total_money = sum(p.get('money', 0) for p in players.values())
    banned_players = sum(1 for p in players.values() if p.get('is_banned') == 1)

    return render_template_string(
        HTML_LAYOUT,
        players=players,
        store_items=store_items,
        total_players=total_players,
        total_money=total_money,
        banned_players=banned_players
    )

@app.route('/admin/update_player', methods=['POST'])
def update_player():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    orig_uname = request.form.get('original_username')
    new_uname = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    
    money_amount = int(request.form.get('money_amount', 0))
    money_action = request.form.get('money_action', 'add')
    admin_msg = request.form.get('admin_message', '')

    db = load_data()
    if orig_uname in db["players"]:
        player = db["players"].pop(orig_uname)
        
        # حاسبة الفلوس الجديدة
        current_money = player.get("money", 0)
        if money_action == "add":
            player["money"] = current_money + money_amount
        elif money_action == "subtract":
            player["money"] = max(0, current_money - money_amount)
        elif money_action == "set":
            if money_amount > 0 or request.form.get('money_amount') == '0':
                player["money"] = money_amount

        player["username"] = new_uname
        player["email"] = email
        player["admin_message"] = admin_msg
        
        db["players"][new_uname] = player
        save_data(db)

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_ban/<username>')
def toggle_ban(username):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    db = load_data()
    if username in db["players"]:
        db["players"][username]["is_banned"] = 1 if db["players"][username].get("is_banned") == 0 else 0
        save_data(db)

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_player/<username>')
def delete_player(username):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    db = load_data()
    if username in db["players"]:
        del db["players"][username]
        save_data(db)

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_store_item', methods=['POST'])
def add_store_item():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    item_id = request.form.get('item_id', '').strip()
    item_name = request.form.get('item_name', '').strip()
    price = int(request.form.get('price', 0))
    icon = request.form.get('icon', '🔫').strip()

    db = load_data()
    if "store_items" not in db:
        db["store_items"] = []

    db["store_items"].append({
        "id": item_id,
        "name": item_name,
        "price": price,
        "icon": icon
    })
    save_data(db)

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
