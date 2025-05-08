#Imports
import pytest
from hsa_b.db import get_db

#THIS IS THE MAIN FILE FOR UNIT TESTING

#BELOW ARE THE HELPER FUNCTIONS FOR UNIT TESTING (they only run when they are called)

#HF 1: pre-registering a user
def register_user(client, username="owen", email="owen25@gmail.com", password="Password123!"):
   return client.post("/auth/register", data={
      "username": username,
     "email": email,
    "password": password
})

#HF 2: pre-logging in a user
def login_user(client, email="owen25@gmail.com", password="Password123!"):
    return client.post("/auth/login", data={
        "email": email,
        "password": password
    })

#HF 3: pre-creating a group
def create_group(client, group_name="g1", group_description="this is g1"):
    return client.post("/create", data={
        "group_name": group_name,
        "group_description": group_description
    })

#HF 4: pre-creating a task
def create_task(client, group_id, task_name="t1", task_description="This is a task.", task_deadline="2025-05-08"):
    return client.post(f"/{group_id}/tasks/create", data={
        "task_name": task_name,
        "task_description": task_description,
        "task_deadline": task_deadline
    })

#BELOW ARE THE FIXTURES FOR UNIT TESTING (they get rerun for each test)

#F1: setting up a test client
@pytest.fixture
def client(app):
    return app.test_client()

#F2: setting up the app for testing
@pytest.fixture
def app():
    from hsa_b import create_app
    app = create_app()
    with app.app_context():
#DB needs to be initialised for every test        
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
        
#BELOW ARE THE ACTUAL UNIT TESTS


#UNIT 1: REGISTRATION


#Test 1.1: Testing that a new user is created when valid registration details are entered
def test_registration_success(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
#DB connection  
    with app.app_context():
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", ("owen25@gmail.com",)).fetchone()
#Ensuring that user has been created
        assert user is not None
#Ensuring redirect to login page
        assert response.status_code == 302

#Test 1.2: Ensuring correct error message when user has not entered a username
def test_registration_missing_username(client, app):
    response = client.post("/auth/register", data={
        "username": "",
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
#Ensuring correct response
    assert b"Username is required." in response.data

#Test 1.3: Ensuring correct error message when user has not entered an email
def test_registration_missing_email(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "",
        "password": "Password123!"
    })
#Ensuring correct response
    assert b"Email is required." in response.data

#Test 1.4: Ensuring correct error message when user has not entered a password
def test_registration_missing_password(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": ""
    })
#Ensuring correct response
    assert b"Password is required." in response.data

#Test 1.5: Ensuring correct error message when user has entered a password that is too short
def test_registration_short_password(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "short"
    })
#Ensuring correct response
    assert b"Password must be at least 8 characters long" in response.data

#Test 1.6: Ensuring correct error message when user has entered a password that does not meet
#the other password requirements such as having a special character, Uppercase character etc.
def test_registration_invalid_password(client, app):
    response = client.post("/auth/register", data={
        "username": "owen",
        "email": "owen25@gmail.com",
        "password": "password"
    })
#Ensuring correct response
    assert b"Password must contain at least: one number, one lowercase letter, one uppercase letter and one special character." in response.data  # Check for error message

#Test 1.7: Ensuring correct error message when user has attempted to register using an email that has already been used before
def test_registration_duplicate_email(client, app):
#Two registrations are made this time to test this
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
#Ensuring correct response
    assert b"Account with email owen25@gmail.com is already registered." in response.data  # Check for error message


#UNIT 2: LOGIN


#Test 2.1: Test successful login with valid credentials
def test_login_success(client, app):
#Easier to use HF to resgister user here
    register_user(client)

#Log in registered user
    response = client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
#Ensure redirected afer successfully logging in
    assert response.status_code == 302
#Ensure specifically redirected to group page
    assert response.location.endswith("/")

#Test 2.2: Test correct response when an incorrect email is used
def test_login_incorrect_email(client, app):
    register_user(client)
    response = client.post('/auth/login', data={'email': 'incorrect@gmail.com', 'password': 'Password123!'})
#Ensures user remains on the same page
    assert response.status_code == 200
#Ensures correct response
    assert b'Incorrect email.' in response.data  # Check for the error message

#Test 2.3: Test correct response when an incorrect password is used
def test_login_incorrect_password(client, app):
    register_user(client)
