CREATE TABLE IF NOT EXISTS AUTHORS (
    author_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    ISBN TEXT
);
CREATE TABLE IF NOT EXISTS BOOKS (
    ISBN TEXT PRIMARY KEY,
    title TEXT,
    page_count INTEGER,
    average_rating INTEGER,
    author_name TEXT
);
CREATE TABLE IF NOT EXISTS BOOKS_AUTHORS (
    BA_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ISBN TEXT,
    author_id INTEGER
);
CREATE TABLE IF NOT EXISTS USERS (
    user_name  TEXT PRIMARY KEY,
    user_first_name TEXT,
    user_last_name TEXT,
    password TEXT    
);
CREATE TABLE IF NOT EXISTS USERS_BOOKS (
    UB_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    ISBN TEXT,
    Saved_Date TEXT
);

