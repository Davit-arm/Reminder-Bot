import telebot
from dotenv import load_dotenv
from logic import DB_manager
import os
import time
import datetime
from datetime import datetime
import threading
import schedule

load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
DATABASE = os.getenv('DATABASE')
bot = telebot.TeleBot(API_TOKEN)
manager = DB_manager(DATABASE)

# def remind(user_id):
#     while True:
#         try:

#             now = datetime.now().date()
#             #now = now_date.strftime("%d-%m-%Y")
#             active_tasks = manager.get_active_tasks(user_id)
#             tasks_to_remove = []
#             for task in active_tasks:
#                 user_id = task['user_id']
#                 info = task['info']
#                 deadline = task['deadline']
#                 days_left = (deadline - now).days
#                 if days_left == 0:
#                     bot.send_message(user_id, f'Reminder: Your task: "{info}" is due today!')
#                     tasks_to_remove.append(task)
#                 elif days_left == 1:
#                     bot.send_message(user_id, f'Reminder: Your task: "{info}" is due tommorow!')
#                 else:
#                     bot.send_message(user_id, f'Reminder: Your task: "{info}" is due on {deadline.strftime("%m-%d-%Y")}!')

#             for old_tasks in tasks_to_remove:
#                 active_tasks.remove(old_tasks)
#         except Exception as e:
#             print(f'An error has occured in the reminder function, please contact the developer. Error details: {e}')

# def reminder_start(user_id):
#         try:
#             schedule.every(1).hours.do(remind, user_id)

#             while True:
#                 schedule.run_pending()
#                 time.sleep(1)
#         except Exception as e:
#             print(f'An error has occured while starting reminders, please contact the developer, error info:{e}')



@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, """Hello, im a reminder bot, i can help you keep tracks of your tasks and deadlines. When you add  new task
i save them in my database, and every hour check if you have any tasks with deadlines approaching, if so
i will send you a reminder message every day. to get started use /help command to see all the available commands.""")
    
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_chat_action(message.chat.id, action='typing')
    bot.reply_to(message, """/add <info about the task or just a name>, <deadline(mm-dd-yyyy)> - adds a new task with a deadline
(DONT FORGET THE COMMA BETWEEN THE TASK AND THE DEADLINE!!!)
/see_tasks - shows you all the tasks you have added so far
/delete <info about the task or just a name> - deletes the task with the given info""")

@bot.message_handler(commands=['add'])
def add(message):
    bot.send_chat_action(message.chat.id, action='typing')
    try:
        content = message.text[len('/add '):]
        if ',' not in content:
            bot.reply_to(message, 'please add a comma (,) between the task and the deadline')
        else:
            info, deadline = content.rsplit(',',1)
            info = info.strip()
            deadline = deadline.strip()
            user_id = message.from_user.id
            response = manager.add_task(user_id, info, deadline, message.from_user.username)
            bot.reply_to(message,response)
            try:
                #reminder_thread = threading.Thread(target=reminder_start,daemon=True)
                #reminder_thread.start()
                bot.send_message(message.chat.id, 'Reminder has started for your tasks!')
                print('reminder started')
            except Exception as e:
                bot.send_message(message.chat.id, f'An error has occured while starting reminders, please contact the developer, error info:{e}')
                print(e)
            # print(response)
            # #starting a reminder thread everytime a new task is added
            # try:
            #     time.sleep(2) #waiting for 2 seconds to ensure that the task is added before the reminder starts, to prevent an error
            #     manager.remind_users(bot,user_id)
            #     bot.send_message(message.chat.id, 'Reminder has started for your tasks!')
            #     print('reminder started')
            # except Exception as e:
            #     bot.send_message(message.chat.id, f'An error has occured while starting reminders, please contact the developer, error info:{e}')
            #     print(e)
    except Exception as e:
        bot.reply_to(message, f'An error has occured, please contact the developer, error info:{e}')
        print(e)

@bot.message_handler(commands=['see_tasks'])
def tasks(message):
    bot.send_chat_action(message.chat.id, action='typing')
    delete = bot.send_message(message.chat.id, 'Fetching your tasks, this might take a while...')
    try:
        tasks = manager.view_tasks(message.from_user.id)
        if len(tasks) == 0:
            bot.send_message(message.chat.id, 'You have no tasks added yet, use /add to add a task.')
        else:
            bot.send_message(message.chat.id, 'Here are your tasks:')
            tasks_sorted = ''
            for idx, (info, deadline) in enumerate(tasks,start=1):
                tasks_sorted += f'{idx}. Task: {info} | Deadline: {deadline}\n'
            bot.send_message(message.chat.id, tasks_sorted)
            bot.delete_message(message.chat.id, delete.message_id)
    except Exception as e:
        bot.reply_to(message, f'An error has occured, please contact the developer, error info:{e}')
        print(tasks)
        print(e)
    

@bot.message_handler(commands=['delete'])
def delete(message):
    info = ' '.join(message.text.split()[1:])
    bot.send_chat_action(message.chat.id, action='typing')
    try:
        response = manager.delete_task(message.from_user.id, info)
        bot.reply_to(message,response)
        print(response)
    except Exception as e:
        bot.reply_to(message, f'An error has occured, please contact the developer, error info:{e}')
    
def remind():
    
    try:
        users_ids = manager.get_all_users()
        now = datetime.now().date()
        #now = now_date.strftime("%d-%m-%Y")
        for user_id in users_ids:
            active_tasks = manager.get_active_tasks(user_id)
            #tasks_to_remove = []
            for task in active_tasks:
                info = task['info']
                deadline = task['deadline']
                days_left = (deadline - now).days
                if days_left == 0:
                    bot.send_message(user_id, f'Reminder: Your task: "{info}" is due today!')
                    time.sleep(1)
                    manager.delete_task(user_id, info)
                elif days_left == 1:
                    bot.send_message(user_id, f'Reminder: Your task: "{info}" is due tommorow!')
                else:
                    bot.send_message(user_id, f'Reminder: Your task: "{info}" is due on {deadline.strftime("%m-%d-%Y")}!')

        # for old_tasks in tasks_to_remove:
        #     active_tasks.remove(old_tasks)
    except Exception as e:
        print(f'An error has occured in the reminder function, please contact the developer. Error details: {e}')

def reminder_start():
        try:
            remind()
            schedule.every(1).hours.do(remind)

            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            print(f'An error has occured while starting reminders, please contact the developer, error info:{e}')


        




if __name__ == '__main__':
    manager = DB_manager(DATABASE)
    reminder_thread = threading.Thread(target=reminder_start, daemon=True)
    reminder_thread.start()
    manager.make_tables()
    bot.infinity_polling()
    

