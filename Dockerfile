FROM python:3.4

RUN pip3 install graypy aiohttp

COPY httpserver.py /
EXPOSE 8080
ENTRYPOINT ["python3", "/httpserver.py"]
CMD ["localhost"]
