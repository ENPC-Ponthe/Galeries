FROM tiangolo/uwsgi-nginx-flask:python3.6
MAINTAINER Philippe Ferreira De Sousa

ENV FLASK_APP=ponthe
ENV PROD_MODE=true

RUN apt-key update && apt-get update && apt-get install -y redis-server openssl
RUN git clone https://github.com/vishnubob/wait-for-it.git /wait-for-it

ADD ./app/ /app/

RUN mkdir -p /app/instance/uploads && mkdir -p /app/instance/club_folder/waiting_zone && mkdir -p /app/instance/club_folder/apk && mkdir -p /app/instance/thumbs && mkdir -p /app/instance/club_folder/logs && mkdir -p /app/instance/upload_tmp && mkdir -p /app/instance/keys

RUN pip install /app
RUN pip install --upgrade pip
RUN pip install flask-restplus

RUN pip install git+https://github.com/PhilippeFerreiraDeSousa/Flask-Tus.git#egg=Flask-Tus-Ponthe
