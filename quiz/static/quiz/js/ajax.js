"use strict";

function ajax_submit(dataObj, errorElId, url='') {
    var request = new XMLHttpRequest();
    const csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
    request.open("POST", url, true);
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
                errorEl.classList.remove('opacity-zero');
                setTimeout(function() {
                    errorEl.classList.add('opacity-zero');
                }, 2000);
            }
        }
    };
    const data = JSON.stringify(dataObj);
    request.send(data);
}