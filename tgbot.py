import requests, time, json, datetime

API_URL = "https://api.telegram.org/"
TGBOT_KEY = "bot7867289047:AAGt3v6ZxYUyrS9PG_U6qnEnwlgDCdxOgwI"

if __name__  == "__main__":
    offset = None
    try:
        while True:
            time.sleep(1) #делает паузу в 1 сек, чтобы не заспамить
            data = {"offset": offset}
            try:
                resp = requests.get(API_URL + TGBOT_KEY + "/getUpdates", data = data) #чтобы получать обновления от бота(права, добавили, кто-то вышел итд)
            except requests.exceptions.ReadTimeout:
                continue
            if resp.status_code != 200:
                print("Ошибка запроса, код:", resp.status_code)
                continue
            updates = resp.json() 
            if updates["ok"] != True:
                continue
            if len(updates['result']) < 1:
                continue
            #вытягивает числа у update_id  из  файла updates и создает из них список, после чего вытягивает max число 
            #updates['result'] квадратными скобками вытягивает список, который пришел в ответе
            offset = max([u["update_id"] for u in updates['result']]) + 1 #благодаря 1 он смещает id и тем самым сообщение придет единожды

            with open('users.json', 'r', encoding="utf8") as us_file: #чтение файла users
                us_data = json.load(us_file)

            with open('temp.json', 'r', encoding="utf8") as us_file: #записывает нажатый на сайте вопрос, чтобы далее сравнить ответы 
                temp = json.load(us_file)
            
            for u in updates['result']:
                if "message" in u:
                    if u["message"]["text"] == "/start": #при команде start меняет статус пользователя на true
                        user_id = str(u["message"]["chat"]["id"])
                        if us_data["users"][user_id]["status"] == "False":
                            us_data["users"][user_id]["status"] = "True"
                            with open('users.json', 'w') as file: 
                                json.dump(us_data, file)
                            data = {"chat_id": user_id, "text": "Добро пожаловать в Quiz-бот!"}  
                            requests.post(API_URL + TGBOT_KEY + "/sendMessage", data = data)
                        else:
                            continue
                    else:
                        print(datetime.datetime.now()) #печатает время
                        user_id = str(u["message"]["chat"]["id"])
                        if user_id not in us_data["users"]:
                            continue
                        if temp["answer"] == u["message"]["text"]:
                            print(us_data["users"][user_id]["title"], 'получает 1 очко', f'({u["message"]["text"]})')
                            us_data["users"][user_id]["score"] += 1  #добавляет +1 очко в словарь в файле users
                            with open('users.json', 'w', encoding="utf8") as file: 
                                json.dump(us_data, file, ensure_ascii=False)
                        else:
                            print(us_data["users"][user_id]["title"], 'ошибся', f'({u["message"]["text"]}) != ({temp["answer"]})')
    except KeyboardInterrupt:
        exit()
