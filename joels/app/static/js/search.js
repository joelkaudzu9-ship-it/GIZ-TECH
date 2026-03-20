// app/static/js/search.js

class SearchManager {
    constructor() {
        this.searchInput = document.getElementById('searchInput');
        this.searchResults = document.getElementById('searchResults');
        this.searchTimeout = null;
        this.minChars = 2;

        if (this.searchInput) {
            this.init();
        }
    }

    init() {
        this.searchInput.addEventListener('input', () => this.handleInput());
        this.searchInput.addEventListener('focus', () => this.handleFocus());

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!this.searchInput.contains(e.target) && !this.searchResults?.contains(e.target)) {
                this.hideResults();
            }
        });

        // Keyboard navigation
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateResults('down');
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateResults('up');
            } else if (e.key === 'Enter') {
                e.preventDefault();
                this.selectCurrent();
            } else if (e.key === 'Escape') {
                this.hideResults();
            }
        });
    }

    handleInput() {
        const query = this.searchInput.value.trim();

        clearTimeout(this.searchTimeout);

        if (query.length < this.minChars) {
            this.hideResults();
            return;
        }

        this.searchTimeout = setTimeout(() => this.search(query), 300);
    }

    handleFocus() {
        if (this.searchInput.value.trim().length >= this.minChars) {
            this.search(this.searchInput.value.trim());
        }
    }

    async search(query) {
        this.showLoading();

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.results && data.results.length > 0) {
                this.renderResults(data.results);
            } else {
                this.showNoResults();
            }
        } catch (error) {
            console.error('Search failed:', error);
            this.showError();
        }
    }

    renderResults(results) {
        if (!this.searchResults) return;

        this.searchResults.innerHTML = results.map((result, index) => `
            <a href="/product/${result.slug || result.id}"
               class="search-result-item"
               data-index="${index}"
               ${index === 0 ? 'id="first-result"' : ''}>
                <img src="${result.thumbnail || '/static/images/placeholder.jpg'}"
                     alt="${result.title}"
                     class="search-result-image"
                     onerror="this.src='/static/images/placeholder.jpg'">
                <div class="search-result-info">
                    <h4>${this.highlightText(result.title, this.searchInput.value)}</h4>
                    <p>MWK ${result.price.toLocaleString()}</p>
                </div>
                ${result.is_sold ? '<span class="sold-badge-small">Sold</span>' : ''}
            </a>
        `).join('');

        this.searchResults.classList.remove('hidden');
        this.currentIndex = 0;
    }

    highlightText(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    }

    showLoading() {
        if (!this.searchResults) return;
        this.searchResults.innerHTML = '<div class="search-result-item">Searching...</div>';
        this.searchResults.classList.remove('hidden');
    }

    showNoResults() {
        if (!this.searchResults) return;
        this.searchResults.innerHTML = '<div class="search-result-item">No products found</div>';
        this.searchResults.classList.remove('hidden');
    }

    showError() {
        if (!this.searchResults) return;
        this.searchResults.innerHTML = '<div class="search-result-item">Search failed. Try again.</div>';
        this.searchResults.classList.remove('hidden');
    }

    hideResults() {
        if (this.searchResults) {
            this.searchResults.classList.add('hidden');
        }
        this.currentIndex = -1;
    }

    navigateResults(direction) {
        const items = this.searchResults?.querySelectorAll('.search-result-item');
        if (!items || !items.length) return;

        if (direction === 'down') {
            this.currentIndex = (this.currentIndex + 1) % items.length;
        } else {
            this.currentIndex = (this.currentIndex - 1 + items.length) % items.length;
        }

        items.forEach((item, i) => {
            if (i === this.currentIndex) {
                item.classList.add('selected');
                item.focus();
            } else {
                item.classList.remove('selected');
            }
        });
    }

    selectCurrent() {
        const selected = this.searchResults?.querySelector('.search-result-item.selected');
        if (selected) {
            window.location.href = selected.href;
        }
    }
}

// Initialize search
document.addEventListener('DOMContentLoaded', () => {
    window.searchManager = new SearchManager();
});