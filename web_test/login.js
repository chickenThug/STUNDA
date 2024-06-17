document.addEventListener('DOMContentLoaded', function() {
    // Move these and pick appropriate ones
    const preSelectedUsername = "user";
    const preSelectedPassword = "password";

    document.getElementById('login-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username === preSelectedUsername && password === preSelectedPassword) {
            // Set session storage to ensure user logged in
            sessionStorage.setItem('loggedIn', 'true');
            window.location.href = "verify.html";
        } else {
            document.getElementById('error-message').textContent = "Invalid username or password";
        }
    });
});