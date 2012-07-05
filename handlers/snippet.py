import tornado.web
from tornado import gen

from handlers.base import *

class SnippetHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(u"snippet-add.html")

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def post(self):
        authenticated_user = self.get_current_user()
        db_user = yield gen.Task(self.db.profile.find_one, {"openid", authenticated_user['openid']})
        title = self.get_argument("title")
        description = self.get_argument("description", "")
        scope = "private" if self.get_argument("private", None) else "public"
        snippet = self.get_argument("snippet", "")
        language = self.get_argument("language", "")
        yield gen.Task(self.db.snippet.insert, {
            "user": user['_id'],
            "title": title,
            "scope": scope,
            "snippet": snippet,
            "language": language
        })
