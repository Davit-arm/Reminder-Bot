import sqlite3
import datetime
from datetime import datetime
import os
from dotenv import load_dotenv
import threading
import time
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
            return 'Task added successfully, to view your tasks use /see_tasks, i will be reminding you everyday before the deadline!'
        except sqlite3.Error as e:
            return f'A Database error occured, please contact the developer. Error details: {e}'
        except Exception as e:
            return f'An error occured, please contact the developer. Error details: {e}'
        
    def view_tasks(self, user_id):
        try:
            con = sqlite3.connect(self.db_name)
            with con:
                cur = con.cursor()
                cur.execute('''SELECT info, deadline FROM users WHERE user_id = ?''',(user_id,))
                rows = cur.fetchall()

                return rows
        except sqlite3.Error as e:
            return f'A Database error occured, please contact the developer. Error details: {e}'
        except Exception as e: 
            return f'An error occured, please contact the developer. Error details: {e}'
        

    def delete_task(self, user_id, info):
        try:
            con = sqlite3.connect(self.db_name)
            with con:
                cur = con.cursor()
                new_info = info.strip()
                cur.execute('''DELETE FROM users WHERE user_id = ? AND info = ?''',(user_id, new_info))
                return 'Task deleted successfully.'
        except sqlite3.Error as e:
            return f'A Database error occured, please contact the developer. Error details: {e}'
        except Exception as e:
            return f'An error occured, please contact the developer. Error details: {e}'
        
    def get_active_tasks(self, user_id):
        active_tasks = []
        try:
            con = sqlite3.connect(self.db_name)
            cur = con.cursor()
            with con:
                cur.execute('''SELECT user_id, info, deadline FROM users WHERE user_id = ?''',(user_id,))
                rows = cur.fetchall()
                for user_id,info, deadline in rows:
                    deadline_date = datetime.strptime(deadline, "%d-%m-%Y")
                    if deadline_date >= datetime.now():
                        active_tasks.append({"user_id":user_id,"info": info, "deadline": deadline_date})
                return active_tasks
                    
        except sqlite3.Error as e:
            print(f'A database error has occured, please contact the developer. Error details: {e}')
        except Exception as e:
            print(f'An error has occured, please contact the developer. Error details: {e}')

    def remind_users(self, bot, user_id):
        def _remind():
            
            reminded_tasks = set()
            while True:
                now = datetime.now()
                active_tasks = self.get_active_tasks(user_id)
                today_str = now.strftime("%d-%m-%Y")
                for task in active_tasks:
                    info = task['info']
                    deadline = task['deadline']
                    
                    


                    if deadline.date() >= now.date():
                        days_left =  (deadline.date() - now.date()).days
                        key = (user_id,info, today_str)


                        if key not in reminded_tasks:

                            if days_left == 0:
                                message = f'Reminder: Your task "{info}" is due today!'
                                
                            elif days_left == 1:
                                message = f'Reminder: Your task "{info}" is due tommorow!'
                                
                            else:
                                message = f'Reminder: Your task "{info}" is due {deadline.strftime("%d-%m-%Y")}!'
                                
                            bot.send_message(user_id, message)
                            reminded_tasks.add(key)
                time.sleep(3600) 
        threading.Thread(target=_remind, daemon=True).start()
        
                    

                            



if __name__ == '__main__':
    manager = DB_manager(os.getenv('DATABASE'))
    manager.make_tables()

