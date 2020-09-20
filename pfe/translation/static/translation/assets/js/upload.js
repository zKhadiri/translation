$(document).on('submit', '#frm1', function(e) {
    e.preventDefault();

    $.ajax({
        type: 'POST',
        url: '/start-now/',
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        succes: function() {
            console.log('aa')
            alert('ok');
        }
    })
});