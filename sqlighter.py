import sqlite3

class SQLighter:

    # Инициирование подключения к БД
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
    
    # Получение списка (словаря) релизов. По умолчанию берутся только активные релизы
    def get_all_releases(self, active=True, all_releases=False):
        with self.connection:
            additional_info = ''
            if active:
                additional_info = " WHERE active = TRUE"
            else:
                additional_info = " WHERE active = FALSE"
            
            if all_releases:
                additional_info = ''

            names = self.cursor.execute("SELECT release_short_name FROM releases{}".format(additional_info)).fetchall()
            ids = self.cursor.execute("SELECT release_id FROM releases{}".format(additional_info)).fetchall()
            result = {}
            i = 0
            while (i < len(names)):
                name = str(names[i]).replace("(", "").replace("'", "").replace(",", "").replace(")", "").strip()
                release_id = str(ids[i]).replace("(", "").replace(",", "").replace(")", "").strip()
                result[name] = release_id
                i += 1
            return result

    # Получение русских названий релизов
    def get_releases_long_names(self, active=True, all_releases=False):
        with self.connection:
            additional_info = ''
            if active:
                additional_info = " WHERE active = TRUE"
            else:
                additional_info = " WHERE active = FALSE"
            
            if all_releases:
                additional_info = ''
            return self.cursor.execute("SELECT release_long_name FROM releases{}".format(additional_info)).fetchall()

    # Получение русского названий релиза по его ИД
    def get_release_long_name_by_id(self, release_id):
        with self.connection:
            return self.cursor.execute("SELECT release_long_name FROM releases WHERE release_id={}".format(release_id)).fetchall()

    # Добавление нового релиза в БД
    def add_release(self, release_id, release_short_name, release_long_name, site_id="NULL"):
        with self.connection:
            self.cursor.execute("INSERT INTO releases (release_id, site_id, release_short_name, release_long_name) VALUES ({}, NULL, '{}', '{}')".format(str(release_id), release_short_name, release_long_name)).fetchall()
            return 
    
    # Получение полной информации по статусу релиза (серии)
    def get_status(self, release_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM episodes WHERE release_id={}".format(str(release_id))).fetchall()
    
    # Получение информации об активности релиза
    def get_active_status(self, release_id):
        with self.connection:
            return self.cursor.execute("SELECT active FROM releases WHERE release_id={}".format(str(release_id))).fetchall()
    
    # Старт релиза, добавление новой серии на отслеживание
    def add_episodes_info(self, release_id, parameters):
        with self.connection:
            additional_params_column = ""
            additional_params = ""
            today = 0
            if (len(parameters) == 4):
                today = int(parameters[1])
                current_ep = parameters[2]
                max_ep = parameters[3]
                additional_params_column = ", today, current_ep, max_ep"
                additional_params = ", {}, {}, {}".format(today, current_ep, max_ep)
            if (len(parameters) == 3):
                today = int(parameters[1])
                current_ep = parameters[2]
                additional_params_column = ", today, current_ep"
                additional_params = ", {}, {}".format(today, current_ep)
            if (len(parameters) == 2):
                today = int(parameters[1])
                additional_params_column = ", today"
                additional_params = ", " + str(today)
            deadline = parameters[0]
            top_release = 0 if deadline > 2 else 1
            additional_params_column += ", subs, decor, voice, timing, fixs"
            if (deadline == 7):
                universal_status = "0" + "|" + str(today) + "|" + str(deadline)
                additional_params += ", " + "'{}', ".format(universal_status) * 4 + "'" + universal_status + "'"
            else:
                if (deadline == 4):
                    additional_params += ", '0|{0}|1', '0|{0}|1', '0|{0}|2', '0|{0}|3', '0|{0}|4'".format(str(today))
                else:
                    additional_params += ", '0|{0}|1', '0|{0}|1', '0|{0}|1', '0|{0}|2', '0|{0}|2'".format(str(today))       
            return self.cursor.execute("INSERT INTO episodes (release_id, top_release, deadline{}) VALUES ({}, {}, {}{})".format(
                additional_params_column, release_id, top_release, deadline, additional_params)).fetchall()

    # Изменение информации по релизу (серии)
    def edit_episodes_info(self, release_id, new_params):
        with self.connection:
            return self.cursor.execute("UPDATE episodes SET top_release = {}, current_ep = {}, max_ep = {}, today = {}, deadline = {}, subs = '{}', decor = '{}', voice = '{}', timing = '{}', fixs = '{}' WHERE release_id = {};".format(
                new_params[1], new_params[2], new_params[3], new_params[4], new_params[5], new_params[6], new_params[7], new_params[8], new_params[9], new_params[10], release_id)).fetchall()

    # Установка релиза неактивным
    def set_not_active_release(self, release_id):
        with self.connection:
            self.cursor.execute("UPDATE releases SET active = FALSE WHERE release_id = '{}';".format(release_id)).fetchall()

    # Закрытие подключения к БД
    def close(self):
        self.connection.close()