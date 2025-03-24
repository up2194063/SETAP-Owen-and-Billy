-- ENABLE THE USE OF FOREIGN KEYS
PRAGMA foreign_keys = ON;

-- DROP TABLES IF PRE-EXISTING
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS payments_users;
DROP TABLE IF EXISTS tasks_users;
DROP TABLE IF EXISTS users_groups;



-- CREATE TABLE FOR USERS
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- CREATE TABLE FOR GROUPS
CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY,
    group_name TEXT NOT NULL,
    group_description TEXT
);

-- CREATE TABLE FOR PAYMENTS
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    payment_name TEXT NOT NULL,
    payment_description TEXT,
    payment_deadline TEXT NOT NULL,
    payment_amount REAL NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
);

-- CREATE TABLE FOR TASKS
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_deadline TEXT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
);

-- CREATE INTERSECTION TABLE FOR PAYMENTS AND USERS
CREATE TABLE payments_users (
    payment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (payment_id) REFERENCES payments (payment_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- CREATE INTERSECTION TABLE FOR TASKS AND USERS
CREATE TABLE tasks_users (
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- CREATE INTERSECTION TABLE FOR USERS AND GROUPS
CREATE TABLE users_groups (
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    group_creator TEXT NOT NULL,
    CHECK (group_creator IN ('Y', 'N')),
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
);
