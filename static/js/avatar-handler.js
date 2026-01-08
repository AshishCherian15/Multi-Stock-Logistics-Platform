// Global Avatar Handler - Updates avatars across all pages in real-time

// Listen for avatar updates from localStorage (cross-tab communication)
window.addEventListener('storage', function(e) {
    if (e.key === 'avatar_updated') {
        const data = JSON.parse(e.newValue);
        updateAllAvatarsGlobally(data.url);
    }
});

// Listen for custom avatar update events
window.addEventListener('avatarUpdated', function(e) {
    updateAllAvatarsGlobally(e.detail.avatarUrl);
});

// Update all avatar instances on the page
function updateAllAvatarsGlobally(avatarUrl) {
    const cacheBuster = '?t=' + Date.now();
    const finalUrl = avatarUrl.includes('?') ? avatarUrl : avatarUrl + cacheBuster;
    
    // Update all avatar images
    document.querySelectorAll('img[alt*="avatar"]').forEach(img => {
        if (img.src && !img.src.includes('placeholder')) {
            img.src = finalUrl;
        }
    });
    
    // Update navbar avatar
    const navAvatar = document.querySelector('.navbar img[alt*="avatar"]');
    if (navAvatar) {
        navAvatar.src = finalUrl;
    }
    
    // Update profile page avatar
    const profileAvatar = document.getElementById('profilePhoto');
    if (profileAvatar) {
        profileAvatar.src = finalUrl;
        profileAvatar.style.display = 'block';
        const icon = document.getElementById('profileIcon');
        if (icon) icon.style.display = 'none';
    }
}

// Handle avatar image load errors globally
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('img[alt*="avatar"]').forEach(img => {
        img.addEventListener('error', function() {
            // Show initials fallback
            const wrapper = this.closest('.avatar-wrapper');
            if (wrapper) {
                const initials = wrapper.querySelector('.avatar-initials');
                if (initials) {
                    this.style.display = 'none';
                    initials.style.display = 'flex';
                }
            }
        });
    });
});

// Retry loading failed avatars after 2 seconds
function retryFailedAvatars() {
    document.querySelectorAll('img[alt*="avatar"][style*="display: none"]').forEach(img => {
        const originalSrc = img.dataset.originalSrc || img.src;
        img.src = originalSrc + '?retry=' + Date.now();
        img.style.display = 'block';
    });
}

// Auto-retry failed avatars every 30 seconds
setInterval(retryFailedAvatars, 30000);
