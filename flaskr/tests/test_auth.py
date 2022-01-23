

import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    # Assert that the client is able to get to the register view. Status code 200 means everything OK. "client.get" will return the Response object from Flask. 
    # If we receive a 500 Internal Server Error, that means the rendering of the view has failed.
    assert client.get('/auth/register').status_code == 200
    # Generate a random username and password and assert if it works. "client.post" will make a POST request, converting the data dict into a form data.
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # "headers" will have a "Location" header with the login URL when the register view redirects to the login view. 
    # This means that, when we have registered, we should have been redirected to the login view, which is what we are checking here.
    assert 'http://localhost/auth/login' == response.headers['Location']

    # We check that the new user takes part from the db.
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# This tells Pytest to run the same test function with different arguments. We use it to test different invalid input and error messages without writing the same code three times.
# A b'string' is a byte literal, which is what the view will return. It is important to take that in account or we could report non existent errors.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


# When testing login, we have to check that "session" contains the user_id. Checking the data in the database seems trivial.
def test_login(client, auth):
    # Checking that the view renders correctly.
    assert client.get('/auth/login').status_code == 200
    # Login in should lead us to the main page.
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # Checking that the user_id is 1 (the only one connected) and that the username is correctly located.
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

# Checking that the error messages work correctly.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

# When logging out, "session" should NOT contain the user_id.
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session