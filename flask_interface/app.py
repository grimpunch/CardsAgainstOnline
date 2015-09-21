import os
from flask import Flask, render_template
from flask.ext.login import LoginManager
# from .forms import LoginForm
from CardsAgainstGame.GameHandler import Game

lm = LoginManager()
app = Flask(__name__)
lm.init_app(app)
app.template_folder = os.path.join(os.getcwd(),'../templates')
app.static_folder = os.path.join(os.getcwd(),'../static')
app.game = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user')
def user():
    # return the user as a string
    return "peter"

@app.route('/pregame')
def pregame():
    # return if we are in pregame
    return True

@app.route('/hand')
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


@lm.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


if __name__ == "__main__":
        app.run()

