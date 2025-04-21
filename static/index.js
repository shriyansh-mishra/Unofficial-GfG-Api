document.addEventListener('DOMContentLoaded', function () {
    const profileForm = document.getElementById('profile-form');
    const resultContainer = document.getElementById('result-container');
    const resultJson = document.getElementById('result-json');
    const endpointSelect = document.getElementById('endpoint-select');
    const loadingSpinner = document.getElementById('loading-spinner');

    profileForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        if (!username) {
            alert('Please enter a username');
            return;
        }

        const endpoint = endpointSelect.value;

        loadingSpinner.style.display = 'block';
        resultContainer.style.display = 'none';

        try {
            const response = await fetch(`/api/${endpoint}?username=${encodeURIComponent(username)}`);
            const data = await response.json();

            resultJson.textContent = JSON.stringify(data, null, 2);
            resultContainer.style.display = 'block';
        } catch (error) {
            resultJson.textContent = JSON.stringify({ error: 'Failed to fetch data. Please try again.' }, null, 2);
            resultContainer.style.display = 'block';
            console.error('Error:', error);
        } finally {
            loadingSpinner.style.display = 'none';
        }
    });
});