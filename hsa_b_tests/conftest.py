import pytest

from hsa_b import create_app, db 

@pytest.fixture()
def app():
    app = create_app("sqlite://") # essentially creates a temporary db for the test
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture()
def client(app):
    return app.test_client() # allows simulation of requests