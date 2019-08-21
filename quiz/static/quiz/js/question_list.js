"use strict;"

$(document).ready(function() {
    $('#question-datatable').DataTable( {
        stateSave: true,
        "fnDrawCallback": function( oSettings ) {
            document.getElementById('main-container').classList.remove('opacity-zero');
            document.getElementById('spinner').classList.add('opacity-zero');
            setTimeout(function() {
                document.getElementById('spinner').className = 'd-none';
            }, 1000);
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