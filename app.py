

# -- coding: utf-8 --"

from flask import Flask,render_template,request, flash, redirect, url_for, jsonify
from werkzeug import secure_filename
from flask_mail import Mail,Message
import os
from flask_login import LoginManager, UserMixin, login_user , logout_user , current_user , login_required
import mysql.connector
from itsdangerous import URLSafeTimedSerializer, SignatureExpired 
import string
import random 

liste_char=string.ascii_letters+string.digits

app = Flask(__name__)

dbconnexion = mysql.connector.connect(host="vps.enpc.org", port="7501", \
    user="enpc-ponthe",password="Ponthasm7gorique2017", \
    database="enpc-ponthe")

app.secret_key = 'd66HREGTHUVGDRfdt4'
DOSSIER_UPS = './static/uploads/'
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

def connexion(dict_events) :
    cursor = dbconnexion.cursor()
    cursor.execute ( "SELECT DISTINCT annees FROM Dossier")
    liste_annees = cursor.fetchall()
    for annee in liste_annees :
        cursor.execute(" SELECT DISTINCT events FROM Dossier WHERE annees =  '%s' " % (annee[0]))
        liste_events = cursor.fetchall()
        dict_events[annee[0]] = []
        for event in liste_events :
            dict_events[annee[0]].append(event[0])
    cursor.close()

@login_manager.user_loader
def user_loader(email):
    users = {}
    cursor = dbconnexion.cursor()
    cursor.execute("SELECT * FROM Admin")
    liste_admin = cursor.fetchall()
    cursor.close()
    for admin in liste_admin:
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
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = {}
    cursor = dbconnexion.cursor()
    cursor.execute("SELECT * FROM Admin")
    liste_admin = cursor.fetchall()
    cursor.close()
    for admin in liste_admin:
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
        user.id = email
        user.is_authenticated = True
        return user
    else:
        return

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = {}
    cursor = dbconnexion.cursor()
    cursor.execute("SELECT * FROM Admin")
    liste_admin = cursor.fetchall()
    for admin in liste_admin:
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
        user.id = email
        login_user(user)
        return getHome()
    return getLoginPage()


@app.route('/creation-compte', methods=['GET', 'POST'])
def creation():
    if request.method == 'POST' :
        user.nom = request.form['nom']
        user.prenom = request.form['prenom']
        user.id = request.form['email']
        user.MDP = request.form['password']
        user.CMDP = request.form['confirmation_password']
        if user.MDP == user.CMDP :
            token = s.dumps(user.id)
            msg = Message('Confirm Email', sender = 'clubpontheenpc@gmail.com',recipients = [user.id] )
            link = url_for('confirm_email', token = token,  _external = True)
            msg.body = 'Votre lien est {}'.format(link)
            mail.send(msg)
            return render_template('mail_confirmation.html', m = user.id,)
        else : 
            flash(u'Les deux mots de passe ne concordent pas', "error_password")
    return render_template('creation-compte.html')

@app.route('/reset-password', methods =['GET','POST'])
def reset():
    if request.method == 'POST' :
        user.id = request.form['email']
        user.MDP = request.form['password']
        token = s.dumps(user.id)
        msg = Message('Reset Email' , sender = 'clubpontheenpc@gmail.com', recipients = [user.id] )
        link = url_for('reset_email', token = token, _external =True )
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html', m = user.id)
    return render_template('reset-password.html')
    
@app.route('/reset_email/<token>')
def reset_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        reset_admin = "UPDATE Admin SET password = '%s' WHERE email = '%s' " % (user.MDP, user.id)
        cursor.execute(reset_admin)
        dbconnexion.commit()
        cursor.close()
    except SignatureExpired :
        return '<h1> The token is expired </h1> ' 
    return getLoginPage()
        
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        add_admin = "INSERT INTO Admin(lastname, firstname, email, password) VALUES('%s', '%s', '%s', '%s')" % (user.nom, user.prenom , user.id, user.MDP ) 
        cursor.execute(add_admin)
        dbconnexion.commit()
        cursor.close()
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
@app.route('/login')
def getLoginPage():
    return render_template('login.html')

@app.route('/materiel',methods=['GET','POST'])
@login_required
def reservation() :
    dict_events = {}
    connexion(dict_events)
    if request.method == 'POST':
        msg = Message(request.form['message'],sender= 'clubpontheenpc@gmail.com', recipients= 'clubpontheenpc@gmail.com', events = liste_ev)
        mail.send(msg)
        return render_template("mail_envoye.html" , p=request.form['prenom'], n=request.form['nom'])
    return render_template( 'materiel.html', dict_events = dict_events)

