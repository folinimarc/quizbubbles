"use strict";

var flipcard = document.getElementById('flipcard');
Array.from(document.querySelectorAll('.toggle-card')).forEach(function(el) {
    el.addEventListener('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        if (flipcard.classList.contains('flipped')) {
            flipcard.classList.remove('flipped');
        } else {
            flipcard.classList.add('flipped');
        }
    }, true)
});