// Profile Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize profile page functionality
    initializeProfilePage();
    
    // Add form validation
    setupFormValidation();
    
    // Add smooth animations
    animateElements();
});

function initializeProfilePage() {
    // Add hover effects for profile card
    const profileCard = document.querySelector('.profile-card');
    if (profileCard) {
        profileCard.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        profileCard.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    }
    
    // Add click handlers for permission items
    const permissionItems = document.querySelectorAll('.permission-item');
    permissionItems.forEach(item => {
        item.addEventListener('click', function() {
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
}

function setupFormValidation() {
    const form = document.querySelector('.profile-form');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input');
    
    inputs.forEach(input => {
        // Real-time validation on blur
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        // Clear validation on focus
        input.addEventListener('focus', function() {
            clearFieldValidation(this);
        });
    });
    
    // Form submission validation
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showMessage('Tafadhali sahihisha makosa yaliyoonyeshwa.', 'error');
        } else {
            showLoadingState();
        }
    });
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';
    
    // Clear previous errors
    clearFieldValidation(field);
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        errorMessage = 'Hii sehemu ni lazima ijazwe.';
        isValid = false;
    }
    
    // Email validation
    if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            errorMessage = 'Ingiza barua pepe halali.';
            isValid = false;
        }
    }
    
    // Phone validation (Kenyan format)
    if (fieldName === 'phone_number' && value) {
        const phoneRegex = /^(\+254|0)[17]\d{8}$/;
        if (!phoneRegex.test(value)) {
            errorMessage = 'Ingiza nambari ya simu halali (mfano: +254712345678).';
            isValid = false;
        }
    }
    
    // Name validation
    if ((fieldName === 'first_name' || fieldName === 'last_name') && value) {
        if (value.length < 2) {
            errorMessage = 'Jina lazima liwe na angalau herufi 2.';
            isValid = false;
        }
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.style.borderColor = '#e74c3c';
    field.style.boxShadow = '0 0 0 3px rgba(231, 76, 60, 0.1)';
    
    // Create or update error message
    let errorDiv = field.parentNode.querySelector('.error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

function clearFieldValidation(field) {
    field.style.borderColor = '#ecf0f1';
    field.style.boxShadow = 'none';
    
    const errorDiv = field.parentNode.querySelector('.error-message');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function showLoadingState() {
    const submitBtn = document.querySelector('.btn-primary');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Inahifadhi...';
        submitBtn.style.opacity = '0.7';
    }
}

function showMessage(message, type) {
    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type}`;
    messageDiv.textContent = message;
    
    // Insert at top of main content
    const main = document.querySelector('.profile-main');
    main.insertBefore(messageDiv, main.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

function animateElements() {
    // Animate sections on load
    const sections = document.querySelectorAll('.profile-section, .edit-section, .account-section, .permissions-section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            section.style.transition = 'all 0.6s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animate permission items
    const permissionItems = document.querySelectorAll('.permission-item');
    permissionItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.4s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, (index * 50) + 500);
    });
}

// Auto-save functionality (optional)
function setupAutoSave() {
    const form = document.querySelector('.profile-form');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input');
    let autoSaveTimeout;
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(autoSaveTimeout);
            autoSaveTimeout = setTimeout(() => {
                saveToLocalStorage();
            }, 1000);
        });
    });
    
    // Load from localStorage on page load
    loadFromLocalStorage();
}

function saveToLocalStorage() {
    const form = document.querySelector('.profile-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem('profile_form_data', JSON.stringify(data));
    
    // Show auto-save indicator
    showAutoSaveIndicator();
}

function loadFromLocalStorage() {
    const savedData = localStorage.getItem('profile_form_data');
    if (!savedData) return;
    
    try {
        const data = JSON.parse(savedData);
        const form = document.querySelector('.profile-form');
        
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && input.type !== 'hidden') {
                input.value = data[key];
            }
        });
    } catch (e) {
        console.log('Error loading saved data:', e);
    }
}

function showAutoSaveIndicator() {
    // Create or update auto-save indicator
    let indicator = document.querySelector('.auto-save-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(46, 204, 113, 0.9);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }
    
    indicator.textContent = '💾 Imehifadhiwa otomatiki';
    indicator.style.opacity = '1';
    
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// Initialize auto-save if needed
// setupAutoSave();
