CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    reminder_time TEXT
);

CREATE TABLE records (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    date DATE,
    mood INTEGER CHECK (mood >= 1 AND mood <= 5),
    study_hours REAL CHECK (study_hours >= 0),
    sleep_hours REAL CHECK (sleep_hours >= 0),
    comment TEXT
);

CREATE INDEX idx_records_user_date ON records(user_id, date);
CREATE INDEX idx_records_date ON records(date);