INSERT OR IGNORE INTO users (telegram_id, username, first_name) 
VALUES (123456789, 'test_user', 'Тест');

INSERT OR REPLACE INTO mood_entries (user_id, entry_date, mood_score, work_hours, sleep_hours, comment)
SELECT 
    (SELECT id FROM users WHERE telegram_id = 123456789),
    date('now', '-' || n || ' days'),
    CASE 
        WHEN n % 3 = 0 THEN 5
        WHEN n % 3 = 1 THEN 4
        ELSE 3
    END,
    4.0 + (n % 5),
    6.0 + (n % 3),
    CASE 
        WHEN n = 0 THEN 'Отличный день'
        WHEN n = 3 THEN 'Недоспал'
        WHEN n = 5 THEN 'Устал'
        WHEN n = 7 THEN 'Много работал'
        WHEN n = 10 THEN 'Выспался'
        WHEN n = 12 THEN 'Хорошо'
        ELSE NULL
    END
FROM (SELECT 0 as n UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 
       UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 
       UNION SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14);

INSERT OR IGNORE INTO user_settings (user_id, reminder_time)
SELECT id, '20:00:00' FROM users WHERE telegram_id = 123456789;