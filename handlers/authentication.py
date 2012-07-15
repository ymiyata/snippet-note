import tornado.auth
import tornado.web
import tornado.escape
from tornado import gen

from db.mongotask import *
from handlers.base import *
from static import messages, reserved_keywords
from decorators import require_activation

import re
import string

class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/")

class GoogleLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    @gen.engine
    def get(self):
        if self.get_argument("openid.mode", None):
            openid = self.get_argument("openid.claimed_id")
            authenticated_user = yield MongoTask(self.get_authenticated_user)
            if not authenticated_user:
                raise tornado.web.HTTPError(500, "Google authentication failed")
            db_user = yield MongoTask(self.db.profile.find_one, {"openid": openid})
            if not db_user:
                db_user = {
                    "openid": openid,
                    "email": authenticated_user['email'],
                    "activated": False
                }
                yield MongoTask(self.db.profile.insert, db_user, safe=True)
            else:
                del db_user['_id']
            self.set_secure_cookie("user", self.json_serialize(db_user), httponly=True)
            self.redirect(u"/")
            return
        self.authenticate_redirect()

class ActivationHandler(BaseHandler):
    __USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9]+[\w-]+$")

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @gen.engine
    def post(self):
        username = self.get_argument("username", None)
        if username:
            lowercase_username = string.lower(username)
            if lowercase_username in reserved_keywords:
                self.set_status(409)
                self.write(messages['response']['activation_error_reserved'] % username)
                self.finish()
                return
            username_taken = yield MongoTask(self.db.profile.find, {
                "username": lowercase_username
            })
            if username_taken:
                self.set_status(409)
                self.write(messages['response']['activation_error_duplicate'] % username)
                self.finish()
                return
            if not self.__USERNAME_REGEX.match(username):
                self.set_status(400)
                self.write(messages['response']['activation_error_invalid_character'])
                self.finish()
                return
            authenticated_user = self.get_current_user()
            yield MongoTask(self.db.profile.update, {"openid": authenticated_user['openid']}, {
                "$set": {
                    "username": lowercase_username,
                    "activated": True
                }
            }, safe=True)
            authenticated_user['username'] = lowercase_username
            authenticated_user['activated'] = True
            self.set_secure_cookie("user", self.json_serialize(authenticated_user), httponly=True)
            self.write(messages['response']['activation_success'])
        else:
            self.set_status(400)
            self.write(messages['response']['activation_error_username_empty'])
        self.finish()
