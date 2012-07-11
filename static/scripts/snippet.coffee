$ ->
    languageMap =
        "Bash": "sh"
        "C": "c_cpp"
        "C++": "c_cpp"
        "Clojure": "clojure"
        "CoffeeScript": "coffee"
        "C#": "csharp"
        "CSS": "css"
        "F#": "ocaml"
        "Go": "golang"
        "HTML": "html"
        "Java": "java"
        "JavaScript": "javascript"
        "Latex": "latex"
        "Lua": "lua"
        "OCAML": "ocaml"
        "Perl": "perl"
        "PHP": "php"
        "Python": "python"
        "Ruby": "ruby"
        "Scala": "scala"
        "SQL": "sql"
        "Tex": "latex"
        "XML": "xml"
        "XQuery": "xquery"
        "YAML": "yaml"

    setMode = (modeName) ->
        for name, mode of languageMap
            if name is modeName
                LanguageMode = ace.require("ace/mode/#{languageMap[name]}").Mode
                editor.getSession().setMode(new LanguageMode)
                return true
        NormalMode = ace.require("ace/mode/text").Mode
        editor.getSession().setMode(new NormalMode)
        false

    editor = ace.edit "editor"
    editor.setTheme "ace/theme/twilight"
    setMode $("#language-selector").val()

    $("#language-selector").change ->
        setMode $(this).val()
        return

    editor.getSession().on 'change', ->
        $("#snippet-data").text editor.getSession().getValue()
        return

    $("#scope-button-group button").click ->
        scope = if $(this).attr('data-scope') is 'public' then "" else "private"
        $("#scope-button-group input[name='private']").val(scope)
        return
    return

