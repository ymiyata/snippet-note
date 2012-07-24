import tornado.web
from tornado import gen

import asyncmongo

import json
import bson.json_util

from pyes import ES

from static import messages
from db.mongotask import *

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        if not hasattr(self, "_db"):
            settings = dict(
                host="127.0.0.1",
                port=27017,
                dbname="snippetnote"
            )
            self._db = asyncmongo.Client(pool_id="snippetnote_pool", **settings)
        return self._db

    @property
    def es(self):
        if not hasattr(self, "_es"):
            self._es = ES("127.0.0.1:9200")
        return self._es

    def json_deserialize(self, json_data):
        return json.loads(json_data, object_hook=bson.json_util.object_hook)

    def json_serialize(self, data):
        return json.dumps(data, default=bson.json_util.default).replace("</", "<\\/")

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return self.json_deserialize(user_json)
        return None

    def get_home_url(self):
        user = self.get_current_user()
        if user and user['username']:
            return u"/%s" % user['username']
        return u"/"

    def write_error(self, status_code, **kwargs):
        if status_code in messages['error']:
            message = messages['error'][status_code]
        else:
            message = messages['error']['default']
        self.render(u"error.html", code=status_code, message=message)

class IndexHandler(BaseHandler):
    def get(self):
        next_url = self.get_argument("next", None)
        user = self.get_current_user()
        if next_url:
            if user:
                self.redirect(next_url)
            else:
                self.redirect(u"/")
            return
        if user and user.get('username'):
            self.redirect(u"/%s" % user.get("username"))
        else:
            self.render(u"index.html")
