import json, ast, requests, datetime
from tgbot import API_URL, TGBOT_KEY

from flask import Flask, render_template, request, redirect, url_for, make_response
#render_template - лезет в папку templates

app = Flask(__name__) #говорит фласку, что это файл бэка

def load_data():
    try:
        with open('questions.json', 'r', encoding="utf8") as j_file: #при использовании with файл открывается, а затем автоматически закроется без использования close()
            j_data = json.load(j_file)
            error = ""
        with open('users.json', 'r', encoding="utf8") as u_file: 
            u_data = json.load(u_file)
            error = ""
        
    except Exception as e:
        j_data = ""
        u_data = ""
        error = "Ошибка при открытии файла " + e.__repr__()
    return j_data, u_data, error

@app.route("/") #говорит фласку, что это главная страница
def index():
    login = request.cookies.get("login") #пытается достать логин из куков
    status = False
    j_data = ""
    u_data = ""
    error = ""
    if login: #если в логин что-то записалось, то  он выполнит
        status = True
        j_data, u_data, error = load_data()
    return render_template("index.html", status=status, login=login, j_data=j_data, u_data=u_data, error=error)

@app.post("/login") #авторизация
def login():
    login = request.form.get("login")
    if login == "admin":
        j_data, u_data, error = load_data()
        response = make_response(render_template("index.html", status=True, login=login, j_data=j_data, u_data=u_data, error=error)) #создаем ответ
        response.set_cookie("login", login) #сохраняем в куки ответа логин
        return response
    return redirect(url_for("index")) #возвращение в стартовую страницу без авторизации

@app.post("/logout") #выход из аккаунта
def logout():
    response = make_response(render_template("index.html")) #создаем ответ
    response.delete_cookie("login") #чистим куки логина
    return response

@app.post("/upload") #загрузка файлов
def upload():
    f = request.files["file"] #file - это переменная в которой у нас будет файл
    f.save(r"C:\Users\dasle\Desktop\quizBot\questions.json") #сохраняем наш файл в папку
    return redirect(url_for("index"))

@app.post("/send") #отправка сообщений через бота
def send():
    q = ast.literal_eval(request.form.get("q")) #literal_eval переводит вопрос из текста в словарь
    options = [[{"text": q["options"][0]}, {"text": q["options"][1]}], #первый ряд с кнопками-ответами
               [{"text": q["options"][2]}, {"text": q["options"][3]}]] #второй ряд с кнопками-ответами
    with open('temp.json', 'w', encoding="utf8") as file:
        json.dump(q, file, ensure_ascii= False)
    
    with open('users.json', 'r', encoding="utf8") as us_file: #открываем файл users
        us_data = json.load(us_file)
    print(datetime.datetime.now())
    for u in us_data["users"]:
        if us_data["users"][u]['status'] != "True":
            continue
        data = {"chat_id": u,      
                 "text": "<b>Вопрос: </b> <i>{0}</i>".format(q["title"]),
                 "parse_mode": "HTML",
                 "reply_markup": {       #кнопки
                      "keyboard": options,
                      "one_time_keyboard": True #после нажатия кнопки исчезают
                 }}  
        resp = requests.post(API_URL + TGBOT_KEY + "/sendMessage", json = data)
        print(resp.json())
    print(datetime.datetime.now())
    return redirect(url_for("index")) 

@app.route("/dashboard") 
def dashboard():
    with open('users.json', 'r', encoding="utf8") as j_file: 
        j_data = json.load(j_file)
    return render_template("dashboard.html", j_data=j_data)

@app.post("/clearscore") 
def clear_score():

    with open('users.json', 'r', encoding="utf8") as us_file: 
        us_data = json.load(us_file)

    for u in us_data["users"]:    
        us_data["users"][u]["score"] = 0

    with open('users.json', 'w', encoding="utf8") as us_file: 
        json.dump(us_data, us_file, ensure_ascii=False)

    return redirect(url_for("index"))

@app.post("/sendmessage")
def send_message():
    resp = request.form.to_dict()
    user_id = resp['users']
    text = resp['text']
    if user_id == "-1":
        with open('users.json', 'r', encoding="utf8") as us_file: 
            us_data = json.load(us_file)
        for u in us_data["users"]:
            data = {"chat_id": u, "text": text} 
            resp = requests.post(API_URL + TGBOT_KEY + "/sendMessage", data = data)
            print(resp.json())
        return redirect(url_for("index"))
    else:
        data = {"chat_id": user_id, "text": text}  
        resp = requests.post(API_URL + TGBOT_KEY + "/sendMessage", data = data)
        print(resp.json())
        return redirect(url_for("index")) 