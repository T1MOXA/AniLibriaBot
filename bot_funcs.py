import re

def getKeyByValue(value_list, value):
    key = None
    for current_key, current_value in value_list.items():
        if current_value == value:
            key = current_key
    return key

def checkValidString(string):
    return (not bool(re.search(r'[а-яА-ЯёЁ:"=]', string)) and bool(string) and len(string) > 3)