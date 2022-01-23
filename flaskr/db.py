# Module to control SQLite
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    # "g" is an special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request.
    # The connection is stored and reused if "get_db" is called a second time in the same request.
    if 'db' not in g:
        # "sqlite3.connect" establishes a connection to the file pointed at by the DATABASE configuration key. It does not have to exist yet, and won't until we initialize the db.
        g.db = sqlite3.connect(
            # "current_app" is another special object that points to the Flask application handling the request. As we have used an application factory, there is no application object.
            # get_db will be called when the application has been created and is handling a request, so "current_app" can be used.
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # With the following, we tell the connection to return rows behaving like dicts, so we can access those columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db',None)

    # If "g.db" was set, it is closed.
    if db is not None:
        db.close()

def init_db():
    # First, we obtain a database connection in order to execute the commands read from the file.
    db = get_db()

    # "open_resource" opens a file relative to our package, useful as we do not necessarily know where is it located after deploying. 
    with current_app.open_resource('schema.sql') as f:
        # "executescript" (sqlite3) allows for executing multiple SQL statements at once. The rest of the parameters are used to read the file properly
        db.executescript(f.read().decode('utf8'))

# We define a command line command called "init-db" which calls the init_db function ans shows a success message to the user.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """"Clear the existing data and create new tables."""
    init_db()
    click.echo('Database initialized')

# Function to register with the application instance
def init_app(app):
    # Call function "close_db" after cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # New command that can be called with the flask command.
    app.cli.add_command(init_db_command)
