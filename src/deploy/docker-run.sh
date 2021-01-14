#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x


## Secure endpoints
./oauth2-proxy --config oauth2-proxy.cfg 2>&1 | tee /var/log/oauth2-proxy/oauth2proxy.log &

exec uwsgi --gevent 100 --show-config --http-websockets --enable-threads --threads 4 -b 32768
