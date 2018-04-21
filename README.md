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
cd web
export FLASK_APP=ponthe
flask db migrate
flask db upgrade
```

### Fixtures
Supprimer la BDD et charges les fixtures de tous les fichiers YAML de *web/fixtures/* :
```
cd web
ponthe/manager.py load_fixtures
```

## Mettre en production

Depuis la racine faire :
```
docker-compose up
```

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

Charger les fixtures dans le container :
```
docker run -it pontheenpcorg_web python ponthe/manager.py load_fixtures   # not working :'(
```

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

## SQLAlchemy
On utilise un modèle de "joined table inheritance"
* http://flask-sqlalchemy.pocoo.org/2.3/customizing/
On pourrait rendre implicite les ids en prolongeant le modèle de SLQAlchemy
* http://docs.sqlalchemy.org/en/latest/orm/inheritance.html
Ambigüités de jointure dûs à l'héritage :
* http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html
