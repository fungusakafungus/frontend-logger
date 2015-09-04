import sys

import asyncio
from aiohttp import web
import logging
import graypy


def build_small_png():
    import struct
    import zlib
    def chunk(type, data):
        return (struct.pack('>I', len(data)) + type + data
                + struct.pack('>I', zlib.crc32(type + data)))
    png = (b'\x89PNG\r\n\x1A\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 1, 0, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(struct.pack('>BB', 0, 0)))
           + chunk(b'IEND', b''))
    return png


PNG = build_small_png()
GRAYLOG_HOST = sys.argv[1]
GRAYLOG = graypy.GELFHandler(GRAYLOG_HOST, debugging_fields=False)

logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def handle(request):
    imgfile = request.match_info.get('imgfile', 'blank.png')
    message = request.GET.get('message', 'frontend.metrics')
    record = logging.LogRecord('frontend-logger', 6, imgfile, 0, message, None, None)
    if 'referer' in request.headers:
        record.http_referer = request.headers['referer']
    if 'user-agent' in request.headers:
        record.http_user_agent = request.headers['user-agent']
    record.query_string = request.query_string
    record.__dict__.update(request.GET)
    del record.stack_info
    GRAYLOG.emit(record)
    logging.info("%s?%s", request.path, request.query_string)

    return web.Response(body=PNG)


@asyncio.coroutine
def healthcheck(request):
    return web.Response(body='OK'.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', '/favicon.ico', lambda request: web.Response())
    app.router.add_route('*', '/healthcheck', healthcheck)
    app.router.add_route('GET', '/{imgfile}', handle)

    srv = yield from loop.create_server(app.make_handler(),
                                        '0.0.0.0', 8080)
    print("Server started at http://0.0.0.0:8080, logging to %s" % GRAYLOG_HOST)
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
