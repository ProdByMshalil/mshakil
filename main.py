import os
import json
from flask import Flask, request, jsonify, render_template_string, redirect, url_for

app = Flask(__name__)
DATA_FILE = "players_data.json"

# ══════════════════════════════════════════════════
# 💾 إدارة البيانات
# ══════════════════════════════════════════════════
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"players": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"players": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ══════════════════════════════════════════════════
# ⚡ الـ Endpoints الخاصة بـ API
# ══════════════════════════════════════════════════

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    email = str(data.get('email', '')).strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "اسم المستخدم وكلمة السر مطلوبان"}), 400

    db = load_data()
    players = db.get("players", {})

    for p_name, p_data in players.items():
        if p_name.lower() == username.lower():
            return jsonify({"status": "error", "message": "اسم المستخدم مستخدم بالفعل"}), 400
        if email and p_data.get("email", "").lower() == email.lower():
            return jsonify({"status": "error", "message": "البريد الإلكتروني مستخدم بالفعل"}), 400

    players[username] = {
        "username": username,
        "password": password,
        "email": email,
        "money": 1000,
        "score": 0,
        "is_banned": 0,
        "admin_message": "",
        "unlocked_weapons": ["Pistol"]
    }
    
    db["players"] = players
    save_data(db)

    return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    user_input = str(data.get('username', '')).strip().lower()
    password = str(data.get('password', '')).strip()

    if not user_input or not password:
        return jsonify({"status": "error", "message": "يرجى إدخال اسم المستخدم وكلمة السر"}), 400

    db = load_data()
    players = db.get("players", {})
    found_player = None

    for uname, pdata in players.items():
        p_name = str(pdata.get("username", "")).strip().lower()
        p_email = str(pdata.get("email", "")).strip().lower()
        
        if user_input == p_name or user_input == p_email:
            found_player = pdata
            break

    if not found_player:
        return jsonify({"status": "error", "message": "الحساب غير موجود! تأكد من البيانات"}), 401

    if str(found_player.get("password", "")).strip() != password:
        return jsonify({"status": "error", "message": "كلمة السر غير صحيحة!"}), 401

    if found_player.get("is_banned", 0) == 1:
        msg = found_player.get("admin_message", "تم حظر حسابك من قبل الإدارة")
        return jsonify({"status": "error", "message": msg, "is_banned": 1}), 403

    return jsonify({
        "status": "success",
        "username": found_player["username"],
        "email": found_player.get("email", ""),
        "money": found_player.get("money", 0),
        "score": found_player.get("score", 0),
        "is_banned": 0,
        "unlocked_weapons": found_player.get("unlocked_weapons", ["Pistol"])
    }), 200


@app.route('/get_player/<username>', methods=['GET'])
def get_player(username):
    db = load_data()
    players = db.get("players", {})
    
    for uname, pdata in players.items():
        if uname.lower() == username.lower():
            return jsonify({"status": "success", "player": pdata}), 200
            
    return jsonify({"status": "error", "message": "اللاعب غير موجود"}), 404


@app.route('/update_player', methods=['POST'])
def update_player():
    data = request.json or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()

    db = load_data()
    players = db.get("players", {})

    player = None
    for uname, pdata in players.items():
        if uname.lower() == username.lower():
            player = pdata
            break

    if not player or str(player.get("password", "")).strip() != password:
        return jsonify({"status": "error", "message": "غير مصرح بالتعديل"}), 401

    if player.get("is_banned", 0) == 1:
        return jsonify({"status": "error", "message": "الحساب محظور", "is_banned": 1}), 403

    if "money" in data:
        player["money"] = int(data["money"])
    if "score" in data:
        player["score"] = int(data["score"])
    if "unlocked_weapons" in data and isinstance(data["unlocked_weapons"], list):
        player["unlocked_weapons"] = data["unlocked_weapons"]

    save_data(db)
    return jsonify({"status": "success", "message": "تم تحديث البيانات بنجاح", "player": player}), 200


