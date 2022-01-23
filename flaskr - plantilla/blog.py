# We are about to create a blog. This will list all posts, allow logged in users to create posts, and allow the author of a post to edit or delete it.

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

# Defining the blueprint for "blog".
bp = Blueprint('blog',__name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html',posts=posts)


# "login_required" does, as expected, require a login in order to access this route.
@bp.route('/create', methods=("GET","POST"))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            # We make a request and add the post into the list of posts of our db
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            # Commit to save changes
            db.commit()
            # Redirects us to the index so we can see the new post.
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


# To create the "update" and "delete" views, we need to fetch a post by its id and check if the logged in user matches the author.
# As we will need to get the post and call it, we create it as a different function to prevent duplicate code.
# We define "check_author=True" so, if we need to check a post later without checking the author, we are able with the same code.
def get_post(id, check_author=True):

    # A different way of writing previous lines. Useful if we do not need the request for multiple operations.
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # At any error, we use "abort" to raise an special exception (HTTP status code).
    if post is None:
        abort(404, f"Post id {id} does not exist.")
    
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    
    return post

# We define a URL to update a post by its URL. We use "<int:id>" as it must be an integer. "<id>" would be interpreted as a string.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # We get the post first.
    post = get_post(id)

    # We are able to update the post information: title, body...
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        # If there is no error, we make a request and then update the post.
        else:
            db = get_db()
            # As we can see, we use UPDATE instead of INSERT for this part.
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            # Commiting the final version.
            db.commit()
            # And getting back to the index.
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# It is interesting to notice that both actions could be done in only one view and template, but we are separating them for the tutorial as it is clearer.

# As it does not have its own template, "delete" will only handle the POST method and redirect to the index view.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))