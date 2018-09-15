# Galeries Ponthé

### Installation

Exécuter
```
./install.sh
```

### Dévelopement

Activer l'environnement de développement Python :
```
source venv/bin/activate
```

Lancer l'application
```
FLASK_APP=ponthe flask run
```
Pour le rendre disponible sur le réseau ajouter `--host=0.0.0.0` (écoute toutes les IPs publiques)

## ORM

### Migration
Générer les migrations dans *web/migrations/versions* :
```
cd web/app
export FLASK_APP=ponthe
flask db migrate
flask db upgrade
```

### Fixtures
Supprimer la BDD, les images / photos et charger les fixtures :
```
cd web/app
ponthe/manager.py load_fixtures
```

## Mettre en production

Juste faire `deploy.sh` pour faire une sauvegarde de la bdd et redéployer. Pour des objectifs spécifique voir ci-dessous.

Pour rebuild l'image web après modification des fichiers copiés :
```
docker-compose up --build
```

Après modification du .env :
```
docker-compose rm db
docker-compose up
```

Configurer le proxy pass du VPS vers le container docker :
```
sudo cp nginx/ponthe.enpc.org.conf /etc/nginx/sites-available/ponthe.enpc.org
sudo ln -s /etc/nginx/sites-available/ponthe.enpc.org /etc/nginx/sites-enabled/ponthe.enpc.org
sudo certbot --nginx --noninteractive --agree-tos --email root@clubinfo.enpc.fr -d ponthe.enpc.org
sudo systemctl reload nginx
```
Charger les données initiales (catégories) dans le container:
```
docker-compose exec web python ponthe/manager.py load_data
```

Charger les fixtures dans le container :
```
docker-compose exec web python ponthe/manager.py load_fixtures
```

Créer les comptes des nouveaux élèves :
Demander le csv *mon_csv.csv* de création de compte de uPont au KI et faire
```
scp -P 7502 mon_csv.csv ponthe@ponthe.enpc.org:accounts.csv
docker-compose exec web python ponthe/manager.py create_accounts
```

## Ajouter des fichiers aux galeries :

Les consulter :
```
ssh ponthe@localhost -p 7502
```

En ajouter l'event TOSS à l'année 2018 :
```
scp -P 7502 -r TOSS ponthe@ponthe.enpc.org:waiting_zone/2018/
```
où TOSS est un répertoire de photos et vidéos

## TODO

* SQLAlchemy example : https://jeffknupp.com/blog/2014/01/29/productionizing-a-flask-application/
* Générer la doc avec sphinxcontrib-httpdomain :
* set up linters : https://jeffknupp.com/blog/2016/12/09/how-python-linters-will-save-your-large-python-project/
* Docker : http://www.patricksoftwareblog.com/using-docker-for-flask-application-development-not-just-production/

## Ressources :

* http://flask.pocoo.org/docs/0.12/tutorial/introduction/
* http://www.patricksoftwareblog.com/flask-tutorial/
* https://jeffknupp.com/blog/2014/01/29/productionizing-a-flask-application/
* http://freemiumdownload.com/downloads/lifestyle-blog-free-bootstrap-template/
Public domain code snippets :
* http://flask.pocoo.org/snippets/
Slugification :
* http://flask.pocoo.org/snippets/5/
Password salt hashing:
* http://flask.pocoo.org/snippets/54/

## SQLAlchemy
On utilise un modèle de "joined table inheritance"
* http://flask-sqlalchemy.pocoo.org/2.3/customizing/
On pourrait rendre implicite les ids en prolongeant le modèle de SLQAlchemy
* http://docs.sqlalchemy.org/en/latest/orm/inheritance.html
Ambigüités de jointure dûs à l'héritage :
* http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html

## TODO

* Thumbnail : https://github.com/silentsokolov/flask-thumbnails
* Map : https://developers.google.com/maps/documentation/javascript/tutorial
* OpenId Connect : https://github.com/ory/hydra
* Template de galerie
* WTForm
* Uppy : uppy-server et dashboard locales
* React Native
  * Map : https://github.com/react-community/react-native-maps
  * Firebase :
https://medium.com/@salonikogta/beginners-guide-to-implementing-push-notifications-in-android-e896ef54b831
https://firebase.google.com/pricing/
https://firebase.google.com/docs/web/setup?authuser=0
https://console.firebase.google.com/u/0/project/enpc-d6bbe/notification
  * (Web notif https://developers.google.com/web/fundamentals/codelabs/push-notifications/)
