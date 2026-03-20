// app/static/js/animations.js
document.addEventListener('DOMContentLoaded', function() {
    if (typeof gsap === 'undefined') return;

    // Check if elements exist before animating
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    const heroActions = document.querySelector('.hero-actions');

    if (heroTitle) {
        gsap.from(heroTitle, {
            duration: 0.8,
            y: 30,
            opacity: 0,
            ease: 'power2.out'
        });
    }

    if (heroSubtitle) {
        gsap.from(heroSubtitle, {
            duration: 0.8,
            y: 20,
            opacity: 0,
            delay: 0.2,
            ease: 'power2.out'
        });
    }

    if (heroActions) {
        gsap.from(heroActions, {
            duration: 0.6,
            y: 10,
            opacity: 0,
            delay: 0.4,
            ease: 'power2.out'
        });
    }

    // Scroll animations
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        const cards = document.querySelectorAll('.product-card');
        cards.forEach((card, i) => {
            gsap.from(card, {
                scrollTrigger: {
                    trigger: card,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                duration: 0.6,
                y: 30,
                opacity: 0,
                delay: i * 0.05,
                ease: 'power2.out'
            });
        });

        const features = document.querySelectorAll('.feature-card');
        features.forEach((feature, i) => {
            gsap.from(feature, {
                scrollTrigger: {
                    trigger: feature,
                    start: 'top 85%',
                    toggleActions: 'play none none none'
                },
                duration: 0.6,
                y: 20,
                opacity: 0,
                delay: i * 0.1,
                ease: 'back.out(1.2)'
            });
        });
    }
});