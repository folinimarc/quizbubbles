"use strict;"

function redrawTable() {
    $('#question-datatable').DataTable()
       .rows().invalidate('data')
       .draw(false);
}

$(document).ready(function() {

    // init datatable
    $('#question-datatable').DataTable( {
        stateSave: true,
        stateDuration: -1,
        "fnDrawCallback": function( oSettings ) {
            // hide spinner when table is completely loaded
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

    // redraw table when checkbox is clicked
    document.getElementById('check-full-question').addEventListener('click', redrawTable);

    // init additional session storage
    if (typeof(Storage) !== undefined) {
        sessionStorage = window.sessionStorage;
        const checkbox = document.getElementById('check-full-question');
        // set checkbox state to saved value if available
        const checkState = sessionStorage.getItem('statusFullQuestionCheckbox');
        if (checkState !== undefined) {
            checkbox.checked = (checkState == 'true'); //sessionstorage content is always a string. Convert true or false string to boolean.
            redrawTable();
        }
        // listen to changes on checkbox and update sessionStorage
        checkbox.addEventListener('change', function() {
            sessionStorage.setItem('statusFullQuestionCheckbox', checkbox.checked);
        });
      }
});