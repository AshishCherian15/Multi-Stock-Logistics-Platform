/**
 * Search Module
 * Handles the center search functionality with live results
 */

/**
 * Perform search and display results
 */
function performCenterSearch() {
    const query = document.getElementById('centerSearch').value;
    const resultsDiv = document.getElementById('centerSearchResults');

    if (query.length < 2) {
        resultsDiv.style.display = 'none';
        return;
    }

    resultsDiv.style.display = 'block';
    resultsDiv.innerHTML = '<div class="p-3 text-center"><i class="fas fa-spinner fa-spin text-primary"></i> <span class="ms-2">Searching...</span></div>';

    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                resultsDiv.innerHTML = data.results.map(item =>
                    `<a href="${item.url}" class="d-flex align-items-center p-3 text-decoration-none border-bottom search-result-item">
                        <div class="me-3" style="width:40px;height:40px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;display:flex;align-items:center;justify-content:center">
                            <i class="fas fa-${item.icon} text-white"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-bold text-dark">${item.title || item.name || 'Unknown'}</div>
                            <small class="text-muted"><i class="fas fa-tag me-1"></i>${item.subtitle || item.category || 'Item'}</small>
                        </div>
                        <i class="fas fa-chevron-right text-muted"></i>
                    </a>`
                ).join('');
            } else {
                resultsDiv.innerHTML = `
                    <div class="p-4 text-center text-muted">
                        <i class="fas fa-search fa-2x mb-2"></i>
                        <p>No results found for "${query}"</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            resultsDiv.innerHTML = `
                <div class="p-4 text-center text-danger">
                    <i class="fas fa-exclamation-circle fa-2x mb-2"></i>
                    <p>Search failed. Please try again.</p>
                </div>
            `;
        });
}

// Close search results when clicking outside
document.addEventListener('click', function (event) {
    const searchInput = document.getElementById('centerSearch');
    const resultsDiv = document.getElementById('centerSearchResults');

    if (searchInput && resultsDiv) {
        if (!searchInput.contains(event.target) && !resultsDiv.contains(event.target)) {
            resultsDiv.style.display = 'none';
        }
    }
});

// Add CSS for search result hover effect
const style = document.createElement('style');
style.textContent = `
    .search-result-item {
        transition: all 0.2s ease;
    }
    .search-result-item:hover {
        background: #f8f9fa;
    }
`;
document.head.appendChild(style);
