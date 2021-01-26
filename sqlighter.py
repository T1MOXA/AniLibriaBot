import sqlite3

class SQLighter:

    # Инициирование подключения к БД
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
    
    # Получение списка (словаря) активных релизов
    def get_active_releases(self, active=True):
        with self.connection:
            names = self.cursor.execute("SELECT release_name FROM releases WHERE active = TRUE").fetchall()
            ids = self.cursor.execute("SELECT release_id FROM releases WHERE active = TRUE").fetchall()
            result = {}
            i = 0
            while (i < len(names)):
                name = str(names[i]).replace("(", "").replace("'", "").replace(",", "").replace(")", "").strip()
                release_id = str(ids[i]).replace("(", "").replace(",", "").replace(")", "").strip()
                result[name] = release_id
                i += 1
            return result
    
    # Добавление нового релиза в БД
    def add_release(self, release_id, release_name, site_id="NULL"):
        with self.connection:
            self.cursor.execute("INSERT INTO releases (release_id, site_id, release_name) VALUES ({}, NULL, '{}')".format(str(release_id), release_name)).fetchall()
            return self.cursor.execute("INSERT INTO episodes (release_id) VALUES ({})".format(str(release_id))).fetchall()
    
    # Получение полной информации по статусу релиза (серии)
    def get_status(self, release_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM episodes WHERE release_id={}".format(str(release_id))).fetchall()
    
    # Изменение информации по релизу (серии)
    def edit_release(self, release_id, new_params):
        with self.connection:
            return self.cursor.execute("UPDATE episodes SET top_release = {}, current_ep = {}, max_ep = {}, today = {}, deadline = {}, subs = '{}', decor = '{}', voice = '{}', timing = '{}', fixs = '{}' WHERE release_id = {};".format(
                new_params[1], new_params[2], new_params[3], new_params[4], new_params[5], new_params[6], new_params[7], new_params[8], new_params[9], new_params[10], release_id)).fetchall()

    # Закрытие подключения к БД
    def close(self):
        self.connection.close()