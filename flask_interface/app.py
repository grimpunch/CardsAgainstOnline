from flask import Flask
from views import *
from flask.ext.login import LoginManager

lm = LoginManager()
app = Flask(__name__)
# lm.init_app(app)

if __name__ == "__main__":
    app.run()

