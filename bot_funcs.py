import re
from sqlighter import SQLighter

# Функция для проверки ключа по значению.
# Пример: на входе список релизов типа {Test1 : 12345, Test: 23456}, и нужный ID=12345, на выходе получаем имя релиза "Test1".
def get_key_by_value(value_list, value):
    key = None
    for current_key, current_value in value_list.items():
        if current_value == value:
            key = current_key
    return key

# Проверка строки на содержание кириллицы и спецсимволов, список можно расширять при необходимости
def check_valid_string(string):
    return (not bool(re.search(r'[а-яА-ЯёЁ"\'={}\[\]]', string)) and bool(string) and len(string) > 3)

def increase_day(db, release_id):
    try:
        test_avaible = SQLighter.get_status(db, release_id)[0]
    except:
        print("Релиз не найден!")
    status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
    status_from_db[4] = str(int(status_from_db[4]) + 1)
    status_from_db[6] = step_add_day(status_from_db[6])
    status_from_db[7] = step_add_day(status_from_db[7])
    status_from_db[8] = step_add_day(status_from_db[8])
    status_from_db[9] = step_add_day(status_from_db[9])
    status_from_db[10] = step_add_day(status_from_db[10])
    SQLighter.edit_episodes_info(db, release_id, status_from_db)

# Формирование статуса по релизу.
# TODO: пока что фейковые данные, нужно частично брать из БД, частично с сайта.
# С сайта примерно так: https://api.anilibria.tv/v2/getTitle?id=8796, отсюда выдирать нужные поля (приходит в формате json)
def get_status(db, release_id):
    try:
        test_avaible = SQLighter.get_status(db, release_id)[0]
    except:
        return "Релиз не найден. Возможно, он уже закрыт или ещё не стартован. Обратитесь с администратору бота."
    status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
    top = status_from_db[1]
    episode = status_from_db[2]
    max_episode = status_from_db[3]
    if max_episode == "None":
        max_episode = "?"
    today = status_from_db[4]
    deadline = status_from_db[5]

    subs = step_status(status_from_db[6], "s")
    decor = step_status(status_from_db[7], "d")
    voice = step_status(status_from_db[8], "v")
    timing = step_status(status_from_db[9], "t")
    fixs = step_status(status_from_db[10], "f")

    head = str.format("Серия {} из {}. День {} из {}:\n", episode, max_episode, today, deadline)
    status_tag = "\n#Status"
    status = head + "\n" + subs + decor + voice + timing + fixs + status_tag

    return str(status)

# Функция для подготовки статуса по каждому этапу
def step_status(data, mod):
    step_info = data.replace("'", "").split("|")
    mod_list = {
        's': "Субтитры",
        'd': "Оформление",
        'v': "Озвучка",
        't': "Тайминг",
        'f': "Фиксы"
    }
    return "{} {} (дедлайн {}/{})\n".format("❌" if step_info[0]=="0" else "✅", mod_list[mod], step_info[1], step_info[2])

# Функция для обновления в статусе текущего дня (срабатывает в 00:00)
def step_add_day(data):
    step_info = data.replace("'", "").split("|")
    if step_info[0]=="0":
        day = int(step_info[1]) + 1
    else:
        day = int(step_info[1])
    return "{}|{}|{}".format(step_info[0], str(day), step_info[2])

# Функция для определния дедлайна релиза в зависимости от типа (топ, нетоп, неонгоинг)
def set_release_type(release_type):
    release_type_info = {
        'top': 2,
        'nontop': 4,
        'old': 7
    }
    try:
        return release_type_info[release_type]
    except:
        return 0

# Формирование справки.
def get_help():
    header_info = "Менеджер релизов - бот, предназначенный для контроля за работой над релизами. Он способен сообщать ответственным за релиз, что происходит задержка.\n"
    additional_info = "При добавлении бота в группу он будет ежедневно в 20:00 по МСК отправлять статусные сообщения по релизу. Последние сообщения бота можно найти по хештегу #Status."
    command_new_release = "/new_release [Release_name] - Создание нового релиза. Можно вызвать только в группе релиза после добавления туда бота. Название релиза только на английском языке. Если не указать название релиза - бот попытается взять имя группы.\n\n"
    command_status = "/status [Release_name] - Вызов статуса релиза. В группах работает без названия релиза, а в личных сообщениях - только с названием (название должно соответствовать заданому при создании релиза).\n\n"
    command_start_release = "/start_release [Release_type]* [Deadline_offset] [Current_ep] [Max_ep] - Команда для начала работы над релизом. Можно вызвать только в группе релиза.\nПараметры:\n• Тип релиза* (Top, NonTop, Old)\n• Смещение дня релиза (если совпадает с дедлайном - значит 0).\n• Текущий эпизод (если бот был добавлен не сразу)\n• Всего эпизодов (если известно).\n\n"
    bottom = "* - звёздочкой отмечены обязательные параметры."
    help_info = header_info + additional_info + "\n\nСписок доступных команд:\n" + command_new_release + command_status + command_start_release + bottom
    return help_info