"use strict;"

$(document).ready(function() {
    $('#question-datatable').DataTable( {
        stateSave: true,
        "fnDrawCallback": function( oSettings ) {
            document.getElementById('main-container').classList.remove('opacity-zero');
        },
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