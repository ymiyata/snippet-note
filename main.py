#!/usr/bin/env python

try:
    import tornado
    import pymongo
    import asyncmongo
except ImportError, error:
    module = error.args[-1].split()[-1]
    raise ImportError("%s\nInstall using: pip install %s" % (error, module))

import sys

if sys.version_info < (2, 6):
    raise AssertionError("Python 2.6 or later required")

import os.path
import re
import uuid
import base64

import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options

from handlers.snippet import *
from handlers.authentication import *

define("port", default=8000, type=int)

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            title=u"Snippet Home",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            login_url=u"/login/google",
        )
        handlers = [
            (r"/", IndexHandler),
            (r"/home", HomeHandler),
            (r"/snippet", SnippetHandler),
            (r"/logout", LogoutHandler),
            (r"/login/google", GoogleLoginHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
