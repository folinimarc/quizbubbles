function removeMessage(event) {
    const el = event.target;
    if (el.classList.contains('message')) {
        el.parentNode.removeChild(el);
    }
}

// kick off
document.getElementById('message-box').addEventListener('click', removeMessage);