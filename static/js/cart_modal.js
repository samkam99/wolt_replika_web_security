'use strict';

const cart = document.getElementById("cart");
const openBtn = document.querySelector(".open_cart");
const closeBtn = document.querySelector(".cart_close");

openBtn.onclick = () => (cart.style.display = 'block')
closeBtn.onclick = () => (cart.style.display = 'none')
window.onclick = (event) => {
    if(event.target == cart) cart.style.display = 'none';
}


// ////////////////////////////// ADD TO CART BUTTON ////////////////////////////// //
document.addEventListener('DOMContentLoaded', () => {
    // Get all "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.add_btn');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', () => {
            const itemPk = button.dataset.itemId;
            const itemTitle = button.closest('.card_info').querySelector('h4').innerText;
            const itemPrice = button.closest('.card_add').querySelector('.item_price').innerText;
            const itemImage = document.querySelector('.item_image').getAttribute('src');


            // Prepare data to send to the server
            const data = {
                item_pk: itemPk,
                item_title: itemTitle,
                item_price: itemPrice,
                item_image: itemImage
            };
            console.log(data)

            // Send POST request to the server
            fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message); // Success message
                if (data.cart) {
                    updateCartUI(data.cart); // Dynamically update the cart
                }
            })
            .catch(error => console.error('Error adding item to cart:', error));
            
        });
    });
});

function updateCartUI(cart) {
    const cartItemsContainer = document.querySelector('.cart_item_dropdown .items');
    const orderButton = document.querySelector('button[type="submit"] p:last-child'); // Update selector if needed
    cartItemsContainer.innerHTML = ''; // Clear existing items

    let totalPrice = 0; // Initialize total price

    console.log('Cart Data:', cart); // Log the cart contents

    cart.forEach(item => {
        const itemTotal = parseFloat(item.item_price) * item.quantity; // Calculate item total
        console.log('Item:', item, 'Item Total:', itemTotal); // Debugging
        totalPrice += itemTotal; // Add to total price

        const cartItem = `
            <li class="item">
                <img src="/static/${item.item_image || 'dishes/default_image.png'}" alt="${item.item_image}">
                <div>
                    <p class="item_title">${item.item_title}</p>
                    <p class="item_price">${item.item_price} kr</p>
                </div>
                <p class="amount">${item.quantity}</p>
                <button class="remove_btn" id="remove_btn-${item.item_pk}" data-item-id="${item.item_pk}">&times;</button>
            </li>
        `;
        cartItemsContainer.insertAdjacentHTML('beforeend', cartItem);
    });

    console.log('Final Total Price:', totalPrice); // Debugging

    // Update the total price in the order button
    if (orderButton) {
        orderButton.textContent = `${totalPrice.toFixed(2)} kr`;
    } else {
        console.error('Order button not found!');
    }

    // Re-attach event listeners to new remove buttons
    const newRemoveButtons = document.querySelectorAll('.remove_btn');
    newRemoveButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent page refresh
            const itemPk = event.target.getAttribute('data-item-id');
            console.log('Remove Button Clicked, Item PK:', itemPk); // Debugging
            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'item_pk': itemPk })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Updated Cart Data:', data.cart); // Debugging
                updateCartUI(data.cart);
            })
            .catch(error => console.error('Error removing item:', error));
        });
    });
}



// ////////////////////////////// REMOVE FROM CART BUTTON ////////////////////////////// //

document.addEventListener("DOMContentLoaded", () => {
    const removeButtons = document.querySelectorAll('.remove_btn');

    removeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent page refresh

            const itemPk = event.target.getAttribute('data-item-id'); // Get the item's PK
            console.log(`Removing item with PK: ${itemPk}`);

            // Send a POST request to the server to remove the item
            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'item_pk': itemPk }) // Send the PK to the server
            })
            .then(response => response.json())
            .then(data => {
                if (data.cart) {
                    // Update the cart UI with the new state of the cart
                    updateCartUI(data.cart);
                } else {
                    console.error('Failed to update cart:', data.error || 'Unknown error');
                }
            })
            .catch(error => console.error('Error removing item from cart:', error));
        });
    });
});

// Function to dynamically update the cart UI
function updateCartUI(cart) {
    const cartItemsContainer = document.querySelector('.cart_item_dropdown .items');
    const orderButton = document.querySelector('button[type="submit"] p:last-child'); // Update selector if needed
    cartItemsContainer.innerHTML = ''; // Clear existing items

    let totalPrice = 0; // Initialize total price

    console.log('Cart Data:', cart); // Log the cart contents

    cart.forEach(item => {
        const itemTotal = parseFloat(item.item_price) * item.quantity; // Calculate item total
        console.log('Item:', item, 'Item Total:', itemTotal); // Debugging
        totalPrice += itemTotal; // Add to total price

        const cartItem = `
            <li class="item">
                <img src="/static/${item.item_image}" alt="${item.item_image}">
                <div>
                    <p class="item_title">${item.item_title}</p>
                    <p class="item_price">${item.item_price} kr</p>
                </div>
                <p class="amount">${item.quantity}</p>
                <button class="remove_btn" id="remove_btn-${item.item_pk}" data-item-id="${item.item_pk}">&times;</button>
            </li>
        `;
        cartItemsContainer.insertAdjacentHTML('beforeend', cartItem);
    });

    console.log('Final Total Price:', totalPrice); // Debugging

    // Update the total price in the order button
    if (orderButton) {
        orderButton.textContent = `${totalPrice.toFixed(2)} kr`;
    } else {
        console.error('Order button not found!');
    }

    // Re-attach event listeners to new remove buttons
    const newRemoveButtons = document.querySelectorAll('.remove_btn');
    newRemoveButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent page refresh
            const itemPk = event.target.getAttribute('data-item-id');
            console.log('Remove Button Clicked, Item PK:', itemPk); // Debugging
            fetch('/remove_from_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 'item_pk': itemPk })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Updated Cart Data:', data.cart); // Debugging
                updateCartUI(data.cart);
            })
            .catch(error => console.error('Error removing item:', error));
        });
    });
}


