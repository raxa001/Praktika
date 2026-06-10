import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import db
import stats
from datetime import datetime
import threading
import time
import requests

# Если используешь прокси - раскомментируй и укажи свои настройки
# proxy_url = 'socks5://127.0.0.1:9150'  # для Tor
# или
# proxy_url = 'http://username:password@ip:port'  # для HTTP прокси

# telebot.apihelper.proxy = {'http': proxy_url, 'https': proxy_url}

bot = telebot.TeleBot('8882488095:AAFG5kP5qbu_d5Ye7t44YVP25Jz7S7wiook')

user_step = {}
user_temp = {}

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Записать де'), KeyboardButton('Статистик'))
    markup.add(KeyboardButton('Хьа Историй'), KeyboardButton('Настройки'))
    markup.add(KeyboardButton('Очистить данные'), KeyboardButton('Новкъостал'))
    return markup

def check_reminders():
    while True:
        now = datetime.now().strftime('%H:%M')
        users = db.get_all_users()
        for user_id, remind_time in users:
            if remind_time == now:
                try:
                    bot.send_message(user_id, 'Напоминаю! Д1аязде хьан де х1инца.', reply_markup=main_menu())
                except:
                    pass
        time.sleep(60)

reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

@bot.message_handler(commands=['start'])
def start_message(message):
    db.create_user(message.chat.id)
    bot.send_message(message.chat.id, 'Ассалам алейку! Со бот для отслеживания настроения и продуктивности ва.\n\n Аз хьон г1о дег да ха - мишта набаро е дешаро е влиять ду хьа настроенен.\n\nКнопкажт п1елгаж 1ат те1де.', reply_markup=main_menu())

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Хьа новкъости командаж:\n\n/start - болх д1абувл бе\n/add - тахан 1а даьр записывать деж кнопк\n/stats - б1архьаж статистика\n/history - хьа ерриг историй\n/settings - напоминаний ха хувц воали хьо?\n/clear - д1адах деррига данныж\n/help - новкъостал эший?')

@bot.message_handler(commands=['add'])
def add_command(message):
    start_add(message)

@bot.message_handler(commands=['stats'])
def stats_command(message):
    show_stats_menu(message)

@bot.message_handler(commands=['history'])
def history_command(message):
    show_history(message)

@bot.message_handler(commands=['settings'])
def settings_command(message):
    bot.send_message(message.chat.id, 'Укхаз 1оязде напоминаний ха ЧЧ:ММ (массала 19:00)', reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Отмена')))
    user_step[message.chat.id] = 'waiting_time'

@bot.message_handler(commands=['clear'])
def clear_command(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('хьау, даяхк', callback_data='confirm_clear'))
    markup.add(InlineKeyboardButton('а, ма яхк', callback_data='cancel_clear'))
    bot.send_message(message.chat.id, 'Точно удалить де воали хьо данныяж? т1ехьа бал хуг ба хьон', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Записать де')
def start_add(message):
    user_step[message.chat.id] = 'mood'
    markup = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 6):
        buttons.append(InlineKeyboardButton(str(i), callback_data=f'mood_{i}'))
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'НАстроений мишт я хьа от 1до5 ? \n1 - му я, 5 - покайфу я', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Статистик')
def show_stats_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Укх к1ер', callback_data='stats_week'))
    markup.add(InlineKeyboardButton('Укх бетт', callback_data='stats_month'))
    markup.add(InlineKeyboardButton('Инсайтаж', callback_data='stats_insights'))
    bot.send_message(message.chat.id, 'выбрать дел период статистики:', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Хьа Историй')
def show_history(message):
    data = db.get_all_records(message.chat.id)
    if not data:
        bot.send_message(message.chat.id, 'Хьог пока записяж яц братан!')
        return
    
    text = 'Хьа записяж:\n\n'
    for row in data:
        text += f'{row[0]} | Настроений: {row[1]} | Дешар: {row[2]}ч | Наб: {row[3]}ч\n'
        if row[4]:
            text += f'Йовхар: {row[4]}\n'
        text += '---\n'
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: message.text == 'Настройки')
def settings_button(message):
    settings_command(message)

@bot.message_handler(func=lambda message: message.text == 'Очистить данные')
def clear_button(message):
    clear_command(message)

@bot.message_handler(func=lambda message: message.text == 'Новкъостал')
def help_button(message):
    help_message(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    
    if call.data.startswith('mood_'):
        mood = int(call.data.split('_')[1])
        user_temp[chat_id] = {'mood': mood}
        user_step[chat_id] = 'study'
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('1'), KeyboardButton('2'), KeyboardButton('4'))
        markup.add(KeyboardButton('6'), KeyboardButton('8'), KeyboardButton('Другое'))
        bot.edit_message_text('Мас сахьт доа ду 1а дешара е болха?', chat_id, call.message.message_id)
        bot.send_message(chat_id, 'Е предложеный вариант выбрать де, е хьай число 1оязде', reply_markup=markup)
    
    elif call.data.startswith('study_'):
        hours = float(call.data.split('_')[1])
        user_temp[chat_id]['study'] = hours
        user_step[chat_id] = 'sleep'
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('6'), KeyboardButton('7'), KeyboardButton('8'))
        markup.add(KeyboardButton('9'), KeyboardButton('Вождар'))
        bot.send_message(chat_id, 'Мас сахьта наб яй 1а?', reply_markup=markup)
    
    elif call.data == 'skip_comment':
        user_temp[chat_id]['comment'] = None
        save_record(chat_id)
    
    elif call.data == 'confirm_clear':
        db.clear_user_data(chat_id)
        bot.edit_message_text('Хьа мел ду данныяж удалить дер аз 🤣🤣🤣', chat_id, call.message.message_id)
    
    elif call.data == 'cancel_clear':
        bot.edit_message_text('Удаление отменено.', chat_id, call.message.message_id)
    
    elif call.data.startswith('stats_'):
        if call.data == 'stats_week':
            result = stats.get_week_stats(chat_id)
        elif call.data == 'stats_month':
            result = stats.get_month_stats(chat_id)
        elif call.data == 'stats_insights':
            result = stats.get_insights(chat_id)
        bot.send_message(chat_id, result)

