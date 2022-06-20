#!/usr/bin/env python
#
# Runs a Tornado web server with a django project
# Make sure to edit the DJANGO_SETTINGS_MODULE to point to your settings.py
#

import sys
import tornado.httpserver
from tornado.options import parse_command_line
import tornado.ioloop
import tornado.web
import proj.asgi

GLOBAL_CHARSET = "utf-8"


class AsgiHandler(tornado.web.RequestHandler):
    '''
        Credit to @plter on GitHub for the ASGI Handler
        https://github.com/plter/tornado_asgi_handler
    '''

    def initialize(self, asgi_app) -> None:
        super().initialize()
        self._asgi_app = asgi_app

    async def handle_request(self):
        headers = []
        for k in self.request.headers:
            for v in self.request.headers.get_list(k):
                headers.append(
                    (k.encode(GLOBAL_CHARSET).lower(), v.encode(GLOBAL_CHARSET))
                )

        scope = {
            "type": self.request.protocol,
            "http_version": self.request.version,
            "path": self.request.path,
            "method": self.request.method,
            "query_string": self.request.query.encode(GLOBAL_CHARSET),
            "headers": headers,
            "client": (self.request.remote_ip, 0)
        }

        async def receive():
            return {'body': self.request.body, "type": "http.request", "more_body": False}

        async def send(data):
            if data['type'] == 'http.response.start':
                self.set_status(data['status'])
                self.clear_header("content-type")
                for h in data['headers']:
                    if len(h) == 2:
                        self.add_header(
                            h[0].decode(GLOBAL_CHARSET),
                            h[1].decode(GLOBAL_CHARSET)
                        )
            elif data['type'] == 'http.response.body':
                self.write(data['body'])
            else:
                raise RuntimeError(
                    f"Unsupported response type \"{data['type']}\" for asgi app")

        await self._asgi_app(scope, receive, send)

    async def get(self):
        await self.handle_request()

    async def post(self):
        await self.handle_request()

    async def delete(self):
        await self.handle_request()


class StaticFileHandler_Error(tornado.web.StaticFileHandler):
    '''
        Static file handler with error pages
    '''

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render('app/templates/404.html')
        elif status_code == 403:
            self.render('app/templates/403.html')
        else:
            self.render('app/templates/500.html')


def main():
    asgi_app = proj.asgi.application
    parse_command_line()
    tornado_app = tornado.web.Application(
        [
            ("/static/(.*)", StaticFileHandler_Error,
             {'path': 'static'}),  # Serve Static Files
            ("/media/(.*)", StaticFileHandler_Error,
             {'path': 'media'}),  # Serve Media Files
            # Serve Django Application
            ('.*', AsgiHandler, dict(asgi_app=asgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    port = 8080 if len(sys.argv) != 2 else int(sys.argv[1])
    server.listen(port)
    print(F"Application running on http://localhost:{port}/")
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
