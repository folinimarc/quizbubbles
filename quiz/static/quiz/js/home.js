"use strict";

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