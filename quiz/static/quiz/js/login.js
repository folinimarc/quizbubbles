function submit_pw() {
    const password = document.querySelector('input[name=password]').value;
    ajax_submit({'password': password}, 'error-message-login');
}