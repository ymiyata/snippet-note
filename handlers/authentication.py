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
            try:
                db_user = yield MongoTask(self.db.profile.find_one, {"openid": openid})
            except Exception as e:
                raise tornado.web.HTTPError(500, "Error while accesssing database: %r" % e)
            print db_user
            if not db_user:
                db_user = {"openid": openid, "email": authenticated_user['email']}
                try:
                    response = yield MongoTask(self.db.profile.insert, db_user)
                except Exception as e:
                    raise tornado.web.HTTPError(500, "Error while accesssing database: %r" % e)
            else:
                del db_user['_id']
            self.set_secure_cookie("user", 
                                   tornado.escape.json_encode(db_user),
                                   httponly=True)
            self.redirect(u"/browse")
            return
        self.authenticate_redirect()