# ══════════════════════════════════════════════════
# 🖥️ لوحة التحكم الأدمن التفاعلية (HTML)
# ══════════════════════════════════════════════════
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة إدارة مشروع اللعبة</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background-color: #0b132b; color: #ffffff; padding: 20px; }
        h1 { text-align: center; margin: 25px 0; color: #4cc9f0; font-size: 26px; }
        .card { background: #1c2541; border-radius: 12px; padding: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.4); max-width: 1200px; margin: 0 auto; overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; min-width: 900px; }
        th, td { padding: 12px 8px; text-align: center; border-bottom: 1px solid #3a506b; font-size: 14px; }
        th { background: #0b132b; color: #4cc9f0; font-weight: 600; }
        input[type="number"], input[type="text"] { background: #0b132b; border: 1px solid #3a506b; color: #fff; padding: 6px 8px; border-radius: 6px; text-align: center; font-size: 13px; }
        .inp-sm { width: 75px; }
        .inp-md { width: 120px; }
        .btn { padding: 6px 12px; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: bold; transition: 0.2s; color: white; }
        .btn-save { background: #3a86ff; }
        .btn-save:hover { background: #2563eb; }
        .btn-ban { background: #e63946; }
        .btn-ban:hover { background: #d62828; }
        .btn-unban { background: #38b000; }
        .btn-unban:hover { background: #2b9348; }
        .banned-row { background: rgba(230, 57, 70, 0.15); }
        .empty-msg { text-align: center; padding: 30px; color: #8d99ae; font-size: 16px; }
    </style>
</head>
<body>

    <h1>🎮 لوحة تحكم سيرفر اللعبة</h1>

    <div class="card">
        <table>
            <thead>
                <tr>
                    <th>اسم المستخدم</th>
                    <th>البريد الإلكتروني</th>
                    <th>كلمة السر</th>
                    <th>الرصيد ($)</th>
                    <th>السكور</th>
                    <th>الأسلحة المفتوحة</th>
                    <th>رسالة الحظر</th>
                    <th>الحالة / الإجراء</th>
                    <th>حفظ</th>
                </tr>
            </thead>
            <tbody>
                {% if players %}
                    {% for uname, p in players.items() %}
                    <tr class="{{ 'banned-row' if p.is_banned else '' }}">
                        <form action="/admin/update_user" method="POST">
                            <input type="hidden" name="target_username" value="{{ p.username }}">
                            <td><strong>{{ p.username }}</strong></td>
                            <td>{{ p.email or 'غ/م' }}</td>
                            <td><code>{{ p.password }}</code></td>
                            <td><input type="number" name="money" value="{{ p.money }}" class="inp-sm"></td>
                            <td><input type="number" name="score" value="{{ p.score or 0 }}" class="inp-sm"></td>
                            <td><input type="text" name="weapons" value="{{ (p.unlocked_weapons or []) | join(',') }}" class="inp-md"></td>
                            <td><input type="text" name="admin_message" value="{{ p.admin_message or '' }}" placeholder="سبب الحظر" class="inp-md"></td>
                            <td>
                                {% if p.is_banned %}
                                    <button type="submit" name="action" value="unban" class="btn btn-unban">فك الحظر</button>
                                {% else %}
                                    <button type="submit" name="action" value="ban" class="btn btn-ban">حظر</button>
                                {% endif %}
                            </td>
                            <td>
                                <button type="submit" name="action" value="save" class="btn btn-save">حفظ 💾</button>
                            </td>
                        </form>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr>
                        <td colspan="9" class="empty-msg">لا يوجد لاعبين مسجلين في قاعدة البيانات حتى الآن. قم بإنشاء حساب من اللعبة أولاً!</td>
                    </tr>
                {% endif %}
            </tbody>
        </table>
    </div>

</body>
</html>
"""

@app.route('/admin', methods=['GET'])
def admin_panel():
    db = load_data()
    return render_template_string(ADMIN_HTML, players=db.get("players", {}))


@app.route('/admin/update_user', methods=['POST'])
def admin_update_user():
    target = request.form.get('target_username')
    action = request.form.get('action')
    money = request.form.get('money')
    score = request.form.get('score')
    weapons_raw = request.form.get('weapons', '')
    admin_msg = request.form.get('admin_message', '')

    db = load_data()
    players = db.get("players", {})

    if target in players:
        p = players[target]
        if money is not None and money != '':
            p["money"] = int(money)
        if score is not None and score != '':
            p["score"] = int(score)
            
        if weapons_raw:
            p["unlocked_weapons"] = [w.strip() for w in weapons_raw.split(',') if w.strip()]
        
        p["admin_message"] = admin_msg

        if action == "ban":
            p["is_banned"] = 1
        elif action == "unban":
            p["is_banned"] = 0

        save_data(db)

    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
