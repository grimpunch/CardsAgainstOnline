"""
flask_interface/app.py

Contains the views and url mappings for the web application.

"""
from enum import Enum
import os
from flask import Flask, render_template, redirect, make_response, jsonify, session
from flask import request
from CardsAgainstGame.GameHandler import Game, TurnState, GameState
from functools import wraps
from flask_interface.utils import create_expiration_cookie_time
from flask_socketio import SocketIO, emit, disconnect
from threading import Thread, Event
import time
import json


class LobbyState(Enum):
    WaitingForHost = 1
    WaitingForGameCreation = 2
    InGame = 3


CAH_lobby_server = Flask(__name__)
CAH_lobby_server.template_folder = os.path.join(os.getcwd(), 'templates')
CAH_lobby_server.static_folder = os.path.join(os.getcwd(), 'static')
CAH_lobby_server.session_key = str(os.urandom(24))
CAH_lobby_server.config['SECRET_KEY'] = 'secret!'
CAH_lobby_server.lobby_state = LobbyState
CAH_lobby_server.current_game = None
CAH_lobby_server.external_address = None
socketio = SocketIO(CAH_lobby_server)


class GameLoopThread(Thread):
    def __init__(self, stop_event, interrupt_event):
        self.stop_event = stop_event
        self.interrupt_event = interrupt_event
        Thread.__init__(self)

    def run(self):
        while not self.stop_event.is_set():
            self.loop_process()
            if self.interrupt_event.is_set():
                self.log_interrupted_process()
                self.interrupt_event.clear()

    def loop_process(self):
        if CAH_lobby_server.current_game:
            CAH_lobby_server.current_game.update_game()
        time.sleep(1)

    def log_interrupted_process(self):
        print("Interrupted Game Loop!")


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
                self.log_interrupted_process()
                self.interrupt_event.clear()

    def loop_process(self):
        time.sleep(1)

    def log_interrupted_process(self):
        print("Interrupted!")


# SocketIO Web-socket handling functionality.
@socketio.on('my event', namespace='/ws')
def test_message(message):
    session['players_ready'] = session.get('players_ready', 0) + 1
    print('message received from client')
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('user_connected', namespace='/ws')
def client_connected(data):
    print(data)
    if not data:
        print('Client data called with no data')
        return
    if not CAH_lobby_server.current_game:
        emit('no_host')
        return
    if 'client_connect' in data.values() and 'user' in data.keys():
        print('User %s connected' % data['user'])
        print('User %s\'s ID is %s' % (data['user'], data['user_id']))
        player = CAH_lobby_server.current_game.get_player_by_name(data['user'])
        if not player:
            return
        player.connected = True
        emit('player_connected',
             {'username': player.get_name(),
              'player_count': CAH_lobby_server.current_game.get_player_count()})
        return


@socketio.on('disconnect', namespace='/ws')
def test_disconnect():
    if not CAH_lobby_server.current_game:
        print('Removing Clients from non-active game server')
        disconnect()
    print('Client disconnected')


# ##########################################

STOP_EVENT = Event()
INTERRUPT_EVENT = Event()
CAH_lobby_server.game_thread = GameLoopThread(STOP_EVENT, INTERRUPT_EVENT)
CAH_lobby_server.websocket_thread = WebsocketLoopThread(STOP_EVENT, INTERRUPT_EVENT)
CAH_lobby_server.lobby_state = LobbyState.WaitingForHost


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
        username_cookie = request.cookies.get('username')
        is_valid_player = request.cookies.get('username') is not None
        if not is_valid_player:
            # str(request.cookies.get('session')) not in CAH_lobby_server.session_key:
            response = make_response(redirect('/login'))
            response.set_cookie('session', '', expires=0)
            response.set_cookie('username', '', expires=0)
            return response
        else:
            return func(*args, **kwargs)

    return decorated


@CAH_lobby_server.route('/login')
def login():
    """
    handled in javascript
    """
    return render_template('login.html')


@CAH_lobby_server.route('/add_player', methods=['POST'])
def add_player():
    """
    Api endpoint with variable username as post.
    Username is stored in cookie.
    """
    if 'username' in request.form and CAH_lobby_server.current_game:
        username = request.form['username']
        if username == '' or len(username) == 0:
            return 'Please enter a valid username'
        elif username in CAH_lobby_server.current_game.get_player_names():
            return 'Username' + username + 'has been taken already'
        else:
            print(username + " joined")
            CAH_lobby_server.current_game.add_player(player_name=username)
            response = make_response(redirect('/play', code=302))
            expires = create_expiration_cookie_time()  # function generates 2 day cookie expiration date. (currently)
            response.set_cookie('username', username, expires=expires)
            response.set_cookie('session', CAH_lobby_server.session_key, expires=expires)
            return response
    else:
        return login()


