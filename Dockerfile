FROM nginx

COPY jessie-backports.preferences /etc/apt/preferences.d/
RUN echo "deb http://http.debian.net/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y vim fortune-mod
RUN apt-get install -y python3
RUN apt-get install -y python3-aiohttp
RUN apt-get install -y python3-pip
RUN pip3 install graypy

COPY nginx.conf /etc/nginx/nginx.conf
RUN mkdir /var/www
RUN /usr/games/fortune > /var/www/index.html
#ENTRYPOINT /usr/sbin/nginx

COPY httpserver.py /
ENTRYPOINT ["python3", "/httpserver.py"]
CMD ["localhost"]
