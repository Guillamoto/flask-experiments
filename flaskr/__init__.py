# THIS FILE SERVES TWO PURPOSES: IT WILL CONTAIN THE APPLICATION FACTORY, AND SIGNALS PYTHON TO TREAT "flaskr" DIRECTORY AS A PACKAGE.

# Module importation
import os
from flask import Flask

# We create the Application Factory: a method to create the Flask objects to use.
# "test_config" is defined here, but its importance is shown later.
def create_app(test_config=None):
    # Creation of the Flask instance, where:
        # __name__ refers to the name of the current module
        # instance_relavive_config=True tells the app that the configuration files are relative to the instance folder. The instance folder is located outside the flaskr package
        # and can hold local data which should not be committed to version control, such as configuration secrets and the database file.
    app = Flask(__name__, instance_relative_config=True)

    # Sets up a default configuration for the app.
    app.config.from_mapping(
        # Used by Flask to keep data safe. It should be generated randomly when deploying.
        SECRET_KEY='dev',
        # Path where the SQLite database file will be saved. It is under "app.instance_path", which is the path that Flask has chosen for the instance folder.
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    # Load the instance config, if it exists, when not testing.
    if test_config is None:

        # Overrides the default configuration with values from "config.py".
        app.config.from_pyfile('config.py', silent=True)
    # Load the test config if passed in.
    else:
        # Overrides the default configuration with values from the test_config parameters. This is useful to later write and configure the tests independently.
        app.config.from_mapping(test_config)


    # Ensuring that the instance folder exists:
    try:
        # Ensures that "app.instance_path" exists. It is not created automatically by Flask, but we need it for the SQLite database file.
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Simple page that says hello:

    # Creates a simple route so we can see the application working. It creates a connection between the URL "/hello" and the string 'Hello, World!' in this case.
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    # Implementation of "close_db" and "init_db_command" into our factory.
    from . import db
    db.init_app(app)

    # Implementation of our blueprint "auth" into the application factory.
    from . import auth
    app.register_blueprint(auth.bp)

    # Implementation of our blueprint "blog" into the application factory.
    from . import blog
    app.register_blueprint(blog.bp)
    # The blog blueprint does not have a "url_prefix", so the index view will be at "/", create view at "/create" and so on.
    # With "add_url_rule" we allow that both "/index" and "/blog.index" lead to the same URL.
    # If we create a url_prefix we would define different endpoints for index and blog.index, so their URLs would be different.
    app.add_url_rule('/', endpoint='index')

    # Return of the generated Flask instance.
    return app