@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == 'study')
def get_study_hours(message):
    chat_id = message.chat.id
    try:
        if message.text == 'Другое':
            bot.send_message(chat_id, 'Кол-во часов 1ояжде:')
            return
        hours = float(message.text)
        user_temp[chat_id]['study'] = hours
        user_step[chat_id] = 'sleep'
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('6'), KeyboardButton('7'), KeyboardButton('8'))
        markup.add(KeyboardButton('9'), KeyboardButton('Вождар'))
        bot.send_message(chat_id, 'Мас сахьта наб яй 1а?', reply_markup=markup)
    except:
        bot.send_message(chat_id, '1ояжде число (массала 5 или 4.5)')

@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == 'sleep')
def get_sleep_hours(message):
    chat_id = message.chat.id
    try:
        if message.text == 'Вождар':
            bot.send_message(chat_id, 'Кол-во часов 1оязде:')
            return
        hours = float(message.text)
        user_temp[chat_id]['sleep'] = hours
        user_step[chat_id] = 'comment'
        
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Пропустить де'))
        bot.send_message(chat_id, 'к1еззиг комментарий язде воали хьо? Е цхьа хьам 1ояздее , е пропустить де 1отоъе', reply_markup=markup)
    except:
        bot.send_message(chat_id, '1ояжде число (Массала 7 или 7.5)')

@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == 'waiting_time')
def save_reminder_time(message):
    chat_id = message.chat.id
    if message.text == 'Отмена':
        bot.send_message(chat_id, 'Настройк отменить яр', reply_markup=main_menu())
        user_step.pop(chat_id, None)
        return
    
    try:
        time_str = message.text
        datetime.strptime(time_str, '%H:%M')
        db.save_reminder_time(chat_id, time_str)
        bot.send_message(chat_id, f'Время напоминия установить яр на {time_str}', reply_markup=main_menu())
        user_step.pop(chat_id, None)
    except:
        bot.send_message(chat_id, 'Харца формат. Ха 1оязди ишт ЧЧ:ММ (Массала 19:00)')

@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == 'comment')
def get_comment(message):
    chat_id = message.chat.id
    if message.text == 'Пропустить де':
        user_temp[chat_id]['comment'] = None
    else:
        user_temp[chat_id]['comment'] = message.text
    save_record(chat_id)

def save_record(chat_id):
    data = user_temp[chat_id]
    db.add_record(chat_id, data['mood'], data['study'], data['sleep'], data['comment'])
    bot.send_message(chat_id, 'Все данныЯЖ сохранить дер! Баркал новкъост.', reply_markup=main_menu())
    user_step.pop(chat_id, None)
    user_temp.pop(chat_id, None)


print('Проверк юдаж латт')
bot.get_me()
print('Все, бот хьаэттар')

bot.polling()