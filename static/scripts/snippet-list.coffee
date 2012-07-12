$ ->
    keep = 10
    prepareblock = (block) ->
        block.addClass('collapsable')
        collapse keep, block
        block.append $("<li/>").text("...").addClass("ellipsis")
        return
    numlines = (block) ->
        lines = $('ol.linenums li', block)
        return lines.size()
    collapse = (begin, block) ->
        n = numlines(block)
        lines = $('ol.linenums li', block)
        if block.hasClass 'collapsable'
            block.addClass('collapsed')
            $(lines[i]).addClass('hidden') for i in [begin..n]
            $("li.ellipsis", block).removeClass('hidden')
        return
    expand = (block) ->
        block.removeClass 'collapsed'
        $('ol.linenums li', block).removeClass 'hidden'
        $("li.ellipsis", block).addClass('hidden')
        return

    prettyPrint()
    codeblocks = $ '.prettyprint.linenums'
    prepareblock $(block) for block in codeblocks when numlines($(block)) > keep

    codeblocks.click ->
        block = $ this
        if block.hasClass('collapsed') then expand block else collapse keep, block
        return
    return

