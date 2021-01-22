import re

def get_key_by_value(value_list, value):
    key = None
    for current_key, current_value in value_list.items():
        if current_value == value:
            key = current_key
    return key

def check_valid_string(string):
    return (not bool(re.search(r'[а-яА-ЯёЁ:"=]', string)) and bool(string) and len(string) > 3)

def get_status():
    head = str.format("Статус серии {}, день {} из {}:\n", 1, 1, 4)
    subs = "✓ Субтитры (дедлайн 1/1)\n"
    decor = "✓ Оформление (дедлайн 2/3)\n"
    voice = "✓ Озвучка 4/4 (дедлайн 3/3)\n"
    timing = "✓ Тайминг (дедлайн 4/4)\n"
    fixs = "Х Фиксы 1/2 (дедлайн 4/4)\n\n"
    status_tag = "#Status"
    status = head + "\n" + subs + decor + voice + timing + fixs + status_tag
    return status

def get_help():
    header_info = "Менеджер релизов - бот, предназначенный для контроля за работой над релизами. Он способен сообщать ответственным за релиз, что происходит задержка.\n"
    additional_info = "При добавлении бота в группу он будет ежедневно в 20:00 по МСК отправлять статусные сообщения по релизу. Последние сообщения бота можно найти по хештегу #Status."
    command_new_release = "/new_release [Release_name] - Создание нового релиза. Можно вызвать только в группе релиза после добавления туда бота. Название релиза только на английском языке. Если не указать название релиза - бот попытается взять имя группы.\n\n"
    command_status = "/status [Release_name] - Вызов статуса релиза. В группах работает без названия релиза, а в личных сообщениях - только с названием (название должно соответствовать заданому при создании релиза).\n\n"
    help_info = header_info + additional_info + "\n\nСписок доступных команд:\n" + command_new_release + command_status
    return help_info