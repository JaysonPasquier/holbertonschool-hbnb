document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('token') || getCookie('token');
    if (!token) {
        window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.href);
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const placeId = urlParams.get('place_id');

    if (!placeId) {
        showError('No place specified');
        return;
    }

    document.getElementById('cancel-button').href = `/place.html?id=${placeId}`;

    fetchPlaceDetails(placeId);

    checkAuthentication();

    document.getElementById('review-form').addEventListener('submit', function(e) {
        e.preventDefault();
        submitReview(placeId);
    });
});

function fetchPlaceDetails(placeId) {
    fetch(`/api/v1/places/${placeId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch place details');
            }
            return response.json();
        })
        .then(place => {
            document.getElementById('place-title').textContent = place.title;
            document.getElementById('place-loading').style.display = 'none';
            document.title = `Review: ${place.title}`;
        })
        .catch(error => {
            showError(`Error loading place details: ${error.message}`);
        });
}

function submitReview(placeId) {
    const text = document.getElementById('review-text').value.trim();
    const rating = parseInt(document.getElementById('review-rating').value);

    if (!text) {
        showError('Please provide a review text');
        return;
    }

    if (isNaN(rating) || rating < 1 || rating > 5) {
        showError('Please select a rating between 1 and 5');
        return;
    }

    // Get user ID from localStorage
    const userId = localStorage.getItem('user_id');

    if (!userId) {
        showError('Unable to identify user. Please log in again.');
        setTimeout(() => {
            window.location.href = `/login.html?redirect=add_review.html?place_id=${placeId}`;
        }, 2000);
        return;
    }

    const token = localStorage.getItem('token') || getCookie('token');

    if (!token) {
        showError('Authentication token not found. Please log in again.');
        setTimeout(() => {
            window.location.href = `/login.html?redirect=add_review.html?place_id=${placeId}`;
        }, 2000);
        return;
    }

    const reviewData = {
        text: text,
        rating: rating,
        place_id: placeId,
        user_id: userId
    };

    console.log("Submitting review:", reviewData);

    fetch('/api/v1/reviews/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token.startsWith('Bearer ') ? token : `Bearer ${token}`
        },
        body: JSON.stringify(reviewData)
    })
    .then(response => {
        if (!response.ok) {
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('text/html')) {
                return response.text().then(html => {
                    console.error('Received HTML instead of JSON:', html.substring(0, 200) + '...');
                    throw new Error(`Server error ${response.status}: Not a valid JSON response`);
                });
            }

            return response.text().then(text => {
                try {
                    const data = JSON.parse(text);
                    throw new Error(data.error || `Server error: ${response.status}`);
                } catch (e) {
                    console.error('Server response:', text.substring(0, 200) + '...');
                    throw new Error(`Server error ${response.status}: ${e.message}`);
                }
            });
        }
        return response.json();
    })
    .then(data => {
        window.location.href = `/place.html?id=${placeId}`;
    })
    .catch(error => {
        console.error('Error submitting review:', error);
        showError(`Error submitting review: ${error.message}. Check console for details.`);
    });
}

function showError(message) {
    const errorElement = document.getElementById('error');
    document.getElementById('place-loading').style.display = 'none';
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}


function checkAuthentication() {
    const token = localStorage.getItem('token') || getCookie('token');
    const loginLink = document.getElementById('login-link');

    if (token) {
        loginLink.textContent = 'My Account';
    } else {
        loginLink.textContent = 'Login';
        loginLink.style.display = 'block';
    }
}