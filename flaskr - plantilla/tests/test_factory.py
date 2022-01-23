# Tests over the application factory.

from flaskr import create_app

# "assert" is a statement used for debugging
# It allows us to dfetect problems early in our program where the cause is clear. We are telling the program to test a condition, and trigger an error if the condition is false.
def test_config():
    assert not create_app().testing
    assert create_app({'TESTING':True}).testing

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'