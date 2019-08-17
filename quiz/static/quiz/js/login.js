function ajax_submit_pw() {
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
                document.getElementById('error-message').style.opacity = 1;
                setTimeout(function() {
                    document.getElementById('error-message').style.opacity = 0;
                }, 2000);
            }
        }
    };
    const password = document.querySelector('input[name=password]').value;
    const data = JSON.stringify({"password": password});
    request.send(data);
}