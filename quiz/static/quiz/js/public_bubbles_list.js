"use strict;"

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        dom: 'frtip',
        responsive: true,
        stateSave: true,
        stateDuration: -1,
        pageLength: 25,
        bLengthChange: false,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search..."
        },
        initComplete: function(settings, json) {
            document.getElementById('loading-container').classList.remove('opacity-zero');
        },
        fnDrawCallback: function( oSettings ) {
            // hide pagination if there is just one page
            var pagination = $(this).closest('.dataTables_wrapper').find('.dataTables_paginate');
            pagination.toggle(this.api().page.info().pages > 1);
            // add classes to search and length elements to left align on mobile
            $(this).closest('.dataTables_wrapper').find('.dataTables_filter').addClass('text-center text-sm-left');
            //$(this).closest('.dataTables_wrapper').find('.dataTables_length').addClass('text-left text-md-left');
            /*
            // hide filter
            var filter = $(this).closest('.dataTables_wrapper').find('.dataTables_filter');
            filter.toggle(this.api().page.info().pages > 1);
            // hide nr entries
            var filter = $(this).closest('.dataTables_wrapper').find('.dataTables_length');
            filter.toggle(this.api().page.info().pages > 1);
            */
        }
    });
});