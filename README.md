# Galleries Ponthé

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

### ORM

Migration :
```
cd web
export FLASK_APP=ponthe
flask db migrate
flask db upgrade
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
