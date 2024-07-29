document.addEventListener("DOMContentLoaded", function() {
    // Select the <div> with id "certificate-link"
    const container = document.getElementById("certificate-link");

    if (container) {
        // Find the <a> tag within the container
        const link = container.querySelector("a");

        if (link) {
            // Get the href attribute of the link
            const href = link.href;

            if (href) {
                // Split the URL to get the file name
                const urlParts = href.split('/');
                const fileName = decodeURIComponent(urlParts[urlParts.length - 1]);

                // Update the text content of the link
                link.textContent = fileName;
            } else {
                console.error('The href attribute is missing or empty.');
            }
        } else {
            console.error('No <a> tag found within the element with id "certificate-link".');
        }
    } else {
        console.error('Element with id "certificate-link" not found.');
    }
});

