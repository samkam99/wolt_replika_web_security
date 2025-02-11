'use strict';

// ////////// CREATE ITEM MODAL ////////// //

const modal = document.getElementById("myModal");
const openBtn = document.getElementById("openBtn");
const closeBtn = document.querySelector(".close");

openBtn.onclick = () => (modal.style.display = 'block');
closeBtn.onclick = () => (modal.style.display = 'none');
window.onclick = (event) => {
    if (event.target == modal) modal.style.display = 'none';
}

// ////////// UPDATE ITEM MODAL ////////// //
// Handle "Edit" button click to open the modal with the item's current data
document.querySelectorAll(".open-edit-btn").forEach(button => {
    button.addEventListener("click", function() {
        // Get the ID of the item being edited
        const itemId = this.getAttribute("data-item-id");
        console.log("Clicked item ID:", itemId);

        // Find the matching item by item_pk (assumes `items` is available in scope)
        const itemData = items.find(item => {
            console.log(`Checking item_pk ${item.item_pk} against itemId ${itemId}`);
            return item.item_pk === itemId;
        });

        console.log("itemData:", itemData); // Log the found item for debugging

        if (itemData) {
            // Populate modal fields with the item's current data
            document.getElementById("modal_item_pk").value = itemData.item_pk;
            document.getElementById("modal_item_title").value = itemData.item_title;
            document.getElementById("modal_item_description").value = itemData.item_description;
            document.getElementById("modal_item_price").value = itemData.item_price;

            // Open the modal
            document.getElementById("myEditModal").style.display = "block";
        } else {
            console.error("Item data not found for ID:", itemId);
        }
    });
});

// Add event listener to close the modal
document.querySelector(".closeEditBtn").addEventListener("click", function() {
    document.getElementById("myEditModal").style.display = "none";
});

// Handle form submission for updating an item
document.getElementById("updated_modal_content").addEventListener("submit", async function(e) {
    // e.preventDefault(); // Prevent default form submission

    const formData = new FormData(this); // Get form data

    try {
        // Send PUT request to backend
        const response = await fetch('/update/items', {
            method: 'PUT',
            body: formData
        });
        console.log("Sending PUT request to backend...");
        
        console.log("Raw Response:", response);
        if (!response.ok) {
            const error = await response.text();
            console.error("Update failed:", error);
            alert(`Error: ${error}`);
            return;
        }
        
        const result = await response.json();
        console.log("Update result:", result); // Log the response to check if it's the expected format
        
        // Check if a new image is provided in the response
        if (result.newImageName) {
            const itemId = formData.get("item_pk"); // Get the item ID from the form
            console.log("New image name:", result.newImageName);
            console.log("Updating image for item:", itemId);
            
            // Find the image element for the specific item
            const imageElement = document.getElementById(`image-${itemId}`);
            console.log("Found image element:", imageElement);

            // Check if image element exists
            if (imageElement) {
                // Update the src to the new image and append a timestamp to prevent caching
                imageElement.src = `/static/images/${result.newImageName}?t=${new Date().getTime()}`;
                console.log(`Image updated for item ${itemId}`);
            } else {
                console.error(`Image element not found for item ID: ${itemId}`);
            }
        }

        // Close the modal
        document.getElementById("myEditModal").style.display = "none";
        alert("Item updated successfully!");
    } catch (error) {
        console.error("Error updating item:", error);
        alert("An error occurred. Please try again.");
    }
});

// ////////// ITEM REMOVE AFTER DELETE ////////// //
document.querySelectorAll("button[title='Delete item']").forEach(button => {
    button.addEventListener("click", async (event) => {
        event.preventDefault(); // Prevent default behavior

        // Get the item PK from the data-item-id attribute of the clicked button
        const itemPk = event.target.getAttribute("data-item-id");
        const itemElement = document.getElementById(`item-${itemPk}`);

        // Debugging: Check if itemPk and itemElement are properly fetched
        console.log(`Item PK: ${itemPk}`);
        console.log(`Target item element:`, itemElement);

        try {
            const deleteUrl = event.target.getAttribute("mix-delete");
            console.log(`Sending DELETE request to: ${deleteUrl}`);

            const response = await fetch(deleteUrl, { method: "DELETE" });

            if (response.ok) {
                console.log(`Response OK: Deleting item with PK ${itemPk}`);

                // If the delete is successful, remove the item from the DOM
                itemElement.remove();
                console.log(`Item with PK ${itemPk} removed from the DOM.`);
            } else {
                console.error("Failed to delete item:", await response.text());
            }
        } catch (error) {
            console.error("Error deleting item:", error);
        }
    });
});








