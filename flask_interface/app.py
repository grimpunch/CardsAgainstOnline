"""
flask_interface/app.py

Contains the views and url mappings for the web application.

"""

import os
from flask import Flask, render_template, redirect, make_response, jsonify
from flask import request
from CardsAgainstGame.GameHandler import Game
from functools import wraps
from flask_interface.utils import create_expiration_cookie_time
from threading import Thread, Event
import time

APP = Flask(__name__)
APP.template_folder = os.path.join(os.getcwd(), 'templates')
APP.static_folder = os.path.join(os.getcwd(), 'static')
APP.session_key = str(os.urandom(24))
APP.game = None
APP.external_address = None



class GameLoopThread(Thread):
    def __init__(self, stop_event, interrupt_event):
        self.stop_event = stop_event
        self.interrupt_event = interrupt_event
        Thread.__init__(self)

    def run(self):
        while not self.stop_event.is_set():
            self.loop_process()
            if self.interrupt_event.is_set():
                self.interrupted_process()
                self.interrupt_event.clear()

    def loop_process(self):
        if APP.game:
            print("Processing!")
            APP.game.update()
        time.sleep(1)

    def interrupted_process(self):
        print("Interrupted!")


STOP_EVENT = Event()
INTERRUPT_EVENT = Event()
APP.thread = GameLoopThread(STOP_EVENT, INTERRUPT_EVENT)


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
        if str(request.cookies.get('username')) is None or not APP.game or str(request.cookies.get('session')) not in APP.session_key:
            response = make_response(redirect('/login'))
            response.set_cookie('session', '', expires=0)
            response.set_cookie('username', '', expires=0)
            return response
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
            expires = create_expiration_cookie_time()  # function generates 2 day cookie expiration date. (currently)
            response.set_cookie('username', username, expires=expires)
            response.set_cookie('session', APP.session_key, expires=expires)
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
    uid = None
    if APP.game:
        uid = APP.game.get_player_by_name(username).get_id()
    return jsonify(id=uid, name=username)

@APP.route('/czar')
def czar():
    """
    API endpoint: returns user who is the czar as a string
    :return:
    """
    no_czar_response = jsonify(czar_chosen=False, czar='')
    if not APP.game:
        return no_czar_response
    else:
        if not APP.game.card_czar:
            return no_czar_response
        else:
            return jsonify(czar_chosen=True, czar=APP.game.card_czar.name)


@APP.route('/pregame')
def pregame():
    """
    Api endpoint: return if we are in pregame
    """
    if APP.game:
        return jsonify(pregame=APP.game.pre_game)
    else:
        return jsonify(pregame=False)


@APP.route('/hand')
@login_required
def hand():
    """
    Api endpoint: return the hand
    """
    username = request.cookies.get('username')
    return render_template(
        "hand.html",
        hand=APP.game.get_player_by_name(username).hand
    )


@APP.route('/host', methods=['GET', 'POST'])
def host():
    """
    host a new game if a game is not started.
    """
    if not APP.game:
        print('hosting game')
        APP.game = Game()
        response = make_response(redirect('/host', code=302))
        response.set_cookie('username', 'HOST')
        return response
    return render_template('game_screen.html')

@APP.route('/address')
def address():
    return APP.external_address


@APP.route('/play')
@login_required
def play():
    """
    called when the game is running
    """
    return render_template('game_screen.html')

@APP.route("/interrupt")
def interrupt():
    INTERRUPT_EVENT.set()
    return "OK", 200

# http://flask.pocoo.org/snippets/67/
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@APP.route("/shutdown")
def shutdown():
    STOP_EVENT.set()
    APP.thread.join()
    shutdown_server()
    return "OK", 200
