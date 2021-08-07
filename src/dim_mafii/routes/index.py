from flask import Blueprint, render_template

index_blueprint = Blueprint('/', __name__, template_folder='templates')


@index_blueprint.route("/")
def index():
    return render_template('index.html')
