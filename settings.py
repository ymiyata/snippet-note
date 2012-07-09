import os.path
import uuid
import base64

import tornado.options
from tornado.options import define, options

from modules.snippet import *

define("port", default=8000, help="Run server on the given port", type=int)
define("debug", default=False, help="Debug mode")
tornado.options.parse_command_line()

settings = dict(
    title=u"Snippet Home",
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    xsrf_cookies=True,
    cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
    login_url=u"/",
    ui_modules={"Snippet": SnippetModule},
)

