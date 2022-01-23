# We are about to develop the authentication method for our website.
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# We create a blueprint called "auth". a Blueprint is a way to organize a group of related views and other code. This blueprint needs to know whjere its defined, for which we pass
# the argument "__name__" as 2nd argument. The "url_prefix" will be prepended to all the URLs we associate with this blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')

# We import and register this blueprint from the factory by using app.register_blueprint(). 


# When a user visits the /auth/register URL, this view will return an HTML form for them to fill out. After it is submitted, it will validate the input and either show the form again
# with an error message or create the new user and go to the login page. We do this with the following:


# We associate the URL "/register" with the register view function. When flask receives a request to "/auth/register" it will call the register view and use its return value as response.
@bp.route('/register', methods=('GET','POST'))
def register():
    # If the user submited the form, the request.method will be POST.
    if request.method == 'POST':
        # "request.form" is an special type of dict mapping. The user will input there their username and password.
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # Validating that these parameters are not empty.
        if not username:
            error = "An username is required."
        elif not password:
            error = "A password is required."


        # If the validation succeeds, we insert the new user data into the database.
        if error is None:
            try:
                # "db.execute" allows to take a SQL query with "?" placeholders for any user input, and a tuple of values to replace them with.
                # This library will take care automatically of escaping the values.
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    # We should NEVER storage passwords directly. We securely hash the password, and store that hash.
                    (username, generate_password_hash(password))
                )
                # As we are modifying data with our query, we have to commit afterwards to save the changes.
                db.commit()
            # We can expect an IntegrityError when the user does already exist. In this case, we show the following error.
            except db.IntegrityError:
                error = f"User {username} is already registered."
            # After everything is working properly, we redirect the user to the login page. 
            else:
                # "url_for" generates the URL for the login view based on its name.
                # "redirect" allows to generate a redirect response to the generated URL.
                return redirect(url_for("auth.login"))

        # If the validation fails, an error is shown. We use "flash" to store messages that can be retrieved when rendering the template.
        flash(error)

    # What the user sees as he navigates to auth/register, or if there was a validation error, is an HTML page with the registration form. 
    # render_template() will render a template containing the HTML, which we will write in the next step.
    return render_template('auth/register.html')


# Now, we prepare the "Login" view.


@bp.route("/login", methods=("GET","POST"))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # We query the user and save it in a variable.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        # "fetchone" returns one row from the query. If there is no result, it returns "None".
        # Validating that these parameters are not empty.
        if user is None:
            error = "Incorrect username."

        # Checks the password securely and compares it with the hash stored. If the match, the password is valid.
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password."

        if error is None:
            # "session" is a dict that stores data across requests. When the validation succeds, the user's id is stored in a new session. This data is stored in a cookie
            # that is sent to the browser, and it then sends it back with subsequent requests. Flask signs the data securely, so it can't be tampered with.
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# We register a function that runs before the view function, no matter what URL is requested. With this function we check is a user is stored in the session and get
# that user's data from the database, storing it in "g.user", which will last for the length of the request.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',(user_id,)
        ).fetchone()

# We register a logout. In this function, we remove the id from the session, so "load_logged_in_user" does not load a user on subsequent requests.
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# In order to require an authentication in other views, we use a decorator so we can use it to check for each view.
# This decorator returns a new view function that wraps the original view it's applied to. This new function will check if a user is loaded, and otherwise will redirect to the login.
# If a user is loaded, the original view is called and continues normally.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# "url_for" generates a URL to a view based on a name and arguments. This name associated is called the "endpoint", and by default its the same as the name of the view function.
# For example: the "hello()" view used in the tutorial has the name "hello" and can be linked with "url_for('hello')"

# When using a blueprint, the name of the blueprint is prepended to the name of the function, so the endpoint for the login function is 'auth.login', as we added it to the
# 'auth' blueprint.

