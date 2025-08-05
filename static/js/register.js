// Church Membership Registration Form JavaScript

class MembershipForm {
    constructor() {
        this.form = document.getElementById('memberForm');
        this.progressBar = document.querySelector('.progress-fill');
        this.progressText = document.querySelector('.progress-text');
        this.submitButton = document.querySelector('button[type="submit"]');
        this.formError = document.getElementById('formError');
        
        // Debug logging
        console.log('Form elements found:', {
            form: !!this.form,
            progressBar: !!this.progressBar,
            progressText: !!this.progressText,
            submitButton: !!this.submitButton,
            formError: !!this.formError
        });
        
        if (!this.form) {
            console.error('Registration form not found!');
            return;
        }
        
        if (!this.submitButton) {
            console.error('Submit button not found!');
            return;
        }
        
        this.totalFields = this.form.querySelectorAll('input[required], select[required]').length;
        this.currentStep = 1;
        this.maxSteps = 4;
        
        console.log(`Found ${this.totalFields} required fields`);
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupConditionalFields();
        this.setupFormValidation();
        this.updateProgress();
        this.setupAccessibility();
    }

    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Real-time validation
        this.form.querySelectorAll('input, select').forEach(field => {
            field.addEventListener('blur', () => this.validateField(field));
            field.addEventListener('input', () => this.updateProgress());
        });

