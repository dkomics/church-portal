// Admin Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard functionality
    initializeDashboard();
    
    // Auto-refresh statistics every 5 minutes
    setInterval(refreshStats, 300000);
    
    // Add smooth animations
    animateElements();
});

function initializeDashboard() {
    // Add click handlers for action cards
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Add loading state
            const icon = this.querySelector('.action-icon');
            icon.style.transform = 'rotate(360deg)';
            icon.style.transition = 'transform 0.5s ease';
            
            setTimeout(() => {
                icon.style.transform = 'rotate(0deg)';
            }, 500);
        });
    });
    
    // Add hover effects for stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Initialize role progress bars animation
    animateProgressBars();
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.role-progress');
    
    // Use Intersection Observer for animation on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const width = progressBar.style.width;
                progressBar.style.width = '0%';
                
                setTimeout(() => {
                    progressBar.style.width = width;
                }, 100);
            }
        });
    }, { threshold: 0.5 });
    
    progressBars.forEach(bar => observer.observe(bar));
}

function animateElements() {
    // Animate stat cards on load
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animate action cards
    const actionCards = document.querySelectorAll('.action-card');
    actionCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateX(0)';
        }, (index * 100) + 300);
    });
}

function refreshStats() {
    // Fetch updated statistics from the server
    fetch('/auth/api/dashboard-stats/')
        .then(response => response.json())
        .then(data => {
            updateStatCards(data);
            showRefreshNotification();
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
        });
}

function updateStatCards(data) {
    // Update stat numbers with animation
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach((element, index) => {
        const currentValue = parseInt(element.textContent);
        let newValue;
        
        switch(index) {
            case 0: newValue = data.total_users; break;
            case 1: newValue = data.active_users; break;
            case 2: newValue = data.role_stats.Administrator || 0; break;
            case 3: newValue = data.role_stats['Secretary/Clerk'] || 0; break;
            default: return;
        }
        
        if (currentValue !== newValue) {
            animateNumber(element, currentValue, newValue);
        }
    });
}

function animateNumber(element, start, end) {
    const duration = 1000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.round(start + (end - start) * progress);
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        }
    }
    
    requestAnimationFrame(updateNumber);
}

function showRefreshNotification() {
    // Create and show a subtle refresh notification
    const notification = document.createElement('div');
    notification.className = 'refresh-notification';
    notification.textContent = 'Takwimu zimesasishwa';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);
        z-index: 1000;
        opacity: 0;
        transform: translateX(100px);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Animate out and remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100px)';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + D for Dashboard
    if (e.altKey && e.key === 'd') {
        e.preventDefault();
        window.location.href = '/auth/admin-dashboard/';
    }
    
    // Alt + U for User Management
    if (e.altKey && e.key === 'u') {
        e.preventDefault();
        window.location.href = '/auth/user-management/';
    }
    
    // Alt + L for Audit Logs
    if (e.altKey && e.key === 'l') {
        e.preventDefault();
        window.location.href = '/auth/audit-logs/';
    }
    
    // Alt + H for Home
    if (e.altKey && e.key === 'h') {
        e.preventDefault();
        window.location.href = '/';
    }
});

// Add tooltips for keyboard shortcuts
function addKeyboardShortcutTooltips() {
    const shortcuts = [
        { selector: 'a[href="/auth/admin-dashboard/"]', shortcut: 'Alt + D' },
        { selector: 'a[href="/auth/user-management/"]', shortcut: 'Alt + U' },
        { selector: 'a[href="/auth/audit-logs/"]', shortcut: 'Alt + L' },
        { selector: 'a[href="/"]', shortcut: 'Alt + H' }
    ];
    
    shortcuts.forEach(({ selector, shortcut }) => {
        const element = document.querySelector(selector);
        if (element) {
            element.title = `${element.textContent.trim()} (${shortcut})`;
        }
    });
}

// Initialize tooltips when DOM is ready
document.addEventListener('DOMContentLoaded', addKeyboardShortcutTooltips);

// Handle responsive navigation on mobile
function initializeMobileNav() {
    const nav = document.querySelector('.dashboard-nav');
    let isCollapsed = false;
    
    if (window.innerWidth <= 768) {
        const toggleButton = document.createElement('button');
        toggleButton.className = 'nav-toggle';
        toggleButton.innerHTML = '☰';
        toggleButton.style.cssText = `
            background: none;
            border: none;
            font-size: 1.5rem;
            color: #2c3e50;
            cursor: pointer;
            padding: 0.5rem;
            margin-right: 1rem;
        `;
        
        nav.parentNode.insertBefore(toggleButton, nav);
        
        toggleButton.addEventListener('click', function() {
            isCollapsed = !isCollapsed;
            nav.style.display = isCollapsed ? 'none' : 'flex';
            this.innerHTML = isCollapsed ? '☰' : '✕';
        });
        
        // Initially collapse on mobile
        nav.style.display = 'none';
        isCollapsed = true;
    }
}

// Initialize mobile navigation
window.addEventListener('resize', initializeMobileNav);
document.addEventListener('DOMContentLoaded', initializeMobileNav);
