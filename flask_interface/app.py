"""
flask_interface/app.py

Contains the views and url mappings for the web application.

"""
import json

import os
from flask import Flask, render_template, redirect, make_response, jsonify, session
from flask import request
from CardsAgainstGame.GameHandler import Game, SUBMISSION_STATE, JUDGING_STATE
from functools import wraps
from flask_interface.utils import create_expiration_cookie_time
from flask_socketio import SocketIO, emit, disconnect
from threading import Thread, Event
import time

APP = Flask(__name__)
APP.template_folder = os.path.join(os.getcwd(), 'templates')
APP.static_folder = os.path.join(os.getcwd(), 'static')
APP.session_key = str(os.urandom(24))
APP.config['SECRET_KEY'] = 'secret!'
APP.game = None
APP.external_address = None
socketio = SocketIO(APP)


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
            APP.game.update()
        time.sleep(1)

    def interrupted_process(self):
        print("Interrupted!")


class WebsocketLoopThread(Thread):
    def __init__(self, stop_event, interrupt_event):
        self.stop_event = stop_event
        self.interrupt_event = interrupt_event
        self.count = 0
        Thread.__init__(self)

    def run(self):
        while not self.stop_event.is_set():
            self.loop_process()
            if self.interrupt_event.is_set():
                self.interrupted_process()
                self.interrupt_event.clear()

    def loop_process(self):
        time.sleep(1)

    def interrupted_process(self):
        print("Interrupted!")


# SocketIO Websocket handling functionality.
@socketio.on('my event', namespace='/ws')
def test_message(message):
    session['players_ready'] = session.get('players_ready', 0) + 1
    print('message received from client')
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('user_connected', namespace='/ws')
def client_connected(message):
    print(message)
    if not message:
        print('Client message called with no message')
        return
    if not APP.game:
        emit('no_host')
        return
    if 'client_connect' in message.values() and 'user' in message.keys():
        print('User %s connected' % message['user'])
        print('User %s\'s ID is %s' % (message['user'],message['user_id']))
        player = APP.game.get_player_by_name(message['user'])
        if not player:
            return
        player.connected = True
        return


@socketio.on('disconnect', namespace='/ws')
def test_disconnect():
    if not APP.game:
        print('Removing Clients from non-active game server')
        disconnect()
    print('Client disconnected')
# ##########################################

STOP_EVENT = Event()
INTERRUPT_EVENT = Event()
APP.game_thread = GameLoopThread(STOP_EVENT, INTERRUPT_EVENT)
APP.websocket_thread = WebsocketLoopThread(STOP_EVENT, INTERRUPT_EVENT)


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
        #a get socket.io between play and user
    return jsonify(id=uid, name=username)


@APP.route('/czar')
def czar():
    """
    API endpoint: returns user who is the czar as a string
    :return:
    """
    no_czar_response = jsonify(czar_chosen=False, czar='', current_black_card_text='', num_answers=0)
    if not APP.game:
        return no_czar_response
    else:
        if not APP.game.card_czar:
            return no_czar_response
        else:
            return jsonify(czar_chosen=True, czar=APP.game.card_czar.name,
                           current_black_card_text=APP.game.current_black_card.text,
                           num_answers=APP.game.current_black_card.num_answers
                           )


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

@APP.route('/judgement')
@login_required
def judgement():
    """
    Api endpoint: return the submitted white cards for judgement
    """
    username = request.cookies.get('username')
    return render_template(
        "judgement.html",
        judgement_cards=APP.game.cards.judged_cards,
        czar=APP.game.card_czar
    )

@socketio.on('submit_white_card', namespace='/ws')
@login_required
def submit_white_card(data):
    """
    Call submit white card, to remove card from players hand and add it to judge pile
    """
    submitted_white_card_id = int(data["submitted_white_card_id"])
    username = request.cookies.get('username')
    if APP.game:
        player = APP.game.get_player_by_name(username)
        APP.game.submit_white_card(player, submitted_white_card_id)
        if APP.game.turn_state == JUDGING_STATE:
            response = make_response(redirect('/judgement', code=302))
            return response
        else:
            # Returns just a placeholder for now.
            return "OK", 200
    else:
        return "Fucked up fam", 500


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


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@APP.route("/shutdown")
def shutdown():
    STOP_EVENT.set()
    APP.game_thread.join()
    shutdown_server()
    return "OK", 200
