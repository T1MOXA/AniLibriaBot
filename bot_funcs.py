import re
from sqlighter import SQLighter

# Словари (работают аналогом swich-case)
release_type_info = {
    'top': 2,
    'nontop': 4,
    'old': 7
}
mod_list = {
    's': "Субтитры",
    'd': "Оформление",
    'v': "Озвучка",
    't': "Тайминг",
    'f': "Фиксы"
}

step_list = {
    's': 6,
    'd': 7,
    'v': 8,
    't': 9,
    'f': 10
}

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

# Проверка доступности статуса релиза
def check_release_available(db, release_id):
    available = True
    try:
        test_available = SQLighter.get_status(db, release_id)[0]
    except:
        print("WARNING: Релиз с ИД " + str(release_id) + " не найден.")
        available = False
    return available

# Выполняется в 00:00, увеличиваем текущий день в статусе
def increase_day(db, release_id):
    if (check_release_available(db, release_id)):
        status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
        status_from_db[4] = str(int(status_from_db[4]) + 1)
        status_from_db[6] = step_change_day(status_from_db[6])
        status_from_db[7] = step_change_day(status_from_db[7])
        status_from_db[8] = step_change_day(status_from_db[8])
        status_from_db[9] = step_change_day(status_from_db[9])
        status_from_db[10] = step_change_day(status_from_db[10])
        SQLighter.edit_episodes_info(db, release_id, status_from_db)

# Формирование статуса по релизу.
# TODO: Можно частично брать инфу о релизе с сайта.
# С сайта примерно так: https://api.anilibria.tv/v2/getTitle?id=8796, отсюда выдирать нужные поля (приходит в формате json)
def get_status(db, release_id):
    if (check_release_available(db, release_id)):
        status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
        # Топовый релиз или нет (булевое, записывается через 0 и 1)
        top = status_from_db[1]
        # Текущий эпизод
        episode = status_from_db[2]
        # Всего эпизодов, если неизвестно - ставим вопрос
        max_episode = status_from_db[3]
        if max_episode == "None":
            max_episode = "?"
        # Текущий день
        today = status_from_db[4]
        # Дедлайн
        deadline = status_from_db[5]

        subs = step_status(status_from_db[6], get_key_by_value(mod_list, "Субтитры"))
        decor = step_status(status_from_db[7], get_key_by_value(mod_list, "Оформление"))
        voice = step_status(status_from_db[8], get_key_by_value(mod_list, "Озвучка"))
        timing = step_status(status_from_db[9], get_key_by_value(mod_list, "Тайминг"))
        fixs = step_status(status_from_db[10], get_key_by_value(mod_list, "Фиксы"))

        status = str(SQLighter.get_active_status(db, release_id)[0]).replace("(", "").replace(")", "").replace(",", "").strip()
        if (status == "0"):
            status = "Завершён."
        else:
            status = "Активен."
        head = str.format("Статус релиза: {}\n\nСерия {} из {}. День {} из {}:\n", status, episode, max_episode, today, deadline)
        status_tag = "\n#Status"
        status = head + "\n" + subs + decor + voice + timing + fixs + status_tag

        return str(status)
    else:
        return "Релиз не найден."

# Функция для подготовки статуса по каждому этапу
def step_status(data, mod):
    step_info = data.replace("'", "").split("|")
    return "{} {} (дедлайн {}/{})\n".format("❌" if step_info[0]=="0" else "✅", mod_list[mod], step_info[1], step_info[2])

# Функция для обновления в статусе текущего дня (срабатывает в 00:00)
def step_change_day(data, clear=False, days=0):
    step_info = data.replace("'", "").split("|")
    if (not clear):
        if step_info[0]=="0":
            day = int(step_info[1]) + 1
        else:
            day = int(step_info[1])
        return "{}|{}|{}".format(step_info[0], str(day), step_info[2])
    else:
        return "{}|{}|{}".format(0, days, step_info[2])

# Функция для определния дедлайна релиза в зависимости от типа (топ, нетоп, неонгоинг)
def set_release_type(release_type):
    try:
        return release_type_info[release_type]
    except:
        return 0

# Проверка статуса этапа релиза
def check_step_completed(db, release_id, step):
    if (check_release_available(db, release_id)):
        status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
        step_info = status_from_db[step_list[step]].replace("'", "").split("|")
        if step_info[0]=="1":
            return True
        else:
            return False
    else:
        return False

# Продвижение по этапам релиза
def step_completing(db, release_id, step):
    if (check_release_available(db, release_id)):
        status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
        # 6 - субтитры, 7 - оформление, 8 - озвучка, 9 - тайминг, 10 - фиксы, остальное не трогаем.
        status_from_db[6] = status_from_db[6].replace("'", "")
        status_from_db[7] = status_from_db[7].replace("'", "")
        status_from_db[8] = status_from_db[8].replace("'", "")
        status_from_db[9] = status_from_db[9].replace("'", "")
        status_from_db[10] = status_from_db[10].replace("'", "")
        step_info = status_from_db[step_list[step]].split("|")
        if step_info[0]=="0":
            step_info[0] = "1"
        status_from_db[step_list[step]] = "{}|{}|{}".format(step_info[0], step_info[1], step_info[2])
        message = "Статус серии обновлён на сервере. Текущее состояние релиза можно узнать командой /status."
        try:
            SQLighter.edit_episodes_info(db, release_id, status_from_db)
        except:
            message = "Ошибка при обновлении статуса серии! Обратитесь к администратору бота."
        return message
    else:
        return "Релиз не найден."

