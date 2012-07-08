from datetime import datetime

import tornado.web
import tornado.httpclient
from tornado import gen
import bson

from languages import languages
from mongotask import MongoTask
from handlers.base import *

class SnippetHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(u"snippet.html", snippet=None)

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

class SnippetUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def get(self, snippet_id=None):
        if not snippet_id:
            raise tornado.httpclient.HTTPError(405, "Snippet ID is required") 
        snippet = yield MongoTask(self.db.snippet.find_one, {
            "_id": bson.objectid.ObjectId(snippet_id)
        })
        self.render(u"snippet.html", snippet=snippet)

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def post(self, snippet_id=None):
        if not snippet_id:
            raise tornado.httpclient.HTTPError(405, "Snippet ID is required") 
        title = self.get_argument("title")
        description = self.get_argument("description", "")
        snippet = self.get_argument("snippet", "")
        language = self.get_argument("language", "")
        yield MongoTask(self.db.snippet.update, {
                "_id": bson.objectid.ObjectId(snippet_id)
            }, {
                "$set": {
                    "title": title,
                    "description": description,
                    "snippet": snippet,
                    "language": language
                }
            })
        self.redirect(u"/mine")


class SnippetListHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        snippet_per_page = 10 
        authenticated_user = self.get_current_user()
        db_user = yield MongoTask(self.db.profile.find_one, {
            "openid": authenticated_user['openid']
        })
        query = {"user": db_user['_id']}
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
        self.render(u"snippet-list.html", relative_url="mine", 
                                          snippets=snippets,
                                          language=language,
                                          page=page,
                                          snippet_per_page=snippet_per_page)

