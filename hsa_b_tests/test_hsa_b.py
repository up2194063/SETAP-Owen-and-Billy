import pytest
from hsa_b.db import get_db

# Helper function to register a user
def register_user(client, username="owen", email="owen25@gmail.com", password="Password123!"):
   return client.post("/auth/register", data={
      "username": username,
     "email": email,
    "password": password
})

# Helper function to login a user
def login_user(client, email="owen25@gmail.com", password="Password123!"):
    return client.post("/auth/login", data={
        "email": email,
        "password": password
    })

# Helper function to create a group
def create_group(client, group_name="g1", group_description="this is g1"):
    return client.post("/create", data={
        "group_name": group_name,
        "group_description": group_description
    })

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

#REGISTRATION

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

#TESTING LOGIN

#Test 1: Test successful login with valid credentials

def test_login_success(client, app):
    # Register a user first using the helper function
    register_user(client)

    # Log in with valid credentials
    response = client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })

    assert response.status_code == 302  # Should redirect after successful login
    assert response.location.endswith("/")  # Ensure redirection to groups or main page

#Test 2: Test correct response when an incorrect email is used
def test_login_incorrect_email(client, app):
    register_user(client)
    response = client.post('/auth/login', data={'email': 'incorrect@gmail.com', 'password': 'Password123!'})
    assert response.status_code == 200  # Expect a 200 OK status when the error page renders
    assert b'Incorrect email.' in response.data  # Check for the error message

#Test 3: Test correct response when an incorrect password is used
def test_login_incorrect_password(client, app):
    register_user(client)
    # Attempt to log in with invalid credentials
    response = client.post('/auth/login', data={'email': 'owen25@gmail.com', 'password': 'invalidPassword'})
    
    # Ensure that the response code is 200 (login page is rendered again after the error)
    assert response.status_code == 200

    # Check if the flash message for incorrect password is present in the response body (rendered HTML)
    assert b'Incorrect password.' in response.data  # Check for the error message in HTML

    
    
#TESTING GROUP PAGE

# Test 1: Test successful creation of a group
def test_group_creation_successful(client, app):
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    response = client.post("/create", data={
        "group_name": "g1",
        "group_description": "This is g1."
    })
    
    assert response.status_code == 302  # Should redirect after successful creation
    assert response.location.endswith("/")  # Ensure redirection to groups page
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        assert group is not None  # Check that the group was created

# Register and log in a user
def test_group_edit_successful(client, app):
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    # Create a group
    create_group(client, group_name="g1", group_description="This is g1.")
    
    # Fetch the group ID for the created group
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    # Update the group name from "g1" to "g2"
    response = client.post(f"/{group_id}/update", data={
        "group_name": "g2",
        "group_description": "This is g2."
    })
    
    assert response.status_code == 302  # Should redirect after successful update
    assert response.location.endswith("/")  # Ensure redirection to groups page
    # Verify that the group name has been updated in the database
    with app.app_context():  # Create a new app context for database access
        db = get_db()  # Get the database connection
        updated_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
        assert updated_group is not None  # Check that the group still exists
        assert updated_group["group_name"] == "g2"  # Check that the group name has been updated
        assert updated_group["group_description"] == "This is g2."  # Check that the group name has been updated

def test_group_edit_empty_group_name(client, app):
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    create_group(client, group_name="g1", group_description="This is g1.")
    
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    
    response = client.post(f"/{group_id}/update", data={
        "group_name": "",
        "group_description": "This is g1."
    })
    
    # Expect 200 OK because form is re-rendered
    assert response.status_code == 200
    # Check that error message is shown to user
    assert b"Group name is required." in response.data
    # Verify the group has NOT been updated in the database
    with app.app_context():
        db = get_db()
        updated_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
        assert updated_group is not None
        assert updated_group["group_name"] == "g1"
        assert updated_group["group_description"] == "This is g1."

def test_group_edit_empty_description_success(client, app):
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
    create_group(client, group_name="g1", group_description="This is g1.")
    
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    
    # Update group with empty description (allowed)
    response = client.post(f"/{group_id}/update", data={
        "group_name": "g1",
        "group_description": ""
    })
    
    assert response.status_code == 302  # Redirect after successful update
    assert response.location.endswith("/")  # Redirect to groups page
    # Verify that the group description is now empty
    with app.app_context():
        db = get_db()
        updated_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
        assert updated_group is not None
        assert updated_group["group_description"] == ""

def test_group_deletion_success(client, app):
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    # Create a group
    create_group(client, group_name="g1", group_description="This is g1.")
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    # Send POST request to delete the group
    response = client.post(f"/{group_id}/delete")
    # Check for redirect to groups index page
    assert response.status_code == 302
    assert response.location.endswith("/")
    # Verify group is deleted from the database
    with app.app_context():
        db = get_db()
        deleted_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
        assert deleted_group is None