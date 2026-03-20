// app/static/js/dashboard.js

class DashboardManager {
    constructor() {
        this.initCharts();
        this.initFileUpload();
        this.initDataTables();
        this.initAutoSave();
    }

    initCharts() {
        // Initialize any dashboard charts
        this.initSalesChart();
        this.initProductsChart();
    }

    initSalesChart() {
        const canvas = document.getElementById('salesChart');
        if (!canvas || typeof Chart === 'undefined') return;

        // Chart is initialized in the template
    }

    initProductsChart() {
        const canvas = document.getElementById('productsChart');
        if (!canvas || typeof Chart === 'undefined') return;

        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Sold', 'Available', 'Featured'],
                datasets: [{
                    data: [
                        parseInt(canvas.dataset.sold || 0),
                        parseInt(canvas.dataset.available || 0),
                        parseInt(canvas.dataset.featured || 0)
                    ],
                    backgroundColor: ['#ef4444', '#10b981', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                cutout: '70%'
            }
        });
    }

    initFileUpload() {
        const uploadArea = document.getElementById('fileUploadArea');
        const fileInput = document.getElementById('images');

        if (!uploadArea || !fileInput) return;

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length) {
                fileInput.files = files;
                this.handleFilePreview(files);
            }
        });

        fileInput.addEventListener('change', () => {
            this.handleFilePreview(fileInput.files);
        });
    }

    handleFilePreview(files) {
        const preview = document.getElementById('imagePreview');
        if (!preview) return;

        Array.from(files).forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const previewItem = document.createElement('div');
                    previewItem.className = 'preview-item';
                    previewItem.innerHTML = `
                        <img src="${e.target.result}" alt="Preview">
                        <button type="button" class="remove-image" onclick="this.parentElement.remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    preview.appendChild(previewItem);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    initDataTables() {
        // Add sorting to tables
        document.querySelectorAll('.data-table').forEach(table => {
            const headers = table.querySelectorAll('th[data-sortable="true"]');

            headers.forEach(header => {
                header.addEventListener('click', () => {
                    const index = Array.from(header.parentNode.children).indexOf(header);
                    this.sortTable(table, index);
                });
            });
        });
    }

    sortTable(table, column) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAsc = table.dataset.sortOrder !== 'asc';

        rows.sort((a, b) => {
            const aVal = a.children[column].textContent.trim();
            const bVal = b.children[column].textContent.trim();

            if (isAsc) {
                return aVal.localeCompare(bVal, undefined, { numeric: true });
            } else {
                return bVal.localeCompare(aVal, undefined, { numeric: true });
            }
        });

        rows.forEach(row => tbody.appendChild(row));
        table.dataset.sortOrder = isAsc ? 'asc' : 'desc';
    }

    initAutoSave() {
        const forms = document.querySelectorAll('[data-autosave="true"]');

        forms.forEach(form => {
            const inputs = form.querySelectorAll('input, textarea, select');

            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.autoSave(form);
                });
            });
        });
    }

    async autoSave(form) {
        const formData = new FormData(form);
        const saveIndicator = document.getElementById('autosave-indicator');

        if (saveIndicator) {
            saveIndicator.textContent = 'Saving...';
        }

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (saveIndicator) {
                saveIndicator.textContent = 'Saved';
                setTimeout(() => {
                    saveIndicator.textContent = '';
                }, 2000);
            }

            if (data.success) {
                showToast('Changes saved', 'success');
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
            if (saveIndicator) {
                saveIndicator.textContent = 'Save failed';
            }
        }
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.dashboard-page')) {
        window.dashboard = new DashboardManager();
    }
});