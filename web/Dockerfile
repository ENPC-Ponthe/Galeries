FROM tiangolo/uwsgi-nginx-flask:python3.6
MAINTAINER Philippe Ferreira De Sousa

ENV FLASK_APP=ponthe
ENV PROD_MODE=true

RUN apt-key update && apt-get update && apt-get install -y redis-server openssl
RUN git clone https://github.com/vishnubob/wait-for-it.git /wait-for-it

COPY ./app /app

RUN mkdir -p /app/instance/static
RUN mkdir -p /app/instance/tmp/uploads

RUN pip install /app

VOLUME /app/instance/static
