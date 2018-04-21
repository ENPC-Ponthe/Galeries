FROM tiangolo/uwsgi-nginx-flask:python3.6

ENV NGINX_MAX_UPLOAD 1000m
ENV STATIC_PATH /app/ponthe/static
ENV FLASK_APP=ponthe

COPY ./app /app

RUN pip install /app