@app.route('/depotfichiers', methods=['GET', 'POST'])
@login_required
def depotfichiers():
    dict_events = {}
    connexion(dict_events)
    if request.method == 'POST':
        evenement=request.form['evenement']
        annee=request.form['annee']
        if request.form['Envoyer']=='Envoyer':
            if evenement: # on verifie que evenement est non vide
                if annee: # on verifie que date est non vide
                    directory=DOSSIER_UPS+annee+'/'
                    createFolder(directory)
                    directory2=directory+evenement+'/'
                    createFolder(directory2)
                    return redirect(url_for('upload', annee = annee, event = evenement))
                else:
                    flash(u"Veuillez indiquer la date de l'evenement","error_date")
            else:
                flash(u"Veuillez indiquer le nom de l'evenement","error_event")
        if request.form['Envoyer']=='create_event':
            return redirect('/create_event')
        if request.form['Envoyer']=='create_annee':
            return redirect('/create_annee')
    cursor = dbconnexion.cursor()
    liste_events = []
    cursor.execute("SELECT DISTINCT events FROM Events")
    var = cursor.fetchall()
    for event in var :
        liste_events.append(event[0])
    liste_annees = []
    cursor.execute("SELECT DISTINCT annees FROM Annees")
    var = cursor.fetchall()
    for annee in var :
        liste_annees.append(annee[0])   
    cursor.close()
    ev=sorted(liste_events)
    an=sorted(liste_annees)
    return render_template('depotfichiers.html',dict_event=ev,dict_annee=an, dict_events=dict_events) 


@app.route ('/archives/<cat>')
@login_required 
def archives_categorie(cat):
    dict_events = {}
    connexion(dict_events)
    cursor = dbconnexion.cursor()
    selection = " SELECT events, annees, filename FROM Dossier WHERE (couv = '%s' AND cat ='%s' )" % (1,cat)
    cursor.execute(selection)
    liste_events_annees = cursor.fetchall()
    cursor.close()
    return render_template('archives_categorie.html', liste_events_annees = liste_events_annees, dict_events = dict_events ) 
    
    
@app.route('/archive/<annee>')
@login_required
def archives_annee(annee):
    dict_events = {}
    connexion(dict_events)
    dict_events_annee = {}
    cursor = dbconnexion.cursor()
    selection = " SELECT events,filename FROM Dossier WHERE (couv = '%s' AND annees = '%s' )" % (1,annee)
    cursor.execute(selection)
    events = cursor.fetchall()
    for event in events:
        dict_events_annee[event[0]] = event[1] 
    return render_template('archives_annee.html', annee = annee ,events_annee = dict_events_annee, dict_events=dict_events )
     
@app.route('/archives/<annee>/<event>')
@login_required
def archives_evenement(annee,event):
    dict_events = {}
    connexion(dict_events)
    liste_filename = []
    cursor = dbconnexion.cursor()
    selection = "SELECT filename FROM Dossier WHERE (events = '%s' AND annees ='%s') " % (event,annee)
    cursor.execute(selection)
    var = cursor.fetchall()
    cursor.close()
    for filename in var :
        liste_filename.append(filename[0])
    return render_template('archives_evenement.html', annee = annee, event = event, dict_events=dict_events, filename = liste_filename)

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    dict_events = {}
    connexion(dict_events)
    if request.method == 'POST':
        new_event=request.form['new_event']
        if new_event:
            cursor = dbconnexion.cursor()
            add_event = "INSERT INTO Events (events) VALUES('%s')" % (new_event)
            cursor.execute(add_event) 
            dbconnexion.commit()
            cursor.close()
            return redirect('/depotfichiers')
        else:
            flash(u"Veuillez indiquer le nom du nouvel evenement","error_new_event")
    return render_template('create_event.html', dict_events=dict_events) 

@app.route('/create_annee', methods=['GET', 'POST'])
@login_required
def create_annee():
    dict_events = {}
    connexion(dict_events)
    if request.method == 'POST':
        new_annee = request.form['new_annee']
        if new_annee:
            cursor = dbconnexion.cursor()
            add_annee = "INSERT INTO Annees (annees) VALUES('%s')" % (new_annee)
            cursor.execute(add_annee) 
            dbconnexion.commit()
            cursor.close()
            return redirect('depotfichiers')
    else:
        flash(u"Veuillez indiquer la nouvelle annee","error_new_annee")
    return render_template('create_annee.html', dict_events=dict_events) 
    
@app.route('/upload/<annee>/<event>', methods=['GET', 'POST'])
@login_required
def upload(annee, event):
    dict_events = {}
    connexion(dict_events)
    t1=True
    t2=True
    if request.method == 'POST':
        for f in request.files.getlist('photos'):
            if f:
                if extension_ok(f.filename.lower()): # on verifie que son extension est valide
                    _, ext = os.path.splitext(f.filename)
                    filename = ""
                    for i in range(54):
                        filename += liste_char[random.randint(0,len(liste_char)-1)]
                    filename= filename + ext
                    f.save( DOSSIER_UPS + annee + '/' + event + '/' + filename)
                    cursor = dbconnexion.cursor()
                    add_lien = "INSERT INTO Dossier (events,annees,filename) VALUES ('%s','%s','%s')" % (event,annee,filename)
                    cursor.execute(add_lien)
                    dbconnexion.commit()
                    cursor.close()
                else:
                    t1=False
            else:
                t2=False
        if t1==True:
            if t2==True:
                flash(u'Bravo! Vos images ont ete envoyees! :)','succes')
            else:
                flash(u'Vous avez oublie le fichier !', 'error')
        if t1==False:
            flash(u'Ce fichier ne porte pas l extension png, jpg, jpeg, gif ou bmp !', 'error')
    return render_template('upload.html' , dict_events=dict_events)

@app.route('/')
@login_required
def getHome():
    return redirect('/index')

@app.route('/<name>')
@login_required
def getResource(name):
    dict_events = {}
    connexion(dict_events)
    return render_template(name+'.html', dict_events = dict_events )

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
