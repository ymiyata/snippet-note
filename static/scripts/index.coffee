$ ->
    prettyPrint()
    $('#activationForm').ajaxForm {
        type: "POST"
        beforeSubmit: (array, $form, options) ->
            $('#submitButton').button 'loading'
            return
        success: (responseText, statusText, xhr, $form) ->
            window.location.href = '/'
            return
        error: (xhr, statusText, errorThrown) ->
            $('#submitButton').button 'reset'
            $('#message').html xhr.responseText
            $('#message').removeClass('hidden')
            return
    }
    return
