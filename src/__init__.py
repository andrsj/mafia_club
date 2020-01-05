import os

from flask import Flask
from src.zlo.adapters.orm import make_sqlalchemy
from src.zlo.config import get_postgres_url
from zlo.routes.games import GamesView
from zlo.routes.users import PlayerView


def init_db():
    db = make_sqlalchemy(get_postgres_url(os.environ))
    db.configure_mappings()
    return db


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        # Include our Routes
        from src.zlo.routes import index_blueprint

        app.register_blueprint(index_blueprint)
        app.add_url_rule('/player/', view_func=PlayerView.as_view('player'))
        # app.add_url_rule('/player/', view_func=PlayerView.as_view('player'))
        app.add_url_rule('/game/', view_func=GamesView.as_view('game'))
        return app
