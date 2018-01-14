from flask import Flask,render_template,redirect,request
from flask_login import LoginManager, UserMixin, login_user , logout_user , current_user , login_required

app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!
login_manager = LoginManager()

login_manager.init_app(app)

# Mock.
users = {'user': {'password': 'secret'}}

class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    # this must be done by fetching user from database
    if email not in users:
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    # this must be done by fetching user from database
    if email not in users:
        return
    user = User()
    user.id = email
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return getLoginPage()

    email = request.form['email']
    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        login_user(user)
        return getHome()
    return getLoginPage()

@app.route('/logout')
def logout():
    logout_user()
    return getHome()

# handle login failed
@app.errorhandler(401)
def handleError(e):
    print("Erreur lors de l'authentification : ", e)
    return login()

# Authoriser la page de login
@app.route('/login.html')
def getLoginPage():
    return render_template('login.html')

@app.route('/')
@login_required
def getHome():
        return redirect('/index.html')

@app.route('/<name>.html')
@login_required
def getResource(name):
        return render_template(name+'.html')

if __name__ == '__main__':
    app.run(debug=True)
