import os
from CardsAgainstGame.GameHandler import Game
from flask import Flask, render_template, url_for
from functools import wraps
from flask import request, Response

app = Flask(__name__)
print(os.path.join(os.getcwd(),'../templates'))
app.template_folder = os.path.join(os.getcwd(),'../templates')
app.static_folder = os.path.join(os.getcwd(),'../static')
app.game = None

class User():
    def __init__(self):
        self.username = None
    def set_username(name):
        self.username = name
    def get_username():
        return self.username

user = User()

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if user.get_username() is None or not game:
            return redirect(url_for('/login')
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/add_player/<username>', methods=['POST'])
def add_player(username):
   user.set_username(username) 

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user')
@login_required
def user():
    # return the user as a string
    return "peter"

@app.route('/pregame')
@login_required
def pregame():
    # return if we are in pregame
    return True

@app.route('/hand')
@login_required
def hand():
    # show the hand
    return "You have cards!"

@app.route('/host')
def host():
    # host a new game if a game is not started.
    if not app.game:
        app.game = Game()
    return render_template('game_screen.html')

@app.route('/play')
def play():
    # called when in the game
    return "Playing"

if __name__ == "__main__":
    app.run(port=8888)



