"use strict";

// start games functions
function start_sprint() {
    const player = document.querySelector('input[name=player-sprint]').value;
    const gametype = 0;
    ajax_submit({'action': 'startSprint', 'player': player, 'gametype': gametype}, 'error-message-sprint');
}

function start_marathon() {
    const player = document.querySelector('input[name=player-marathon]').value;
    const gametype = 1;
    ajax_submit({'action': 'startMarathon', 'player': player, 'gametype': gametype}, 'error-message-marathon');
}

// give focus to inputs upon hovering
Array.from(document.querySelectorAll('.flip-card')).forEach(function(el) {
    el.addEventListener('mouseover', function(event) {
        const input = document.querySelector('.flip-card:hover input');
        if (input) {
            input.focus();
        }
    });
});

// trigger start from buttons and from enter keydown in name input
var sprintBtn = document.getElementById('btn-start-sprint');
if (sprintBtn) {
    sprintBtn.addEventListener('click', start_sprint);
    document.querySelector('input[name=player-sprint]').addEventListener('keydown', function(event) {
        if (event.keyCode == 13) {
            start_sprint();
        }
    });
}

var marathonBtn = document.getElementById('btn-start-marathon');
if (marathonBtn) {
    marathonBtn.addEventListener('click', start_marathon);
    document.querySelector('input[name=player-marathon]').addEventListener('keydown', function(event) {
        if (event.keyCode == 13) {
            start_marathon();
        }
    });
}