#Logging in with registered user
    response = client.post('/auth/login', data={'email': 'owen25@gmail.com', 'password': 'invalidPassword'})    
#Ensuring that the user remains on the same page
    assert response.status_code == 200
#Ensuring correct response
    assert b'Incorrect password.' in response.data  # Check for the error message in HTML

    
    
#UNIT 3: GROUP


#Test 3.1: Test successful creation of a group
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
#Ensuring user is regirected after successful creation
    assert response.status_code == 302
#Ensuring user is redirected to group page
    assert response.location.endswith("/")
#DB connection
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
#Ensuring DB is updated and contains newly created group
        assert group is not None

#Test 3.2: Test successful group edit
def test_group_edit_successful(client, app):
#Regisering and logging in user
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
    
#Creating a group via hf
    create_group(client, group_name="g1", group_description="This is g1.")
    
#Fetching new group ID and establishing db connection
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
#Updating the group name and description (g1 --> g2, This is g1. --> This is g2.)
    response = client.post(f"/{group_id}/update", data={
        "group_name": "g2",
        "group_description": "This is g2."
    })
#Ensuring redirect after successfully updating group
    assert response.status_code == 302
#Ensuring user is specifically redirected back to the group page
    assert response.location.endswith("/")
#DB connection
    with app.app_context():
        db = get_db()
        updated_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
#Enduring group name and description have both been updated
        assert updated_group["group_name"] == "g2"
        assert updated_group["group_description"] == "This is g2."

#Test 3.3: Test correct response when user attempts to make the group nameless
def test_group_edit_empty_group_name(client, app):
#Registering and logging in
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })
#Creating group via hf
    create_group(client, group_name="g1", group_description="This is g1.")
#DB connection
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    response = client.post(f"/{group_id}/update", data={
        "group_name": "",
        "group_description": "This is g1."
    })
    
#Ensuring user stays on same page
    assert response.status_code == 200
#Ensuring correct response
    assert b"Group name is required." in response.data
#Checking that the group has not been changed in the DB
    with app.app_context():
        db = get_db()
        updated_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
        assert updated_group is not None
        assert updated_group["group_name"] == "g1"
        assert updated_group["group_description"] == "This is g1."

#Test 3.4: Test successful edit when a user wants to remove the group description (VALID)
def test_group_edit_empty_description(client, app):
#Registration, logging in, group creation
    register_user(client)
    client.post("/auth/login", data={
        "email": "owen25@gmail.com",
        "password": "Password123!"
    })   
    create_group(client, group_name="g1", group_description="This is g1.")
#DB connection
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    
#Updating group by removing description
    response = client.post(f"/{group_id}/update", data={
        "group_name": "g1",
        "group_description": ""
    })
#Ensuring user is redirected specifically to the groups page
    assert response.status_code == 302
    assert response.location.endswith("/")
#Verifying with DB that description is now empty
    with app.app_context():
        db = get_db()
        updated_group = db.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,)).fetchone()
        assert updated_group is not None
        assert updated_group["group_description"] == ""

#Test 3.5: Test successful deletion of a group
def test_group_deletion(client, app):
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


#UNIT 4: TASK


#Test 4.1: Test successful creation of a group
def test_create_task(client, app):
#Registering, logging in, creating group
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
#Creating task via hf
    response = create_task(client, group_id)
#Ensuring user is redirected back to tasks page
    assert response.status_code == 302
    assert response.location.endswith(f"/{group_id}/tasks/")
#Checking with DB that the task has been created properly
    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        assert task is not None
        assert task["task_description"] == "This is a task."
        assert task["task_deadline"] == "2025-05-08"

