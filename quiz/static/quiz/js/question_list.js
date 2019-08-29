"use strict;"

function redrawTable() {
    $('#table').DataTable()
       .rows().invalidate('data')
       .draw(false);
}

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        dom: 'frtip',
        responsive: true,
        stateSave: true,
        stateDuration: -1,
        pageLength: 25,
        bLengthChange: false,
        initComplete: function(settings, json) {
            document.getElementById('loading-container').classList.remove('opacity-zero');
        },
        fnDrawCallback: function( oSettings ) {
            //hide pagination if there is just one page
            var pagination = $(this).closest('.dataTables_wrapper').find('.dataTables_paginate');
            pagination.toggle(this.api().page.info().pages > 1);
            // add classes to search and length elements to left align on mobile
            $(this).closest('.dataTables_wrapper').find('.dataTables_filter').addClass('text-left');
            //$(this).closest('.dataTables_wrapper').find('.dataTables_length').addClass('text-left text-md-left');
            /*
            // hide filter
            var filter = $(this).closest('.dataTables_wrapper').find('.dataTables_filter');
            filter.toggle(this.api().page.info().pages > 1);
            // hide nr entries
            var length = $(this).closest('.dataTables_wrapper').find('.dataTables_length');
            length.toggle(this.api().page.info().pages > 1);
            */
        },
        columnDefs: [
        {   targets: 1,
            render: function ( data, type, row, meta ) {
                if (document.getElementById('check-full-question').checked) {
                    return data;
                } else {
                    return data.substring(0,15) + '...';
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