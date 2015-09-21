import os
from flask import Flask, render_template, url_for, redirect, session, make_response
from flask import request, Response
from CardsAgainstGame.GameHandler import Game
from functools import wraps
app = Flask(__name__)
print(os.path.join(os.getcwd(),'../templates'))
app.template_folder = os.path.join(os.getcwd(),'../templates')
app.static_folder = os.path.join(os.getcwd(),'../static')
app.game = None


def login_required(f):
    """
    Redirects to login if not authenticated.
    :param f:
    :return:
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        print(request.cookies.get('username'))
        if request.cookies.get('username') is None or not app.game:
            return redirect('/login')
        else:
            return f(*args, **kwargs)
    return decorated

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/add_player', methods=['POST'])
def add_player():
    if 'username' in request.form and app.game:
        username = request.form['username']
        if username is not '' and username not in app.game.get_player_names():
            print(username + " joined")
            app.game.add_player(player_name=username)
            response = make_response(redirect('/play', code=302))
            response.set_cookie('username', username)
            return response
        else:
            return 'Please enter a valid username'
    else:
        return login()


@app.route('/')
@app.route('/index')
def index():
    return login()


@app.route('/user')
@login_required
def user():
    # return the user as a string
    username = request.cookies.get('username')
    return username


@app.route('/pregame')
@login_required
def pregame():
    # return if we are in pregame
    return True


@app.route('/hand')
@login_required
def hand():
    return render_template("hand.html", hand=app.game.get_player_by_name(user.get_username()).hand)

@app.route('/host', methods=['GET','POST'])
def host():
    # host a new game if a game is not started.
    if not app.game:
        print('hosting game')
        app.game = Game()
    return render_template('game_screen.html')


@app.route('/play')
@login_required
def play():
    # called when in the game
    return render_template('game_screen.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)



