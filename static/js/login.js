// Login Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    const submitButton = document.querySelector('.btn-login');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    // Form validation
    function validateForm() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        
        if (!username || !password) {
            return false;
        }
        
        return true;
    }

    // Handle form submission
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                showMessage('Tafadhali jaza sehemu zote zinazohitajika.', 'error');
                return;
            }

            // Add loading state
            submitButton.classList.add('loading');
            submitButton.disabled = true;
        });
    }

    // Real-time validation feedback
    function addValidationFeedback() {
        [usernameInput, passwordInput].forEach(input => {
            if (input) {
                input.addEventListener('blur', function() {
                    if (!this.value.trim()) {
                        this.style.borderColor = '#e74c3c';
                    } else {
                        this.style.borderColor = '#27ae60';
                    }
                });

                input.addEventListener('focus', function() {
                    this.style.borderColor = '#667eea';
                });
            }
        });
    }

    // Show messages
    function showMessage(message, type = 'info') {
        const existingMessages = document.querySelector('.messages');
        if (existingMessages) {
            existingMessages.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = 'messages';
        messageDiv.innerHTML = `
            <div class="alert alert-${type}">
                ${message}
            </div>
        `;

        const formContainer = document.querySelector('.login-form-container');
        const title = document.querySelector('.login-title');
        formContainer.insertBefore(messageDiv, title.nextSibling);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    // Initialize validation
    addValidationFeedback();

    // Handle remember me functionality
    const rememberCheckbox = document.querySelector('input[name="remember_me"]');
    if (rememberCheckbox) {
        // Load saved username if remember me was checked
        const savedUsername = localStorage.getItem('remembered_username');
        if (savedUsername && usernameInput) {
            usernameInput.value = savedUsername;
            rememberCheckbox.checked = true;
        }

        // Save/remove username based on checkbox
        loginForm.addEventListener('submit', function() {
            if (rememberCheckbox.checked) {
                localStorage.setItem('remembered_username', usernameInput.value);
            } else {
                localStorage.removeItem('remembered_username');
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Enter key to submit form
        if (e.key === 'Enter' && (usernameInput === document.activeElement || passwordInput === document.activeElement)) {
            if (validateForm()) {
                loginForm.submit();
            }
        }
    });

    // Auto-focus username field if empty
    if (usernameInput && !usernameInput.value) {
        usernameInput.focus();
    } else if (passwordInput && usernameInput.value) {
        passwordInput.focus();
    }

    // Handle browser back button
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            // Remove loading state if page is restored from cache
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
        }
    });

    // Accessibility improvements
    function improveAccessibility() {
        // Add ARIA labels
        usernameInput?.setAttribute('aria-describedby', 'username-help');
        passwordInput?.setAttribute('aria-describedby', 'password-help');

        // Add screen reader announcements for form validation
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.style.position = 'absolute';
        announcer.style.left = '-10000px';
        announcer.style.width = '1px';
        announcer.style.height = '1px';
        announcer.style.overflow = 'hidden';
        document.body.appendChild(announcer);

        window.announceToScreenReader = function(message) {
            announcer.textContent = message;
        };
    }

    improveAccessibility();
});
