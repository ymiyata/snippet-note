#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options

from urls import urls
from settings import settings

class SnippetNoteApplication(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, urls, **settings)

def main():
    http_server = tornado.httpserver.HTTPServer(SnippetNoteApplication())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
