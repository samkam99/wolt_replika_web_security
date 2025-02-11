// Show the password confirmation modal
function showPasswordModal() {
    const modal = document.getElementById("password-modal");
    modal.style.display = "flex";
}

// Close the password confirmation modal
function closePasswordModal() {
    const modal = document.getElementById("password-modal");
    modal.style.display = "none";
}

// Handle password confirmation form submission for delete
document.getElementById("password-confirmation-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form submission

    const password = document.getElementById("confirm-password").value;

    if (!password) {
        alert("Password is required to delete the profile.");
        return;
    }

    try {
        const response = await fetch(`/users/${userPk}`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ password }),
        });

        if (response.ok) {
            alert("Profile deleted successfully!");
            window.location.href = "/signup"; // Redirect after successful deletion
        } else {
            const message = await response.text();
            alert(`Error: ${message}`);
        }
    } catch (error) {
        alert("An error occurred: " + error.message);
    } finally {
        closePasswordModal(); // Close the modal
    }
});

// Toggle between profile view and edit form
function toggleEditForm(show) {
    const editSection = document.getElementById("profile-edit-section");
    const viewSection = document.getElementById("profile-view-section");

    if (show) {
        editSection.style.display = "block"; // Show the edit form
        viewSection.style.display = "none"; // Hide the profile view
    } else {
        editSection.style.display = "none"; // Hide the edit form
        viewSection.style.display = "block"; // Show the profile view
    }
}

// Handle save form submission for updating profile
document.querySelector("#profile-edit-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const userName = document.getElementById("user_name").value;
    const userLastName = document.getElementById("user_last_name").value;
    const userEmail = document.getElementById("user_email").value;

    if (!userName || !userLastName || !userEmail) {
        alert("All fields are required.");
        return;
    }

    try {
        const response = await fetch("/update-profile", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                user_name: userName,
                user_last_name: userLastName,
                user_email: userEmail,
            }),
        });

        if (response.ok) {
            alert("Profile updated successfully!");
            toggleEditForm(false); // Switch back to profile view
            window.location.reload(); // Reload the page to reflect changes
        } else {
            const error = await response.text();
            alert(`Error: ${error}`);
        }
    } catch (error) {
        alert("An error occurred: " + error.message);
    }
});
