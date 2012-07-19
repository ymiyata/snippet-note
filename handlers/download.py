from handlers.base import BaseHandler

class DownloadHandler(BaseHandler):
    @tornado.web.authenticated
    @require_activation
    @tornado.web.asynchronous
    @gen.engine
    def get(self, snippet_id):
        

