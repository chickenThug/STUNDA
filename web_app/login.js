document.addEventListener('DOMContentLoaded', function() {

    // Function that compares user entered credentials to those saved on server for login
    document.getElementById('login-form').addEventListener('submit', async function(event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const isValid = await checkLogin(username, password);
            // if valid credentials --> set session storage and locate user to verification page
            if (isValid) {
                sessionStorage.setItem('loggedIn', 'true');
                sessionStorage.setItem('username', username);
                window.location.href = "verify.html";
            } else {
                document.getElementById('error-message').textContent = "Invalid username or password";
            }
        } catch (error) {
            document.getElementById('error-message').textContent = "An error occurred during login. Please try again.";
            console.error('Login request error:', error);
        }
    });

    /* Function that checks entered credentials to those saved on the server. 
    Returns boolean value true if credentials were correct, else false. */
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
