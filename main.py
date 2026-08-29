import os
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DATA_FILE = "players_data.json"

# ══════════════════════════════════════════════════
# 💾 إدارة البيانات (JSON Storage)
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
# ⚡ الـ Endpoints الخاصة بـ Godot API
# ══════════════════════════════════════════════════

# 1. إنشاء حساب جديد
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

    # الفحص عن تكرار اسم المستخدم أو البريد
    for p_name, p_data in players.items():
        if p_name.lower() == username.lower():
            return jsonify({"status": "error", "message": "اسم المستخدم مستخدم بالفعل"}), 400
        if email and p_data.get("email", "").lower() == email.lower():
            return jsonify({"status": "error", "message": "البريد الإلكتروني مستخدم بالفعل"}), 400

    # إنشاء اللاعب الجديد
    players[username] = {
        "username": username,
        "password": password,
        "email": email,
        "money": 1000,
        "is_banned": 0,
        "admin_message": "",
        "unlocked_weapons": ["Pistol"]
    }
    
    db["players"] = players
    save_data(db)

    return jsonify({"status": "success", "message": "تم إنشاء الحساب بنجاح"}), 201

# 2. تسجيل الدخول (يدعم البريد أو اسم المستخدم)
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
        "is_banned": 0,
        "unlocked_weapons": found_player.get("unlocked_weapons", [])
    }), 200

# ══════════════════════════════════════════════════
# 🖥️ لوحة التحكم الأدمن (Web Admin Dashboard)
# ══════════════════════════════════════════════════
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم باللاعبين</title>
    <style>
        body { font-family: sans-serif; background-color: #121212; color: #fff; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #1e1e1e; }
        th, td { border: 1px solid #333; padding: 12px; text-align: center; }
        th { background-color: #252525; }
        .banned { color: #ff5252; font-weight: bold; }
        .active { color: #4caf50; font-weight: bold; }
    </style>
</head>
<body>
    <h2>🎮 لوحة إدارة اللاعبين</h2>
    <table>
        <tr>
            <th>اسم المستخدم</th>
            <th>البريد الإلكتروني</th>
            <th>كلمة السر</th>
            <th>الرصيد</th>
            <th>الحالة</th>
        </tr>
        {% for uname, p in players.items() %}
        <tr>
            <td>{{ p.username }}</td>
            <td>{{ p.email or 'غ/م' }}</td>
            <td>{{ p.password }}</td>
            <td>{{ p.money }}</td>
            <td class="{{ 'banned' if p.is_banned else 'active' }}">
                {{ 'محظور' if p.is_banned else 'نشط' }}
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route('/admin', methods=['GET'])
def admin_panel():
    db = load_data()
    return render_template_string(HTML_TEMPLATE, players=db.get("players", {}))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
