import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, datetime
import threading
import time
import schedule
from config import BOT_TOKEN
from db_handler import DatabaseHandler
from analyzer import Analyzer

bot = telebot.TeleBot(BOT_TOKEN)
db = DatabaseHandler()
user_steps = {}
reminder_jobs = {}

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('➕ Записать день'))
    kb.add(KeyboardButton('📊 Статистика'))
    kb.add(KeyboardButton('📜 История'), KeyboardButton('⚙️ Настройки'))
    kb.add(KeyboardButton('❓ Помощь'), KeyboardButton('🗑 Очистить данные'))
    return kb

def send_daily_reminder(chat_id, bot_instance):
    try:
        bot_instance.send_message(
            chat_id,
            "⏰ Напоминание!\n\nНе забудь записать свой день:\n• настроение (1-5)\n• сколько работал\n• сколько спал\n\nНажми ➕ Записать день",
            reply_markup=main_menu()
        )
    except Exception as e:
        print(f"Ошибка напоминания {chat_id}: {e}")

def schedule_reminder_for_user(user_id, reminder_time, bot_instance):
    job_id = f"reminder_{user_id}"
    if job_id in reminder_jobs:
        schedule.cancel_job(reminder_jobs[job_id])
    job = schedule.every().day.at(reminder_time).do(send_daily_reminder, user_id, bot_instance)
    reminder_jobs[job_id] = job

def start_scheduler():
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)
    threading.Thread(target=run_scheduler, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message):
    db.connect()
    user_id = db.get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    reminder_time = db.get_reminder_time(user_id)
    db.close()
    
    schedule_reminder_for_user(message.from_user.id, reminder_time, bot)
    
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}!\n\nЯ трекер настроения и продуктивности.\n\nКаждый день записывай:\n• настроение (1-5)\n• сколько работал/учился\n• сколько спал\n\nКоманды:\n/add - записать день\n/stats - статистика\n/history - история\n/settings - настройки\n/clear - очистить данные\n/help - помощь\n\nИспользуй кнопки внизу",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['add'])
def add_command(message):
    user_steps[message.from_user.id] = {'step': 1}
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(InlineKeyboardButton('1', callback_data='m1'))
    kb.add(InlineKeyboardButton('2', callback_data='m2'))
    kb.add(InlineKeyboardButton('3', callback_data='m3'))
    kb.add(InlineKeyboardButton('4', callback_data='m4'))
    kb.add(InlineKeyboardButton('5', callback_data='m5'))
    bot.send_message(message.chat.id, "Оцени свое настроение сегодня от 1 до 5, где 1 — ужасно, 5 — отлично.", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '➕ Записать день')
def add_button(message):
    user_steps[message.from_user.id] = {'step': 1}
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(InlineKeyboardButton('1', callback_data='m1'))
    kb.add(InlineKeyboardButton('2', callback_data='m2'))
    kb.add(InlineKeyboardButton('3', callback_data='m3'))
    kb.add(InlineKeyboardButton('4', callback_data='m4'))
    kb.add(InlineKeyboardButton('5', callback_data='m5'))
    bot.send_message(message.chat.id, "Оцени свое настроение сегодня от 1 до 5, где 1 — ужасно, 5 — отлично.", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('m'))
