messages = {}
messages['error'] = {
    400: "You have made a bad request",
    401: "You need to be authenticated to access this page",
    403: "You are not allowed to access this page",
    404: "Sorry. The page was not found",
    405: "Unsupported request method",
    500: "Oops. Something went wrong. Please try again later",
    'default': "Oops. Something went wrong. Please try again later"
}
messages['response'] = {
    'activation_error_duplicate': "Username '%s' is already taken, please choose another username",
    'activation_error_reserved': "'%s' is a reserved keyword, please choose another username",
    'activation_error_username_empty': "Username field is empty. Please enter username",
    'activation_error_invalid_character': "Username must only contain alphanumeric characters, underscores, or dashes and it must not start with a dash",
    "activation_success": "Your acount is activated. You can start saving snippets!"
}

languages = {}
languages = {
    "Plain Text": "misc",
    "Bash": "bsh",
    "C": "c",
    "C#": "csh",
    "C++": "cpp",
    "Clojure": "clj",
    "CoffeeScript": "coffee",
    "Common Lisp": "cl",
    "CSS": "css",
    "Emacs Lisp": "el",
    "F#": "fs",
    "Go": "go",
    "Haskell": "hs",
    "HTML": "html",
    "Java": "java",
    "JavaScript": "js",
    "Latex": "latex",
    "Lisp": "lisp",
    "Lua": "lua",
    "Nemerle": "n",
    "Objective C": "m",
    "OCAML": "ml",
    "Perl": "pl",
    "PHP": "php",
    "Protocol Buffers": "proto",
    "Python": "py",
    "Ruby": "rb",
    "Scala": "scala",
    "Scheme": "scm",
    "SQL": "sql",
    "Tex": "tex",
    "Visual Basic": "vb",
    "VHDL": "vhdl",
    "Wiki Text": "wiki",
    "XML": "xml",
    "XQuery": "xq",
    "XSLT": "xsl",
    "YAML": "yaml"
}

reserved_keywords = [
    "activation",
    "browse",
    "help",
    "language",
    "login",
    "logout",
    "settings",
    "snippet"
]
