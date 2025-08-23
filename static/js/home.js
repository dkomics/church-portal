// Church Portal Home Page JavaScript

class HomePage {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStatistics();
        this.setupAnimations();
        this.setupAccessibility();
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Add click tracking for analytics (if needed)
        document.querySelectorAll('.btn, .action-card, .feature-link').forEach(element => {
            element.addEventListener('click', (e) => {
                this.trackClick(e.target);
            });
        });

        // Handle navigation active states
        this.updateActiveNavigation();
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics/');
            if (response.ok) {
                const stats = await response.json();
                this.updateStatistics(stats);
            }
        } catch (error) {
            console.warn('Could not load updated statistics:', error);
            // Statistics will show default values from template
        }
    }

    updateStatistics(stats) {
        // Update statistics cards with fresh data
        const statElements = {
            'total_members': document.querySelector('.stat-card:nth-child(1) h4'),
            'new_members_this_month': document.querySelector('.stat-card:nth-child(2) h4'),
            'baptized_members': document.querySelector('.stat-card:nth-child(3) h4'),
            'membership_class_completed': document.querySelector('.stat-card:nth-child(4) h4')
        };

        Object.keys(statElements).forEach(key => {
            const element = statElements[key];
            if (element && stats[key] !== undefined) {
                this.animateNumber(element, parseInt(element.textContent) || 0, stats[key]);
            }
        });
    }

    animateNumber(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.round(start + (end - start) * easeOutQuart);
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.stat-card, .feature-card, .action-card').forEach(el => {
            observer.observe(el);
        });
    }

    setupAccessibility() {
        // Add keyboard navigation support
        document.querySelectorAll('.action-card').forEach(card => {
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    card.click();
                }
            });
        });

        // Add ARIA labels for better screen reader support
        document.querySelectorAll('.stat-card').forEach((card, index) => {
            const titles = ['Jumla ya Washirika', 'Washirika Wapya', 'Waliobatizwa', 'Darasa la Ushirika'];
            card.setAttribute('aria-label', titles[index] || 'Takwimu');
        });

        // Announce page load to screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = 'Ukurasa wa nyumbani umepakiwa. Karibu katika mfumo wa usajili wa washirika.';
        document.body.appendChild(announcement);
    }

    updateActiveNavigation() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath || 
                (currentPath === '/' && link.textContent.trim() === 'Nyumbani')) {
                link.classList.add('active');
            }
        });
    }

    trackClick(element) {
        // Simple click tracking for analytics
        const action = element.textContent.trim() || element.getAttribute('aria-label') || 'Unknown';
        const category = element.closest('.hero-actions') ? 'Hero Action' :
                        element.closest('.actions-grid') ? 'Quick Action' :
                        element.closest('.features-grid') ? 'Feature Link' : 'General';
        
        console.log(`Click tracked: ${category} - ${action}`);
        
        // Here you could send to analytics service
        // gtag('event', 'click', { event_category: category, event_label: action });
    }

    // Utility method for showing notifications
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '1000',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });

        // Set background color based on type
        const colors = {
            info: '#3498db',
            success: '#2ecc71',
            warning: '#f39c12',
            error: '#e74c3c'
        };
        notification.style.backgroundColor = colors[type] || colors.info;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Branch selection functionality
function selectBranch(branchId, branchName) {
    // Update active state visually
    document.querySelectorAll('.branch-card').forEach(card => {
        card.classList.remove('active');
    });
    
    const selectedCard = document.querySelector(`[data-branch-id="${branchId}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
    }
    
    // Store selected branch in session storage
    sessionStorage.setItem('selectedBranch', JSON.stringify({
        id: branchId,
        name: branchName
    }));
    
    // Show notification
    showBranchNotification(`Umechagua tawi: ${branchName}`, 'success');
    
    // Reload page with branch parameter or update content dynamically
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('branch', branchId);
    window.location.href = currentUrl.toString();
}

// Show branch selection notification
function showBranchNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `branch-notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">✓</span>
            <span class="notification-message">${message}</span>
        </div>
    `;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '8px',
        backgroundColor: '#2ecc71',
        color: 'white',
        fontWeight: '500',
        zIndex: '1000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
    });

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new HomePage();
    
    // Restore selected branch from session storage
    const selectedBranch = sessionStorage.getItem('selectedBranch');
    if (selectedBranch) {
        try {
            const branch = JSON.parse(selectedBranch);
            const branchCard = document.querySelector(`[data-branch-id="${branch.id}"]`);
            if (branchCard && !branchCard.classList.contains('active')) {
                branchCard.classList.add('active');
            }
        } catch (e) {
            console.warn('Could not restore selected branch:', e);
        }
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Refresh statistics when page becomes visible
        const homePage = new HomePage();
        homePage.loadStatistics();
    }
});

// Add CSS for screen reader only content
const style = document.createElement('style');
style.textContent = `
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
`;
document.head.appendChild(style);
