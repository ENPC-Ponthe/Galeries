from flask import Flask,render_template,request, flash, redirect, url_for, jsonify
from werkzeug import secure_filename
from flask_mail import Mail,Message
import os
from flask_login import LoginManager, UserMixin, login_user , logout_user , current_user , login_required
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, SignatureExpired 

app = Flask(__name__)

dbconnexion = mysql.connector.connect(host="vps.enpc.org", port="7501", \
    user="enpc-ponthe",password="Ponthasm7gorique2017", \
    database="enpc-ponthe")

app.secret_key = 'd66HREGTHUVGDRfdt4'
DOSSIER_UPS = './uploads/'
login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT= 465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'fabien.lespagnol21@gmail.com',
    MAIL_PASSWORD = 'Lavieestbelle94220=GM'
    )
    
mail=Mail(app)

s=URLSafeTimedSerializer(app.secret_key)

class User(UserMixin):
    pass

user = User()

users = {}
cursor = dbconnexion.cursor()
cursor.execute("SELECT * FROM Admin")
var = cursor.fetchall()
for admin in var:
    empDict = {
        'id': admin[0],
        'lastname': admin[1],
        'firstname': admin[2],
        'email': admin[3],
        'password': admin[4]}
    users[str(admin[3])] = empDict
cursor.close()

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
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

@app.route('/creation-compte', methods=['GET', 'POST'])
def creation():
    if request.method == 'POST' :
        user.id = 50 ,
        user.nom=request.form['nom'],
        user.prenom=request.form['prenom'],
        user.email = request.form['email'],
        user.MDP = request.form['password'],
        email = request.form['email']
        token = s.dumps(email, salt = 'email-confirm')
        msg = Message('Confirm Email', sender = 'fabien.lespagnol21@gmail.com',recipients = [email])
        link = url_for('confirm_email', token = token,  _external = True)
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html')
    return render_template('creation-compte.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try :
        email = s.loads(token, salt = 'email-confirm', max_age = 300 )
        cursor = dbconnexion.cursor()
        cursor.execute( " INSERT INTO `Admin` (`id`, `lastname`, `firsname`, `email`, `password`) VALUES (user.id, ,user.nom, user.prenom, user.email, user.MDP) " )
    except SignatureExpired :
        return '<h1> The token is expired </h1> ' 


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
        msg = Message(request.form['message'],sender= 'fabien.lespagnol21@gmail.com', recipients=[request.form['email']])
        mail.send(msg)
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
