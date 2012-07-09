import tornado.auth
import tornado.web
import tornado.escape
from tornado import gen

from mongotask import *
from handlers.base import *

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
                db_user = {"openid": openid, "email": authenticated_user['email']}
                response = yield MongoTask(self.db.profile.insert, db_user, safe=True)
            self.set_secure_cookie("user", self.json_serialize(db_user), httponly=True)
            self.redirect(u"/browse")
            return
        self.authenticate_redirect()
