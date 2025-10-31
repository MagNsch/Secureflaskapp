import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

roles = ["user", "admin"]

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email  = request.form['email']
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        print(role)
        db = get_db()
        error = None

        if not email:
            error = 'Email is required'
        if not username:
            error = 'Username is required.'
        if not role:
            error = 'role is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                if role in roles:
                    db.execute(
                        "INSERT INTO user (username, password, email, role) VALUES (?,?,?,?)",
                        (username, generate_password_hash(password),email, role),
                    )
                    db.commit()
                else:
                    flash("role is not supported")
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT id, username, role FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    """Kræver at brugeren er logget ind"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


def role_required(*roles):
    """Kræver at brugeren har en bestemt rolle (eller en af flere)"""
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            # check rolle
            if g.user['role'] not in roles:
                abort(403)

            return view(**kwargs)
        return wrapped_view
    return decorator
