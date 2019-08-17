function start_sprint() {
    const player = document.querySelector('input[name=player]').value;
    const gametype = 0;
    ajax_submit({'player': player, 'gametype': gametype}, 'error-message-sprint');
}

function ajax_submit(dataObj, errorElId) {
    var request = new XMLHttpRequest();
    const csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
    request.open("POST", '', true);
    request.setRequestHeader("Content-Type", "application/json");
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.onreadystatechange = function () {
        if (request.readyState === 4 && request.status === 200) {
            var response = JSON.parse(request.response);
            if (response.status === 'OK') {
                window.location.replace(response.successRedirectUrl);
            } else {
                let errorEl = document.getElementById(errorElId);
                errorEl.textContent = response.message;
                errorEl.style.opacity = 1;
                setTimeout(function() {
                    errorEl.style.opacity = 0;
                }, 2000);
            }
        }
    };
    const data = JSON.stringify(dataObj);
    request.send(data);
}