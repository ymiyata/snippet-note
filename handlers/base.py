import tornado.escape
import tornado.web
from tornado import gen

import asyncmongo

from languages import languages
from mongotask import *

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not hasattr(self, "_db"):
            settings = dict(
                host="127.0.0.1",
                port=9090,
                dbname="snippetnote"
            )
            self._db = asyncmongo.Client(pool_id="snippetnote_pool", **settings)
        return self._db

    def get_login_url(self):
        return u"/"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        return None

class IndexHandler(BaseHandler):
    def get(self):
        self.render(u"index.html")

class BrowseHandler(BaseHandler):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        snippet_per_page = 10
        query = {"scope": "public"}
        language = self.get_argument("language", None)
        page = int(self.get_argument("page", "0"))
        if language and language in languages:
            query["language"] = language
        snippets = yield MongoTask(
            self.db.snippet.find,
            spec=query,
            limit=snippet_per_page,
            skip=page * snippet_per_page,
            sort=[("_id", -1)]
        )
        self.render(u"snippet-list.html", relative_url="browse", 
                                          snippets=snippets,
                                          language=language,
                                          page=page,
                                          snippet_per_page=snippet_per_page)
