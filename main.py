15/7/2026 - 7:38 ã - samsung SM-A13:
extends Control

# بما أنهم تحت Authscreen مباشرة، لا نكتب Panel/
@onready var username_input = $Emailinput    # إذا كانت هذه الخانة لاسم المستخدم
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

const SERVER_URL = "https://my-game-server-19lc.onrender.com"

# دالة زر الدخول
func _on_LoginButton_pressed():
    if not username_input or not password_input: return
    
    var data = {
        "username": username_input.text,
        "password": password_input.text
    }
    
    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري تسجيل الدخول..."
    http_request.request(SERVER_URL + "/login", headers, HTTPClient.METHOD_POST, json_query)

# دالة زر الانتقال لصفحة التسجيل
func _on_RegisterButton_pressed():
    # هنا سيتم الانتقال للمشهد الجديد الذي ستنشئه للتسجيل
    get_tree().change_scene_to_file("res://RegisterScreen.tscn")

func _on_request_completed(_result, _response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if status_label:
        status_label.text = str(response.get("message", "حدث خطأ"))
15/7/2026 - 7:48 ã - samsung SM-A13:
extends Control

# الربط المباشر مع العقد (أبناء Authscreen)
@onready var username_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

const SERVER_URL = "https://my-game-server-19lc.onrender.com"

func _ready():
    # التأكد من ربط الإشارة برمجياً لضمان عدم حدوث خطأ
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

# دالة زر الدخول
func _on_LoginButton_pressed():
    # تنظيف النصوص من الفراغات الزائدة
    var username = username_input.text.strip_edges()
    var password = password_input.text.strip_edges()
    
    if username == "" or password == "":
        status_label.text = "يرجى ملء جميع الحقول!"
        return
    
    var data = {
        "username": username,
        "password": password
    }
    
    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري تسجيل الدخول..."
    http_request.request(SERVER_URL + "/login", headers, HTTPClient.METHOD_POST, json_query)

# دالة الانتقال لصفحة التسجيل
func _on_RegisterButton_pressed():
    get_tree().change_scene_to_file("res://RegisterScreen.tscn")

# دالة استقبال الرد من السيرفر
func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    print("رد السيرفر: ", response) # لمراقبة الرد في المخرجات
    
    if response_code == 200:
        status_label.text = "تم الدخول بنجاح!"
        # هنا يمكنك الانتقال لشاشة اللعبة الرئيسية مستقبلاً
    else:
        status_label.text = str(response.get("message", "خطأ في الاتصال"))
15/7/2026 - 8:04 ã - samsung SM-A13:
extends Control

@onready var username_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

const SERVER_URL = "https://my-game-server-19lc.onrender.com"

func _on_LoginButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "password": password_input.text.strip_edges()
    }
    
    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري الدخول..."
    http_request.request(SERVER_URL + "/login", headers, HTTPClient.METHOD_POST, json_query)

func _on_RegisterButton_pressed():
    # الانتقال لصفحة التسجيل مباشرة
    get_tree().change_scene_to_file("res://RegisterScreen.tscn")

func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if response_code == 200:
        status_label.text = "تم الدخول بنجاح!"
    else:
        status_label.text = str(response.get("message", "خطأ في الدخول"))
15/7/2026 - 8:05 ã - samsung SM-A13:
extends Control

@onready var username_input = $Usernameinput
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var avatar_option = $OptionButton
@onready var avatar_display = $TextureRect
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

var avatar_paths = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    avatar_option.item_selected.connect(_on_avatar_selected)
    _on_avatar_selected(0)

func _on_avatar_selected(index):
    avatar_display.texture = load(avatar_paths[index])

func _on_RegisterButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": avatar_option.get_selected_id()
    }
    
    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري التسجيل..."
    http_request.request("https://my-game-server-19lc.onrender.com/register", headers, HTTPClient.METHOD_POST, json_query)

func _on_BackToLoginButton_pressed():
    get_tree().change_scene_to_file("res://LoginScreen.tscn")

func _on_request_completed(_result, response_code, _headers, body):
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل! عد لصفحة الدخول."
    else:
        status_label.text = "فشل التسجيل!"
15/7/2026 - 8:10 ã - samsung SM-A13:
extends Control

@onready var username_input = $Usernameinput
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var avatar_option = $OptionButton
@onready var avatar_display = $TextureRect
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

# مسارات الصور (تأكد أنها مطابقة لأسماء ملفاتك)
var avatar_paths = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # ربط إشارة تغيير الاختيار برمجياً
    avatar_option.item_selected.connect(_on_avatar_selected)
    # عرض الصورة الأولى عند بدء التشغيل
    _on_avatar_selected(0)
    
    # ربط الطلب إذا لم يكن مربوطاً
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

func _on_avatar_selected(index):
    if index >= 0 and index < avatar_paths.size():
        avatar_display.texture = load(avatar_paths[index])

func _on_RegisterButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": avatar_option.get_selected_id()
    }
    
    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري التسجيل..."
    http_request.request("https://my-game-server-19lc.onrender.com/register", headers, HTTPClient.METHOD_POST, json_query)

func _on_BackToLoginButton_pressed():
    get_tree().change_scene_to_file("res://LoginScreen.tscn")

func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل! عد لصفحة الدخول."
    else:
        status_label.text = str(response.get("message", "فشل التسجيل"))
15/7/2026 - 8:53 ã - samsung SM-A13 (Offline message):
extends Control

@onready var username_input = $Usernameinput
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var avatar_option = $OptionButton
@onready var avatar_display = $TextureRect
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

const SERVER_URL = "https://my-game-server-19lc.onrender.com"
var avatar_paths = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # ربط تغيير الصورة بالقائمة
    avatar_option.item_selected.connect(_on_avatar_selected)
    _on_avatar_selected(0)
    
    # ربط استقبال الرد من السيرفر
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

# دالة تغيير الصورة عند اختيارها
func _on_avatar_selected(index):
    if index < avatar_paths.size():
        avatar_display.texture = load(avatar_paths[index])

# دالة زر التسجيل
func _on_RegisterButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": avatar_option.get_selected_id()
    }
    
    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري إنشاء الحساب..."
    http_request.request(SERVER_URL + "/register", headers, HTTPClient.METHOD_POST, json_query)

