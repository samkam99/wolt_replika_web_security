'user strict';

document.addEventListener("DOMContentLoaded", () => {
    // Get all category links and sections
    const categoryLinks = document.querySelectorAll(".admin-category a");
    const sections = document.querySelectorAll("main > section:not(#filter)");

    // Function to show only the selected section
    const filterSections = (category) => {
        sections.forEach((section) => {
            if (section.id === category) {
                section.style.display = "block"; // Show matching section
            } else {
                section.style.display = "none"; // Hide other sections
            }
        });
    };

    // Add click event listeners to each category link
    categoryLinks.forEach((link) => {
        link.addEventListener("click", (e) => {
            e.preventDefault(); // Prevent default anchor behavior
            const category = link.getAttribute("data-category");
            filterSections(category); // Filter sections
            console.log(category)
        });
    });

    // Optionally, show the first section by default
    // if (sections.length > 0) {
    //     filterSections(sections[0].id);
    // }
});
