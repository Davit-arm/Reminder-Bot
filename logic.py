import sqlite3
import datetime
import os
from dotenv import load_dotenv
import threading
load_dotenv()

class DB_manager():

    def __init__(self, db_name):
        self.db_name = db_name

    def make_tables(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users ( 
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    info TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    username TEXT)
''')
        con.commit()
        con.close()

    def add_task(self, user_id, info, deadline, username):
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute('''INSERT INTO users (user_id, info, deadline, username) VALUES (?,?,?,?)''',(user_id, info, deadline,username))
            con.commit()
            con.close()
            return 'Task added successfully.'
        except sqlite3.Error as e:
            return f'A Database error occured, please contact the developer. Error details: {e}'
        except Exception as e:
            return f'An error occured, please contact the developer. Error details: {e}'
        
    def view_tasks(self, user_id):
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute('''SELECT info, deadline FROM users WHERE user_id = ?''',(user_id))
            rows = cur.fetchall()
            con.commit()
            con.close()
            return rows
        except sqlite3.Error as e:
            return f'A Database error occured, please contact the developer. Error details: {e}'
        except Exception as e: 
            return f'An error occured, please contact the developer. Error details: {e}'
        

    def delete_task(self, user_id, info):
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            cur.execute('''DELETE FROM users WHERE user_id = ? AND info = ?''',(user_id, info,))
            con.commit()
            con.close()
            return 'Task deleted successfully.'
        except sqlite3.Error as e:
            return f'A Database error occured, please contact the developer. Error details: {e}'
        except Exception as e:
            return f'An error occured, please contact the developer. Error details: {e}'
        
    


if __name__ == '__main__':
    manager = DB_manager(os.getenv('DATABASE'))
    manager.make_tables()

