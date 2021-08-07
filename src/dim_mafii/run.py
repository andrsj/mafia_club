import os

from dim_mafii.flask_app import create_app

from dim_mafii.adapters.bootstrap import bootstrap


cfg = os.environ.copy()
bootstrap(cfg)
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