@CAH_lobby_server.route('/')
@CAH_lobby_server.route('/index')
def index():
    """
    Redirected to login
    """
    return login()


@CAH_lobby_server.route('/user')
@login_required
def user():
    """
    Api endpoint: return the user as a string
    """
    username = request.cookies.get('username')
    uid = None
    if username == "HOST":
        return jsonify(id=0000, name=username)
    if CAH_lobby_server.current_game:
        uid = CAH_lobby_server.current_game.get_player_by_name(username).get_id()
        #  a get socket.io between play and user
    return jsonify(id=uid, name=username)


@CAH_lobby_server.route('/czar')
def czar():
    """
    API endpoint: returns user who is the czar as a string
    :return:
    """
    no_czar_response = jsonify(czar_chosen=False, czar='', current_black_card_text='', num_answers=0)
    if not CAH_lobby_server.current_game:
        return no_czar_response
    else:
        if not CAH_lobby_server.current_game.card_czar:
            return no_czar_response
        else:
            return jsonify(czar_chosen=True, czar=CAH_lobby_server.current_game.card_czar.name,
                           current_black_card_text=CAH_lobby_server.current_game.current_black_card.text,
                           num_answers=CAH_lobby_server.current_game.current_black_card.num_answers
                           )


@CAH_lobby_server.route('/lobby_state')
def lobby_state():
    """
    Api endpoint: return if we are in pregame
    """
    if CAH_lobby_server.current_game:
        return jsonify(lobby_state=CAH_lobby_server.lobby_state.value)
    else:
        return jsonify(lobby_state=LobbyState.WaitingForHost.value)


@CAH_lobby_server.route('/player_count')
def player_count():
    """
    Api endpoint: return number of players in the current game.
    (used to determine whether game can start, so user feedback is useful)
    """
    if CAH_lobby_server.current_game:
        return jsonify(player_count=CAH_lobby_server.current_game.get_player_count())
    else:
        return jsonify(player_count=0)


@CAH_lobby_server.route('/hand')
@login_required
def hand():
    """
    Api endpoint: return the user's current hand
    """
    username = request.cookies.get('username')
    return render_template(
        "hand.html",
        hand=CAH_lobby_server.current_game.get_player_by_name(username).hand
    )


@CAH_lobby_server.route('/judgement')
@login_required
def judgement():
    """
    Api endpoint: return the submitted white cards for judgement
    """
    return render_template(
        "judgement.html",
        judgement_cards=CAH_lobby_server.current_game.cards.judged_cards,
        czar=CAH_lobby_server.current_game.card_czar
    )


@socketio.on('user_submit_white_card', namespace='/ws')
@login_required
def submit_white_card(data):
    """
    Call submit white card, to remove card from players hand and add it to judge pile
    """
    print(data)
    print(data.items())
    submitted_white_card_id = int(data["submitted_white_card_id"])
    username = data["user"]
    if CAH_lobby_server.current_game:
        player = CAH_lobby_server.current_game.get_player_by_name(username)
        CAH_lobby_server.current_game.submit_white_card(player, submitted_white_card_id)

        if CAH_lobby_server.current_game.turn_state == TurnState.Judging:
            response = make_response(redirect('/judgement', code=302))
            return response
        else:
            # Returns just a placeholder for now.
            return "OK", 200
    else:
        return "Fucked up fam", 500


@CAH_lobby_server.route('/host', methods=['GET', 'POST'])
def host():
    """
    host a new game if a game is not started.
    """
    if not CAH_lobby_server.current_game:
        print('hosting game')
        CAH_lobby_server.current_game = Game()  # if no game is currently started, start a new one
        CAH_lobby_server.current_game.game_state = GameState.WaitingForEnoughPlayers
        CAH_lobby_server.lobby_state = LobbyState.WaitingForGameCreation

        response = make_response(redirect('/host', code=302))
        response.set_cookie('username', 'HOST')
        return response
    return render_template('game_screen.html')


@CAH_lobby_server.route('/address')
def address():
    return CAH_lobby_server.external_address


@CAH_lobby_server.route('/play')
@login_required
def play():
    """
    playing users go through this route
    """
    return render_template('game_screen.html')


@CAH_lobby_server.route("/interrupt")
def interrupt():
    INTERRUPT_EVENT.set()
    return "OK", 200


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@CAH_lobby_server.route("/shutdown")
def shutdown():
    STOP_EVENT.set()
    CAH_lobby_server.game_thread.join()
    shutdown_server()
    return "OK", 200
