import sqlite3

class SQLighter:

    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
    
    def get_active_releases(self, active=True):
        with self.connection:
            names = self.cursor.execute("SELECT release_name FROM releases WHERE active = TRUE").fetchall()
            ids = self.cursor.execute("SELECT release_id FROM releases WHERE active = TRUE").fetchall()
            print(ids)
            result = {}
            i = 0
            while (i < len(names)):
                name = str(names[i]).replace("(", "").replace("'", "").replace(",", "").replace(")", "").strip()
                release_id = str(ids[i]).replace("(", "").replace(",", "").replace(")", "").strip()
                result[name] = release_id
                i += 1
            return result
    
    def add_release(self, release_id, release_name, site_id="NULL"):
        with self.connection:
            return self.cursor.execute("INSERT INTO releases (release_id, site_id, release_name) VALUES ({}, NULL, '{}')".format(str(release_id), release_name)).fetchall()
    
    def close(self):
        self.connection.close()