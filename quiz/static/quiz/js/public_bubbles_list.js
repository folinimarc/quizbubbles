"use strict;"

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        responsive: true,
        stateSave: true,
        stateDuration: -1,
        "fnDrawCallback": function( oSettings ) {
            document.getElementById('table-container').classList.remove('opacity-zero');            
        },
    });
});