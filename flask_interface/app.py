import os
# from CardsAgainstGame.GameHandler import Game
from flask import Flask, render_template, url_for, redirect, session
from functools import wraps
from flask import request, Response

app = Flask(__name__)
print(os.path.join(os.getcwd(),'../templates'))
app.template_folder = os.path.join(os.getcwd(),'../templates')
app.static_folder = os.path.join(os.getcwd(),'../static')
app.game = None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if session['username'] is None or not game:
            return redirect(url_for('/login'))
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/add_player', methods=['POST'])
def add_player(username):
    if 'username' in request.args:
        session['username'] = username

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('/login'))

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



