#!/usr/bin/env bash
set -e

if [ ! -d "/home/${SSH_USERNAME}" ]; then
    useradd -ms /bin/bash ${SSH_USERNAME}
    mkdir /home/${SSH_USERNAME}/waiting_zone/
fi

echo "${SSH_USERNAME}:${SSH_PASSWORD}" | chpasswd
chown -R ${SSH_USERNAME}:${SSH_USERNAME} /home/${SSH_USERNAME}

exec "$@"