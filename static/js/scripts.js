// Mimesis Frontend JavaScript

// DOM elements
const culturalForm = document.getElementById('cultural-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.getElementById('btn-text');
const btnLoading = document.getElementById('btn-loading');
const culturalInput = document.getElementById('cultural_preferences');
const chatForm = document.getElementById('chat-form');
const chatMessage = document.getElementById('chat-message');
const chatBtn = document.getElementById('chat-btn');
const chatResponse = document.getElementById('chat-response');
const chatText = document.getElementById('chat-text');
const chatContext = document.getElementById('chat-context');

// Form validation and submission
if (culturalForm) {
    culturalForm.addEventListener('submit', function(e) {
        const input = culturalInput.value.trim();
        
        // Validate input
        if (!input) {
            e.preventDefault();
            showAlert('Please enter your cultural preferences before submitting.', 'error');
            culturalInput.focus();
            return;
        }
        
        if (input.length < 10) {
            e.preventDefault();
            showAlert('Please provide more detailed cultural preferences (at least 10 characters).', 'error');
            culturalInput.focus();
            return;
        }
        
        // Show loading state
        showLoadingState();
    });
    
    // Real-time character count and suggestions
    culturalInput.addEventListener('input', function() {
        const value = this.value.trim();
        const charCount = value.length;
        
        // Remove existing feedback
        const existingFeedback = document.querySelector('.input-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Add character count and suggestions
        const feedback = document.createElement('div');
        feedback.className = 'input-feedback text-sm mt-2';
        
        if (charCount === 0) {
            feedback.innerHTML = '<span class="text-gray-500">Start typing your cultural influences...</span>';
        } else if (charCount < 10) {
            feedback.innerHTML = `<span class="text-orange-500">Add more details (${charCount}/10 minimum)</span>`;
        } else {
            feedback.innerHTML = `<span class="text-green-600"><i class="fas fa-check mr-1"></i>Looking good! (${charCount} characters)</span>`;
        }
        
        culturalInput.parentNode.appendChild(feedback);
    });
}

// Feedback functionality
const feedbackForm = document.getElementById('feedback-form');
const starBtns = document.querySelectorAll('.star-btn');
const ratingValue = document.getElementById('rating-value');
const feedbackSubmit = document.getElementById('feedback-submit');
const feedbackResponse = document.getElementById('feedback-response');

if (feedbackForm && starBtns.length > 0) {
    // Star rating functionality
    starBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const rating = parseInt(this.dataset.rating);
            ratingValue.value = rating;
            
            // Update star display
            starBtns.forEach((star, index) => {
                if (index < rating) {
                    star.classList.remove('text-gray-300');
                    star.classList.add('text-yellow-500');
                } else {
                    star.classList.remove('text-yellow-500');
                    star.classList.add('text-gray-300');
                }
            });
            
            // Enable submit button
            feedbackSubmit.disabled = false;
        });
        
        // Hover effects
        btn.addEventListener('mouseenter', function() {
            const rating = parseInt(this.dataset.rating);
            starBtns.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('text-yellow-400');
                }
            });
        });
        
        btn.addEventListener('mouseleave', function() {
            starBtns.forEach(star => {
                star.classList.remove('text-yellow-400');
            });
        });
    });
    
    // Submit feedback
    feedbackForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const requestId = document.getElementById('request-id').value;
        const rating = ratingValue.value;
        const feedbackText = document.getElementById('feedback-text').value;
        
        if (!rating) {
            showAlert('Please select a star rating.', 'error');
            return;
        }
        
        // Show loading state
        feedbackSubmit.disabled = true;
        feedbackSubmit.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Submitting...';
        
        try {
            const formData = new FormData();
            formData.append('request_id', requestId);
            formData.append('rating', rating);
            formData.append('feedback', feedbackText);
            
            const response = await fetch('/feedback', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Show success message
                feedbackResponse.classList.remove('hidden');
                feedbackForm.style.display = 'none';
                
                // Scroll to response
                feedbackResponse.scrollIntoView({ behavior: 'smooth' });
            } else {
                showAlert(data.error || 'Unable to submit feedback. Please try again.', 'error');
                feedbackSubmit.disabled = false;
                feedbackSubmit.innerHTML = '<i class="fas fa-heart mr-2"></i>Submit Feedback';
            }
        } catch (error) {
            console.error('Feedback error:', error);
            showAlert('Network error. Please check your connection and try again.', 'error');
            feedbackSubmit.disabled = false;
            feedbackSubmit.innerHTML = '<i class="fas fa-heart mr-2"></i>Submit Feedback';
        }
    });
}

