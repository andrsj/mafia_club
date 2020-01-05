import os

from zlo.flask_app import create_app

from zlo.adapters.bootstrap import bootstrap


cfg = os.environ.copy()
bootstrap(cfg)
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

