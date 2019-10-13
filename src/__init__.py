import os

from flask import Flask

from src.adapters.orm import make_sqlalchemy
from src.config import get_postgres_url, get_postgres_config
from src.routes.users import PlayerView


def init_db():
    db = make_sqlalchemy(get_postgres_url(os.environ))
    db.configure_mappings()
    return db


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # app.db = init_db()

    with app.app_context():
        # Include our Routes
        from . routes import index_blueprint

        app.register_blueprint(index_blueprint)
        app.add_url_rule('/player/<p_id>', view_func=PlayerView.as_view('player'))

        return app