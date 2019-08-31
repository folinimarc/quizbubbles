"use strict";

var currentPageIndex = 0;
var maxPageIndex = 7;
var frontVisible = true;
var flipCard = document.querySelector('.flip-card');

Array.from(document.querySelectorAll('.next-button')).forEach(function(el) {
    el.addEventListener('click', nextPage);
});
Array.from(document.querySelectorAll('.previous-button')).forEach(function(el) {
    el.addEventListener('click', previousPage);
});

function nextPage(event) {
    if (currentPageIndex == maxPageIndex) return;
    currentPageIndex += 1;
    flip();
}

function previousPage(event) {
    if (currentPageIndex == 0) return;
    currentPageIndex -= 1;
    flip();
}

function flip() {
    let kls = frontVisible ? '.back' : '.front';
    Array.from(document.querySelectorAll(kls + '>div')).forEach(function(el){
        el.classList.add('d-none');
    });
    document.getElementById('p' + currentPageIndex).classList.remove('d-none');
    flipCard.classList.toggle('flipped');
    frontVisible = !frontVisible;
}