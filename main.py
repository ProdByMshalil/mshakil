# مسارات لوحة تحكم الأدمن (أضفها لملف main.py)
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "12345":
            session['logged_in'] = True
            return "<h1>أهلاً بك في لوحة تحكم عزو</h1>"
        else:
            return "كلمة مرور خاطئة"
    
    if session.get('logged_in'):
        return "<h1>أهلاً بك في لوحة تحكم عزو</h1>"
    
    return """
    <h2>دخول الإدارة</h2>
    <form method='POST'>
        <input name='username' placeholder='اسم المستخدم'>
        <input type='password' name='password' placeholder='كلمة المرور'>
        <button type='submit'>دخول</button>
    </form>
    """
