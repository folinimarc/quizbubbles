"use strict;"

$(document).ready(function() {
    $('#question-datatable').DataTable( {
        columnDefs: [
        {   targets: 1,
            render: function ( data, type, row, meta ) {
                if (document.getElementById('check-full-question').checked) {
                    return data;
                } else {
                    return data.substring(0,10) + '...';
                }
            }
        }]
    });
});

document.getElementById('check-full-question').addEventListener('click', function() {
    $('#question-datatable').DataTable()
       .rows().invalidate('data')
       .draw(false);
});

/*
$(document).ready(function() {
    var jsVariables = JSON.parse(document.getElementById('js-variables').textContent);
    var apiUrl = jsVariables['apiUrl'];
    console.log(apiUrl);
    $('#question-datatable').DataTable( {
        'ajax': {
            'url': apiUrl,
            'type': 'GET',
            'beforeSend': function (request) {
                //request.setRequestHeader('token', token);
            }
        },
        'columns': [
            { 'data': 'id' },
            { 'data': 'question', render: function (data, type, row) {
                return data.substring(0,10) + '[...]';
            }},
            { 'data': 'difficulty' },
            { 'data': 'contributor' },
            { 'data': 'created' },
        ]
    } );
} );
*/