// Load More Pagination Component
class LoadMorePagination {
    constructor(config) {
        this.apiUrl = config.apiUrl;
        this.container = document.getElementById(config.containerId);
        this.loadMoreBtn = document.getElementById(config.buttonId);
        this.page = 1;
        this.pageSize = config.pageSize || 20;
        this.isLoading = false;
        this.hasMore = true;
        this.renderItem = config.renderItem;
        
        this.init();
    }
    
    init() {
        if (this.loadMoreBtn) {
            this.loadMoreBtn.addEventListener('click', () => this.loadMore());
        }
        
        // Optional: Infinite scroll
        if (this.config?.infiniteScroll) {
            window.addEventListener('scroll', () => this.handleScroll());
        }
    }
    
    async loadMore() {
        if (this.isLoading || !this.hasMore) return;
        
        this.isLoading = true;
        this.showLoading();
        
        try {
            const response = await fetch(`${this.apiUrl}?page=${this.page + 1}&page_size=${this.pageSize}`);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                this.appendItems(data.results);
                this.page++;
                this.hasMore = data.next !== null;
            } else {
                this.hasMore = false;
            }
            
            if (!this.hasMore) {
                this.hideLoadMoreButton();
            }
        } catch (error) {
            console.error('Load more error:', error);
        } finally {
            this.isLoading = false;
            this.hideLoading();
        }
    }
    
    appendItems(items) {
        items.forEach(item => {
            const element = this.renderItem(item);
            this.container.insertAdjacentHTML('beforeend', element);
        });
    }
    
    showLoading() {
        if (this.loadMoreBtn) {
            this.loadMoreBtn.disabled = true;
            this.loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        }
    }
    
    hideLoading() {
        if (this.loadMoreBtn) {
            this.loadMoreBtn.disabled = false;
            this.loadMoreBtn.innerHTML = '<i class="fas fa-chevron-down me-2"></i>Load More';
        }
    }
    
    hideLoadMoreButton() {
        if (this.loadMoreBtn) {
            this.loadMoreBtn.style.display = 'none';
        }
    }
    
    handleScroll() {
        if (this.isLoading || !this.hasMore) return;
        
        const scrollPosition = window.innerHeight + window.scrollY;
        const threshold = document.documentElement.scrollHeight - 200;
        
        if (scrollPosition >= threshold) {
            this.loadMore();
        }
    }
}

// Export for use in templates
window.LoadMorePagination = LoadMorePagination;
