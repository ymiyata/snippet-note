from datetime import datetime
import string

import tornado.web
import tornado.httpclient
from tornado import gen

from bson.objectid import ObjectId

from static import languages
from db.mongotask import MongoTask
from handlers.base import BaseHandler
from decorators import require_activation

class SnippetBaseHandler(BaseHandler):
    def owns_snippet(self, snippet):
        user = self.get_current_user()
        return user['username'] == snippet['user']

class SnippetCreateHandler(SnippetBaseHandler):
    @tornado.web.authenticated
    @require_activation
    def get(self):
        self.render(u"snippet.html", snippet=None)

    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def post(self):
        user = self.get_current_user()
        title = self.get_argument("title", "")
        description = self.get_argument("description", "")
        scope = "private" if self.get_argument("private", None) else "public"
        code = self.get_argument("snippet", "")
        language = self.get_argument("language", "")
        yield MongoTask(self.db.snippet.insert, {
            "user": user['username'],
            "title": title,
            "description": description,
            "scope": scope,
            "snippet": code,
            "language": language,
            "created": datetime.now()
        })
        self.redirect(self.get_home_url())

class SnippetUpdateHandler(SnippetBaseHandler):
    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def get(self, snippet_id=None):
        if not snippet_id:
            self.send_error(404)
        snippet = yield MongoTask(self.db.snippet.find_one, {
            "_id": ObjectId(snippet_id)
        })
        if not self.owns_snippet(snippet):
            self.send_error(404)
        self.render(u"snippet.html", snippet=snippet)

    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def post(self, snippet_id=None):
        if not snippet_id:
            self.send_error(404)
        snippet = yield MongoTask(self.db.snippet.find_one, {
            "_id": ObjectId(snippet_id)
        })
        if not self.owns_snippet(snippet):
            self.send_error(404)
        title = self.get_argument("title", "")
        description = self.get_argument("description", "")
        scope = "private" if self.get_argument("private", None) else "public"
        code = self.get_argument("snippet", "")
        language = self.get_argument("language", "Plain Text")
        yield MongoTask(self.db.snippet.update, {
                "_id": ObjectId(snippet_id),
            }, {
                "$set": {
                    "title": title,
                    "description": description,
                    "scope": scope,
                    "snippet": code,
                    "language": language
                }
            }, safe=True)
        self.redirect(self.get_home_url())

class SnippetDeleteHandler(SnippetBaseHandler):
    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def get(self, snippet_id=None):
        if not snippet_id:
            self.send_error(404)
        snippet = yield MongoTask(self.db.snippet.find_one, {
            "_id": ObjectId(snippet_id)
        })
        if not self.owns_snippet(snippet): 
            self.send_error(404)
        yield MongoTask(self.db.snippet.remove, spec_or_id={
            "_id": ObjectId(snippet['_id'])
        }, safe=True)
        self.redirect(self.get_home_url())

class SnippetListHandler(SnippetBaseHandler):
    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def get(self, username=None):
        if not username:
            self.redirect(u"/browse")
            return
        username = string.lower(username)
        snippet_per_page = 10 
        user = self.get_current_user()
        query = {"user": username}
        language = self.get_argument("language", None)
        page = int(self.get_argument("page", "0"))
        if language and language in languages:
            query["language"] = language
        current_users_page = (username == user.get("username"))
        if not current_users_page:
            query["scope"] = "public"
        snippets = yield MongoTask(
            self.db.snippet.find,
            spec=query,
            limit=snippet_per_page,
            skip=page * snippet_per_page,
            sort=[("_id", -1)]
        )
        self.render(u"snippet-list.html", relative_url=username,
                                          editable=current_users_page,
                                          snippets=snippets,
                                          language=language,
                                          page=page,
                                          snippet_per_page=snippet_per_page)

class SnippetDownloadHandler(SnippetBaseHandler):
    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def get(self, snippet_id=None):
        if not snippet_id:
            self.send_error(404)
        snippet = yield MongoTask(self.db.snippet.find_one, {
            "_id": ObjectId(snippet_id)
        })
        if not self.owns_snippet(snippet):
            self.send_error(404)
        self.set_header("Content-Type", "application/force-download")
        self.set_header("Content-Disposition", "attachment; filename=%s" % snippet.get("title"))
        self.write(snippet.get("snippet"))
        self.finish()
