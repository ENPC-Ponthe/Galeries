

# -- coding: utf-8 --"

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
directory2=DOSSIER_UPS

login_manager = LoginManager()
login_manager.init_app(app)

mail=Mail(app)

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT= 465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'clubpontheenpc@gmail.com',
    MAIL_PASSWORD = 'ClubPontheEnpc!'
    )
    
mail=Mail(app)

s=URLSafeTimedSerializer(app.secret_key)

class User(UserMixin):
    pass

user = User()

@login_manager.user_loader
def user_loader(email):
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
    if email not in users:
        return
    user = User()
    user.email = email
    return user


@login_manager.request_loader
def request_loader(request):
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
    email = request.form.get('email')
    if email in users and request.form['password'] == users[email]['password']:
        user = User()
        user.email = email
        user.is_authenticated = True
        return user
    else:
        return

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    if request.method == 'GET':
        return getLoginPage()
    email = request.form['email']
    if request.form['password'] == users[email]['password']:
        user.email = email
        login_user(user)
        return getHome()
    return getLoginPage()

@app.route('/creation-compte', methods=['GET', 'POST'])
def creation():
    if request.method == 'POST' :
        user.nom = request.form['nom']
        user.prenom = request.form['prenom']
        user.email = request.form['email']
        user.MDP = request.form['password']
        token = s.dumps(user.email)
        msg = Message('Confirm Email', sender = 'clubpontheenpc@gmail.com',recipients = [user.email] )
        link = url_for('confirm_email', token = token,  _external = True)
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html', m = user.email)
    return render_template('creation-compte.html')

@app.route('/reset-password', methods =['GET','POST'])
def reset():
    if request.method == 'POST' :
        user.email = request.form['email']
        user.MDP = request.form['password']
        token = s.dumps(user.email)
        msg = Message('Reset Email' , sender = 'clubpontheenpc@gmail.com', recipients = [user.email] )
        link = url_for('reset_email', token = token, _external =True )
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html', m = user.email)
    return render_template('reset-password.html')
    
@app.route('/reset_email/<token>')
def reset_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        reset_admin = "UPDATE Admin SET password = '%s' WHERE email = '%s' " % (user.MDP, user.email)
        cursor.execute(reset_admin)
        dbconnexion.commit()
    except SignatureExpired :
        return '<h1> The token is expired </h1> ' 
    return getLoginPage()
        
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        add_admin = "INSERT INTO Admin(lastname, firstname, email, password) VALUES('%s', '%s', '%s', '%s')" % (user.nom, user.prenom , user.email, user.MDP ) 
        cursor.execute(add_admin)
        dbconnexion.commit()
    except SignatureExpired :
        return '<h1> The token is expired </h1> ' 
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
        msg = Message(request.form['message'],sender= 'clubpontheenpc@gmail.com', recipients= 'clubpontheenpc@gmail.com')
        mail.send(msg)
        return render_template("mail_envoye.html" , p=request.form['prenom'], n=request.form['nom'])
    return render_template( 'materiel.html')

@app.route('/depotfichiers.html', methods=['GET', 'POST'])
@login_required
def depotfichiers():
    cursor = dbconnexion.cursor()
    liste_events = []
    cursor.execute("SELECT DISTINCT events FROM Events")
    var = cursor.fetchall()
    for events in var :
        liste_events.append(events[0])
    liste_annees = []
    cursor.execute("SELECT DISTINCT annees FROM Annees")
    var = cursor.fetchall()
    cursor.close()
    for annees in var :
        liste_annees.append(annees[0])    
    cursor.close()
    if request.method == 'POST':
        evenement=request.form['evenement']
        annee=request.form['annee']
        mois=request.form['mois']
        jour=request.form['jour']
        date=jour+'-'+mois+'-'+annee
        if request.form['Envoyer']=='Envoyer':
            if evenement: # on verifie que evenement est non vide

                if date: # on verifie que date est non vide
                    directory=DOSSIER_UPS+date+'/'
                    createFolder(directory)
                    global directory2
                    directory2=directory+evenement+'/'
                    createFolder(directory2)
                    return redirect('/upload.html')
                else:
                    flash(u"Veuillez indiquer la date de l'evenement","error_date")
            else:
                flash(u"Veuillez indiquer le nom de l'evenement","error_event")
        if request.form['Envoyer']=='create_event':
            return redirect('/create_event.html')
        if request.form['Envoyer']=='create_annee':
            return redirect('/create_annee.html')
    ev=sorted(liste_events)
    an=sorted(liste_annees)
    return render_template('depotfichiers.html',dict_event=ev,dict_annee=an) 


@app.route('/create_event.html', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        new_event=request.form['new_event']
        if new_event:
            cursor = dbconnexion.cursor()
            add_event = "INSERT INTO Events (events) VALUES('%s')" % (new_event)
            cursor.execute(add_event) 
            dbconnexion.commit()
        else:
            flash(u"Veuillez indiquer le nom du nouvel evenement","error_new_event")
    return render_template('create_event.html') 

@app.route('/create_annee.html', methods=['GET', 'POST'])
@login_required
def create_annee():
    if request.method == 'POST':
        new_annee = request.form['new_annee']
        if new_annee:
            cursor = dbconnexion.cursor()
            add_annee = "INSERT INTO Annees (annees) VALUES('%s')" % (new_annee)
            cursor.execute(add_annee) 
        return redirect('depotfichiers.html')
    else:
        flash(u"Veuillez indiquer la nouvelle annee","error_new_annee")
    return render_template('create_annee.html') 
@app.route('/upload.html', methods=['GET', 'POST'])
@login_required
def upload():
    t1=True
    t2=True
    if request.method == 'POST':
        for f in request.files.getlist('photos'):
            if f:
                if extension_ok(f.filename): # on verifie que son extension est valide
                    filename = secure_filename(f.filename)
                    f.save(directory2+filename)
                else:
                    t1=False
            else:
                t2=False
        if t1==True:
            if t2==True:
                flash(u'Bravo! Vos images ont ete envoyees! :)','succes')
            else:
                flash(u'Vous avez oublie le fichier !', 'error')
        if t2==False:
            flash(u'Ce fichier ne porte pas l extension png, jpg, jpeg, gif ou bmp !', 'error')
    return render_template('upload.html')

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

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)


if __name__ == '__main__':
    app.run(debug=True)
