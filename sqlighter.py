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
    
    def get_status(self, release_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM episodes WHERE release_id={}".format(str(release_id))).fetchall()
    
    # Закрытие подключения к БД
    def close(self):
        self.connection.close()