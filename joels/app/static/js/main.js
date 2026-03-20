// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const closeBtn = document.getElementById('mobileMenuClose');
    const overlay = document.getElementById('menuOverlay');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
            document.body.style.overflow = 'hidden';
        });
    }

    function closeMenu() {
        if (menuBtn) menuBtn.classList.remove('active');
        if (mobileMenu) mobileMenu.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    if (overlay) overlay.addEventListener('click', closeMenu);

    document.querySelectorAll('.mobile-nav-link').forEach(link => {
        link.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') closeMenu();
    });
});

// Search
const searchInput = document.getElementById('searchInput');
if (searchInput) {
    searchInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length < 2) return;

        fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                const results = document.getElementById('searchResults');
                if (results) {
                    results.innerHTML = data.results.map(item => `
                        <a href="/product/${item.slug || item.id}" class="search-result-item">
                            <span>${item.title}</span>
                            <small>MWK ${item.price}</small>
                        </a>
                    `).join('');
                    results.classList.remove('hidden');
                }
            });
    });
}

// Toast messages
setTimeout(() => {
    document.querySelectorAll('.toast').forEach(t => t.remove());
}, 3000);