# Завершение работы над серией, начало работы над следующей серией
def ep_completed(db, release_id):
    if (check_release_available(db, release_id)):
        status_from_db = str(SQLighter.get_status(db, release_id)[0]).replace("(", "").replace(")", "").split(", ")
        episode = int(status_from_db[2])
        # Если не знаем количество серий - просто прибавляем 1 к текущей
        if (status_from_db[3] != "?"):
            max_episode = int(status_from_db[3])
            # Если мы не на последней серии - увеличиваем текущий эпизод
            if (episode < max_episode):
                status_from_db[2] = str(episode + 1)
            # Иначе закрываем релиз в целом
            else:
                # Проверяем статус, если уже закрыт - ничего не делаем, если активен - закрываем.
                if (str(SQLighter.get_active_status(db, release_id)[0]).replace("(", "").replace(")", "").replace(",", "").strip() == "1"):
                    SQLighter.set_not_active_release(db, release_id)
                    return "Работа над {} серией завершена!\n\nРелиз завершён!\nВсем спасибо за работу, увидимся на других релизах!\n\n".format(episode)
                else:
                    return "Работа над серией и релизом завершена ранее.\nСтатус последней серии:\n\n".format(episode)
        else:
            status_from_db[2] = str(episode + 1)
        # Вычитаем из текущей даты дедлайн. Если уложились - текущий день будет отрицательным или нулевым, иначе есть задержка и будет меньше времени до следующего дедлайна
        status_from_db[4] = int(status_from_db[4]) - int(status_from_db[5]) - (7 - int(status_from_db[5]))
        
        status_from_db[6] = step_change_day(status_from_db[6], clear=True, days=status_from_db[4])
        status_from_db[7] = step_change_day(status_from_db[7], clear=True, days=status_from_db[4])
        status_from_db[8] = step_change_day(status_from_db[8], clear=True, days=status_from_db[4])
        status_from_db[9] = step_change_day(status_from_db[9], clear=True, days=status_from_db[4])
        status_from_db[10] = step_change_day(status_from_db[10], clear=True, days=status_from_db[4])
        message = "Работа над {} серией завершена!\n\n".format(episode)
        try:
            SQLighter.edit_episodes_info(db, release_id, status_from_db)
        except:
            message = "Ошибка при попытке завершить работу над серией! Обратитесь к администратору бота.\n\n"
        return message
    else:
        return "Релиз не найден."

# Формирование справки.
def get_help():
    header_info = "Менеджер релизов - бот, предназначенный для контроля за работой над релизами. Он способен сообщать ответственным за релиз, что происходит задержка.\n"
    additional_info = "При добавлении бота в группу он будет ежедневно в 20:00 по МСК отправлять статусные сообщения по релизу. Последние сообщения бота можно найти по хештегу #Status."
    command_new_release = "/new_release [Release_short_name]* [Release_long_name]* - Создание нового релиза. Можно вызвать только в группе релиза после добавления туда бота. \nПараметры:\n• Короткое название релиза (только на английском языке без пробелов, знак подчёркивания использовать можно).\n• Длинное название релиза (можно указывать любое название, желательно на русском).\n\n"
    command_start_release = "/start_release [Release_type]* [Today] [Current_ep] [Max_ep] - Команда для начала работы над релизом. Можно вызвать только в группе релиза.\nПараметры:\n• Тип релиза* (Top, NonTop, Old).\n• Текущий день релиза (по умолчанию - 1-й день релиза).\n• Текущий эпизод (если бот был добавлен не сразу)\n• Всего эпизодов (если известно).\n\n"
    command_subs_completed = "/subs_completed - Отметка о завершении работ над переводом.\n\n"
    command_decor_completed = "/decor_completed - Отметка о завершении работ над оформлением.\n\n"
    command_voice_completed = "/voice_completed - Отметка о завершении работ над озвучкой.\n\n"
    command_timing_completed = "/timing_completed - Отметка о завершении работ над таймингом.\n\n"
    command_fixs_completed = "/fixs_completed - Отметка о завершении работ над фиксами.\n\n"
    command_ep_completed = "/ep_completed - Отметка о завершении работ над серией. Можно вызвать только после завершения всех этапов работы над серией. После завершения серии отправляет статус последней серии. Если серия была последней в релизе - завершает релиз.\n\n"
    command_status = "/status [Release_name] - Вызов статуса релиза. В группах работает без названия релиза, а в личных сообщениях - только с названием (название должно соответствовать заданому короткому названию при создании релиза).\n\n"
    command_active_releases = "/active_releases - Вызов списка активных релизов, над которыми идёт работа в данный момент.\n\n"
    command_releases_history = "/releases_history - Вызов списка архивных (неактивных) релизов, используется исключительно для справки.\n\n"
    
    commands = (command_new_release + command_start_release + command_subs_completed + command_decor_completed + 
        command_voice_completed + command_timing_completed + command_fixs_completed + command_ep_completed + command_status + 
        command_active_releases + command_releases_history)

    bottom = "* - звёздочкой отмечены обязательные параметры."
    help_info = header_info + additional_info + "\n\nСписок доступных команд:\n" + commands + bottom
    return help_info