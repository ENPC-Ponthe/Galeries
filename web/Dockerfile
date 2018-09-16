FROM tiangolo/uwsgi-nginx-flask:python3.6
MAINTAINER Philippe Ferreira De Sousa

ENV NGINX_MAX_UPLOAD 10000m
ENV STATIC_PATH /app/ponthe/static
ENV FLASK_APP=ponthe

RUN apt-get update && apt-get install -y redis-server

COPY ./app /app
COPY ./ponthe.prod.cfg /app/instance/ponthe.cfg
RUN mkdir -p /app/instance/club_folder/uploads && mkdir -p /app/instance/club_folder/waiting_zone && mkdir -p /app/instance/upload_tmp && mkdir -p /app/instance/logs

RUN pip install /app
RUN pip install git+git://github.com/PhilippeFerreiraDeSousa/Flask-Tus.git#egg=Flask-Tus-Ponthe
