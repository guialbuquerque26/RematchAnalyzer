// Rematch Analyzer - Main JavaScript

// Loading System
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    const steps = ['step1', 'step2', 'step3', 'step4'];
    let currentStep = 0;
    
    overlay.style.display = 'flex';
    
    const interval = setInterval(() => {
        if (currentStep < steps.length - 1) {
            document.getElementById(steps[currentStep]).classList.remove('active');
            currentStep++;
            document.getElementById(steps[currentStep]).classList.add('active');
        } else {
            clearInterval(interval);
        }
    }, 1000);
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Common Animations
function initPageAnimations() {
    const elements = document.querySelectorAll('[data-animate="fadeInUp"]');
    
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 150);
    });
}

// Form Validation
function validateSteamURL(url) {
    return url.includes('steamcommunity.com') || url.match(/^\d{17}$/);
}

// Auto-hide flash messages
function initFlashMessages() {
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Rematch Analyzer loaded');
    
    // Initialize common features
    initPageAnimations();
    initFlashMessages();
    
    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoading();
        });
    });
    
    // Steam URL validation
    const steamInputs = document.querySelectorAll('input[name*="identifier"]');
    steamInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validateSteamURL(this.value)) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    });
});

// Utility functions
const Utils = {
    formatNumber: (num) => {
        return new Intl.NumberFormat('pt-BR').format(num);
    },
    
    formatPercentage: (num, decimals = 1) => {
        return `${num.toFixed(decimals)}%`;
    },
    
    debounce: (func, wait) => {
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
}; 