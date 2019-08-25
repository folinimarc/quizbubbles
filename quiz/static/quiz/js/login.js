"use strict";

$(document).ready(function() {

    var flipcard = document.getElementById('flipcard');
    var front = document.querySelector('.front');
    var back = document.querySelector('.back');
    if (flipcard.classList.contains('flipped')) {
        flipcard.style.height = back.offsetHeight.toString() + 'px';
    } else {
        flipcard.style.height = front.offsetHeight.toString() + 'px';
    }

    Array.from(document.querySelectorAll('.toggle-card')).forEach(function(el) {
        el.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            if (flipcard.classList.contains('flipped')) {
                setTimeout(function(){
                    flipcard.style.height = front.offsetHeight.toString() + 'px';
                }, 500);
                flipcard.classList.remove('flipped');
            } else {
                setTimeout(function() {
                    flipcard.classList.add('flipped');
                }, 500);
                flipcard.style.height = back.offsetHeight.toString() + 'px';
            }
        }, true)
    });
});