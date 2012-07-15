def require_activation(f):
    def new_f(self, *args):
        user_json = self.get_secure_cookie("user")
        if not user_json:
            self.redirect(u"/")
            return
        user = self.json_deserialize(user_json)
        if not user.get('activated'):
            self.redirect(u"/activation")
            return
        f(self, *args)
    return new_f
