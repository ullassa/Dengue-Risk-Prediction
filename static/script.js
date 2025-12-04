// Custom JavaScript for Dengue Risk Prediction System

// Global variables
let currentModule = '';
let loadingState = false;

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    // Clear any existing error messages first
    clearErrorMessages();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize accessibility features
    initializeAccessibility();
    
    // Check current page and initialize specific features
    detectCurrentPage();
    
    console.log('Dengue Risk Prediction System initialized');
}

// Clear error messages
function clearErrorMessages() {
    const alerts = document.querySelectorAll('.alert-danger');
    alerts.forEach(alert => {
        if (alert.textContent.includes('unexpected error')) {
            alert.remove();
        }
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize form validation
function initializeFormValidation() {
    // Custom validation for all forms
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            } else {
                // Show loading state
                showLoadingState(form);
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for specific fields
    const cityInput = document.getElementById('city');
    if (cityInput) {
        cityInput.addEventListener('input', function() {
            validateCityInput(this);
        });
    }
    
    const locationInput = document.getElementById('location');
    if (locationInput) {
        locationInput.addEventListener('input', function() {
            validateLocationInput(this);
        });
    }
}

// Initialize animations
function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Initialize accessibility features
function initializeAccessibility() {
    // Add keyboard navigation for cards
    const clickableCards = document.querySelectorAll('.card[data-href]');
    clickableCards.forEach(card => {
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                window.location.href = this.getAttribute('data-href');
            }
        });
    });
    
    // Enhance form labels
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        const label = document.querySelector(`label[for="${control.id}"]`);
        if (label && !control.getAttribute('aria-describedby')) {
            // Add aria-describedby for better screen reader support
            const helpText = control.parentNode.querySelector('.form-text');
            if (helpText) {
                const helpId = `${control.id}-help`;
                helpText.id = helpId;
                control.setAttribute('aria-describedby', helpId);
            }
        }
    });
}

// Detect current page and initialize specific features
function detectCurrentPage() {
    const path = window.location.pathname;
    
    if (path.includes('weather-prediction')) {
        currentModule = 'weather';
        initializeWeatherPage();
    } else if (path.includes('symptom-checker')) {
        currentModule = 'symptoms';
        initializeSymptomPage();
    } else if (path.includes('local-alert')) {
        currentModule = 'local';
        initializeLocalAlertPage();
    } else if (path.includes('risk-calculator')) {
        currentModule = 'risk';
        initializeRiskCalculatorPage();
    } else if (path.includes('visualization')) {
        currentModule = 'visualization';
        initializeVisualizationPage();
    } else if (path.includes('prevention')) {
        currentModule = 'prevention';
        initializePreventionPage();
    } else {
        currentModule = 'dashboard';
        initializeDashboard();
    }
}

// Weather prediction page specific initialization
function initializeWeatherPage() {
    const cityInput = document.getElementById('city');
    if (cityInput) {
        // Add city suggestions (basic implementation)
        const commonCities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad'];
        
        cityInput.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            if (value.length > 1) {
                showCitySuggestions(value, commonCities);
            }
        });
    }
}

// Symptom checker page specific initialization
function initializeSymptomPage() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateSymptomCount();
            
            // Special handling for warning signs
            if (this.name === 'bleeding' && this.checked) {
                showWarningAlert();
            }
        });
    });
}

// Local alert page specific initialization
function initializeLocalAlertPage() {
    const locationInput = document.getElementById('location');
    if (locationInput) {
        // Add location suggestions
        const commonLocations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'];
        
        locationInput.addEventListener('input', function() {
            const value = this.value.toLowerCase();
            if (value.length > 1) {
                showLocationSuggestions(value, commonLocations);
            }
        });
    }
}

// Risk calculator page specific initialization
function initializeRiskCalculatorPage() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    let currentScore = 0;
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateRiskScore();
        });
    });
    
    function updateRiskScore() {
        currentScore = 0;
        const riskWeights = {
            'stagnant_water': 3,
            'mosquito_increase': 2,
            'recent_travel': 2,
            'sick_contacts': 2,
            'poor_drainage': 2,
            'water_storage': 2,
            'garden_plants': 1,
            'construction_nearby': 1,
            'ac_cooler': 1,
            'garbage_collection': 1
        };
        
        checkboxes.forEach(checkbox => {
            if (checkbox.checked && riskWeights[checkbox.name]) {
                currentScore += riskWeights[checkbox.name];
            }
        });
        
        showLiveRiskScore(currentScore);
    }
}

