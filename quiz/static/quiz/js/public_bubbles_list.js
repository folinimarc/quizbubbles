"use strict;"

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        responsive: true,
        stateSave: true,
        stateDuration: -1,
        "fnDrawCallback": function( oSettings ) {
            document.getElementById('loading-container').classList.remove('opacity-zero');            
        },
    });
});