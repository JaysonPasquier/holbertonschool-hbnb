document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const placeId = urlParams.get('id');

    if (!placeId) {
        showError('No place ID specified');
        return;
    }

    fetchPlaceDetails(placeId);

    fetchPlaceReviews(placeId);

    checkLoginStatus();
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
            displayPlaceDetails(place);
        })
        .catch(error => {
            showError(`Error loading place details: ${error.message}`);
        });
}

function fetchPlaceReviews(placeId) {
    fetch(`/api/v1/reviews/places/${placeId}/reviews`)
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    return { reviews: [] };
                }
                throw new Error('Failed to fetch reviews');
            }
            return response.json();
        })
        .then(data => {
            const reviews = Array.isArray(data) ? data : (data.reviews || []);
            displayReviews(reviews);
        })
        .catch(error => {
            console.error('Error fetching reviews:', error);
            document.getElementById('reviews-container').innerHTML =
                '<p>Unable to load reviews at this time.</p>';
        });
}

function displayPlaceDetails(place) {
    document.getElementById('place-loading').style.display = 'none';

    const placeInfoSection = document.querySelector('.place-info');
    placeInfoSection.style.display = 'block';

    document.getElementById('place-title').textContent = place.title;
    document.getElementById('place-price').textContent = place.price;
    document.getElementById('place-description').textContent = place.description;

    fetchHostInfo(place.owner_id);

    if (place.amenities && place.amenities.length > 0) {
        fetchAmenities(place.amenities);
    } else {
        document.getElementById('amenities-list').textContent = 'None';
    }

    document.title = `${place.title} - HBnB`;
}

function fetchAmenities(amenityIds) {
    const promises = amenityIds.map(id =>
        fetch(`/api/v1/amenities/${id}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch amenity');
                return response.json();
            })
    );

    Promise.all(promises)
        .then(amenities => {
            const amenityNames = amenities.map(amenity => amenity.name);
            document.getElementById('amenities-list').textContent = amenityNames.join(', ');
        })
        .catch(error => {
            console.error('Error fetching amenities:', error);
            document.getElementById('amenities-list').textContent = 'Unable to load amenities';
        });
}

function fetchHostInfo(ownerId) {
    fetch(`/api/v1/users/${ownerId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch host info');
            }
            return response.json();
        })
        .then(user => {
            document.getElementById('host-name').textContent = `${user.first_name} ${user.last_name}`;
        })
        .catch(error => {
            console.error('Error fetching host info:', error);
            document.getElementById('host-name').textContent = 'Unknown';
        });
}

function displayReviews(reviews) {
    const reviewsContainer = document.getElementById('reviews-container');

    if (!reviews || reviews.length === 0) {
        reviewsContainer.innerHTML = '<p>No reviews yet. Be the first to leave a review!</p>';
        return;
    }

    reviewsContainer.innerHTML = '';

    reviews.forEach(review => {
        const reviewCard = document.createElement('div');
        reviewCard.className = 'review-card';

        const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);

        fetchUserForReview(review, reviewCard, stars);
    });
}

function fetchUserForReview(review, reviewCard, stars) {
    if (review.user && (review.user.first_name || review.user.last_name)) {
        displayReviewWithUser(reviewCard, review,
            `${review.user.first_name} ${review.user.last_name}`, stars);
    } else if (review.user_id) {
        fetch(`/api/v1/users/${review.user_id}`)
            .then(response => response.ok ? response.json() : {first_name: '', last_name: ''})
            .then(user => {
                const userName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
                displayReviewWithUser(reviewCard, review, userName || 'Anonymous', stars);
            })
            .catch(() => {
                displayReviewWithUser(reviewCard, review, 'Anonymous', stars);
            });
    } else {
        displayReviewWithUser(reviewCard, review, 'Anonymous', stars);
    }
}

function displayReviewWithUser(reviewCard, review, userName, stars) {
    reviewCard.innerHTML = `
        <div class="review-user">${userName}:</div>
        <div class="review-text">${review.text}</div>
        <div class="review-rating">Rating: ${stars}</div>
    `;

    const container = document.getElementById('reviews-container');
    if (!reviewCard.parentNode) {
        container.appendChild(reviewCard);
    }
}

function checkLoginStatus() {
    const token = localStorage.getItem('token') || getCookie('token');

    const addReviewButton = document.getElementById('add-review-button');

    if (token) {
        addReviewButton.addEventListener('click', function() {
            const placeId = new URLSearchParams(window.location.search).get('id');
            window.location.href = `/add_review.html?place_id=${placeId}`;
        });
    } else {
        addReviewButton.textContent = 'Login to Write a Review';
        addReviewButton.addEventListener('click', function() {
            window.location.href = `/login.html?redirect=place.html?id=${new URLSearchParams(window.location.search).get('id')}`;
        });
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function showError(message) {
    const errorElement = document.getElementById('place-error');
    document.getElementById('place-loading').style.display = 'none';
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}
