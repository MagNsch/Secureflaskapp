from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('comment', __name__)

@bp.route('/add', methods=["POST"])
@login_required
def add_comment():
    comment_text = request.form['comment']
    post_id = request.form['post_id']

    db = get_db()
    with db:
        db.execute(
            'INSERT INTO comment (post_id, author_id, comment) VALUES (?, ?, ?)',
            (post_id, g.user['id'], comment_text)
            )
        db.commit() 

    return redirect(url_for('index'))   

@bp.route('/delete', methods=['POST'])
@login_required
def delete_comment():
    comment_id = request.form['comment_id']
    db = get_db()
    comment = db.execute('SELECT author_id FROM comment WHERE id = ?', (comment_id,)).fetchone()
    if comment['author_id'] != g.user['id']:
        abort(403)

    db.execute('DELETE FROM comment WHERE id = ?', (comment_id,))
    db.commit()
    return redirect(request.referrer or url_for('blog.index'))

