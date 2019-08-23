"use strict";

// start quizes functions
function redirectOnSuccess(response) {
    window.location.replace(response.successRedirectUrl);
}

function errorSprint(response) {
    onErrorDisplayMessage(response, 'error-message-sprint');
}

function errorMarathon(response) {
    onErrorDisplayMessage(response, 'error-message-marathon');
}

function onErrorDisplayMessage(response, errorElId) {
    let errorEl = document.getElementById(errorElId);
    errorEl.textContent = response.message;
    errorEl.classList.remove('opacity-zero');
    setTimeout(function() {
        errorEl.classList.add('opacity-zero');
    }, 2000);
}

function start_sprint() {
    const username = document.querySelector('input[name=username-sprint]').value;
    const quiztype = 0;
    ajax_submit({'action': 'startSprint', 'username': username, 'quiztype': quiztype}, redirectOnSuccess, errorSprint);
}

function start_marathon() {
    const username = document.querySelector('input[name=username-marathon]').value;
    const quiztype = 1;
    ajax_submit({'action': 'startMarathon', 'username': username, 'quiztype': quiztype}, redirectOnSuccess, errorMarathon);
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
    document.querySelector('input[name=username-sprint]').addEventListener('keydown', function(event) {
        if (event.keyCode == 13) {
            start_sprint();
        }
    });
}

var marathonBtn = document.getElementById('btn-start-marathon');
if (marathonBtn) {
    marathonBtn.addEventListener('click', start_marathon);
    document.querySelector('input[name=username-marathon]').addEventListener('keydown', function(event) {
        if (event.keyCode == 13) {
            start_marathon();
        }
    });
}