def process_mood(c):
    uid = c.from_user.id
    mood = int(c.data[1])
    user_steps[uid]['mood'] = mood
    user_steps[uid]['step'] = 2
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add('0.5', '1', '2', '4', 'Другое')
    bot.edit_message_text(f"Настроение: {mood}/5\n\nСколько часов ты потратил на полезную работу/учебу?", c.message.chat.id, c.message.message_id)
    bot.send_message(c.message.chat.id, "Введи количество часов:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.from_user.id in user_steps and user_steps[m.from_user.id].get('step') == 2)
def process_work(m):
    uid = m.from_user.id
    if m.text == 'Другое':
        bot.send_message(m.chat.id, "Напиши количество часов (например 3.5):")
        return
    try:
        work = float(m.text)
        if work < 0 or work > 24:
            bot.send_message(m.chat.id, "Введи число от 0 до 24")
            return
    except:
        bot.send_message(m.chat.id, "Введи число, например 4 или 5.5")
        return
    user_steps[uid]['work'] = work
    user_steps[uid]['step'] = 3
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add('6', '7', '8', '9', 'Другое')
    bot.send_message(m.chat.id, f"Работа/учеба: {work} ч\n\nСколько часов ты спал?", reply_markup=kb)

@bot.message_handler(func=lambda m: m.from_user.id in user_steps and user_steps[m.from_user.id].get('step') == 3)
def process_sleep(m):
    uid = m.from_user.id
    if m.text == 'Другое':
        bot.send_message(m.chat.id, "Напиши количество часов сна (например 7.5):")
        return
    try:
        sleep = float(m.text)
        if sleep < 0 or sleep > 24:
            bot.send_message(m.chat.id, "Введи число от 0 до 24")
            return
    except:
        bot.send_message(m.chat.id, "Введи число, например 7 или 8.5")
        return
    user_steps[uid]['sleep'] = sleep
    user_steps[uid]['step'] = 4
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('Пропустить', callback_data='skip'))
    bot.send_message(m.chat.id, f"Сон: {sleep} ч\n\nХочешь добавить комментарий? (Напиши текст или нажми «Пропустить»)", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == 'skip')
def skip_comment(c):
    save_to_db(c.message, c.from_user.id, None)

@bot.message_handler(func=lambda m: m.from_user.id in user_steps and user_steps[m.from_user.id].get('step') == 4)
def process_comment(m):
    save_to_db(m, m.from_user.id, m.text)

def save_to_db(msg, uid, comment):
    data = user_steps[uid]
    db.connect()
    user_id = db.get_or_create_user(uid, msg.from_user.username, msg.from_user.first_name)
    db.save_entry(user_id, date.today(), data['mood'], data['work'], data['sleep'], comment)
    db.close()
    txt = f"✅ Данные сохранены!\n\nНастроение: {data['mood']}/5\nРабота: {data['work']} ч\nСон: {data['sleep']} ч"
    if comment:
        txt += f"\nКомментарий: {comment}"
    del user_steps[uid]
    bot.send_message(msg.chat.id, txt, reply_markup=main_menu())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('За неделю', callback_data='stat_week'),
        InlineKeyboardButton('За месяц', callback_data='stat_month'),
        InlineKeyboardButton('Мои инсайты', callback_data='stat_insights'),
        InlineKeyboardButton('График', callback_data='stat_graph')
    )
    bot.send_message(message.chat.id, "Что хочешь узнать?", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '📊 Статистика')
def stats_button(message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton('За неделю', callback_data='stat_week'),
        InlineKeyboardButton('За месяц', callback_data='stat_month'),
        InlineKeyboardButton('Мои инсайты', callback_data='stat_insights'),
        InlineKeyboardButton('График', callback_data='stat_graph')
    )
    bot.send_message(message.chat.id, "Что хочешь узнать?", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith('stat_'))
