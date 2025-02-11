document.addEventListener("DOMContentLoaded", () => {
    // Attach click event listeners to block and unblock buttons
    document.querySelectorAll(".block-button, .unblock-button").forEach((button) => {
        button.addEventListener("click", (event) => {
            const pk = button.dataset.pk; // Get the primary key (user_pk or item_pk)
            const action = button.dataset.action; // Get the action (block/unblock)
            const type = button.dataset.type; // Get the type (user or item)

            // Determine the API endpoint based on type and action
            const url = `/${type}s/${action}/${pk}`;

            // Send PUT request using Fetch API
            fetch(url, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
            })
                .then((response) => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error(`Failed to ${action} ${type}`);
                    }
                })
                .then((data) => {
                    console.log(data);
                    // Update the button dynamically based on the new state
                    if (action === "block") {
                        button.textContent = "Unblock";
                        button.dataset.action = "unblock";
                    } else {
                        button.textContent = "Block";
                        button.dataset.action = "block";
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert(`An error occurred while trying to ${action} the ${type}.`);
                });
        });
    });
});

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