# دالة استقبال الرد (وهنا يتم الانتقال لصفحة الدخول)
func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل بنجاح! جاري الانتقال..."
        
        # الانتظار ثانية ونصف حتى يقرأ اللاعب الرسالة
        await get_tree().create_timer(1.5).timeout 
        
        # الانتقال لصفحة الدخول
        get_tree().change_scene_to_file("res://LoginScreen.tscn")
    else:
        status_label.text = str(response.get("message", "فشل التسجيل"))
15/7/2026 - 9:16 ã - samsung SM-A13:
extends Control

# --- العقد (Nodes) ---
@onready var username_input = $Usernameinput
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

# --- الإعدادات ---
const SERVER_URL = "https://my-game-server-19lc.onrender.com"
var images = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # 1. ربط الـ OptionButton بالـ TextureRect لتغيير الصورة
    option_button.item_selected.connect(_on_image_selected)
    _on_image_selected(0) # عرض الصورة الأولى كافتراضي
    
    # 2. ربط الـ HTTPRequest لاستقبال رد السيرفر
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

# --- دالة تغيير الصورة ---
func _on_image_selected(index):
    if index < images.size():
        texture_rect.texture = load(images[index])

# --- دالة زر التسجيل ---
func _on_RegisterButton_pressed():
    var data = {
        "username": username_input
15/7/2026 - 9:23 ã - samsung SM-A13:
var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": option_button.get_selected_id()
    } # <--- تأكد أن هذا القوس موجود ومغلق!
15/7/2026 - 9:46 ã - samsung SM-A13:
extends Control

@onready var username_input = $Usernameinput
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

const SERVER_URL = "https://my-game-server-19lc.onrender.com"
var images = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # ربط اختيار الصورة
    option_button.item_selected.connect(_on_image_selected)
    _on_image_selected(0)
    
    # ربط استقبال الرد
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

func _on_image_selected(index):
    if index >= 0 and index < images.size():
        texture_rect.texture = load(images[index])

func _on_RegisterButton_pressed():
    # هنا التأكد من إغلاق الأقواس بشكل صحيح:
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": option_button.get_selected_id()
    } # <--- هذا القوس مهم جداً، تأكد أنه موجود!

    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري التسجيل..."
    http_request.request(SERVER_URL + "/register", headers, HTTPClient.METHOD_POST, json_query)

func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل بنجاح! انتقل للدخول."
        await get_tree().create_timer(1.5).timeout
        get_tree().change_scene_to_file("res://LoginScreen.tscn")
    else:
        status_label.text = str(response.get("message", "فشل التسجيل"))

func _on_BackToLoginButton_pressed():
    get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 9:49 ã - samsung SM-A13:
extends Control

# --- تعريف العقد (Nodes) ---
@onready var username_input = $Usernameinput
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

# --- إعدادات ---
const SERVER_URL = "https://my-game-server-19lc.onrender.com"
var images = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # 1. ربط الـ OptionButton بالـ TextureRect
    option_button.item_selected.connect(_on_image_selected)
    _on_image_selected(0)
    
    # 2. ربط الـ HTTPRequest
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

# --- دالة اختيار الصورة (التي سألت عنها) ---
func _on_image_selected(index):
    if index >= 0 and index < images.size():
        texture_rect.texture = load(images[index])

# --- دالة زر التسجيل ---
func _on_RegisterButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": option_button.get_selected_id()
    }

    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري التسجيل..."
    http_request.request(SERVER_URL + "/register", headers, HTTPClient.METHOD_POST, json_query)

# --- دالة استقبال الرد والانتقال ---
func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل! جاري الانتقال..."
        await get_tree().create_timer(1.5).timeout
        get_tree().change_scene_to_file("res://LoginScreen.tscn")
    else:
        status_label.text = str(response.get("message", "فشل التسجيل"))

# --- زر العودة للدخول ---
func _on_BackToLoginButton_pressed():
    get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 9:57 ã - samsung SM-A13:
extends Control

# تعريف العقد (تأكد من مطابقة الأسماء في الشجرة)
@onready var username_input = $Usernameinput
@onready var email_input = $Emailinpt
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var http_request = $AuthRequest

const SERVER_URL = "https://my-game-server-19lc.onrender.com"
var images = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # ربط اختيار الصورة
    option_button.item_selected.connect(_on_image_selected)
    _on_image_selected(0)
    
    # ربط استقبال الرد (يجب التأكد من وجود عقدة AuthRequest)
    if not http_request.request_completed.is_connected(_on_request_completed):
        http_request.request_completed.connect(_on_request_completed)

# دالة الربط بين القائمة والصورة
func _on_image_selected(index):
    if index >= 0 and index < images.size():
        texture_rect.texture = load(images[index])

# دالة زر التسجيل
func _on_RegisterButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": option_button.get_selected_id()
    }

    var json_query = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    status_label.text = "جاري التسجيل..."
    http_request.request(SERVER_URL + "/register", headers, HTTPClient.METHOD_POST, json_query)

# دالة استقبال الرد
func _on_request_completed(_result, response_code, _headers, body):
    var json = JSON.new()
    json.parse(body.get_string_from_utf8())
    var response = json.get_data()
    
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل بنجاح!"
        await get_tree().create_timer(1.5).timeout
        get_tree().change_scene_to_file("res://LoginScreen.tscn")
    else:
        status_label.text = str(response.get("message", "فشل التسجيل"))

func _on_BackToLoginButto_pressed():
    get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 10:01 ã - samsung SM-A13:
extends Control

# تعريف العقد (ملاحظة: الأسماء مطابقة لما هو موجود في شجرة المشهد عندك)
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var username_input = $Usernameinput
@onready var email_input = $Emailinpt
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var http_request = $AuthRequest

# قائمة الصور (تأكد أن هذه الملفات موجودة فعلاً في مجلد المشروع)
var images = ["res://ak47_1.png", "res://ak47_2.png"]

func _ready():
    # 1. الربط البرمجي بين القائمة ودالة تغيير الصورة
    option_button.item_selected.connect(_on_image_selected)
    
    # 2. عرض أول صورة عند فتح الصفحة
    _on_image_selected(0)
    
    # ربط السيرفر
    if http_request:
        http_request.request_completed.connect(_on_request_completed)

