import telebot
from dotenv import load_dotenv
from logic import DB_manager
import os
import time


load_dotenv()
API_TOKEN = os.getenv('BOT_TOKEN')
DATABASE = os.getenv('DATABASE')
bot = telebot.TeleBot(API_TOKEN)
manager = DB_manager(DATABASE)

#reminder
manager.remind_users(bot)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, """Hello, im a reminder bot""")
    
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_chat_action(message.chat.id, action='typing')
    bot.reply_to(message, """/generate <prompt> - Generate an image based on the given prompt.
                             /help - shows this help message""")

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
            response = manager.add_task(message.from_user.id, info, deadline, message.from_user.username)
            bot.reply_to(message,response)
            print(response)
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
    

        


bot.infinity_polling()

