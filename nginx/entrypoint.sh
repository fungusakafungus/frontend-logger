#!/bin/bash -xe

# FRONTEND_LOGGER_PORT=tcp://172.17.0.193:8080
sed -i "s/BACKEND/${FRONTEND_LOGGER_PORT#tcp://}/" /etc/nginx/nginx.conf
exec /usr/sbin/nginx
