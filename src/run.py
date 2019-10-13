import os

from src import create_app
from src.adapters.bootstrap import bootstrap

cfg = os.environ.copy()
bootstrap(cfg)
app = create_app()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
