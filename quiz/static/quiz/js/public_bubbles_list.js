"use strict;"

$(document).ready(function() {

    // init datatable
    $('#table').DataTable( {
        responsive: true,
        stateSave: true,
        stateDuration: -1,
        initComplete: function(settings, json) {
            document.getElementById('loading-container').classList.remove('opacity-zero'); 
          }
    });
});