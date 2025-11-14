document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('.carousel-container');
    if (!carousel) return;

    const track = document.querySelector('.carousel-track');
    const slides = Array.from(track.children);
    const nextButton = document.querySelector('.carousel-button.next');
    const prevButton = document.querySelector('.carousel-button.prev');
    const indicatorsNav = document.querySelector('.carousel-indicators');
    const indicators = Array.from(indicatorsNav.children);

    if (slides.length === 0) return;

    let slideWidth = slides[0].getBoundingClientRect().width;
    const slideInterval = 8000; // 8 segundos
    let currentIndex = 0;
    let autoPlayInterval;

    // --- Funções ---

    const moveToSlide = (targetIndex) => {
        track.style.transform = 'translateX(-' + slideWidth * targetIndex + 'px)';
        slides[currentIndex].classList.remove('active');
        slides[targetIndex].classList.add('active');
        currentIndex = targetIndex;
    };

    const updateIndicators = (targetIndex) => {
        const currentIndicator = indicatorsNav.querySelector('.active');
        if (currentIndicator) currentIndicator.classList.remove('active');
        indicators[targetIndex].classList.add('active');
    };

    const navigateTo = (targetIndex) => {
        moveToSlide(targetIndex);
        updateIndicators(targetIndex);
    };

    const showNextSlide = () => {
        const nextIndex = (currentIndex + 1) % slides.length;
        navigateTo(nextIndex);
    };

    // --- Autoplay ---

    const startAutoPlay = () => {
        stopAutoPlay();
        autoPlayInterval = setInterval(showNextSlide, slideInterval);
    };

    const stopAutoPlay = () => {
        clearInterval(autoPlayInterval);
    };

    // --- Event Listeners ---

    if (nextButton) {
        nextButton.addEventListener('click', () => {
            showNextSlide();
        });
    }

    if (prevButton) {
        prevButton.addEventListener('click', () => {
            const prevIndex = (currentIndex - 1 + slides.length) % slides.length;
            navigateTo(prevIndex);
        });
    }

    if (indicatorsNav) {
        indicatorsNav.addEventListener('click', e => {
            const targetIndicator = e.target.closest('button.indicator');
            if (!targetIndicator) return;
            const targetIndex = indicators.findIndex(dot => dot === targetIndicator);
            navigateTo(targetIndex);
        });
    }

    carousel.addEventListener('mouseenter', stopAutoPlay);
    carousel.addEventListener('mouseleave', startAutoPlay);
    carousel.addEventListener('click', (e) => {
        if (e.target.matches('.carousel-button, .indicator')) {
            stopAutoPlay();
            startAutoPlay();
        }
    });

    window.addEventListener('resize', () => {
        slideWidth = slides[0].getBoundingClientRect().width;
        moveToSlide(currentIndex);
    });

    // --- Inicialização ---
    if (slides.length > 1) {
        startAutoPlay();
    }
});
