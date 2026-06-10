import db

def get_week_stats(user_id):
    records = db.get_records_by_period(user_id, 7)
    if not records:
        return 'За последнюю неделю цхьаккха хьам яц. цхьа записаяж добавить е.'
    
    total_mood = 0
    total_study = 0
    total_sleep = 0
    days = len(records)
    
    for row in records:
        total_mood += row[1]
        total_study += row[2]
        total_sleep += row[3]
    
    avg_mood = total_mood / days
    avg_study = total_study / days
    avg_sleep = total_sleep / days
    
    text = f'Статистик укз к1ера:\n'
    text += f'Всего дней: {days}\n'
    text += f'Среднее настроение: {avg_mood:.1f}\n'
    text += f'Средние часы учебы: {avg_study:.1f}\n'
    text += f'Средние часы сна: {avg_sleep:.1f}\n'
    
    return text

def get_month_stats(user_id):
    records = db.get_records_by_period(user_id, 30)
    if not records:
        return 'За последний месяц цхьаккха хьам яц. цхьа записаяж добавить е'
    
    total_mood = 0
    total_study = 0
    total_sleep = 0
    days = len(records)
    good_days = 0
    
    for row in records:
        total_mood += row[1]
        total_study += row[2]
        total_sleep += row[3]
        if row[1] >= 4:
            good_days += 1
    
    avg_mood = total_mood / days
    avg_study = total_study / days
    avg_sleep = total_sleep / days
    
    text = f'Статистика за месяц:\n'
    text += f'Всего дней: {days}\n'
    text += f'Хороших дней: {good_days}\n'
    text += f'Среднее настроение: {avg_mood:.1f}\n'
    text += f'Средние часы учебы: {avg_study:.1f}\n'
    text += f'Средние часы сна: {avg_sleep:.1f}\n'
    
    return text

def get_insights(user_id):
    records = db.get_records_by_period(user_id, 30)
    if len(records) < 5:
        return 'Нужно больше данных братецц. Добавь записи за 5+ дней.'
    
    sleep_groups = {}
    study_groups = {}
    
    for row in records:
        mood = row[1]
        study = row[2]
        sleep = row[3]
        
        if sleep < 7:
            sleep_key = 'к1еззиг'
        elif sleep <= 9:
            sleep_key = 'мег да хьон'
        else:
            sleep_key = 'дукх'
            
        if sleep_key not in sleep_groups:
            sleep_groups[sleep_key] = []
        sleep_groups[sleep_key].append(mood)
        
        if study < 2:
            study_key = 'к1еззиг'
        elif study <= 6:
            study_key = 'мег да хьон'
        else:
            study_key = 'дукх'
            
        if study_key not in study_groups:
            study_groups[study_key] = []
        study_groups[study_key].append(mood)
    
    text = 'Хьа инсайтаж:\n\n'
    
    if 'мег да хьон' in sleep_groups:
        avg_norm = sum(sleep_groups['мег да хьон']) / len(sleep_groups['мег да хьон'])
        if 'к1еззиг' in sleep_groups:
            avg_low = sum(sleep_groups['к1еззиг']) / len(sleep_groups['к1еззиг'])
            if avg_norm > avg_low:
                text += f'Массала 7-9 сахьата наб еж вакх хьо, настроение на {avg_norm - avg_low:.1f} балла выше чем при сне меньше 7 часов.\n'
    
    if 'мег да хьон' in study_groups:
        avg_norm = sum(study_groups['мег да хьон']) / len(study_groups['мег да хьон'])
        if 'дукх' in study_groups:
            avg_high = sum(study_groups['дукх']) / len(study_groups['дукх'])
            if avg_high < avg_norm:
                text += f'Массала 6 сахььта дешаш ва хьо, настроение падает на {avg_norm - avg_high:.1f} балла.\n'
    
    if text == 'Хьа инсайтаж:\n\n':
        text += 'Д1аху хьай дневник заполнять де, усахахьат выводаж яг е вай'
    
    return text
