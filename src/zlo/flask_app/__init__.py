from flask import Flask
from zlo.routes.games import GamesView
from zlo.routes.users import PlayerView


def create_app():
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    with app.app_context():
        # Include our Routes
        from zlo.routes import index_blueprint

        app.register_blueprint(index_blueprint)
        app.add_url_rule('/player/', view_func=PlayerView.as_view('player'))
        # app.add_url_rule('/player/', view_func=PlayerView.as_view('player'))
        app.add_url_rule('/game/', view_func=GamesView.as_view('game'))
        return app
