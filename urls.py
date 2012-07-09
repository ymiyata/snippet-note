import re

from handlers.base import *
from handlers.snippet import *
from handlers.authentication import *

urls = [
    (r"/", IndexHandler),
    (r"/mine", SnippetListHandler),
    (r"/snippet/delete/(.*)", SnippetDeleteHandler),
    (r"/snippet/(.*)", SnippetUpdateHandler),
    (r"/snippet", SnippetHandler),
    (r"/browse", BrowseHandler),
    (r"/logout", LogoutHandler),
    (r"/login/google", GoogleLoginHandler),
]

