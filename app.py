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
dict_event=dict()
dict_annee=dict()
login_manager = LoginManager()
login_manager.init_app(app)

dict_event['Admissibles']='Admissibles'
dict_event['Biéro']='Biéro'
dict_event['Campagne BDA']='Campagne-BDA'
dict_event['Campagne BDE']='Campagne-BDE'
dict_event['Campagne BDS']='Campagne-BDS'
dict_event['Challenge Centrale Lyon']='Challenge-Centrale-Lyon'
dict_event["Coupe de l'X"]="Coupe-de-l'X"
dict_event["Croisière"]="Croisière"
dict_event["Interne"]="Interne"
dict_event["NDLR"]="NDLR"
dict_event["Scènes ouvertes"]="Scènes-ouvertes"
dict_event["Semaine SKI"]="Semaine-SKI"
dict_event["Skult"]='Skult'
dict_event["Suponts"]='Suponts'
dict_event["TOSS"]="TOSS"
dict_event["tournoi TRIUM"]="tournoi-TRIUM"
dict_event["Trophée Descartes"]="Trophée-Descartes"
dict_event["Voyage"]="Voyage"
dict_event["WE SKI"]="WE-SKI"
dict_event["WEI"]="WEI"

dict_annee["2016"]="2016"
dict_annee["2017"]="2017"
dict_annee["2018"]="2018"

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
        user.id = email
        login_user(user)
        return getHome()
    return getLoginPage()

@app.route('/creation-compte', methods=['GET', 'POST'])
def creation():
    if request.method == 'POST' :
        user.id = 6
        user.nom=request.form['nom']
        user.prenom=request.form['prenom']
        user.email = request.form['email']
        user.MDP = request.form['password']
        email = request.form['email']
        token = s.dumps(email)
        msg = Message('Confirm Email', sender = 'fabien.lespagnol21@gmail.com',recipients = [email])
        link = url_for('confirm_email', token = token,  _external = True)
        msg.body = 'Votre lien est {}'.format(link)
        mail.send(msg)
        return render_template('mail_confirmation.html')
    return render_template('creation-compte.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try :
        email = s.loads(token, max_age = 300 )
        cursor = dbconnexion.cursor()
        print(user.nom)
        add_admin = "INSERT INTO Admin(id, lastname, firstname, email, password) VALUES('%s', '%s', '%s', '%s', '%s')" % (user.id, user.nom, user.prenom , user.email, user.MDP ) 
        cursor.execute(add_admin)
        dbconnexion.commit()
    except SignatureExpired :
        return '<h1> The token is expired </h1> ' 
    return getHome()


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
                    flash(u"Veuillez indiquer la date de l'évenement","error_date")
            else:
                flash(u"Veuillez indiquer le nom de l'évenement","error_event")
        if request.form['Envoyer']=='create_event':
            return redirect('/create_event.html')
        if request.form['Envoyer']=='create_annee':
            return redirect('/create_annee.html')
    ev=sorted(list(dict_event.values()))
    an=sorted(list(dict_annee.values()))
    return render_template('depotfichiers.html',dict_event=ev,dict_annee=an) 


@app.route('/create_event.html', methods=['GET', 'POST'])
@login_required
def create_event():

    if request.method == 'POST':
        new_event=request.form['new_event']
        if new_event:
            dict_event[new_event]=new_event
            return redirect('depotfichiers.html')
        else:
            flash(u"Veuillez indiquer le nom du nouvel évenement","error_new_event")
    return render_template('create_event.html') 

@app.route('/create_annee.html', methods=['GET', 'POST'])
@login_required
def create_annee():

    if request.method == 'POST':
        new_annee=request.form['new_annee']
        if new_annee:
            dict_annee[new_annee]=new_annee
            return redirect('depotfichiers.html')
        else:
            flash(u"Veuillez indiquer la nouvelle année","error_new_annee")
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
