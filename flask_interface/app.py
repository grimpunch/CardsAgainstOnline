"""
flask_interface/app.py

Contains the views and url mappings for the web application.

"""

import os
from flask import Flask, render_template, \
    redirect, make_response
from flask import request
from CardsAgainstGame.GameHandler import Game
from functools import wraps


APP = Flask(__name__)
APP.template_folder = os.path.join(os.getcwd(), 'templates')
APP.static_folder = os.path.join(os.getcwd(), 'static')
APP.game = None


def login_required(func):
    """
    Redirects to login if username not known
    :param func:
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        """
        Here's where the cookie crumbles
        """
        if request.cookies.get('username') is None or not APP.game:
            return redirect('/login')
        else:
            return func(*args, **kwargs)
    return decorated


@APP.route('/login')
def login():
    """
    handled in javascript
    """
    return render_template('login.html')


@APP.route('/add_player', methods=['POST'])
def add_player():
    """
    Api endpoint with variable username as post.
    Username is stored in cookie.
    """
    if 'username' in request.form and APP.game:
        username = request.form['username']
        if username is not '' and username not in APP.game.get_player_names():
            print(username + " joined")
            APP.game.add_player(player_name=username)
            response = make_response(redirect('/play', code=302))
            response.set_cookie('username', username)
            return response
        else:
            return 'Please enter a valid username'
    else:
        return login()


@APP.route('/')
@APP.route('/index')
def index():
    """
    Redirected to login
    """
    return login()


@APP.route('/user')
@login_required
def user():
    """
    Api endpoint: return the user as a string
    """
    username = request.cookies.get('username')
    return username


@APP.route('/pregame')
@login_required
def pregame():
    """
    Api endpoint: return if we are in pregame
    """
    return True


@APP.route('/hand')
@login_required
def hand():
    """
    Api endpoint: return the hand
    """
    return render_template(
        "hand.html",
        hand=APP.game.get_player_by_name(user.get_username()).hand
    )


@APP.route('/host', methods=['GET', 'POST'])
def host():
    """
    host a new game if a game is not started.
    """
    if not APP.game:
        print('hosting game')
        APP.game = Game()
    return render_template('game_screen.html')


@APP.route('/play')
@login_required
def play():
    """
    called when the game is running
    """
    return render_template('game_screen.html')

