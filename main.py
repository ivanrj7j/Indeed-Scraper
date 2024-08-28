from flask import Flask
from blueprints import backend, frontend

app = Flask(__name__, template_folder='templates')

app.register_blueprint(frontend)
app.register_blueprint(backend)
# registering blueprints see https://flask.palletsprojects.com/en/3.0.x/blueprints/

if __name__ == '__main__':
    app.run(debug=True)
