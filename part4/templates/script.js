/*
  This is a SAMPLE FILE to get you started.
  Please, follow the project instructions to complete the tasks.
*/

document.addEventListener('DOMContentLoaded', function() {
    // Check authentication first
    checkAuthentication();

    // Setup price filter with specific options
    setupPriceFilter();

    // Fetch places (will happen regardless of auth status)
    fetchPlaces();
});

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

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function fetchPlaces() {
    // Get auth token if available
    const token = localStorage.getItem('token') || getCookie('token');

    const headers = {
        'Content-Type': 'application/json'
    };

    // Add authorization header if user is logged in
    if (token) {
        headers['Authorization'] = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
    }

    fetch('/api/v1/places', { headers })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const places = Array.isArray(data) ? data : data.places || [];
            displayPlaces(places);
            populatePriceFilter(places);
        })
        .catch(error => {
            console.error('Error fetching places:', error);
            document.getElementById('places-list').innerHTML =
                '<p class="error">Failed to load places. Please try again later.</p>';
        });
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    placesList.innerHTML = '';

    if (places.length === 0) {
        placesList.innerHTML = '<p>No places found matching your criteria.</p>';
        return;
    }

    places.forEach(place => {
        const placeCard = document.createElement('div');
        placeCard.className = 'place-card';
        placeCard.innerHTML = `
            <h2>${place.title}</h2>
            <p>Price per night: $${place.price}</p>
            <button class="details-button" data-id="${place.id}">View Details</button>
        `;
        placesList.appendChild(placeCard);
    });

    document.querySelectorAll('.details-button').forEach(button => {
        button.addEventListener('click', function() {
            const placeId = this.getAttribute('data-id');
            window.location.href = `/place.html?id=${placeId}`;
        });
    });
}

function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');

    priceFilter.innerHTML = '';

    const options = [
        { value: 'all', text: 'All Prices' },
        { value: '10', text: '$10' },
        { value: '50', text: '$50' },
        { value: '100', text: '$100' }
    ];

    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option.value;
        optionElement.textContent = option.text;
        priceFilter.appendChild(optionElement);
    });

}

function populatePriceFilter(places) {
    const priceFilter = document.getElementById('price-filter');

    priceFilter.addEventListener('change', function() {
        if (this.value === 'all') {
            displayPlaces(places);
        } else {
            const maxPrice = parseInt(this.value, 10);
            const filteredPlaces = places.filter(place => place.price <= maxPrice);
            displayPlaces(filteredPlaces);
        }
    });
}

function filterPlacesByPrice(places, maxPrice) {
    if (maxPrice === 'all') {
        displayPlaces(places);
    } else {
        const filteredPlaces = places.filter(place => place.price <= maxPrice);
        displayPlaces(filteredPlaces);
    }
}
