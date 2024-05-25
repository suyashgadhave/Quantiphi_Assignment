document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('linkForm');
    const input = document.getElementById('linkInput');
    const output = document.getElementById('output');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const link = input.value;
        if (link) {
            console.log(link);
            alert(`You entered: ${link}`);
            // Call the backend with the link (assuming the backend URL is /scrape)
            fetch('/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: link }),
            })
            .then(response => response.json())
            .then(data => {
                output.innerText = `Scraped Data: ${JSON.stringify(data)}`;
            })
            .catch(error => {
                console.error('Error:', error);
                output.innerText = 'Failed to scrape the website';
            });

            // Clear the textbox
            input.value = '';
        }
    });
});