def show_statistics(c):
    uid = c.from_user.id
    db.connect()
    user_id = db.get_or_create_user(uid, None, None)
    
    if c.data == 'stat_week':
        data = db.get_weekly(user_id)
        if not data:
            bot.send_message(c.message.chat.id, "Нет данных за неделю")
        else:
            avg_m = sum(d['mood_score'] for d in data) / len(data)
            avg_w = sum(d['work_hours'] for d in data) / len(data)
            avg_s = sum(d['sleep_hours'] for d in data) / len(data)
            bot.send_message(c.message.chat.id, f"📊 ЗА НЕДЕЛЮ\n\nДней: {len(data)}\nСреднее настроение: {avg_m:.1f}/5\nСредняя работа: {avg_w:.1f} ч\nСредний сон: {avg_s:.1f} ч")
    
    elif c.data == 'stat_month':
        data = db.get_monthly(user_id)
        if not data:
            bot.send_message(c.message.chat.id, "Нет данных за месяц")
        else:
            avg_m = sum(d['mood_score'] for d in data) / len(data)
            avg_w = sum(d['work_hours'] for d in data) / len(data)
            avg_s = sum(d['sleep_hours'] for d in data) / len(data)
            bot.send_message(c.message.chat.id, f"📊 ЗА МЕСЯЦ\n\nДней: {len(data)}\nСреднее настроение: {avg_m:.1f}/5\nСредняя работа: {avg_w:.1f} ч\nСредний сон: {avg_s:.1f} ч")
    
    elif c.data == 'stat_insights':
        data = db.get_all(user_id)
        if len(data) < 5:
            bot.send_message(c.message.chat.id, "Нужно минимум 5 дней записей для анализа")
        else:
            insights = Analyzer.get_insights(data)
            bot.send_message(c.message.chat.id, insights)
    
    elif c.data == 'stat_graph':
        data = db.get_all(user_id)
        if len(data) < 2:
            bot.send_message(c.message.chat.id, "Нужно минимум 2 дня для графика")
        else:
            img = Analyzer.make_graph(data)
            bot.send_photo(c.message.chat.id, img)
    
    db.close()
    bot.answer_callback_query(c.id)

@bot.message_handler(commands=['history'])
def history_command(message):
    uid = message.from_user.id
    db.connect()
    user_id = db.get_or_create_user(uid, None, None)
    data = db.get_monthly(user_id)
    db.close()
    if not data:
        bot.send_message(message.chat.id, "Нет записей. Нажми «Записать день»")
        return
    txt = "📜 ИСТОРИЯ (последние 10 записей)\n\n"
    for i, row in enumerate(data[:10]):
        d = row['entry_date']
        txt += f"{i+1}. {d} | Настроение: {row['mood_score']}/5 | Работа: {row['work_hours']}ч | Сон: {row['sleep_hours']}ч\n"
        if row['comment']:
            txt += f"   Комментарий: {row['comment']}\n"
    bot.send_message(message.chat.id, txt)

@bot.message_handler(func=lambda m: m.text == '📜 История')
def history_button(message):
    uid = message.from_user.id
    db.connect()
    user_id = db.get_or_create_user(uid, None, None)
    data = db.get_monthly(user_id)
    db.close()
    if not data:
        bot.send_message(message.chat.id, "Нет записей. Нажми «Записать день»")
        return
    txt = "📜 ИСТОРИЯ (последние 10 записей)\n\n"
    for i, row in enumerate(data[:10]):
        d = row['entry_date']
        txt += f"{i+1}. {d} | Настроение: {row['mood_score']}/5 | Работа: {row['work_hours']}ч | Сон: {row['sleep_hours']}ч\n"
        if row['comment']:
            txt += f"   Комментарий: {row['comment']}\n"
    bot.send_message(message.chat.id, txt)