# الدالة التي تربط اختيار القائمة بالـ TextureRect
func _on_image_selected(index):
    # التأكد أن الرقم موجود في القائمة لتجنب الأخطاء
    if index >= 0 and index < images.size():
        # تغيير صورة الـ TextureRect بناءً على الاختيار
        texture_rect.texture = load(images[index])

# دالة التسجيل (مختصرة)
func _on_RegisterButton_pressed():
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": option_button.get_selected_id()
    }
    var json_query = JSON.stringify(data)
    http_request.request("https://my-game-server-19lc.onrender.com/register", ["Content-Type: application/json"], HTTPClient.METHOD_POST, json_query)

func _on_request_completed(_result, response_code, _headers, body):
    if response_code == 200 or response_code == 201:
        status_label.text = "تم التسجيل!"
    else:
        status_label.text = "فشل التسجيل"
15/7/2026 - 10:27 ã - samsung SM-A13:
extends Control

# تعريف العقد (تأكد أن الأسماء مطابقة تماماً في الشجرة)
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var status_label = $StatusLabel  # تأكد من اسم العقدة هنا
@onready var auth_request = $AuthRequest

var images = [
    "res://ak47_1.png",
    "res://sword_2.png",
    "res://shield_3.png"
]

func _ready():
    # ربط الإشارة برمجياً فقط
    option_button.item_selected.connect(_on_image_selected)
    
    # اختبار الـ Label (تأكد أن النص سيظهر عند بدء اللعبة)
    status_label.text = "مستعد للتسجيل..."
    status_label.modulate = Color.WHITE

func _on_image_selected(index):
    if index >= 0 and index < images.size():
        texture_rect.texture = load(images[index])
        texture_rect.custom_minimum_size = Vector2(100, 100)

func _on_register_button_pressed():
    # هذا الكود يُفترض أن يُستدعى عند ضغط زر التسجيل
    status_label.text = "جاري الاتصال بالسيرفر..."
    # هنا تكملة كود إرسال البيانات (HTTPRequest)

func _on_auth_request_request_completed(result, response_code, headers, body):
    # استقبال رد السيرفر
    if response_code == 200:
        status_label.text = "تم التسجيل بنجاح!"
        status_label.modulate = Color.GREEN
    else:
        status_label.text = "حدث خطأ: كود " + str(response_code)
        status_label.modulate = Color.RED
15/7/2026 - 10:29 ã - samsung SM-A13:
extends Control

# تعريف العقد (تأكد من مطابقة الأسماء في الشجرة)
@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
    "res://ak47_1.png",
    "res://sword_2.png",
    "res://shield_3.png"
]

func _ready():
    # إعداد القائمة
    option_button.add_item("AK47", 0)
    option_button.add_item("Sword", 1)
    option_button.add_item("Shield", 2)
    
    # ربط الإشارات برمجياً (تجنب تكرار الربط في الـ Editor)
    if not option_button.item_selected.is_connected(_on_image_selected):
        option_button.item_selected.connect(_on_image_selected)
    
    # ربط إشارات الأزرار
    $RegisterButton.pressed.connect(_on_register_button_pressed)
    $BackToLoginButton.pressed.connect(_on_back_to_login_pressed)
    
    # تهيئة أول صورة والرسالة
    _on_image_selected(0)
    status_label.text = "أدخل بياناتك للتسجيل"

func _on_image_selected(index):
    if index >= 0 and index < images.size():
        texture_rect.texture = load(images[index])
        texture_rect.custom_minimum_size = Vector2(100, 100)

func _on_register_button_pressed():
    status_label.text = "جاري التسجيل..."
    status_label.modulate = Color.YELLOW
    
    # تحضير البيانات
    var data = {
        "username": username_input.text.strip_edges(),
        "email": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges(),
        "avatar_id": option_button.get_selected_id()
    }
    
    # إرسال الطلب (استخدم المسار الصحيح للسيرفر الخاص بك)
    var json_data = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    auth_request.request("http://your-server-url.com/register", headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
    var response = JSON.parse_string(body.get_string_from_utf8())
    
    if response_code == 200:
        status_label.text = "تم التسجيل بنجاح! جاري الانتقال..."
        status_label.modulate = Color.GREEN
        # هنا يمكنك إضافة كود الانتقال لصفحة أخرى
    else:
        status_label.text = "خطأ في التسجيل: كود " + str(response_code)
        status_label.modulate = Color.RED

func _on_back_to_login_pressed():
    # الانتقال لصفحة الدخول (تأكد من المسار الصحيح للمشهد)
    get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 10:36 ã - samsung SM-A13:
extends Control

# تعريف العقد (تأكد أن أسماء العقد في الشجرة تطابق هذه الأسماء)
@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
	"res://ak47_1.png",
	"res://sword_2.png",
	"res://shield_3.png"
]

func _ready():
	# إعداد القائمة
	option_button.clear() # مسح أي خيارات قديمة
	option_button.add_item("AK47", 0)
	option_button.add_item("Sword", 1)
	option_button.add_item("Shield", 2)
	
	# ربط الإشارات برمجياً
	if not option_button.item_selected.is_connected(_on_image_selected):
		option_button.item_selected.connect(_on_image_selected)
	
	$RegisterButton.pressed.connect(_on_register_button_pressed)
	$BackToLoginButton.pressed.connect(_on_back_to_login_pressed)
	
	# تهيئة أولية
	_on_image_selected(0)
	status_label.text = "أدخل بياناتك للتسجيل"

# دالة تغيير الصورة
func _on_image_selected(index):
	if index >= 0 and index < images.size():
		texture_rect.texture = load(images[index])
		texture_rect.custom_minimum_size = Vector2(100, 100)
		texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED

# دالة زر التسجيل
func _on_register_button_pressed():
	status_label.text = "جاري التسجيل..."
	status_label.modulate = Color.YELLOW
	# كود إرسال البيانات للسيرفر يوضع هنا

# دالة زر الرجوع (المسؤولة عن الخطأ الذي ظهر لك)
func _on_back_to_login_pressed():
	get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 10:42 ã - samsung SM-A13:
extends Control

@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
	"res://ak47_1.png",
	"res://sword_2.png",
	"res://shield_3.png"
]