// Chat functionality
if (chatForm) {
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = chatMessage.value.trim();
        if (!message) {
            showAlert('Please enter a message.', 'error');
            return;
        }
        
        // Show loading state for chat
        chatBtn.disabled = true;
        chatBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            const formData = new FormData();
            formData.append('message', message);
            formData.append('context', chatContext ? chatContext.value : '');
            
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Show chat response
                chatText.textContent = data.response;
                chatResponse.classList.remove('hidden');
                chatMessage.value = '';
                
                // Scroll to response
                chatResponse.scrollIntoView({ behavior: 'smooth' });
            } else {
                showAlert(data.error || 'Unable to get a response. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Chat error:', error);
            showAlert('Network error. Please check your connection and try again.', 'error');
        } finally {
            // Reset chat button
            chatBtn.disabled = false;
            chatBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        }
    });
    
    // Enter key support for chat
    chatMessage.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}

// Utility functions
function showLoadingState() {
    if (submitBtn && btnText && btnLoading) {
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
    }
}

function hideLoadingState() {
    if (submitBtn && btnText && btnLoading) {
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        btnLoading.classList.add('hidden');
    }
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-sm bg-white border-l-4 p-4 rounded-lg shadow-lg`;
    
    if (type === 'error') {
        alert.classList.add('border-red-500', 'bg-red-50');
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle text-red-500 mr-2"></i>
                <span class="text-red-700">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-red-500 hover:text-red-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    } else if (type === 'success') {
        alert.classList.add('border-green-500', 'bg-green-50');
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-check-circle text-green-500 mr-2"></i>
                <span class="text-green-700">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-green-500 hover:text-green-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    } else {
        alert.classList.add('border-blue-500', 'bg-blue-50');
        alert.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-info-circle text-blue-500 mr-2"></i>
                <span class="text-blue-700">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-blue-500 hover:text-blue-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }
    
    document.body.appendChild(alert);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Example suggestions functionality
function fillExample(text) {
    if (culturalInput) {
        culturalInput.value = text;
        culturalInput.focus();
        
        // Trigger input event for validation
        culturalInput.dispatchEvent(new Event('input'));
    }
}

// Add click handlers for example cards
document.addEventListener('DOMContentLoaded', function() {
    const exampleCards = document.querySelectorAll('[data-example]');
    exampleCards.forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', function() {
            const exampleText = this.getAttribute('data-example');
            if (exampleText) {
                fillExample(exampleText);
            }
        });
    });
    
    // Add hover effects to interactive elements
    const interactiveElements = document.querySelectorAll('button, .hover-lift, [data-example]');
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Handle page visibility changes (pause animations when tab is hidden)
document.addEventListener('visibilitychange', function() {
    const spinners = document.querySelectorAll('.fa-spin');
    if (document.hidden) {
        spinners.forEach(spinner => spinner.style.animationPlayState = 'paused');
    } else {
        spinners.forEach(spinner => spinner.style.animationPlayState = 'running');
    }
});

// Smooth scrolling for anchor links
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

// Add copy functionality for results
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    }).catch(function() {
        showAlert('Unable to copy to clipboard', 'error');
    });
}

// Add share functionality
function shareResults() {
    if (navigator.share) {
        navigator.share({
            title: 'My Mimesis Style Identity',
            text: 'Check out my personalized cultural style recommendations from Mimesis!',
            url: window.location.href
        });
    } else {
        copyToClipboard(window.location.href);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (culturalForm && !submitBtn.disabled) {
            culturalForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to close alerts
    if (e.key === 'Escape') {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => alert.remove());
    }
});

// Performance monitoring
window.addEventListener('load', function() {
    // Log page load time for debugging
    const loadTime = performance.now();
    console.log(`Mimesis loaded in ${Math.round(loadTime)}ms`);
});

// Error boundary for unhandled JavaScript errors
window.addEventListener('error', function(e) {
    console.error('Unhandled error:', e.error);
    showAlert('An unexpected error occurred. Please refresh the page.', 'error');
});

// Service worker registration for offline functionality (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Placeholder for future PWA implementation
        console.log('Service Worker support detected');
    });
}
