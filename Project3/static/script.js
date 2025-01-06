let cryptoChart;

// Fetch all cryptocurrencies for dropdown
const fetchCryptoList = async () => {
    try {
        const response = await fetch('https://api.coingecko.com/api/v3/coins/list');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        populateDropdown(data);
    } catch (error) {
        console.error('Error fetching cryptocurrency list:', error);
        alert(`Error fetching cryptocurrency list: ${error.message}`);
    }
};

// Populate dropdown with cryptocurrencies
const populateDropdown = (cryptoList) => {
    const dropdown = document.getElementById('crypto-select');
    cryptoList.forEach((crypto) => {
        const option = document.createElement('option');
        option.value = crypto.id;
        option.textContent = crypto.name;
        dropdown.appendChild(option);
    });
};

// Fetch historical data and train model dynamically
document.getElementById('crypto-select').addEventListener('change', async (event) => {
    const selectedCrypto = event.target.value;

    if (!selectedCrypto) return;

    try {
        // Train model for the selected cryptocurrency
        const response = await fetch('http://127.0.0.1:5000/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cryptocurrency: selectedCrypto }),
        });

        const data = await response.json();

        if (response.ok) {
            alert(`Model trained for ${selectedCrypto}.`);
            fetchCryptoHistory(selectedCrypto); // Update the chart with historical data
            fetchPrediction(selectedCrypto);   // Fetch predicted value
        } else {
            console.error('Error training model:', data.error);
            alert(`Error training model: ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to train model.');
    }
});

// Fetch historical data for the chart
const fetchCryptoHistory = async (crypto) => {
    try {
        const response = await fetch(`https://api.coingecko.com/api/v3/coins/${crypto}/market_chart?vs_currency=usd&days=7`);
        if (!response.ok) throw new Error('Failed to fetch historical data');
        const data = await response.json();

        if (data && data.prices) {
            const prices = data.prices.map(([timestamp, price]) => ({ time: new Date(timestamp).toLocaleDateString(), price }));
            updateChart(prices);
        } else {
            console.error(`No historical data found for ${crypto}`);
            alert(`Error: No historical data found for ${crypto}`);
        }
    } catch (error) {
        console.error(error);
        alert('Error fetching historical data.');
    }
};

// Fetch predicted value
const fetchPrediction = async (crypto) => {
    try {
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cryptocurrency: crypto, days_since: 8 }), // Predict for the next day
        });

        const data = await response.json();

        if (response.ok) {
            const predictionContainer = document.getElementById('prediction-container');
            predictionContainer.textContent = `Predicted price for ${crypto} (next day): $${data.predicted_price.toFixed(2)}`;
        } else {
            console.error('Error fetching prediction:', data.error);
            alert(`Error fetching prediction: ${data.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to fetch prediction.');
    }
};

// Initialize or update the chart
const updateChart = (prices) => {
    const ctx = document.getElementById('crypto-chart').getContext('2d');

    const labels = prices.map((entry) => entry.time);
    const data = prices.map((entry) => entry.price);

    if (cryptoChart) {
        cryptoChart.data.labels = labels;
        cryptoChart.data.datasets[0].data = data;
        cryptoChart.update();
    } else {
        cryptoChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Price (USD)',
                    data,
                    borderColor: 'blue',
                    tension: 0.2,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                },
            },
        });
    }
};

// Fetch data on load
fetchCryptoList();
