FROM python:3.4

RUN pip3 install graypy aiohttp

COPY httpserver.py /
ENTRYPOINT ["python3", "/httpserver.py"]
CMD ["localhost"]
