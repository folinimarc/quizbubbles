"use strict";

function removeMessage(event) {
    const el = event.target;
    if (el.classList.contains('message')) {
        el.parentNode.removeChild(el);
    }
}

// kick off
document.getElementById('message-box').addEventListener('click', removeMessage);
//remove messages after n seconds
setTimeout(function() {
    Array.from(document.querySelectorAll('.message')).forEach(function(el) {
        el.classList.add('opacity-zero');
        setTimeout(function() {
            el.parentElement.removeChild(el);
        }, 1000)
    });
}, 4000);