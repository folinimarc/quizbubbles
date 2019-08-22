"use strict;"

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        responsive: true,
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
    });
});