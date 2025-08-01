// Responsive JavaScript for Mimesis

// Utility functions
function isMobile() {
    return window.innerWidth <= 768;
}

function isTablet() {
    return window.innerWidth > 768 && window.innerWidth <= 1024;
}

function isDesktop() {
    return window.innerWidth > 1024;
}

// Responsive notification system
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600';
    const textSize = isMobile() ? 'text-sm' : 'text-base';
    
    notification.className = `fixed top-4 left-1/2 transform -translate-x-1/2 ${bgColor} text-white px-4 py-2 rounded-lg z-50 ${textSize} max-w-xs sm:max-w-md text-center`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, duration);
}

// Responsive form handling
function handleFormSubmission(form, endpoint, successMessage = 'Success!') {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        
        fetch(endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(successMessage, 'success');
                form.reset();
            } else {
                showNotification(data.error || 'Something went wrong', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Network error. Please try again.', 'error');
        })
        .finally(() => {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        });
    });
}

// Responsive star rating
function initializeStarRating() {
    const ratingStars = document.querySelectorAll('.rating-star');
    
    if (ratingStars.length === 0) return;
    
    ratingStars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            
            // Update radio button
            const radioButton = document.getElementById(`rating-${rating}`);
            if (radioButton) {
                radioButton.checked = true;
            }
            
            // Update star display
            ratingStars.forEach((s, index) => {
                if (index < rating) {
                    s.classList.remove('text-gray-400');
                    s.classList.add('text-yellow-400');
                } else {
                    s.classList.remove('text-yellow-400');
                    s.classList.add('text-gray-400');
                }
            });
        });
        
        // Add touch support for mobile
        if (isMobile()) {
            star.addEventListener('touchstart', function(e) {
                e.preventDefault();
                this.click();
            }, { passive: false });
        }
    });
}

// Responsive share functionality
function initializeShareButtons() {
    const shareButtons = document.querySelectorAll('[onclick*="shareStyle"]');
    
    shareButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const aestheticName = this.getAttribute('data-aesthetic') || 'Style';
            const url = this.getAttribute('data-url') || window.location.href;
            
            if (navigator.share && isMobile()) {
                navigator.share({
                    title: `My ${aestheticName} Style on Mimesis`,
                    text: `Check out my ${aestheticName} style!`,
                    url: url
                }).then(() => {
                    showNotification('Shared successfully!', 'success');
                }).catch(error => {
                    console.log('Error sharing:', error);
                    fallbackShare(aestheticName, url);
                });
            } else {
                fallbackShare(aestheticName, url);
            }
        });
    });
}

function fallbackShare(aestheticName, url) {
    const shareText = `Check out my ${aestheticName} style! ${url}`;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareText).then(() => {
            showNotification('Share text copied to clipboard!', 'success');
        }).catch(() => {
            prompt('Copy this link to share:', shareText);
        });
    } else {
        prompt('Copy this link to share:', shareText);
    }
}

// Responsive copy link functionality
function initializeCopyButtons() {
    const copyButtons = document.querySelectorAll('[onclick*="copyLink"]');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('data-url') || window.location.href;
            
            navigator.clipboard.writeText(url).then(() => {
                showNotification('Link copied to clipboard!', 'success');
            }).catch(() => {
                prompt('Copy this link manually:', url);
            });
        });
    });
}

// Responsive feedback form
function initializeFeedbackForm() {
    const feedbackForm = document.getElementById('rating-form');
    
    if (!feedbackForm) return;
    
    feedbackForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const rating = document.querySelector('input[name="rating"]:checked')?.value;
        const feedback = document.getElementById('feedback')?.value || '';
        
        if (!rating) {
            showNotification('Please select a rating.', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('request_id', this.getAttribute('data-request-id') || '');
        formData.append('rating', rating);
        formData.append('feedback', feedback);
        
        const submitButton = this.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Submitting...';
        
        fetch('/feedback', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Thank you for your feedback!', 'success');
                
                // Reset form
                this.reset();
                document.querySelectorAll('.rating-star').forEach(star => {
                    star.classList.remove('text-yellow-400');
                    star.classList.add('text-gray-400');
                });
            } else {
                showNotification(data.error || 'Failed to submit feedback.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Network error. Please try again.', 'error');
        })
        .finally(() => {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        });
    });
}

// Responsive PWA install button
function initializePWAInstall() {
    let deferredPrompt;
    const installButton = document.getElementById('install-btn');
    
    if (!installButton) return;
    
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        installButton.classList.remove('hidden');
    });
    
    installButton.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                showNotification('Mimesis installed successfully!', 'success');
            }
            
            deferredPrompt = null;
            installButton.classList.add('hidden');
        }
    });
}

// Responsive touch handling
function initializeTouchSupport() {
    if (isMobile()) {
        // Prevent zoom on double tap
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            const now = (new Date()).getTime();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Add passive touch listeners for better performance
        document.addEventListener('touchstart', function() {}, {passive: true});
    }
}

// Responsive resize handling
function handleResize() {
    // Update any responsive elements when window is resized
    const isCurrentlyMobile = isMobile();
    const isCurrentlyTablet = isTablet();
    const isCurrentlyDesktop = isDesktop();
    
    // Add resize-specific logic here if needed
    document.body.classList.toggle('mobile-view', isCurrentlyMobile);
    document.body.classList.toggle('tablet-view', isCurrentlyTablet);
    document.body.classList.toggle('desktop-view', isCurrentlyDesktop);
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all responsive features
    initializeStarRating();
    initializeShareButtons();
    initializeCopyButtons();
    initializeFeedbackForm();
    initializePWAInstall();
    initializeTouchSupport();
    
    // Handle window resize
    window.addEventListener('resize', handleResize);
    handleResize(); // Initial call
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to all forms
    document.querySelectorAll('form').forEach(form => {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            form.addEventListener('submit', function() {
                if (submitButton.disabled) return;
                
                submitButton.disabled = true;
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
                
                // Reset after a delay (in case form submission is handled elsewhere)
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 5000);
            });
        }
    });
    
    console.log('Mimesis responsive JavaScript initialized');
});

// Export functions for use in other scripts
window.MimesisJS = {
    showNotification,
    isMobile,
    isTablet,
    isDesktop,
    handleFormSubmission
};
