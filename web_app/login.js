document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('login-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const isValid = await checkLogin(username, password);
            if (isValid) {
                // Set session storage to ensure user logged in
                sessionStorage.setItem('loggedIn', 'true');
                window.location.href = "verify.html";
            } else {
                document.getElementById('error-message').textContent = "Invalid username or password";
            }
        } catch (error) {
            document.getElementById('error-message').textContent = "An error occurred during login. Please try again.";
            console.error('Login request error:', error);
        }
    });

    async function checkLogin(username, password) {
        const response = await fetch('/stunda/check-login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: username,
                password: password,
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        return result.valid;
    }
});
