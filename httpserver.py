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
GRAYLOG = graypy.GELFHandler('graylog2.staging.aws.jimdo-server.com', debugging_fields=False)

logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def handle(request):
    imgfile = request.match_info.get('imgfile', 'blank.png')
    record = logging.LogRecord('frontend', 6, '', 0, 'frontend.metrics', None, None)
    record.http_host = request.headers['host']
    record.query_string = request.query_string
    GRAYLOG.emit(record)
    logging.info("%s?%s", request, request.query_string)

    return web.Response(body=PNG)


@asyncio.coroutine
def healthcheck(request):
    return web.Response(body='OK'.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', '/healthcheck', healthcheck)
    app.router.add_route('GET', '/{imgfile}', handle)

    srv = yield from loop.create_server(app.make_handler(),
                                        '0.0.0.0', 8080)
    print("Server started at http://0.0.0.0:8080")
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
