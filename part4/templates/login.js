document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('error-message');

    const urlParams = new URLSearchParams(window.location.search);
    const redirect = urlParams.get('redirect');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault();

            hideError();

            const email = emailInput.value.trim();
            const password = passwordInput.value;

            if (!email || !password) {
                showError('Please enter both email and password.');
                return;
            }

            await loginUser(email, password);
        });
    }

    async function loginUser(email, password) {
        try {
            const response = await fetch('/api/v1/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Invalid email or password');
            }

            const data = await response.json();

            setAuthToken(data.access_token);
            localStorage.setItem('user_id', data.user_id);

            if (redirect) {
                window.location.href = redirect;
            } else {
                window.location.href = 'index.html';
            }

        } catch (error) {
            showError(error.message);
            console.error('Login error:', error);
        }
    }

    function setAuthToken(token) {
        localStorage.setItem('token', token);

        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + 7);

        document.cookie = `token=${token}; expires=${expiryDate.toUTCString()}; path=/`;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function hideError() {
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
    }
});