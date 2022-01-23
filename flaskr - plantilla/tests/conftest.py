# All our tests will be located in the "tests" folder, OUTSIDE the "/flaskr".
# Tests are python modules that start with "test_" and each test functions in those modules also start with "test_"

# This file serves as a basis to configure all fixtures used in every test.


import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# We read our sql file with the test data.
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# First, we have to understand "test fixtures". Text fixtures are what initialize test functions.
# They provide a fixed baseline so that tests execute reliably and produce consistent, repeatable results.
# This initialization may setup services, states or other operating environments. We access these with test functions through arguments.
# Usually, for each fixture used by a test function, there is typically a parameter in the test function's definition.

# Regarding fixtures:
    # They have explicit names and are activated by declaring their use from test functions, modules, classes or projects.
    # They are implemented in a modular name, as each fixture name triggers a fixture function, which can call other fixtures.
    # Fixture management scales from simple unit to functional testin, allowing to parametrize fixtures and tests.
    # Teardown logic can be easily and safely managed, not needing to carefully handle errors by hand or micromanage the order that cleanup steps are added.


# Our app fixture will call the factory and pass test_config to configure the application and database for testing instead of using our local development configuration.
@pytest.fixture
def app():
    # This creates and opens a temporary file, returning the file descriptor and path to it.
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        # We are telling that we are TESTING actually. This allows some internal behaviour changes so it's easier to test, and test will use the client to make requests without running the server.
        'TESTING': True,
        # We override the original path to the DATABASE, so we use the temporary file.
        'DATABASE': db_path,
    })

    with app.app_context():
        # We initialize the database and insert the test data.
        init_db()
        get_db().executescript(_data_sql)

    # We return a generator: an iterable object that can be iterated only once. This means that our code will continue from where it left off each time we call it.
    # In this case, that would mean that we are generating a new app, calling again the function would create another different one, and so on.
    yield app

    os.close(db_fd)
    os.unlink(db_path)

# The client fixture will call the "app.test_client" with the application object created with the app fixture. This test will use the client to make requests to the app.
@pytest.fixture
def client(app):
    return app.test_client()

# This fixture is similar to "client", but we create a runner that can call the Click commands registered with the application.
@pytest.fixture
def runner(app):
    return app.test_cli_runner()

# For most views, we need to be a logged in user. To do this in a test, the easiest way is to make a POST request to the login view with the client. 
# Instead of writing that out everything, we write a class with methods to do it and use a fixture to pass the client for each test.

#Class to make the POST request to the login view with the client
class AuthActions(object):
    # We pass a client argument that will become a parameter for the class.
    def __init__(self, client):
        self._client = client

    # We create a function to automate the login. It is remarkable that we are using the test user, included in the @app fixture. (TESTING:True)
    def login(self, username='test', password='test'):
        # We use the POST method to login into the login screen with the data provided.
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    # We define a logout function with a GET method.
    def logout(self):
        return self._client.get('/auth/logout')

# We create the fixture that will check the authentication methods.
@pytest.fixture
def auth(client):
    return AuthActions(client)

