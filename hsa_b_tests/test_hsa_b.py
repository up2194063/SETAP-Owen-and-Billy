from auth import users

def test_registration(client, app):
    response = client.post("/register", data={"username": "owen", "email": "owen25@gmail.com", "password":"Password123!"})

    with app.app_context():
        assert users.query.count() == 1