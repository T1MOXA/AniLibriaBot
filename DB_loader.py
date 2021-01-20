import configparser

def getToken():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    token = config.get('main', 'token')
    return token

def getActiveUsers():
    config = configparser.ConfigParser()
    config.read('users.db')
    userlist = {}
    users = config.items('active_users')
    for user, user_id in users:
        userlist[user] = user_id
    return userlist

# TODO добавить обработку пользователя, если он уже есть в базе
def addActiveUser(user, user_id):
    conf = configparser.ConfigParser()
    conf.read('users.db')
    conf.set('active_users', str(user), str(user_id))
    with open("users.db", "w") as config:
        conf.write(config)

def getActiveReleases():
    config = configparser.ConfigParser()
    config.read('releases.db')
    releaselist = {}
    releases = config.items('active_releases')
    for release, release_id in releases:
        releaselist[release] = release_id
    return releaselist

def addActiveRelease(release, release_id):
    conf = configparser.ConfigParser()
    conf.read('releases.db')
    conf.set('active_releases', str(release), str(release_id))
    with open("releases.db", "w") as config:
        conf.write(config)