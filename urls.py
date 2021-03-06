import re

from handlers.base import *
from handlers.snippet import *
from handlers.authentication import *

urls = [
    (r"/", IndexHandler),
    (r"/snippet/delete/(.+)", SnippetDeleteHandler),
    (r"/snippet/update/(.+)", SnippetUpdateHandler),
    (r"/snippet/download/(.+)", SnippetDownloadHandler),
    (r"/snippet/new", SnippetCreateHandler),
    (r"/browse", SnippetBrowseHandler),
    (r"/logout", LogoutHandler),
    (r"/activation", ActivationHandler),
    (r"/login/google", GoogleLoginHandler),
    (r"/(.+)", UserSnippetListHandler)
]
