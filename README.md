# Galeries Ponthé

This software is a API used for the Ponthe audiovisual club. It is powered by Flask and SQLAlchemy. You can access the documentation by browsing http://localhost:${WEB_PORT}/api/.


# Installation

## Prerequisites

Docker

## Installation
Run

```
docker-compose build
docker-compose up
```

Then, open a new terminal, and enter:

```
docker exec -it galeries_web_1 /bin/bash/
flask db init
flask db upgrade
```

You can then kill the server by running:
```
docker-compose kill
```

# Usage


```
docker-compose up
```

Kill with `docker-compose kill`, delete images with `docker-compose down` and delete volumes with:

```
docker volume rm db_backup
docker volume rm club_folder
```
