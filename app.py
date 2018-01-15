from flask import Flask,render_template,request, flash, redirect, url_for, send_file
from werkzeug import secure_filename
from flask_mail import Mail,Message
import os
from flask_login import LoginManager, UserMixin, login_user , logout_user , current_user , login_required

app = Flask(__name__)
app.secret_key = 'd66HREGTHUVGDRfdt4'
DOSSIER_UPS = './uploads/'
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
    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        user.is_authenticated = True
        return user
    else:
        return

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

@app.route('/materiel.html',methods=['GET','POST'])
@login_required
def reservation() :
    if request.method == 'POST':
        # msg = Message(request.form['message'],sender= ["fabien.lespagnol@eleves.enpc.fr"], recipients=[request.form['Email']])
        # mail.send(msg)
        return render_template("mail_envoye.html" , p=request.form['prenom'], n=request.form['nom'])
    return render_template( 'materiel.html')

@app.route('/depotfichiers.html', methods=['GET', 'POST'])
@login_required
def depotfichiers():
    if request.method == 'POST':

        f = request.files['fic']

        if f: # on verifie qu'un fichier a bien ete envoye

            if extension_ok(f.filename): # on verifie que son extension est valide

                nom = secure_filename(f.filename)

                f.save(DOSSIER_UPS + nom)

                flash(u'Bravo! Vos images ont ete envoyees! :)','succes')

            else:

                flash(u'Ce fichier ne porte pas l extension png, jpg, jpeg, gif ou bmp !', 'error')

    else:
        flash(u'Vous avez oublie le fichier !', 'error')
    return render_template('depotfichiers.html')

@app.route('/')
@login_required
def getHome():
    return redirect('/index.html')

@app.route('/<name>.html')
@login_required
def getResource(name):
        return render_template(name+'.html')

def extension_ok(nomfic):
    """ Renvoie True si le fichier possede une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('png', 'jpg', 'jpeg', 'gif', 'bmp')


if __name__ == '__main__':
    app.run(debug=True)
