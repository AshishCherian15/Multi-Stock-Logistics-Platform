// Global image fallback handler
document.addEventListener('DOMContentLoaded', function() {
    // Handle image loading errors globally
    document.addEventListener('error', function(e) {
        if (e.target.tagName === 'IMG') {
            handleImageError(e.target);
        }
    }, true);
    
    // Replace all placeholder images on page load
    replaceAllPlaceholders();
});

function handleImageError(img) {
    // Prevent infinite loop
    if (img.dataset.fallbackApplied) return;
    
    img.dataset.fallbackApplied = 'true';
    
    // Get appropriate fallback based on context
    const fallbackUrl = getFallbackImage(img);
    
    if (fallbackUrl && img.src !== fallbackUrl) {
        img.src = fallbackUrl;
    } else {
        // If fallback also fails, show placeholder icon
        img.style.display = 'none';
        const placeholder = createPlaceholderElement(img);
        img.parentNode.insertBefore(placeholder, img);
    }
}

function getFallbackImage(img) {
    const alt = img.alt.toLowerCase();
    const className = img.className.toLowerCase();
    
    // Product images
    if (alt.includes('headphone') || alt.includes('audio')) {
        return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop&crop=center';
    }
    if (alt.includes('shirt') || alt.includes('clothing') || alt.includes('fashion')) {
        return 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&crop=center';
    }
    if (alt.includes('coffee') || alt.includes('food') || alt.includes('beverage')) {
        return 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=300&h=300&fit=crop&crop=center';
    }
    if (alt.includes('book') || alt.includes('programming')) {
        return 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=300&fit=crop&crop=center';
    }
    if (alt.includes('phone') || alt.includes('mobile') || alt.includes('iphone') || alt.includes('samsung')) {
        return 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300&h=300&fit=crop&crop=center';
    }
    if (alt.includes('laptop') || alt.includes('macbook') || alt.includes('computer')) {
        return 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300&h=300&fit=crop&crop=center';
    }
    if (alt.includes('shoe') || alt.includes('nike') || alt.includes('adidas') || alt.includes('sneaker')) {
        return 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=center';
    }
    
    // Default fallback
    return 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop&crop=center';
}

function createPlaceholderElement(originalImg) {
    const placeholder = document.createElement('div');
    placeholder.className = 'image-placeholder d-flex align-items-center justify-content-center';
    placeholder.style.cssText = `
        width: ${originalImg.width || 200}px;
        height: ${originalImg.height || 200}px;
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 8px;
        color: #6c757d;
        font-size: 2rem;
    `;
    
    const icon = document.createElement('i');
    icon.className = 'fas fa-image';
    placeholder.appendChild(icon);
    
    return placeholder;
}

function replaceAllPlaceholders() {
    // Replace via.placeholder.com images
    const placeholderImages = document.querySelectorAll('img[src*="via.placeholder"], img[src*="placeholder"]');
    placeholderImages.forEach(img => {
        const fallback = getFallbackImage(img);
        if (fallback) {
            img.src = fallback;
        }
    });
    
    // Add loading="lazy" to all images for better performance
    const allImages = document.querySelectorAll('img');
    allImages.forEach(img => {
        if (!img.loading) {
            img.loading = 'lazy';
        }
        
        // Ensure proper object-fit for product images
        if (img.closest('.product-image, .product-card')) {
            img.style.objectFit = 'cover';
        }
    });
}

// Export for use in other scripts
window.ImageFallback = {
    handleError: handleImageError,
    getFallback: getFallbackImage,
    replaceAll: replaceAllPlaceholders
};