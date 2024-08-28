from flask import Blueprint
from flask import render_template

frontend = Blueprint("frontend", __name__)


@frontend.route('/')
def index():
    return render_template('index.html')