func _ready():
	# تنظيف الخيارات وإعادة إضافتها
	option_button.clear()
	option_button.add_item("AK47", 0)
	option_button.add_item("Sword", 1)
	option_button.add_item("Shield", 2)
	
	# الربط البرمجي (تأكد أن الربط في الـ Editor مفصول)
	if not option_button.item_selected.is_connected(_on_image_selected):
		option_button.item_selected.connect(_on_image_selected)
	
	if not $RegisterButton.pressed.is_connected(_on_register_button_pressed):
		$RegisterButton.pressed.connect(_on_register_button_pressed)
		
	if not $BackToLoginButton.pressed.is_connected(_on_back_to_login_pressed):
		$BackToLoginButton.pressed.connect(_on_back_to_login_pressed)
		
	_on_image_selected(0)

func _on_image_selected(index):
	if index >= 0 and index < images.size():
		texture_rect.texture = load(images[index])
		# لضمان عدم مط الصورة
		texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		texture_rect.custom_minimum_size = Vector2(100, 100)

func _on_register_button_pressed():
	status_label.text = "جاري التسجيل..."
	# أكمل هنا كود الـ HTTPRequest

func _on_back_to_login_pressed():
	get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 10:45 ã - samsung SM-A13:
extends Control

@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
	"res://ak47_1.png",
	"res://sword_2.png",
	"res://shield_3.png"
]

func _ready():
	# تنظيف وتهيئة الواجهة
	status_label.text = "مرحباً! أدخل بياناتك"
	status_label.modulate = Color.WHITE
	
	# التأكد من ربط الإشارات برمجياً
	if not option_button.item_selected.is_connected(_on_image_selected):
		option_button.item_selected.connect(_on_image_selected)
	
	if not $RegisterButton.pressed.is_connected(_on_register_button_pressed):
		$RegisterButton.pressed.connect(_on_register_button_pressed)
	
	# ربط إشارة انتهاء الطلب (مهم جداً لحل مشكلة التعليق)
	if not auth_request.request_completed.is_connected(_on_auth_request_request_completed):
		auth_request.request_completed.connect(_on_auth_request_request_completed)

