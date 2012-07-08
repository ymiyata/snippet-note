import tornado.web

class SnippetModule(tornado.web.UIModule):
    def render(self, snippet, editable):
        return self.render_string("modules/snippet.html", snippet=snippet, editable=editable)
