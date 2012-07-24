from datetime import datetime
import string

import tornado.web
import tornado.httpclient
from tornado import gen

from bson.objectid import ObjectId

from pyes.query import BoolQuery, TermQuery, TextQuery

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

class SnippetListHandler(SnippetBaseHandler):
    def initialize(self, page_size=10):
        self._page_size = page_size

    def get_query_param(self):
        return self.get_argument("q", None)

    def build_query(self):
        query_string = self.get_query_param()
        language = self.get_argument("language", None)
        if query_string:
            query = BoolQuery()
            query.add_should(TextQuery("description", query_string))
            query.add_should(TextQuery("snippet", query_string))
            query.add_should(TextQuery("user", query_string))
            if language and language in languages:
                query.add_must(TermQuery("language", language))
            else:
                query_languages = [l for l in query_string.split(' ') if l in languages]
                query.add_should(TextQuery("language", ' '.join(query_languages)))
        else:
            query = {}
            if language and language in languages:
                query["language"] = language
        return query

    def build_search_params(self):
        params = {}
        page = int(self.get_argument("page", "0"))
        if self.get_query_param():
            params['size'] = self._page_size
            params['start'] = self._page_size * page
            params['sort'] = [{"created": {"order": "desc"}}]
        else:
            params['limit'] = self._page_size
            params['skip'] = self._page_size * page
            params['sort'] = [("_id", -1)]
        return params

    def render(self, template_name, **kwargs):
        page = int(self.get_argument("page", "0"))
        language = self.get_argument("language", None)
        if 'page' not in kwargs:
            kwargs['page'] = page
        if 'language' not in kwargs:
            kwargs['language'] = language
        if 'snippet_per_page' not in kwargs:
            kwargs['snippet_per_page'] = self._page_size
        if 'editable' not in kwargs:
            kwargs['editable'] = False
        super(SnippetListHandler, self).render(template_name, **kwargs)

class SnippetBrowseHandler(SnippetListHandler):
    def build_query(self):
        query = super(SnippetBrowseHandler, self).build_query()
        if self.get_query_param():
            query.add_must(TermQuery("scope", "public"))
        else:
            query["scope"] = "public"
        return query

    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        query = self.build_query()
        params = self.build_search_params()
        if self.get_query_param():
            snippets = self.es.search(query=query.search(**params), 
                                      indices=['snippetindex'],
                                      doc_types=['snippet'])
        else:
            snippets = yield MongoTask(self.db.snippet.find, spec=query, **params)
        self.render(u"snippet-list.html", relative_url="browse", snippets=snippets)

class UserSnippetListHandler(SnippetListHandler):
    def editable(self, username):
        user = self.get_current_user()
        return (username == user.get('username'))

    def build_query(self, username):
        query = super(UserSnippetListHandler, self).build_query()
        username = string.lower(username)
        if self.get_query_param():
            query.add_must(TermQuery("user", username))
            if not self.editable(username):
                query.add_must(TermQuery("scope", "public"))
        else:
            query["user"] = username
            if not self.editable(username):
                query["scope"] = "public"
        return query

    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def get(self, username=None):
        if not username:
            self.redirect(u"/browse")
            return
        username = string.lower(username)
        query = self.build_query(username)
        params = self.build_search_params()
        if self.get_query_param():
            print query.search(**params).serialize()
            snippets = self.es.search(query=query.search(**params),
                                      indices=['snippetindex'],
                                      doc_types=['snippet'])
        else:
            snippets = yield MongoTask(self.db.snippet.find, spec=query, **params)
        self.render(u"snippet-list.html", relative_url=username,
                                          snippets=snippets,
                                          editable=self.editable(username))
