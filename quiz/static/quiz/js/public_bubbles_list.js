"use strict;"

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        responsive: true,
        stateSave: true,
        stateDuration: -1,
        initComplete: function(settings, json) {
            document.getElementById('loading-container').classList.remove('opacity-zero'); 
        },
        "fnDrawCallback": function( oSettings ) {
            //hide pagination if there is just one page
            var pagination = $(this).closest('.dataTables_wrapper').find('.dataTables_paginate');
            pagination.toggle(this.api().page.info().pages > 0);
        }
    });
});