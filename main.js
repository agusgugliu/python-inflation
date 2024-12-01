document.addEventListener('DOMContentLoaded', () => {
    const images = [
        { src: 'images/employment_graph.png', alt: 'Tasa de Empleo' },
        { src: 'images/inflation_graph.png', alt: 'IPC Histórico' },
        { src: 'images/dollar_graph.png', alt: 'Evolución USD' }
    ];

    let currentIndex = 0;
    const kpiImage = document.getElementById('kpiImage');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const exchangeRateTableContainer = document.getElementById('exchangeRateTableContainer');
    const exchangeRateTableBody = document.getElementById('exchangeRateTable').querySelector('tbody');

    function updateImage(index) {
        kpiImage.src = images[index].src;
        kpiImage.alt = images[index].alt;

        if (images[index].src === 'images/dollar_graph.png') {
            exchangeRateTableContainer.style.display = 'block';
            fetchExchangeRateData();
        } else {
            exchangeRateTableContainer.style.display = 'none';
        }
    }

    async function fetchExchangeRateData() {
        try {
            const response = await fetch('/get_exchange_rate_data');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const exchangeRateData = await response.json();
            console.log('Fetched exchange rate data:', exchangeRateData);

            // Clear existing table data
            exchangeRateTableBody.innerHTML = '';

            // Populate the table with the fetched data
            exchangeRateData.forEach(data => {
                const row = document.createElement('tr');
                const dateCell = document.createElement('td');
                const rateCell = document.createElement('td');

                dateCell.textContent = data.date;
                rateCell.textContent = data.rate;

                row.appendChild(dateCell);
                row.appendChild(rateCell);
                exchangeRateTableBody.appendChild(row);
            });
        } catch (error) {
            console.error('Error fetching exchange rate data:', error);
        }
    }

    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex > 0) ? currentIndex - 1 : images.length - 1;
        updateImage(currentIndex);
    });

    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex < images.length - 1) ? currentIndex + 1 : 0;
        updateImage(currentIndex);
    });

    // Initial image
    updateImage(currentIndex);
});