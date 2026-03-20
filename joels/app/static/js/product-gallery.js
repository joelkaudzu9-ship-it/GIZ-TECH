// app/static/js/product-gallery.js

class ProductGallery {
    constructor() {
        this.initGallery();
        this.initLightbox();
    }

    initGallery() {
        const mainImage = document.getElementById('mainImage');
        const thumbnails = document.querySelectorAll('.thumbnail');

        if (!mainImage || !thumbnails.length) return;

        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', () => {
                const imgSrc = thumb.querySelector('img').src;
                mainImage.src = imgSrc;

                // Update active state
                thumbnails.forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
            });
        });
    }

    initLightbox() {
        const lightbox = document.getElementById('lightbox');
        const lightboxImg = document.getElementById('lightboxImage');
        const mainImage = document.getElementById('mainImage');
        const closeBtn = document.querySelector('.lightbox-close');

        if (!lightbox || !mainImage) return;

        // Open lightbox on main image click
        mainImage.addEventListener('click', () => {
            lightboxImg.src = mainImage.src;
            lightbox.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        });

        // Close lightbox
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeLightbox());
        }

        // Click overlay to close
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                this.closeLightbox();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('hidden')) {
                if (e.key === 'Escape') {
                    this.closeLightbox();
                } else if (e.key === 'ArrowLeft') {
                    this.navigateGallery(-1);
                } else if (e.key === 'ArrowRight') {
                    this.navigateGallery(1);
                }
            }
        });
    }

    closeLightbox() {
        const lightbox = document.getElementById('lightbox');
        lightbox.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }

    navigateGallery(direction) {
        const thumbnails = document.querySelectorAll('.thumbnail');
        const currentActive = document.querySelector('.thumbnail.active');
        let currentIndex = Array.from(thumbnails).indexOf(currentActive);
        let newIndex = currentIndex + direction;

        if (newIndex < 0) newIndex = thumbnails.length - 1;
        if (newIndex >= thumbnails.length) newIndex = 0;

        thumbnails[newIndex].click();

        // Update lightbox image
        const lightboxImg = document.getElementById('lightboxImage');
        lightboxImg.src = thumbnails[newIndex].querySelector('img').src;
    }
}

// Initialize gallery
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.product-gallery')) {
        window.gallery = new ProductGallery();
    }
});