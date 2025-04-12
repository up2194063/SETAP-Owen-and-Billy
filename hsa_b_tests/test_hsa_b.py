import pytest
from hsa_b.db import get_db

#Fixtures (get used for each new test)
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def app():
    """Create a new app instance for each test."""
    from hsa_b import create_app
    app = create_app()
    with app.app_context():
#Need to initialise the databse for every test        
        db = get_db()
        db.execute("PRAGMA foreign_keys = ON;")
        
#Also need to make sure that pre-existing tables get dropped 
        try:
            db.execute("DROP TABLE IF EXISTS payments_users;")
            db.execute("DROP TABLE IF EXISTS tasks_users;")
            db.execute("DROP TABLE IF EXISTS users_groups;")
            db.execute("DROP TABLE IF EXISTS payments;")
            db.execute("DROP TABLE IF EXISTS tasks;")
            db.execute("DROP TABLE IF EXISTS groups;")
            db.execute("DROP TABLE IF EXISTS users;")
        except Exception as error:
            print(f"Error dropping tables: {error}")

#Database set up for testing
        db.execute("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        """)
        db.execute("""
            CREATE TABLE groups (
                group_id INTEGER PRIMARY KEY,
                group_name TEXT NOT NULL,
                group_description TEXT
            );
        """)
        db.execute("""
            CREATE TABLE payments (
                payment_id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                payment_name TEXT NOT NULL,
                payment_description TEXT,
                payment_deadline TEXT NOT NULL,
                payment_amount REAL NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
            );
        """)
        db.execute("""
            CREATE TABLE tasks (
                task_id INTEGER PRIMARY KEY,
                group_id INTEGER NOT NULL,
                task_name TEXT NOT NULL,
                task_description TEXT,
                task_deadline TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
            );
        """)
        db.execute("""
            CREATE TABLE payments_users (
                payment_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                payment_creator TEXT NOT NULL,
                CHECK (payment_creator IN ('Y', 'N')),
                FOREIGN KEY (payment_id) REFERENCES payments (payment_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            );
        """)
        db.execute("""
            CREATE TABLE tasks_users (
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                task_creator TEXT NOT NULL,
                CHECK (task_creator IN ('Y', 'N')),
                FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            );
        """)
        db.execute("""
            CREATE TABLE users_groups (
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                group_creator TEXT NOT NULL,
                CHECK (group_creator IN ('Y', 'N')),
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES groups (group_id) ON DELETE CASCADE
            );
        """)

        yield app
#These following tests are testing the robustness of registration
#Test 1: Testing that a new user is created when valid registration details are entered
def test_registration_success(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", ("owen25@gmail.com",)).fetchone()
        assert user is not None
#Additional check for redirect to login page
        assert response.status_code == 302

#Test 2: Ensuring correct error message when user has not entered a username
def test_registration_missing_username(client, app):
    response = client.post("/auth/register", data={
        "username": "",
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    assert b"Username is required." in response.data

#Test 3: Ensuring correct error message when user has not entered an email
def test_registration_missing_email(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "",
        "password": "Password123!"
    })
    
    assert b"Email is required." in response.data

#Test 4: Ensuring correct error message when user has not entered a password
def test_registration_missing_password(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": ""
    })
    
    assert b"Password is required." in response.data

#Test 5: Ensuring correct error message when user has entered a password that is too short
def test_registration_short_password(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "short"
    })
    
    assert b"Password must be at least 8 characters long" in response.data

#Test 6: Ensuring correct error message when user has entered a password that does not meet
#the other password requirements such as having a special character, Uppercase character etc.
def test_registration_invalid_password(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "password"
    })
    
    assert b"Password must contain at least: one number, one lowercase letter, one uppercase letter and one special character." in response.data  # Check for error message

#Test 7: Ensuring correct error message when user has attempted to register using an email that
#has already been used before
def test_registration_duplicate_email(client, app):
    # First registration
    client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    # Attempt to register again with the same email
    response = client.post("/auth/register", data={
        "username": "another_user",
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    assert b"Account with email owen25@gmail.com is already registered." in response.data  # Check for error message