        // Auto-save functionality (optional)
        this.form.addEventListener('input', this.debounce(() => this.autoSave(), 1000));
    }

    setupConditionalFields() {
        const baptizedField = document.getElementById('baptized');
        const baptismDateField = document.getElementById('baptism_date');
        const baptismDateGroup = baptismDateField.closest('.form-group');

        baptizedField.addEventListener('change', () => {
            if (baptizedField.value === 'Yes') {
                baptismDateGroup.classList.add('active');
                baptismDateField.setAttribute('aria-required', 'true');
            } else {
                baptismDateGroup.classList.remove('active');
                baptismDateField.removeAttribute('aria-required');
                baptismDateField.value = '';
                this.clearFieldError(baptismDateField);
            }
        });

        // Initialize conditional fields
        if (baptizedField.value !== 'Yes') {
            baptismDateGroup.classList.add('conditional-field');
        }
    }

    setupFormValidation() {
        // Custom validation rules
        const phoneField = document.getElementById('phone');
        const emergencyPhoneField = document.getElementById('emergency_phone');
        const emailField = document.getElementById('email');
        const dobField = document.getElementById('dob');

        // Phone validation
        [phoneField, emergencyPhoneField].forEach(field => {
            if (field) {
                field.addEventListener('input', () => this.validatePhone(field));
            }
        });

        // Email validation
        if (emailField) {
            emailField.addEventListener('input', () => this.validateEmail(emailField));
        }

        // Date validation
        if (dobField) {
            dobField.addEventListener('change', () => this.validateDate(dobField));
        }
    }

    setupAccessibility() {
        // Add ARIA labels and descriptions
        this.form.querySelectorAll('input, select').forEach(field => {
            const label = this.form.querySelector(`label[for="${field.id}"]`);
            const errorDiv = document.getElementById(`error-${field.name}`);
            
            if (label && label.textContent.includes('*')) {
                field.setAttribute('aria-required', 'true');
            }
            
            if (errorDiv) {
                field.setAttribute('aria-describedby', `error-${field.name}`);
            }
        });

        // Announce form errors to screen readers
        this.formError.setAttribute('role', 'alert');
        this.formError.setAttribute('aria-live', 'polite');
    }

    validateField(field) {
        const value = field.value.trim();
        const isRequired = field.hasAttribute('required') || field.hasAttribute('aria-required');
        
        // Clear previous errors
        this.clearFieldError(field);

        // Required field validation
        if (isRequired && !value) {
            this.showFieldError(field, 'Hii sehemu ni lazima ijazwe.');
            return false;
        }

        // Field-specific validation
        switch (field.type) {
            case 'email':
                return this.validateEmail(field);
            case 'tel':
                return this.validatePhone(field);
            case 'date':
                return this.validateDate(field);
            default:
                return true;
        }
    }

    validateEmail(field) {
        const email = field.value.trim();
        if (!email) return true; // Optional field
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            this.showFieldError(field, 'Tafadhali ingiza barua pepe sahihi.');
            return false;
        }
        return true;
    }

    validatePhone(field) {
        const phone = field.value.trim();
        if (!phone && !field.hasAttribute('required')) return true; // Optional field
        
        // Kenyan phone number validation
        const phoneRegex = /^(\+254|0)[17]\d{8}$/;
        if (phone && !phoneRegex.test(phone.replace(/\s/g, ''))) {
            this.showFieldError(field, 'Tafadhali ingiza namba ya simu sahihi (mfano: 0712345678).');
            return false;
        }
        return true;
    }

    validateDate(field) {
        const date = field.value;
        if (!date) return true; // Optional field
        
        const selectedDate = new Date(date);
        const today = new Date();
        
        if (field.id === 'dob' && selectedDate > today) {
            this.showFieldError(field, 'Tarehe ya kuzaliwa haiwezi kuwa baadaye.');
            return false;
        }
        
        if (field.id === 'registration_date') {
            const oneYearAgo = new Date();
            oneYearAgo.setFullYear(today.getFullYear() - 1);
            
            if (selectedDate < oneYearAgo || selectedDate > today) {
                this.showFieldError(field, 'Tarehe ya usajili ni lazima iwe ndani ya mwaka mmoja uliopita.');
                return false;
            }
        }
        
        return true;
    }

    showFieldError(field, message) {
        const errorDiv = document.getElementById(`error-${field.name}`);
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.setAttribute('role', 'alert');
        }
        field.classList.add('error');
        field.setAttribute('aria-invalid', 'true');
    }

    clearFieldError(field) {
        const errorDiv = document.getElementById(`error-${field.name}`);
        if (errorDiv) {
            errorDiv.textContent = '';
            errorDiv.removeAttribute('role');
        }
        field.classList.remove('error');
        field.removeAttribute('aria-invalid');
    }

    updateProgress() {
        const filledFields = Array.from(this.form.querySelectorAll('input[required], select[required]'))
            .filter(field => field.value.trim() !== '').length;
        
        const progress = Math.round((filledFields / this.totalFields) * 100);
        
        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
        }
        
        if (this.progressText) {
            const step = Math.ceil((progress / 100) * this.maxSteps);
            this.progressText.textContent = `Hatua ${step} ya ${this.maxSteps} (${progress}% imekamilika)`;
        }
    }

    async handleSubmit(event) {
        console.log('Form submission started');
        event.preventDefault();
        
        // Clear previous errors
        this.clearAllErrors();
        
        // Validate all fields
        console.log('Validating form fields...');
        const isValid = this.validateAllFields();
        console.log('Form validation result:', isValid);
        
        if (!isValid) {
            console.log('Form validation failed');
            this.showFormError('Tafadhali sahihisha makosa yaliyoonyeshwa.');
            return;
        }

        // Show loading state
        console.log('Setting loading state...');
        this.setLoadingState(true);

        const formData = new FormData(this.form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        
        console.log('Form data to submit:', data);
        
        // Get CSRF token (try form field first, then cookie)
        let csrfToken = this.getCSRFToken();
        console.log('CSRF token found:', !!csrfToken);
        
        if (!csrfToken) {
            console.error('CSRF token not found!');
            this.showFormError('Hitilafu ya usalama. Tafadhali upakue ukurasa tena.');
            this.setLoadingState(false);
            return;
        }

        try {
            console.log('Sending request to /api/register/');
            const response = await fetch("/api/register/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(data),
            });
            
            console.log('Response received:', {
                status: response.status,
                statusText: response.statusText,
                ok: response.ok
            });

            if (response.ok) {
                console.log('Registration successful!');
                const result = await response.json();
                console.log('Success response:', result);
                this.handleSuccess();
            } else if (response.status >= 500) {
                console.error('Server error:', response.status);
                this.showFormError('Hitilafu ya server. Tafadhali jaribu tena.');
            } else {
                console.log('Validation errors from server');
                const errors = await response.json();
                console.log('Server errors:', errors);
                this.handleValidationErrors(errors);
            }
        } catch (error) {
            console.error('Network error:', error);
            this.showFormError('Mtandao umeshindwa: ' + error.message);
        } finally {
            console.log('Setting loading state to false');
            this.setLoadingState(false);
        }
    }

    validateAllFields() {
        let isValid = true;
        const fields = this.form.querySelectorAll('input, select');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    handleSuccess() {
        this.form.reset();
        this.showFormSuccess('Usajili umefanikiwa! Karibu katika familia ya kanisa.');
        this.updateProgress();
        
        // Clear auto-saved data
        this.clearAutoSave();
        
        // Focus on success message for screen readers
        this.formError.focus();
    }

    handleValidationErrors(errors) {
        Object.keys(errors).forEach(field => {
            const fieldElement = this.form.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const errorMessage = Array.isArray(errors[field]) 
                    ? errors[field].join(' ') 
                    : errors[field];
                this.showFieldError(fieldElement, errorMessage);
            }
        });
        
        // Focus on first error field
        const firstErrorField = this.form.querySelector('.error');
        if (firstErrorField) {
            firstErrorField.focus();
        }
    }

    setLoadingState(loading) {
        if (loading) {
            this.submitButton.disabled = true;
            this.submitButton.classList.add('loading');
            this.submitButton.innerHTML = '<span class="loading-spinner"></span>Inaongoza...';
        } else {
            this.submitButton.disabled = false;
            this.submitButton.classList.remove('loading');
            this.submitButton.innerHTML = 'Sajili';
        }
    }

    showFormError(message) {
        this.formError.textContent = message;
        this.formError.className = 'form-error show';
        this.formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    showFormSuccess(message) {
        this.formError.textContent = message;
        this.formError.className = 'form-success show';
        this.formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    clearAllErrors() {
        this.formError.className = 'form-error';
        this.formError.textContent = '';
        
        this.form.querySelectorAll('.error').forEach(div => {
            div.textContent = '';
            div.removeAttribute('role');
        });
        
        this.form.querySelectorAll('input, select').forEach(field => {
            field.classList.remove('error');
            field.removeAttribute('aria-invalid');
        });
    }

    // Auto-save functionality
    autoSave() {
        const formData = new FormData(this.form);
        const data = {};
        formData.forEach((value, key) => {
            if (value.trim()) {
                data[key] = value;
            }
        });
        
        localStorage.setItem('membershipFormData', JSON.stringify(data));
    }

    loadAutoSave() {
        const savedData = localStorage.getItem('membershipFormData');
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const field = this.form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
            this.updateProgress();
        }
    }

    clearAutoSave() {
        localStorage.removeItem('membershipFormData');
    }

    // Utility functions
    getCSRFToken() {
        // First try to get CSRF token from the form's hidden input field
        const csrfInput = this.form.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput && csrfInput.value) {
            console.log('CSRF token found in form field');
            return csrfInput.value;
        }
        
        // Fallback to cookie method (for authenticated users)
        const cookieToken = this.getCookie('csrftoken');
        if (cookieToken) {
            console.log('CSRF token found in cookie');
            return cookieToken;
        }
        
        console.log('No CSRF token found in form field or cookie');
        return null;
    }
    
    getCookie(name) {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the form when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MembershipForm();
});

// Handle page visibility changes for auto-save
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        // Save form data when user leaves the page
        const form = document.getElementById('memberForm');
        if (form) {
            const membershipForm = new MembershipForm();
            membershipForm.autoSave();
        }
    }
});
