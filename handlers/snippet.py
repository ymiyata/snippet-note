from datetime import datetime

import tornado.web
from tornado import gen

from mongotask import MongoTask
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
        db_user = yield MongoTask(self.db.profile.find_one, {
            "openid": authenticated_user['openid']
        })
        title = self.get_argument("title")
        description = self.get_argument("description", "")
        scope = "private" if self.get_argument("private", None) else "public"
        snippet = self.get_argument("snippet", "")
        language = self.get_argument("language", "")
        yield gen.Task(self.db.snippet.insert, {
            "user": db_user['_id'],
            "title": title,
            "description": description,
            "scope": scope,
            "snippet": snippet,
            "language": language,
            "created": datetime.now()
        })
        self.redirect(u"/mine")

class SnippetListHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        authenticated_user = self.get_current_user()
        db_user = yield MongoTask(self.db.profile.find_one, {
            "openid": authenticated_user['openid']
        })
        snippets = yield MongoTask(self.db.snippet.find, {"user": db_user['_id']});
        self.render(u"snippet-list.html", snippets=snippets)
