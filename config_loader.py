import configparser

# Получение токена бота из конфига
def get_token():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    token = config.get('main', 'token')
    return token

# Получение название файла с БД из конфига
def get_DB():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    token = config.get('main', 'db_file')
    return token