func _on_register_button_pressed():
	# تحديث الحالة فور الضغط
	status_label.text = "جاري التسجيل..."
	status_label.modulate = Color.YELLOW
	
	var data = {
		"username": username_input.text,
		"email": email_input.text,
		"password": password_input.text,
		"avatar_id": option_button.selected
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	auth_request.request("http://your-server-url.com/register", headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	# دالة الرد التي ستخبر المستخدم بالنتيجة
	if response_code == 200:
		status_label.text = "نجاح: تم إنشاء الحساب!"
		status_label.modulate = Color.GREEN
	else:
		status_label.text = "خطأ: حاول مرة أخرى (كود " + str(response_code) + ")"
		status_label.modulate = Color.RED

func _on_image_selected(index):
	if index >= 0 and index < images.size():
		texture_rect.texture = load(images[index])
15/7/2026 - 10:47 ã - samsung SM-A13:
extends Control

# تعريف العقد - تأكد أن الأسماء في شجرة المشهد تطابق هذه تماماً
@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
	"res://ak47_1.png",
	"res://sword_2.png",
	"res://shield_3.png"
]

func _ready():
	# إعداد القائمة
	option_button.clear()
	option_button.add_item("AK47", 0)
	option_button.add_item("Sword", 1)
	option_button.add_item("Shield", 2)
	
	# ربط الإشارات برمجياً (تأكد أنك حذفت أي ربط قديم من واجهة Editor)
	if not option_button.item_selected.is_connected(_on_image_selected):
		option_button.item_selected.connect(_on_image_selected)
	
	if not $RegisterButton.pressed.is_connected(_on_register_button_pressed):
		$RegisterButton.pressed.connect(_on_register_button_pressed)
		
	if not $BackToLoginButton.pressed.is_connected(_on_back_to_login_pressed):
		$BackToLoginButton.pressed.connect(_on_back_to_login_pressed)
		
	if not auth_request.request_completed.is_connected(_on_auth_request_request_completed):
		auth_request.request_completed.connect(_on_auth_request_request_completed)
	
	# تهيئة أولية
	_on_image_selected(0)
	status_label.text = "مرحباً! أدخل بياناتك"
	status_label.modulate = Color.WHITE

func _on_image_selected(index):
	if index >= 0 and index < images.size():
		texture_rect.texture = load(images[index])
		# إعدادات لضبط مقاس الصورة ومنع المط
		texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		texture_rect.custom_minimum_size = Vector2(100, 100)

func _on_register_button_pressed():
	status_label.text = "جاري التسجيل..."
	status_label.modulate = Color.YELLOW
	
	var data = {
		"username": username_input.text,
		"email": email_input.text,
		"password": password_input.text,
		"avatar_id": option_button.selected
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	auth_request.request("http://your-server-url.com/register", headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	if response_code == 200:
		status_label.text = "نجاح: تم إنشاء الحساب!"
		status_label.modulate = Color.GREEN
	else:
		status_label.text = "خطأ: حاول مرة أخرى (كود " + str(response_code) + ")"
		status_label.modulate = Color.RED

func _on_back_to_login_pressed():
	# تأكد أن اسم مشهد الدخول هو LoginScreen.tscn في مجلد المشروع
	get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 10:50 ã - samsung SM-A13:
extends Control

@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
	"res://ak47_1.png",
	"res://sword_2.png",
	"res://shield_3.png"
]

func _ready():
	# 1. إعداد القائمة
	option_button.clear()
	option_button.add_item("AK47", 0)
	option_button.add_item("Sword", 1)
	option_button.add_item("Shield", 2)
	
	# 2. ربط الإشارات برمجياً
	if not option_button.item_selected.is_connected(_on_image_selected):
		option_button.item_selected.connect(_on_image_selected)
	
	if not $RegisterButton.pressed.is_connected(_on_register_button_pressed):
		$RegisterButton.pressed.connect(_on_register_button_pressed)
		
	if not $BackToLoginButton.pressed.is_connected(_on_back_to_login_pressed):
		$BackToLoginButton.pressed.connect(_on_back_to_login_pressed)
		
	if not auth_request.request_completed.is_connected(_on_auth_request_request_completed):
		auth_request.request_completed.connect(_on_auth_request_request_completed)
	
	_on_image_selected(0)
	status_label.text = "مرحباً! أدخل بياناتك"
	status_label.modulate = Color.WHITE

func _on_image_selected(index):
	if index >= 0 and index < images.size():
		texture_rect.texture = load(images[index])
		texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		texture_rect.custom_minimum_size = Vector2(100, 100)

func _on_register_button_pressed():
	# التحقق من البيانات قبل الإرسال
	if username_input.text == "" or email_input.text == "" or password_input.text == "":
		status_label.text = "خطأ: جميع الحقول مطلوبة!"
		status_label.modulate = Color.RED
		return

	status_label.text = "جاري التسجيل..."
	status_label.modulate = Color.YELLOW
	
	var data = {
		"username": username_input.text,
		"email": email_input.text,
		"password": password_input.text,
		"avatar_id": option_button.selected
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	# تأكد من وضع رابط السيرفر الصحيح هنا
	auth_request.request("http://your-server-url.com/register", headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	var response_text = body.get_string_from_utf8()
	
	if response_code == 200:
		# افتراضاً أن السيرفر يرد بـ 'success' عند النجاح
		if "success" in response_text.to_lower():
			status_label.text = "نجاح: تم إنشاء الحساب!"
			status_label.modulate = Color.GREEN
		else:
			status_label.text = "خطأ من السيرفر: " + response_text
			status_label.modulate = Color.RED
	else:
		status_label.text = "فشل الاتصال: كود " + str(response_code)
		status_label.modulate = Color.RED

func _on_back_to_login_pressed():
	get_tree().change_scene_to_file("res://LoginScreen.tscn")
15/7/2026 - 10:54 ã - samsung SM-A13:
https://my-game-server-19lc.onrender.com/admin/dashboard
5:34 Õ - samsung SM-A13:
extends Control

@onready var username_input = $UsernameInput
@onready var email_input = $EmailInput
@onready var password_input = $PasswordInput
@onready var status_label = $StatusLabel
@onready var option_button = $OptionButton
@onready var texture_rect = $TextureRect
@onready var auth_request = $AuthRequest

var images = [
	"res://ak47_1.png",
	"res://sword_2.png",
	"res://shield_3.png"
]

func _ready():
	# 1. إعداد القائمة والصور في الواجهة
	option_button.clear()
	option_button.add_item("AK47", 0)
	option_button.add_item("Sword", 1)
	option_button.add_item("Shield", 2)
	
	# 2. ربط الإشارات برمجياً
	if not option_button.item_selected.is_connected(_on_image_selected):
		option_button.item_selected.connect(_on_image_selected)
	
	if not $RegisterButton.pressed.is_connected(_on_register_button_pressed):
		$RegisterButton.pressed.connect(_on_register_button_pressed)
		
	if not $BackToLoginButton.pressed.is_connected(_on_back_to_login_pressed):
		$BackToLoginButton.pressed.connect(_on_back_to_login_pressed)
		
	if not auth_request.request_completed.is_connected(_on_auth_request_request_completed):
		auth_request.request_completed.connect(_on_auth_request_request_completed)
	
	_on_image_selected(0)
	status_label.text = "مرحباً! أدخل بياناتك"
	status_label.modulate = Color.WHITE

func _on_image_selected(index):
	if index >= 0 and index < images.size():
		texture_rect.texture = load(images[index])
		texture_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		texture_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		texture_rect.custom_minimum_size = Vector2(100, 100)

func _on_register_button_pressed():
	# التحقق من أن الحقول ليست فارغة
	if username_input.text.strip_edges() == "" or email_input.text.strip_edges() == "" or password_input.text.strip_edges() == "":
		status_label.text = "خطأ: جميع الحقول مطلوبة!"
		status_label.modulate = Color.RED
		return

	status_label.text = "جاري التسجيل..."
	status_label.modulate = Color.YELLOW
	
	# تجهيز البيانات للسيرفر (بدون الصورة لأن السيرفر لا يدعمها حالياً)
	var data = {
		"username": username_input.text.strip_edges(),
		"email": email_input.text.strip_edges(),
		"password": password_input.text.strip_edges()
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	
	# الرابط مع إضافة /register
	var url = "https://my-game-server-19lc.onrender.com/register"
	auth_request.request(url, headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	# إذا لم يكن هناك رد إطلاقاً
	if body == null:
		status_label.text = "خطأ: لم يتم الاتصال بالسيرفر!"
		status_label.modulate = Color.RED
		return
		
	var response_text = body.get_string_from_utf8()
	
	# طباعة الرد في الـ Output لمعرفة ما يحدث خلف الكواليس
	print("كود السيرفر: ", response_code)
	print("رد السيرفر: ", response_text)
	
	if response_code == 200 or response_code == 201:
		status_label.text = "نجاح: تم إنشاء الحساب!"
		status_label.modulate = Color.GREEN
		# يمكنك لاحقاً هنا حفظ حالة الدخول والانتقال للعبة
	else:
		# أخذنا أول 30 حرف فقط من الخطأ عشان ما يخرب شكل الـ Label إذا كان HTML
		status_label.text = "فشل التسجيل (كود " + str(response_code) + ")"
		status_label.modulate = Color.RED

func _on_back_to_login_pressed():
	get_tree().change_scene_to_file("res://LoginScreen.tscn")
5:43 Õ - samsung SM-A13:
extends Control

# المسارات الصحيحة (خارج الـ Panel)
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var auth_request = $AuthRequest

func _ready():
	# ربط الأزرار
	if not $LoginButton.pressed.is_connected(_on_login_button_pressed):
		$LoginButton.pressed.connect(_on_login_button_pressed)
		
	if not $RegisterButton.pressed.is_connected(_on_register_button_pressed):
		$RegisterButton.pressed.connect(_on_register_button_pressed)
		
	if not auth_request.request_completed.is_connected(_on_auth_request_request_completed):
		auth_request.request_completed.connect(_on_auth_request_request_completed)
		
	status_label.text = "أدخل الإيميل والباسوورد"
	status_label.modulate = Color.WHITE

func _on_login_button_pressed():
	if email_input.text.strip_edges() == "" or password_input.text.strip_edges() == "":
		status_label.text = "خطأ: أدخل البيانات أولاً!"
		status_label.modulate = Color.RED
		return

	status_label.text = "جاري تسجيل الدخول..."
	status_label.modulate = Color.YELLOW
	
	# إرسال الإيميل والباسوورد فقط كما طلبت
	var data = {
		"email": email_input.text.strip_edges(),
		"password": password_input.text.strip_edges()
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	
	var url = "https://my-game-server-19lc.onrender.com/login"
	auth_request.request(url, headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	if body == null:
		status_label.text = "خطأ في الاتصال بالسيرفر!"
		status_label.modulate = Color.RED
		return
		
	var response_text = body.get_string_from_utf8()
	print("رد السيرفر: ", response_text) # عشان نشوف السيرفر بعت إيه في الـ Output
	
	if response_code == 200 or response_code == 201:
		# محاولة تحويل رد السيرفر إلى قاموس (Dictionary) لقراءة الاسم
		var response_dict = JSON.parse_string(response_text)
		
		var user_name = "يا بطل" # اسم افتراضي لو السيرفر مبعتش الاسم
		
		# إذا كان الرد سليم وفيه كلمة username، نأخذها
		if typeof(response_dict) == TYPE_DICTIONARY and response_dict.has("username"):
			user_name = response_dict["username"]
			
		status_label.text = "مرحباً يا " + user_name + "!"
		status_label.modulate = Color.GREEN
		
	else:
		status_label.text = "خطأ: الإيميل أو كلمة المرور غير صحيحة"
		status_label.modulate = Color.RED

func _on_register_button_pressed():
	get_tree().change_scene_to_file("res://RegisterScreen.tscn")
5:50 Õ - samsung SM-A13:
# إعداد البيانات
	var data = {
		# السيرفر يبحث عن username، لذلك نرسل النص بهذا المفتاح
		"username": email_input.text.strip_edges(), 
		"password": password_input.text.strip_edges()
	}
5:55 Õ - samsung SM-A13:
func _on_auth_request_request_completed(_result, response_code, _headers, body):
	if body == null:
		status_label.text = "خطأ في الاتصال بالسيرفر!"
		status_label.modulate = Color.RED
		return
		
	if response_code == 200 or response_code == 201:
		# هنا نأخذ الإيميل الذي كتبه المستخدم في خانة الإدخال
		var user_email = email_input.text
		
		# نعرض الإيميل في رسالة الترحيب
		status_label.text = "مرحباً يا " + user_email + "!"
		status_label.modulate = Color.GREEN
		
	else:
		status_label.text = "خطأ: الإيميل أو كلمة المرور غير صحيحة"
		status_label.modulate = Color.RED
5:58 Õ - samsung SM-A13:
func _on_login_button_pressed():
    var data = {
        "username": email_input.text.strip_edges(), # نرسل المدخل كـ username
        "password": password_input.text.strip_edges()
    }
    
    var json_data = JSON.stringify(data)
    print("إلى السيرفر: ", json_data) # <--- هذا السطر هو الأهم!
    
    var headers = ["Content-Type: application/json"]
    var url = "https://my-game-server-19lc.onrender.com/login"
    auth_request.request(url, headers, HTTPClient.METHOD_POST, json_data)
5:59 Õ - samsung SM-A13:
extends Control

@onready var email_input = $Emailinput    # خانة اسم المستخدم
@onready var password_input = $Passwordinput # خانة الباسورد
@onready var status_label = $StatusLabel
@onready var auth_request = $AuthRequest

func _ready():
	if not $LoginButton.pressed.is_connected(_on_login_button_pressed):
		$LoginButton.pressed.connect(_on_login_button_pressed)
	
	status_label.text = "أدخل بيانات الدخول"
	status_label.modulate = Color.WHITE

func _on_login_button_pressed():
	if email_input.text.strip_edges() == "" or password_input.text.strip_edges() == "":
		status_label.text = "خطأ: أدخل البيانات أولاً!"
		status_label.modulate = Color.RED
		return

	status_label.text = "جاري الاتصال..."
	status_label.modulate = Color.YELLOW
	
	# البيانات التي يتوقعها سيرفرك (استخدام username بناءً على نجاحك السابق)
	var data = {
		"username": email_input.text.strip_edges(),
		"password": password_input.text.strip_edges()
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	
	# الرابط الرئيسي فقط كما اكتشفت
	var url = "https://my-game-server-19lc.onrender.com/"
	
	auth_request.request(url, headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	if body == null:
		status_label.text = "خطأ في الاتصال!"
		return
		
	var response_text = body.get_string_from_utf8()
	
	if response_code == 200:
		# نجاح الدخول - نعرض اسم المستخدم الذي دخل به
		status_label.text = "مرحباً يا " + email_input.text.strip_edges() + "!"
		status_label.modulate = Color.GREEN
		
		# هنا يمكنك إضافة الانتقال لمشهد اللعبة بعد ثانية
		# await get_tree().create_timer(1.0).timeout
		# get_tree().change_scene_to_file("res://MainGame.tscn")
	else:
		# في حال فشل الدخول
		status_label.text = "خطأ: تأكد من البيانات"
		status_label.modulate = Color.RED
6:01 Õ - samsung SM-A13:
extends Control

# تعريف العقد (تأكد أن أسماء العقد في شجرة المشهد تطابق هذه)
@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var auth_request = $AuthRequest
@onready var login_button = $LoginButton
@onready var register_button = $RegisterButton

func _ready():
    # ربط الإشارات برمجياً (هذا يغنيك عن ربطها من المحرر)
    # تأكد من حذف أي ربط قديم في تبويب Node في المحرر لتجنب التكرار
    login_button.pressed.connect(_on_login_button_pressed)
    register_button.pressed.connect(_on_register_button_pressed)
    auth_request.request_completed.connect(_on_auth_request_request_completed)
    
    status_label.text = "مرحباً! أدخل بياناتك"
    status_label.modulate = Color.WHITE

func _on_login_button_pressed():
    if email_input.text.strip_edges() == "" or password_input.text.strip_edges() == "":
        status_label.text = "خطأ: تأكد من ملء جميع الحقول!"
        return

    status_label.text = "جاري تسجيل الدخول..."
    
    var data = {
        "username": email_input.text.strip_edges(),
        "password": password_input.text.strip_edges()
    }
    
    var json_data = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    
    # الرابط الأساسي الذي يعمل معك
    var url = "https://my-game-server-19lc.onrender.com/"
    auth_request.request(url, headers, HTTPClient.METHOD_POST, json_data)

func _on_register_button_pressed():
    # الانتقال لصفحة التسجيل
    get_tree().change_scene_to_file("res://RegisterScreen.tscn")

func _on_auth_request_request_completed(_result, response_code, _headers, body):
    var response_text = body.get_string_from_utf8()
    
    if response_code == 200:
        status_label.text = "مرحباً يا " + email_input.text.strip_edges() + "!"
        status_label.modulate = Color.GREEN
    else:
        status_label.text = "خطأ: تأكد من البيانات"
        status_label.modulate = Color.RED
6:08 Õ - samsung SM-A13:
extends Control

@onready var email_input = $Emailinput
@onready var password_input = $Passwordinput
@onready var status_label = $StatusLabel
@onready var auth_request = $AuthRequest

func _ready():
	# ربط الأزرار برمجياً - تأكد أنك حذفت أي ربط قديم من واجهة المحرر
	$LoginButton.pressed.connect(_on_login_button_pressed)
	$RegisterButton.pressed.connect(_on_register_button_pressed)
	auth_request.request_completed.connect(_on_auth_request_request_completed)

func _on_login_button_pressed():
	status_label.text = "جاري الاتصال..."
	
	# نرسل "email" كما طلبت أنت
	var data = {
		"email": email_input.text.strip_edges(),
		"password": password_input.text.strip_edges()
	}
	
	var json_data = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	var url = "https://my-game-server-19lc.onrender.com/"
	
	print("نرسل للسيرفر: ", json_data) # هذا السطر سيخبرنا بالضبط ماذا نرسل
	auth_request.request(url, headers, HTTPClient.METHOD_POST, json_data)

func _on_auth_request_request_completed(_result, response_code, _headers, body):
	var response_text = body.get_string_from_utf8()
	print("رد السيرفر: ", response_text) # هذا السطر سيخبرنا لماذا يرفض السيرفر
	
	if response_code == 200:
		status_label.text = "تم الدخول بنجاح!"
		status_label.modulate = Color.GREEN
	else:
		status_label.text = "خطأ (كود " + str(response_code) + ")"
		status_label.modulate = Color.RED
6:13 Õ - jabra:
from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ezzo_super_secret_key_2026"  # مفتاح أمان الجلسات
DB_FILE = "database.db"

# إنشاء وتحديث قاعدة البيانات لتشمل الحظر والرسائل الإدارية
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            avatar_id INTEGER DEFAULT 1,
            money INTEGER DEFAULT 600,
            is_banned INTEGER DEFAULT 0,
            admin_message TEXT DEFAULT ""
        )
    ''')
    # صيانة للتأكد من وجود الأعمدة الجديدة لو كانت القاعدة قديمة
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN admin_message TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 🎨 واجهات الـ HTML (التصميم الاحترافي)
# ==========================================

# 1️⃣ الصفحة الرئيسية (اللعبة تحت التطوير)
HOME_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سيرفر لعبة عزو | تحت التطوير</title>
    <style>
        body {
            background: linear-gradient(135deg, #0f0c1b, #201335);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.05);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-width: 500px;
            width: 90%;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff007f, #7f00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(127, 0, 255, 0.5);
        }
        p {
            font-size: 1.2rem;
            color: #ccc;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(45deg, #7f00ff, #ff007f);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 50px;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(255, 0, 127, 0.4);
            transition: 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(255, 0, 127, 0.8);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 اللعبة تحت التطوير 🎮</h1>
        <p>مرحباً بك في سيرفر لعبة عزو المطور! نحن نعمل على بناء عالم ألعاب أسطوري.</p>
        <a href="#" class="btn">اللعبة قريباً 🚀</a>
    </div>
</body>
</html>
"""

# 2️⃣ صفحة تسجيل دخول الإدارة
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم | تسجيل الدخول</title>
    <style>
        body {
            background: linear-gradient(135deg, #0f0c1b, #150d22);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.03);
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            width: 100%;
            max-width: 400px;
            box-sizing: border-box;
        }
        h2 { text-align: center; color: #ff007f; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 8px; color: #aaa; }
        .input-group input {
            width: 100%; padding: 12px; background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px;
            color: white; outline: none; box-sizing: border-box;
        }
        .submit-btn {
            width: 100%; padding: 12px; background: linear-gradient(45deg, #7f00ff, #ff007f);
            border: none; border-radius: 8px; color: white; font-size: 1.1rem; font-weight: bold; cursor: pointer;
        }
        .alert { background: #ff3333; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>تسجيل دخول الإدارة 🔐</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        <form action="/admin/login" method="POST">
            <div class="input-group">
                <label>اسم المستخدم الإداري</label>
                <input type="text" name="username" required>
            </div>
            <div class="input-group">
                <label>كلمة المرور</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="submit-btn">دخول</button>
        </form>
    </div>
</body>
</html>
"""

# 3️⃣ لوحة التحكم الاحترافية للمشرف (اللاعبين، الفلوس، الحظر، الرسائل)
ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحكم عزو الأسطورية 👑</title>
    <style>
        body {
            background: #0b0813;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #ff007f;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        h1 {
            background: linear-gradient(45deg, #00f0ff, #ff007f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .logout-btn {
            background: #ff3333; color: white; padding: 10px 20px; text-decoration: none;
            border-radius: 8px; font-weight: bold; transition: 0.2s;
        }
        .logout-btn:hover { background: #cc0000; box-shadow: 0 0 10px #ff3333; }
        
        .alert-success { background: #22c55e; color: white; padding: 12px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: bold;}

        table {
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        th, td {
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        th {
            background: rgba(127, 0, 255, 0.2);
            color: #00f0ff;
            font-size: 1.1rem;
        }
        tr:hover { background: rgba(255, 255, 255, 0.03); }
        
        .badge { padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; }
        .badge-active { background: #22c55e; color: #fff; }
        .badge-banned { background: #ef4444; color: #fff; }

        .btn {
            padding: 8px 12px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s;
        }
        .btn-ban { background: #ef4444; color: white; text-decoration: none; display: inline-block; }
        .btn-ban:hover { background: #dc2626; }
        .btn-unban { background: #10b981; color: white; text-decoration: none; display: inline-block; }
        .btn-unban:hover { background: #059669; }
        
        .action-form { display: inline-flex; gap: 5px; margin: 0; }
        .input-style {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            padding: 6px;
            border-radius: 6px;
            outline: none;
        }
        .input-money { width: 70px; text-align: center; }
        .input-msg { width: 150px; }
        .btn-add { background: #7f00ff; color: white; }
        .btn-add:hover { background: #6b00d6; }
        .btn-msg { background: #00f0ff; color: #0b0813; }
        .btn-msg:hover { background: #00c8d6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👑 لوحة تحكم الإمبراطور عزو 👑</h1>
        <a href="/admin/logout" class="logout-btn">تسجيل الخروج 🚪</a>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for message in messages %}
          <div class="alert-success">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <table>
        <thead>
            <tr>
                <th>اللاعب 👤</th>
                <th>البريد الإلكتروني 📧</th>
                <th>الفلوس الحاليّة 💰</th>
                <th>حالة الحساب 🚦</th>
                <th>رسالة الإدارة له 💬</th>
                <th>خيارات التحكم السريعة 🛠️</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td style="font-weight: bold; color: #ff007f;">{{ user[0] }}</td>
                <td>{{ user[1] }}</td>
                <td style="color: #ffd700; font-weight: bold;">${{ user[4] }}</td>
                <td>
                    {% if user[5] == 1 %}
                    <span class="badge badge-banned">محظور 🔴</span>
                    {% else %}
                    <span class="badge badge-active">نشط 🟢</span>
                    {% endif %}
                </td>
                <td style="color: #aaa; font-style: italic;">
                    {{ user[6] if user[6] != "" else "لا توجد رسالة مبعوثة" }}
                </td>
                <td>
                    {% if user[5] == 1 %}
                    <a href="/admin/unban/{{ user[0] }}" class="btn btn-unban">فك الحظر ✅</a>
                    {% else %}
                    <a href="/admin/ban/{{ user[0] }}" class="btn btn-ban">حظر اللاعب 🚫</a>
                    {% endif %}

                    <form action="/admin/add_money/{{ user[0] }}" method="POST" class="action-form">
                        <input type="number" name="amount" class="input-style input-money" placeholder="المبلغ" required min="1">
                        <button type="submit" class="btn btn-add">زيادة 💰</button>
                    </form>

                    <form action="/admin/send_message/{{ user[0] }}" method="POST" class="action-form">
                        <input type="text" name="message" class="input-style input-msg" placeholder="اكتب رسالة للاعب..." required>
                        <button type="submit" class="btn btn-msg">إرسال 💬</button>
                    </form>
                </td>
            </tr>
            {% else %}
            <tr>
                <td colspan="6" style="text-align: center; color: #888;">لا يوجد لاعبون مسجلون في السيرفر حالياً!</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

# ==========================================
# 🌐 التحكم بالصفحات والمشرفين (Routes)
# ==========================================

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/admin')
def admin():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # يمكنك تغيير بيانات الدخول السرية الخاصة بك من هنا
    if username == "admin" and password == "12345":
        session['logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash("خطأ في اسم المستخدم أو الباسوورد!")
        return redirect(url_for('admin'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin'))

# لوحة التحكم الحقيقية بعد الدخول
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin'))
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, password, avatar_id, money, is_banned, admin_message FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return render_template_string(ADMIN_DASHBOARD_HTML, users=users)


# ==========================================
# 🛠️ عمليات لوحة التحكم (Actions)
# ==========================================

# حظر لاعب
@app.route('/admin/ban/<username>')
def ban_player(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    flash(f"تم حظر اللاعب {username} بنجاح! 🚫")
    return redirect(url_for('admin_dashboard'))

# فك حظر لاعب
@app.route('/admin/unban/<username>')
def unban_player(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_banned = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    flash(f"تم إلغاء الحظر عن اللاعب {username} بنجاح! ✅")
    return redirect(url_for('admin_dashboard'))

# زيادة الفلوس للاعب
@app.route('/admin/add_money/<username>', methods=['POST'])
def add_money(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    amount = int(request.form.get('amount', 0))
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET money = money + ? WHERE username = ?", (amount, username))
    conn.commit()
    conn.close()
    flash(f"تم إضافة {amount}$ إلى حساب اللاعب {username}! 💰")
    return redirect(url_for('admin_dashboard'))

# إرسال كلمة/رسالة مخصصة للاعب تظهر له في اللعبة
@app.route('/admin/send_message/<username>', methods=['POST'])
def send_message(username):
    if not session.get('logged_in'): return redirect(url_for('admin'))
    msg = request.form.get('message', '')
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET admin_message = ? WHERE username = ?", (msg, username))
    conn.commit()
    conn.close()
    flash(f"تم إرسال الرسالة إلى {username} بنجاح! 💬")
    return redirect(url_for('admin_dashboard'))


# ==========================================
# 🎮 واجهة الـ API للعبة (Godot)
# ==========================================

# عند التسجيل
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    avatar_id = data.get('avatar_id', 1)

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "الرجاء تعبئة جميع الحقول!"}), 400

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, avatar_id) VALUES (?, ?, ?, ?)",
            (username, email, password, avatar_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "تم إنشاء حسابك بنجاح!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "اسم المستخدم مستخدم بالفعل!"}), 400

# عند تسجيل الدخول من اللعبة
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password, email, avatar_id, money, is_banned, admin_message FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row and row[0] == password:
        # التحقق إذا كان اللاعب محظوراً
        if row[4] == 1:
            return jsonify({
                "status": "error", 
                "message": "🚫 تم حظر حسابك من قبل الإدارة! يرجى مراجعة المسؤول عزو."
            }), 403
            
        return jsonify({
            "status": "success",
            "message": f"أهلاً بك يا {username}!",
            "email": row[1],
            "avatar_id": row[2],
            "money": row[3],
            "admin_message": row[5] # هنا نرسل الكلمة التي كتبها الآدمن للاعب ليقرأها في جادوت!
        }), 200
    else:
        return jsonify({"status": "error", "message": "اسم المستخدم أو كلمة المرور خاطئة!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
6:15 Õ - samsung SM-A13:



samsung SM-A13 is available
6:16 Õ - samsung SM-A13:
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "database.db"

# دالة الدخول (تقرأ الإيميل والباسورد)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    # نأخذ الإيميل بدلاً من اليوزر نيم
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # البحث في قاعدة البيانات عن طريق الإيميل
    cursor.execute("SELECT username, password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    # التحقق من الباسورد
    if row and row[1] == password:
        return jsonify({"status": "success", "username": row[0]}), 200
    else:
        return jsonify({"status": "error", "message": "بيانات الدخول خاطئة"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