// Visualization page specific initialization
function initializeVisualizationPage() {
    // Initialize any chart interactions or map features
    if (typeof L !== 'undefined') {
        // Leaflet map is available
        console.log('Map functionality ready');
    }
}

// Prevention page specific initialization
function initializePreventionPage() {
    // Add smooth scrolling to prevention sections
    const preventionLinks = document.querySelectorAll('a[href^="#prevention"]');
    preventionLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// Dashboard specific initialization
function initializeDashboard() {
    // Add hover effects to feature cards
    const featureCards = document.querySelectorAll('.card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
        });
    });
}

// Utility functions

// Show loading state on form submission
function showLoadingState(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        submitBtn.disabled = true;
        
        // Store original text for potential restoration
        submitBtn.setAttribute('data-original-text', originalText);
    }
}

// City input validation
function validateCityInput(input) {
    const value = input.value.trim();
    if (value.length < 2) {
        input.setCustomValidity('Please enter at least 2 characters');
    } else if (!/^[a-zA-Z\s]+$/.test(value)) {
        input.setCustomValidity('City name should only contain letters and spaces');
    } else {
        input.setCustomValidity('');
    }
}

// Location input validation
function validateLocationInput(input) {
    const value = input.value.trim();
    if (value.length < 2) {
        input.setCustomValidity('Please enter at least 2 characters');
    } else {
        input.setCustomValidity('');
    }
}

// Show city suggestions (basic implementation)
function showCitySuggestions(value, cities) {
    const suggestions = cities.filter(city => 
        city.toLowerCase().includes(value)
    );
    
    // This could be enhanced with a dropdown
    console.log('City suggestions:', suggestions);
}

// Show location suggestions
function showLocationSuggestions(value, locations) {
    const suggestions = locations.filter(location => 
        location.toLowerCase().includes(value)
    );
    
    console.log('Location suggestions:', suggestions);
}

// Update symptom count display
function updateSymptomCount() {
    const checkedSymptoms = document.querySelectorAll('input[type="checkbox"]:checked');
    const count = checkedSymptoms.length;
    
    // Could add a live counter display
    console.log(`Symptoms selected: ${count}`);
}

// Show warning alert for critical symptoms
function showWarningAlert() {
    if (!document.querySelector('.warning-alert')) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger warning-alert mt-3';
        alert.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Warning:</strong> Bleeding is a serious symptom. Please seek immediate medical attention.
        `;
        
        const form = document.querySelector('form');
        if (form) {
            form.appendChild(alert);
        }
    }
}

// Show live risk score
function showLiveRiskScore(score) {
    let existingDisplay = document.querySelector('.live-score-display');
    
    if (!existingDisplay) {
        existingDisplay = document.createElement('div');
        existingDisplay.className = 'live-score-display alert alert-info mt-3';
        
        const form = document.querySelector('form');
        if (form) {
            form.appendChild(existingDisplay);
        }
    }
    
    let riskLevel = 'Low';
    let colorClass = 'alert-success';
    
    if (score >= 12) {
        riskLevel = 'Very High';
        colorClass = 'alert-danger';
    } else if (score >= 8) {
        riskLevel = 'High';
        colorClass = 'alert-warning';
    } else if (score >= 5) {
        riskLevel = 'Medium';
        colorClass = 'alert-info';
    } else if (score >= 2) {
        riskLevel = 'Low-Medium';
        colorClass = 'alert-primary';
    }
    
    existingDisplay.className = `live-score-display alert ${colorClass} mt-3`;
    existingDisplay.innerHTML = `
        <i class="fas fa-calculator me-2"></i>
        <strong>Current Risk Score: ${score}</strong> - ${riskLevel} Risk Level
    `;
}

// Error handling
function showError(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    }
}

// Success message
function showSuccess(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Export data functionality (basic)
function exportData(data, filename) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = filename;
    link.click();
}

// Local storage functions
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Error saving to localStorage:', error);
        return false;
    }
}

function getFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return null;
    }
}

// Performance monitoring
function logPerformance(action) {
    if (typeof performance !== 'undefined') {
        console.log(`${action} completed in ${performance.now()}ms`);
    }
}

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    // Only show error for critical errors, not all errors
    if (event.error && event.error.message && !event.error.message.includes('ResizeObserver')) {
        console.log('JavaScript error detected:', event.error.message);
        // Comment out the automatic error display for debugging
        // showError('An unexpected error occurred. Please try again.');
    }
});

// Prevent form resubmission on page refresh
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

// Service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker registration would go here
        console.log('Service worker support detected');
    });
}

// Export functions for external use
window.DengueApp = {
    showError,
    showSuccess,
    printPage,
    exportData,
    saveToLocalStorage,
    getFromLocalStorage
};
