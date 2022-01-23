# There, we have to ensure that "get_db" returns the same connection each time it is called within an application context, and after the context, it should be closed.

import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    # "app._context" allows us to work over an application, even when we have not generated one.
    with app.app_context():
        db = get_db()
        assert db is get_db()

    # "pytest.raises" is a context manager which allows us to check for errors we are intentionally inducing in our tests.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

# init-db command should call the init_db function and output a message.
def test_init_db_command(runner, monkeypatch):
    # We define a class to control when has the object been called or not.
    class Recorder(object):
        called = False

    # We generate a fake function which just calls the object created.
    def fake_init_db():
        Recorder.called = True

    # Monkeypatch is a fixture that replaces the init_db function with one that records that it has been called (using the Recorder object).
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # As we invoke it using the previously defined runner
    result = runner.invoke(args=['init-db'])
    # We will obtain our result over a fake function and just checking that the Click command works.
    assert 'Initialized' in result.output
    assert Recorder.called

