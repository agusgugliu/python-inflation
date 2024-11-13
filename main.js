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

    function updateImage(index) {
        kpiImage.src = images[index].src;
        kpiImage.alt = images[index].alt;
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