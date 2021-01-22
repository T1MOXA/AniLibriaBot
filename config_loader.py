import configparser

def get_token():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    token = config.get('main', 'token')
    return token

def get_DB():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    token = config.get('main', 'db_file')
    return token