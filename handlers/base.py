import tornado.escape

import asyncmongo

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
        return u"/login/google"

    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if user_json:
            return tornado.escape.json_decode(user_json)
        return None

class IndexHandler(BaseHandler):
    def get(self):
        self.render(u"index.html")

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        json_user = self.get_secure_cookie("user")
        if json_user:
            email = tornado.escape.json_decode(json_user)['email']
            self.render("home.html", email=email)
        else:
            self.redirect("/")
