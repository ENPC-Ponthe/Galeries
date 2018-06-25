FROM       ubuntu:16.04
MAINTAINER Philippe Ferreira De Sousa

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd

RUN useradd -ms /bin/bash ponthe
RUN echo "${SSH_USERNAME}:${SSH_PASSWORD}" | chpasswd
RUN mkdir /home/ponthe/uploads/ /home/ponthe/waiting_zone/
RUN chown -R ponthe:ponthe /home/ponthe

RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
