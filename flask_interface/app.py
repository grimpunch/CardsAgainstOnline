from flask import Flask
from flask.ext.login import LoginManager
from .forms import LoginForm

lm = LoginManager()
app = Flask(__name__)
lm.init_app(app)


@app.route('/')
@app.route('/index')
def index():
    return "Hello to Cards against Humanity!"

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
    # contact the game host
    return True

@app.route('/play')
def hand():
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

