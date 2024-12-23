import sqlite3

class DbClient:
    def __init__(self, db_file_path):
        print("making a connection...")
        self._connection = sqlite3.connect(db_file_path)

    def close(self):
        print("closing the connection...")
        self._connection.close()

    def query(self, statement, params):
        cursor = self._connection.cursor()
        result = cursor.execute(statement, params)
        self._connection.commit()
     
        return result
    
