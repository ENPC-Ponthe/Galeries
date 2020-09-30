FROM tiangolo/uwsgi-nginx-flask:python3.6
MAINTAINER Philippe Ferreira De Sousa

ENV FLASK_APP=ponthe
ENV PROD_MODE=true

RUN apt-key update && apt-get update && apt-get install -y redis-server openssl
RUN sudo apt-get install --reinstall ca-certificates
RUN sudo mkdir /usr/local/share/ca-certificates/cacert.org
RUN sudo wget -P /usr/local/share/ca-certificates/cacert.org http://www.cacert.org/certs/root.crt http://www.cacert.org/certs/class3.crt
RUN sudo update-ca-certificates
RUN git config --global http.sslCAinfo /etc/ssl/certs/ca-certificates.crt
RUN git clone https://github.com/vishnubob/wait-for-it.git /wait-for-it

COPY ./app /app
COPY custom.conf /etc/nginx/conf.d/

RUN mkdir -p /app/instance/static
RUN mkdir -p /app/instance/tmp/uploads

RUN pip install /app

VOLUME /app/instance/static
