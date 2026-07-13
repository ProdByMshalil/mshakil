from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import hashlib
import time

app = FastAPI()

SECRET_SALT = "MySuperSecretGameSalt2026"

# 🔑 بيانات لوحة التحكم الخاصة بك (الأدمن)
ADMIN_EMAIL = "ez9@gmail.com"
ADMIN_PASSWORD = "ez9password"

def run_query(query, params=()):
    conn = sqlite3.connect("game_data.db")
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    result = cursor.fetchall()
    conn.close()
    return result

# إنشاء الجداول
run_query("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)")
run_query("CREATE TABLE IF NOT EXISTS leaderboard (username TEXT PRIMARY KEY, score INTEGER)")

class UserAuth(BaseModel):
    username: str
    password: str

class ScoreSubmit(BaseModel):
    username: str
    score: int
    timestamp: int
    sign: str

class AdminLogin(BaseModel):
    email: str
    password: str

# 1️⃣ موقع تعريف اللعبة العادي (Landing Page)
@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <html>
        <head>
            <title>EZ9 Shooter | Official Website</title>
            <style>
                body { background-color: #0b0c10; color: #c5c6c7; font-family: sans-serif; text-align: center; padding: 50px; }
                h1 { color: #66fcf1; font-size: 50px; }
                p { font-size: 20px; color: #45f3ff; }
                .btn { background-color: #1f2833; color: #66fcf1; border: 2px solid #66fcf1; padding: 15px 30px; font-size: 18px; cursor: pointer; border-radius: 5px; text-decoration: none; }
            </style>
        </head>
        <body>
            <h1>EZ9 SHOOTER</h1>
            <p>موقع اللعبة الرسمي - السيرفر والدرع شغالين بنجاح!</p>
            <br><br>
            <a href="#" class="btn">تحميل اللعبة قريباً</a>
        </body>
    </html>
    """

# 2️⃣ صفحة التحكم السرية للمسؤول (/admin)
@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return """
    <html>
        <head>
            <title>لوحة تحكم المسؤول | EZ9</title>
            <style>
                body { background-color: #121212; color: white; font-family: sans-serif; direction: rtl; text-align: center; padding: 40px; }
                .box { background: #1e1e1e; max-width: 500px; margin: 0 auto; padding: 20px; border-radius: 10px; border: 1px solid #ff4545; }
                input { width: 80%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
                button { background: #ff4545; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; font-weight: bold; }
                table { width: 100%; margin-top: 20px; border-collapse: collapse; }
                th, td { border: 1px solid #333; padding: 10px; text-align: center; }
                th { background: #ff4545; }
                #dashboard { display: none; max-width: 700px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div id="login-box" class="box">
                <h2>🔒 تسجيل دخول المسؤول</h2>
                <input type="email" id="email" placeholder="البريد الإلكتروني (Gmail)"><br>
                <input type="password" id="password" placeholder="كلمة المرور"><br>
                <button onclick="loginAdmin()">دخول</button>
                <p id="err" style="color:red;"></p>
            </div>

            <div id="dashboard">
                <h2>🛡️ لوحة تحكم السيرفر (EZ9 Shield)</h2>
                <hr>
                <h3>👥 الحسابات المسجلة في اللعبة</h3>
                <table id="users-table"><tr><th>اسم المستخدم</th></tr></table>
                <br>
                <h3>🏆 لوحة الصدارة الحالية</h3>
                <table id="scores-table"><tr><th>اللاعب</th><th>السكور</th></tr></table>
            </div>

            <script>
                async function loginAdmin() {
                    let email = document.getElementById('email').value;
                    let password = document.getElementById('password').value;
                    
                    let res = await fetch('/admin/dashboard-data', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({email: email, password: password})
                    });
                    
                    if (res.status === 200) {
                        let data = await res.json();
                        document.getElementById('login-box').style.display = 'none';
                        document.getElementById('dashboard').style.display = 'block';
                        
                        // ملء جدول المستخدمين
                        let uTable = document.getElementById('users-table');
                        data.users.forEach(u => { uTable.innerHTML += `<tr><td>${u}</td></tr>`; });
                        
                        // ملء جدول السكورات
                        let sTable = document.getElementById('scores-table');
                        data.leaderboard.forEach(s => { sTable.innerHTML += `<tr><td>${s.username}</td><td>${s.score}</td></tr>`; });
                    } else {
                        document.getElementById('err').innerText = 'البيانات غلط يا معلم!';
                    }
                }
            </script>
        </body>
    </html>
    """

# الباب السري اللي بيجيب البيانات للوحة التحكم بعد التأكد من الباسورد
@app.post("/admin/dashboard-data")
def get_dashboard_data(admin: AdminLogin):
    if admin.email != ADMIN_EMAIL or admin.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Forbidden")
    
    db_users = run_query("SELECT username FROM users")
    db_scores = run_query("SELECT username, score FROM leaderboard ORDER BY score DESC")
    
    users_list = [row[0] for row in db_users]
    scores_list = [{"username": row[0], "score": row[1]} for row in db_scores]
    
    return {"users": users_list, "leaderboard": scores_list}

# باقي أبواب اللعبة (تسجيل، دخول، إرسال سكور)
@app.post("/register")
def register_user(user: UserAuth):
    pwd_hash = hashlib.sha256(user.password.encode()).hexdigest()
    try:
        run_query("INSERT INTO users (username, password_hash) VALUES (?, ?)", (user.username, pwd_hash))
        return {"status": "success"}
    except:
        raise HTTPException(status_code=400, detail="Taken")

@app.post("/login")
def login_user(user: UserAuth):
    pwd_hash = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = run_query("SELECT * FROM users WHERE username = ? AND password_hash = ?", (user.username, pwd_hash))
    if not db_user:
        raise HTTPException(status_code=401, detail="Error")
    return {"status": "success"}

@app.post("/submit_score")
def submit_score(data: ScoreSubmit):
    current_time = int(time.time())
    if abs(current_time - data.timestamp) > 5:
        raise HTTPException(status_code=403)
    if data.score > 1000:
        raise HTTPException(status_code=403)
    
    raw_string = f"{data.username}{data.score}{data.timestamp}{SECRET_SALT}"
    server_sign = hashlib.sha256(raw_string.encode()).hexdigest()
    if data.sign != server_sign:
        raise HTTPException(status_code=403)
    
    run_query("INSERT OR REPLACE INTO leaderboard (username, score) VALUES (?, ?)", (data.username, data.score))
    return {"status": "success"}
