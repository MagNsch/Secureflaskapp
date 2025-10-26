import os

from flask import Flask, render_template
from flask_socketio import SocketIO


socketio = SocketIO(cors_allowed_origins="*")

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        MAX_CONTENT_LENGTH =1 * 1024 * 1024,
        MAX_FORM_MEMORY_SIZE = 0.2 * 1024 * 1024,
        MAX_FORM_PARTS = 1000

    )

    @app.errorhandler(413)
    def too_large(e):
        return "Anmodning er for stor. Maks 1 MB., 413"


    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass 
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    from .blog import get_comments_for_post
    app.jinja_env.globals.update(get_comments_for_post=get_comments_for_post)
    
    from . import comment
    app.register_blueprint(comment.bp)
    
    return app