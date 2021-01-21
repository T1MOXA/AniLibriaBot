import re

def getKeyByValue(value_list, value):
    key = None
    for current_key, current_value in value_list.items():
        if current_value == value:
            key = current_key
    return key

def checkValidString(string):
    return (not bool(re.search(r'[а-яА-ЯёЁ:"=]', string)) and bool(string) and len(string) > 3)

def getStatus():
    head = str.format("Статус серии {}, день {} из {}:\n", 1, 1, 4)
    subs = "✓ Субтитры (дедлайн 1/1)\n"
    decor = "✓ Оформление (дедлайн 2/3)\n"
    voice = "✓ Озвучка 4/4 (дедлайн 3/3)\n"
    timing = "✓ Тайминг (дедлайн 4/4)\n"
    fixs = "Х Фиксы 1/2 (дедлайн 4/4)\n"
    deploy = "Х Сборка (дедлайн 4/4)\n\n"
    status_tag = "#Status"
    status = head + "\n\n" + subs + decor + voice + timing + fixs + deploy + status_tag
    return status