from app import app, lm

@app.route('/')
@app.route('/index')
def index():
    return "Hello to Cards against Humanity!"

@app.route('/hello')
def hello():
    return "Hello!"

@lm.user_loader
def load_user(user_id):
    return User.get(user_id)



