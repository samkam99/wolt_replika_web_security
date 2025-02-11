document.addEventListener("DOMContentLoaded", function () {
    // Pass restaurants data from Flask to JavaScript
    const restaurantData = JSON.parse(document.getElementById("restaurant-data").textContent);

    // Initialize the map
    const map = L.map('map').setView([55.6845, 12.564148], 12);

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 20,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Function to populate map and list
    function populateRestaurants(restaurants) {
        const listContainer = document.getElementById('restaurant-list-items');

        restaurants.forEach(function (restaurant) {
            // Add marker to the map
            const marker = L.marker(restaurant.coords).addTo(map);
            marker.bindPopup(`<b>${restaurant.name}</b>`);

            // Add restaurant to the list
            const listItem = document.createElement('li');
            listItem.textContent = restaurant.name;
            listItem.addEventListener('click', function () {
                map.setView(restaurant.coords, 15);
                marker.openPopup();
            });
            listContainer.appendChild(listItem);
        });
    }

    // Populate the map and list
    populateRestaurants(restaurantData);

    // Adjust map size on window resize
    window.addEventListener("resize", function () {
        map.invalidateSize();
    });
});