@bot.message_handler(commands=['settings'])
def settings_command(message):
    uid = message.from_user.id
    db.connect()
    user_id = db.get_or_create_user(uid, None, None)
    current_time = db.get_reminder_time(user_id)
    db.close()
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(f'Изменить время напоминания (сейчас {current_time[:5]})', callback_data='set_time'),
        InlineKeyboardButton('Оставить как есть', callback_data='settings_close')
    )
    bot.send_message(message.chat.id, f"⚙️ НАСТРОЙКИ\n\nСейчас напоминания приходят в {current_time[:5]}\n\nВыбери действие:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '⚙️ Настройки')
def settings_button(message):
    uid = message.from_user.id
    db.connect()
    user_id = db.get_or_create_user(uid, None, None)
    current_time = db.get_reminder_time(user_id)
    db.close()
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(f'Изменить время напоминания (сейчас {current_time[:5]})', callback_data='set_time'),
        InlineKeyboardButton('Оставить как есть', callback_data='settings_close')
    )
    bot.send_message(message.chat.id, f"⚙️ НАСТРОЙКИ\n\nСейчас напоминания приходят в {current_time[:5]}\n\nВыбери действие:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == 'set_time')
def ask_new_time(c):
    bot.edit_message_text("Введи новое время для напоминаний в формате ЧЧ:ММ (например 21:00)", c.message.chat.id, c.message.message_id)
    bot.register_next_step_handler(c.message, save_new_time)

def save_new_time(message):
    try:
        time_str = message.text.strip()
        datetime.strptime(time_str, '%H:%M')
        db.connect()
        user_id = db.get_or_create_user(message.from_user.id, None, None)
        db.set_reminder_time(user_id, f"{time_str}:00")
        schedule_reminder_for_user(message.from_user.id, f"{time_str}:00", bot)
        db.close()
        bot.send_message(message.chat.id, f"✅ Время напоминания изменено на {time_str}", reply_markup=main_menu())
    except:
        bot.send_message(message.chat.id, "❌ Неправильный формат. Используй ЧЧ:ММ (например 21:00)", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: c.data == 'settings_close')
def close_settings(c):
    bot.edit_message_text("Настройки сохранены", c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id)

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, 
        "ПОМОЩЬ\n\n"
        "Команды:\n"
        "/start - запуск бота\n"
        "/add - записать данные за сегодня\n"
        "/stats - показать статистику\n"
        "/history - история записей\n"
        "/settings - настройки времени напоминаний\n"
        "/clear - очистить все данные\n\n"
        "Как записать день:\n"
        "1. Нажми «Записать день» или /add\n"
        "2. Выбери настроение (1-5)\n"
        "3. Введи часы работы/учебы\n"
        "4. Введи часы сна\n"
        "5. Добавь комментарий (по желанию)")

@bot.message_handler(func=lambda m: m.text == '❓ Помощь')
def help_button(message):
    bot.send_message(message.chat.id, 
        "ПОМОЩЬ\n\n"
        "Команды:\n"
        "/start - запуск бота\n"
        "/add - записать данные за сегодня\n"
        "/stats - показать статистику\n"
        "/history - история записей\n"
        "/settings - настройки времени напоминаний\n"
        "/clear - очистить все данные\n\n"
        "Как записать день:\n"
        "1. Нажми «Записать день» или /add\n"
        "2. Выбери настроение (1-5)\n"
        "3. Введи часы работы/учебы\n"
        "4. Введи часы сна\n"
        "5. Добавь комментарий (по желанию)")

@bot.message_handler(commands=['clear'])
def clear_command(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('Да, очистить всё', callback_data='clear_yes'))
    kb.add(InlineKeyboardButton('Нет, отмена', callback_data='clear_no'))
    bot.send_message(message.chat.id, "⚠️ Ты уверен? Все данные будут удалены безвозвратно.", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text == '🗑 Очистить данные')
def clear_button(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton('Да, очистить всё', callback_data='clear_yes'))
    kb.add(InlineKeyboardButton('Нет, отмена', callback_data='clear_no'))
    bot.send_message(message.chat.id, "⚠️ Ты уверен? Все данные будут удалены безвозвратно.", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data in ['clear_yes', 'clear_no'])
def process_clear(c):
    if c.data == 'clear_yes':
        uid = c.from_user.id
        db.connect()
        user_id = db.get_or_create_user(uid, None, None)
        db.delete_all(user_id)
        db.close()
        bot.edit_message_text("✅ Все данные очищены", c.message.chat.id, c.message.message_id)
    else:
        bot.edit_message_text("❌ Отмена", c.message.chat.id, c.message.message_id)
    bot.answer_callback_query(c.id)

if __name__ == "__main__":
    print("Бот запущен")
    start_scheduler()
    bot.polling()