#Test 4.2: Test correct response when user attempts to create a task without a task name
#Registering, logging in, group creation
def test_create_task_empty_task_name(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
#Attempting to create a task with an empty task name
    response = client.post(f"/{group_id}/tasks/create", data={
        "task_name": "",
        "task_description": "Description for task",
        "task_deadline": "2025-05-08"
    })
 #Ensuring user stays on same page
    assert response.status_code == 200
#Ensuring correct response
    assert b"Task name is required." in response.data

#Test 4.3: Test correct respons when user attempts to create a task without a task description
def test_create_task_empty_task_deadline(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
#Attempting to create a task with an empty deadline
    response = client.post(f"/{group_id}/tasks/create", data={
        "task_name": "Valid Task Name",
        "task_description": "Description for task",
        "task_deadline": ""
    })
#Ensuring user stay on same page and correct response is made
    assert response.status_code == 200  # No redirect due to validation error
    assert b"Task deadline is required." in response.data

#Test 4.4: Test successful edit of a task name
def test_edit_task_name(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    create_task(client, group_id)
    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        task_id = task["task_id"]
    response = client.post(f"/{group_id}/tasks/{task_id}/update", data={
        "task_name": "New Task Name",
        "task_description": task["task_description"],
        "task_deadline": task["task_deadline"]
    })
#Ensuring user is redirected back to tasks page
    assert response.status_code == 302
    assert response.location.endswith(f"/{group_id}/tasks/")
#DB connection, ensuring successful update
    with app.app_context():
        db = get_db()
        updated = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        assert updated["task_name"] == "New Task Name"

#Test 4.5: Test successful edit of a task description
def test_edit_task_description(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    create_task(client, group_id)
    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        task_id = task["task_id"]
    new_description = "Updated description text"
    response = client.post(f"/{group_id}/tasks/{task_id}/update", data={
        "task_name": task["task_name"],
        "task_description": new_description,
        "task_deadline": task["task_deadline"]
    })
#Ensuring user is redirected back to tasks page
    assert response.status_code == 302
    assert response.location.endswith(f"/{group_id}/tasks/")
#DB connection, ensuring correct description
    with app.app_context():
        db = get_db()
        updated = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        assert updated["task_description"] == new_description

#Test 4.6: Test successful edit of a task deadline
def test_edit_task_deadline(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)
    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]
    create_task(client, group_id)
    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        task_id = task["task_id"]
    new_deadline = "2030-12-31"
    response = client.post(f"/{group_id}/tasks/{task_id}/update", data={
        "task_name": task["task_name"],
        "task_description": task["task_description"],
        "task_deadline": new_deadline
    })
#Ensuring user has been redirected back to tasks page
    assert response.status_code == 302
    assert response.location.endswith(f"/{group_id}/tasks/")
#DB connection, ensuring correct change made
    with app.app_context():
        db = get_db()
        updated = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        assert updated["task_deadline"] == new_deadline

#Test 4.7: Test correct response when user attempts to edit a task so that it has no name
def test_edit_task_empty_name(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)

    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]

    create_task(client, group_id)

    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        task_id = task["task_id"]

#Attempting to update task with empty name
    response = client.post(f"/{group_id}/tasks/{task_id}/update", data={
        "task_name": "",
        "task_description": task["task_description"],
        "task_deadline": task["task_deadline"]
    })
#Ensuring user stays on same page and correct response given
    assert response.status_code == 200
    assert b"Task Name is required." in response.data

#Test 4.8: Test correct response when user attempts to edit a task so that it has no deadline
def test_edit_task_empty_deadline(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)

    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]

    create_task(client, group_id)

    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        task_id = task["task_id"]

#Attempting to update task with empty deadline
    response = client.post(f"/{group_id}/tasks/{task_id}/update", data={
        "task_name": task["task_name"],
        "task_description": task["task_description"],
        "task_deadline": ""
    })
#Ensuring user stays on same page and correct reponse is given
    assert response.status_code == 200
    assert b"Deadline is required" in response.data

#Test 4.9: Test successful deletion of a task
def test_edit_task_delete_task(client, app):
    register_user(client)
    client.post("/auth/login", data={"email": "owen25@gmail.com", "password": "Password123!"})
    create_group(client)

    with app.app_context():
        db = get_db()
        group = db.execute("SELECT * FROM groups WHERE group_name = ?", ("g1",)).fetchone()
        group_id = group["group_id"]

    create_task(client, group_id)

    with app.app_context():
        db = get_db()
        task = db.execute("SELECT * FROM tasks WHERE task_name = ?", ("t1",)).fetchone()
        task_id = task["task_id"]

    response = client.post(f"/{group_id}/tasks/{task_id}/delete")

    assert response.status_code == 302
    assert response.location.endswith(f"/{group_id}/tasks/")
#DB connection, ensuring task is deleted
    with app.app_context():
        db = get_db()
        deleted_task = db.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        assert deleted_task is None
