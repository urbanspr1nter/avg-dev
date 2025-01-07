import sqlite3
# DB Client 
class DbClient:
    def __init__(self, db_file_path):
        self._connection = sqlite3.connect(db_file_path)
        self._cursor = self._connection.cursor()

    def close(self):
        self._connection.close()

    def query(self, statement, params):
        result = self._cursor.execute(statement, params)
        self._connection.commit()
        
        return result

    def last_row_id(self):
        return self._cursor.lastrowid
    
