#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# run gatekeeper
./keycloak-gatekeeper --config gatekeeper.conf 2>&1 | tee /var/log/gatekeeper/gatekeeper.log &

exec uwsgi --gevent 100 --show-config --http-websockets --enable-threads --threads 4
