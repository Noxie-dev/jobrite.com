/**
 * MoneyRite Error Handling and DOM Validation System
 * Provides robust error handling, logging, and DOM validation for MoneyRite tools
 */

// Enhanced Error Handler Class
class MoneyRiteErrorHandler {
    static logError(context, error, additionalInfo = {}) {
        const errorEntry = {
            timestamp: new Date().toISOString(),
            context: context,
            error: {
                name: error.name,
                message: error.message,
                stack: error.stack
            },
            userAgent: navigator.userAgent,
            url: window.location.href,
            additionalInfo: additionalInfo
        };

        // Log to console with detailed information
        console.group(`🚨 MoneyRite Error: ${context}`);
        console.error('Error Details:', errorEntry);
        console.error('Original Error:', error);
        if (Object.keys(additionalInfo).length > 0) {
            console.info('Additional Info:', additionalInfo);
        }
        console.groupEnd();

        // Store error for debugging (optional)
        try {
            const errors = JSON.parse(localStorage.getItem('moneyrite_errors') || '[]');
            errors.push(errorEntry);
            // Keep only last 10 errors to prevent storage bloat
            if (errors.length > 10) {
                errors.splice(0, errors.length - 10);
            }
            localStorage.setItem('moneyrite_errors', JSON.stringify(errors));
        } catch (storageError) {
            console.warn('Failed to store error log:', storageError);
        }

        return errorEntry;
    }

    static handleModalError(toolName, error) {
        this.logError(`Modal Error - ${toolName}`, error, { toolName });
        
        // Create fallback modal
        return this.createFallbackModal(toolName, error);
    }

    static validateDOMReady() {
        return document.readyState === 'complete' || document.readyState === 'interactive';
    }

    static createFallbackModal(toolName, error) {
        const fallbackContent = `
            <div class="fallback-modal" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="color: #dc2626; margin-bottom: 1rem;">Financial Tool Temporarily Unavailable</h3>
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    We're experiencing technical difficulties with the ${toolName}.
                </p>
                <p style="color: #6b7280; margin-bottom: 2rem;">
                    Please try refreshing the page or contact support if the issue persists.
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button onclick="location.reload()" 
                            style="background: #3b82f6; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.5rem; cursor: pointer;">
                        Refresh Page
                    </button>
                    <button onclick="modalManager.closeModal()" 
                            style="background: #6b7280; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.5rem; cursor: pointer;">
                        Close
                    </button>
                </div>
                <details style="margin-top: 2rem; text-align: left;">
                    <summary style="cursor: pointer; color: #6b7280;">Technical Details (for developers)</summary>
                    <pre style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; margin-top: 0.5rem; font-size: 0.8rem; overflow: auto;">
Error: ${error.message}
Context: ${toolName}
Time: ${new Date().toLocaleString()}
                    </pre>
                </details>
            </div>
        `;
        
        return fallbackContent;
    }

    static async waitForCondition(condition, timeout = 5000, interval = 100) {
        const startTime = Date.now();
        
        return new Promise((resolve, reject) => {
            const check = () => {
                try {
                    if (condition()) {
                        resolve(true);
                        return;
                    }
                    
                    if (Date.now() - startTime >= timeout) {
                        reject(new Error(`Condition timeout after ${timeout}ms`));
                        return;
                    }
                    
                    setTimeout(check, interval);
                } catch (error) {
                    reject(error);
                }
            };
            
            check();
        });
    }
}

// DOM Validator Class
class DOMValidator {
    static isReady() {
        return document.readyState === 'complete' || document.readyState === 'interactive';
    }

    static async waitForElement(selector, timeout = 5000) {
        if (document.querySelector(selector)) {
            return document.querySelector(selector);
        }

        return MoneyRiteErrorHandler.waitForCondition(
            () => document.querySelector(selector),
            timeout
        ).then(() => document.querySelector(selector));
    }

    static validateModalContainer() {
        const container = document.getElementById('moneyrite-modal-container');
        if (!container) {
            throw new Error('Modal container not found. MoneyRite modal system may not be initialized.');
        }
        return container;
    }

    static ensureStylesLoaded() {
        const moneyRiteStyles = document.querySelector('link[href*="moneyrite-tools.css"]');
        if (!moneyRiteStyles) {
            console.warn('MoneyRite styles may not be loaded');
            return false;
        }
        
        // Check if styles are actually loaded
        if (moneyRiteStyles.sheet) {
            try {
                // Try to access the stylesheet rules to ensure it's loaded
                const rules = moneyRiteStyles.sheet.cssRules || moneyRiteStyles.sheet.rules;
                if (rules && rules.length > 0) {
                    return true;
                }
            } catch (e) {
                // Cross-origin stylesheets may throw errors, but that's okay
                return true;
            }
        }
        
        return false;
    }

    static async waitForStylesLoaded(timeout = 5000) {
        return MoneyRiteErrorHandler.waitForCondition(
            () => this.ensureStylesLoaded(),
            timeout
        );
    }

    static validateScriptsLoaded() {
        const requiredScripts = [
            'MoneyRiteTools',
            'MoneyRiteErrorHandler',
            'safeCardClick'
        ];
        
        const missing = requiredScripts.filter(script => !window[script]);
        
        if (missing.length > 0) {
            throw new Error(`Required scripts not loaded: ${missing.join(', ')}`);
        }
        
        return true;
    }

    static async waitForScriptsLoaded(timeout = 5000) {
        return MoneyRiteErrorHandler.waitForCondition(
            () => {
                try {
                    this.validateScriptsLoaded();
                    return true;
                } catch (e) {
                    return false;
                }
            },
            timeout
        );
    }

    static validateRequiredElements(selectors) {
        const missing = [];
        const found = {};

        selectors.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                found[selector] = element;
            } else {
                missing.push(selector);
            }
        });

        if (missing.length > 0) {
            throw new Error(`Required elements not found: ${missing.join(', ')}`);
        }

        return found;
    }

    static validateMoneyRiteSetup() {
        const errors = [];
        const warnings = [];

        // Check DOM readiness
        if (!this.isReady()) {
            errors.push('DOM not ready');
        }

        // Check required scripts
        try {
            this.validateScriptsLoaded();
        } catch (error) {
            errors.push(`Scripts: ${error.message}`);
        }

        // Check styles
        if (!this.ensureStylesLoaded()) {
            warnings.push('MoneyRite styles may not be fully loaded');
        }

        // Check modal container
        try {
            this.validateModalContainer();
        } catch (error) {
            errors.push(`Modal container: ${error.message}`);
        }

        // Check required DOM elements
        const requiredSelectors = [
            '#moneyrite-modal-container',
            '.modal-backdrop',
            '.modal-content',
            '.modal-header',
            '.modal-body'
        ];

        try {
            this.validateRequiredElements(requiredSelectors);
        } catch (error) {
            errors.push(`DOM elements: ${error.message}`);
        }

        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }

    static async waitForMoneyRiteReady(timeout = 5000) {
        return MoneyRiteErrorHandler.waitForCondition(
            () => {
                const validation = this.validateMoneyRiteSetup();
                return validation.isValid;
            },
            timeout
        );
    }

    static validateMoneyRiteSetup() {
        const validationResults = {
            domReady: this.isReady(),
            stylesLoaded: this.ensureStylesLoaded(),
            modalContainer: false,
            moneyRiteTools: false,
            modalManager: false,
            errors: []
        };

        try {
            // Check modal container
            this.validateModalContainer();
            validationResults.modalContainer = true;
        } catch (error) {
            validationResults.errors.push(`Modal container: ${error.message}`);
        }

        try {
            // Check MoneyRiteTools
            if (window.MoneyRiteTools) {
                validationResults.moneyRiteTools = true;
                
                // Check modal manager
                if (window.MoneyRiteTools.modalManager) {
                    validationResults.modalManager = true;
                } else {
                    validationResults.errors.push('Modal manager not initialized');
                }
            } else {
                validationResults.errors.push('MoneyRiteTools not available');
            }
        } catch (error) {
            validationResults.errors.push(`MoneyRiteTools validation: ${error.message}`);
        }

        return validationResults;
    }

    static async waitForMoneyRiteReady(timeout = 10000) {
        const startTime = Date.now();
        
        return new Promise((resolve, reject) => {
            const check = () => {
                try {
                    const validation = this.validateMoneyRiteSetup();
                    
                    if (validation.domReady && 
                        validation.modalContainer && 
                        validation.moneyRiteTools && 
                        validation.modalManager) {
                        resolve(validation);
                        return;
                    }
                    
                    if (Date.now() - startTime >= timeout) {
                        reject(new Error(`MoneyRite setup timeout after ${timeout}ms. Issues: ${validation.errors.join(', ')}`));
                        return;
                    }
                    
                    setTimeout(check, 100);
                } catch (error) {
                    reject(error);
                }
            };
            
            check();
        });
    }

    static validateFormElements(formId, requiredFields = []) {
        const form = document.getElementById(formId);
        if (!form) {
            throw new Error(`Form not found: ${formId}`);
        }

        const missing = [];
        const found = {};

        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                found[fieldId] = field;
            } else {
                missing.push(fieldId);
            }
        });

        if (missing.length > 0) {
            throw new Error(`Required form fields not found in ${formId}: ${missing.join(', ')}`);
        }

        return { form, fields: found };
    }

    static checkElementVisibility(element) {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);
        
        return (
            rect.width > 0 &&
            rect.height > 0 &&
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            style.opacity !== '0'
        );
    }

    static validateAccessibility(element) {
        const issues = [];
        
        if (!element) {
            issues.push('Element does not exist');
            return issues;
        }

        // Check for proper ARIA attributes
        if (element.getAttribute('role') === 'button' && !element.hasAttribute('aria-label')) {
            issues.push('Button missing aria-label');
        }

        // Check for keyboard accessibility
        if (element.onclick && element.tabIndex < 0) {
            issues.push('Clickable element not keyboard accessible');
        }

        // Check color contrast (basic check)
        const style = window.getComputedStyle(element);
        if (style.color === style.backgroundColor) {
            issues.push('Poor color contrast detected');
        }

        return issues;
    }

    static validateScriptsLoaded() {
        const requiredScripts = [
            'MoneyRiteTools',
            'MoneyRiteErrorHandler',
            'DOMValidator'
        ];

        const missing = requiredScripts.filter(script => !window[script]);
        
        if (missing.length > 0) {
            throw new Error(`Required scripts not loaded: ${missing.join(', ')}`);
        }

        return true;
    }

    static validateModalStructure() {
        const container = document.getElementById('moneyrite-modal-container');
        if (!container) {
            throw new Error('Modal container not found');
        }

        const requiredElements = [
            '.modal-backdrop',
            '.modal-content',
            '.modal-header',
            '.modal-title',
            '.modal-close',
            '.modal-body'
        ];

        const missing = requiredElements.filter(selector => !container.querySelector(selector));
        
        if (missing.length > 0) {
            throw new Error(`Modal structure incomplete. Missing: ${missing.join(', ')}`);
        }

        return container;
    }

    static async waitForScriptsReady(timeout = 10000) {
        const startTime = Date.now();
        
        return new Promise((resolve, reject) => {
            const checkScripts = () => {
                try {
                    if (window.MoneyRiteTools && 
                        window.MoneyRiteTools.modalManager && 
                        window.MoneyRiteErrorHandler) {
                        resolve(true);
                        return;
                    }
                    
                    if (Date.now() - startTime >= timeout) {
                        reject(new Error(`Scripts not ready after ${timeout}ms`));
                        return;
                    }
                    
                    setTimeout(checkScripts, 50);
                } catch (error) {
                    reject(error);
                }
            };
            
            checkScripts();
        });
    }

    static validateFormElements(formId) {
        const form = document.getElementById(formId);
        if (!form) {
            throw new Error(`Form not found: ${formId}`);
        }

        const inputs = form.querySelectorAll('input, select, textarea');
        const invalidElements = [];

        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) {
                invalidElements.push(input.id || input.name || 'unnamed input');
            }
        });

        if (invalidElements.length > 0) {
            throw new Error(`Required form fields are empty: ${invalidElements.join(', ')}`);
        }

        return { form, inputs: Array.from(inputs) };
    }

    static checkBrowserCompatibility() {
        const features = {
            localStorage: typeof Storage !== 'undefined',
            fetch: typeof fetch !== 'undefined',
            promises: typeof Promise !== 'undefined',
            arrow_functions: (() => { try { eval('() => {}'); return true; } catch(e) { return false; } })(),
            const_let: (() => { try { eval('const x = 1; let y = 2;'); return true; } catch(e) { return false; } })()
        };

        const unsupported = Object.entries(features)
            .filter(([feature, supported]) => !supported)
            .map(([feature]) => feature);

        if (unsupported.length > 0) {
            console.warn('Browser compatibility issues:', unsupported);
            return { compatible: false, unsupported };
        }

        return { compatible: true, unsupported: [] };
    }
}

// Safe wrapper function for card clicks
function safeCardClick(toolName, handlerFunction) {
    return async function(event) {
        const startTime = performance.now();
        
        try {
            // Prevent default behavior and event bubbling
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }

            // Log click attempt
            console.log(`🎯 MoneyRite: ${toolName} card clicked`);

            // Comprehensive MoneyRite setup validation
            console.log('🔍 Validating MoneyRite setup...');
            await DOMValidator.waitForMoneyRiteReady(5000);
            
            const validation = DOMValidator.validateMoneyRiteSetup();
            if (validation.errors.length > 0) {
                throw new Error(`Setup validation failed: ${validation.errors.join(', ')}`);
            }
            
            console.log('✅ MoneyRite setup validation passed');

            // Execute the handler function with error boundary
            await handlerFunction();

            // Log successful execution
            const executionTime = performance.now() - startTime;
            console.log(`✅ MoneyRite: ${toolName} opened successfully in ${executionTime.toFixed(2)}ms`);

            // Check if execution time meets performance requirements (<500ms)
            if (executionTime > 500) {
                console.warn(`⚠️ Performance: ${toolName} took ${executionTime.toFixed(2)}ms (target: <500ms)`);
            }

        } catch (error) {
            const executionTime = performance.now() - startTime;
            
            MoneyRiteErrorHandler.logError(`Card Click - ${toolName}`, error, {
                toolName,
                executionTime: executionTime.toFixed(2),
                eventType: event ? event.type : 'unknown'
            });

            // Try to show fallback modal
            try {
                if (window.MoneyRiteTools && window.MoneyRiteTools.modalManager) {
                    const fallbackContent = MoneyRiteErrorHandler.createFallbackModal(toolName, error);
                    window.MoneyRiteTools.modalManager.openModal(
                        `${toolName} - Error`,
                        fallbackContent,
                        `${toolName.toLowerCase()}-error`
                    );
                } else {
                    // Last resort: show alert
                    alert(`Sorry, the ${toolName} is temporarily unavailable. Please refresh the page and try again.`);
                }
            } catch (fallbackError) {
                MoneyRiteErrorHandler.logError('Fallback Modal Creation', fallbackError);
                alert(`Sorry, there was an error opening the ${toolName}. Please refresh the page.`);
            }
        }
    };
}

// Performance monitoring utilities
class PerformanceMonitor {
    static timers = new Map();

    static startTimer(name) {
        this.timers.set(name, performance.now());
    }

    static endTimer(name) {
        const startTime = this.timers.get(name);
        if (startTime) {
            const duration = performance.now() - startTime;
            this.timers.delete(name);
            console.log(`⏱️ ${name}: ${duration.toFixed(2)}ms`);
            return duration;
        }
        return null;
    }

    static measureFunction(name, fn) {
        return async function(...args) {
            PerformanceMonitor.startTimer(name);
            try {
                const result = await fn.apply(this, args);
                PerformanceMonitor.endTimer(name);
                return result;
            } catch (error) {
                PerformanceMonitor.endTimer(name);
                throw error;
            }
        };
    }
}

// Debounce utility to prevent rapid clicking
function debounce(func, wait) {
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

// Export utilities to global scope
window.MoneyRiteErrorHandler = MoneyRiteErrorHandler;
window.DOMValidator = DOMValidator;
window.safeCardClick = safeCardClick;
window.PerformanceMonitor = PerformanceMonitor;
window.debounce = debounce;

// Initialize error handling on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 MoneyRite Error Handler initialized');
    
    // Validate initial setup
    try {
        DOMValidator.ensureStylesLoaded();
        console.log('✅ MoneyRite styles validation passed');
    } catch (error) {
        MoneyRiteErrorHandler.logError('Initial Setup Validation', error);
    }
});
// M
obile and Accessibility Enhancements
class MobileAccessibilityManager {
    static init() {
        this.setupTouchHandlers();
        this.setupKeyboardNavigation();
        this.setupFocusManagement();
        this.setupScreenReaderSupport();
        this.setupViewportHandling();
        console.log('🔧 Mobile & Accessibility Manager initialized');
    }

    static setupTouchHandlers() {
        // Add touch feedback to MoneyRite cards
        const cards = document.querySelectorAll('[data-tool]');
        
        cards.forEach(card => {
            // Touch start - add loading state
            card.addEventListener('touchstart', function(e) {
                this.classList.add('loading');
                
                // Haptic feedback if available
                if (navigator.vibrate) {
                    navigator.vibrate(50);
                }
            }, { passive: true });
            
            // Touch end - remove loading state
            card.addEventListener('touchend', function(e) {
                setTimeout(() => {
                    this.classList.remove('loading');
                }, 100);
            }, { passive: true });
            
            // Touch cancel - cleanup
            card.addEventListener('touchcancel', function(e) {
                this.classList.remove('loading');
            }, { passive: true });
        });
    }

    static setupKeyboardNavigation() {
        // Enhanced keyboard navigation for cards
        const cards = document.querySelectorAll('[data-tool]');
        
        cards.forEach((card, index) => {
            card.addEventListener('keydown', function(e) {
                switch(e.key) {
                    case 'Enter':
                    case ' ':
                        e.preventDefault();
                        this.click();
                        break;
                    case 'ArrowRight':
                    case 'ArrowDown':
                        e.preventDefault();
                        const nextCard = cards[index + 1] || cards[0];
                        nextCard.focus();
                        break;
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        e.preventDefault();
                        const prevCard = cards[index - 1] || cards[cards.length - 1];
                        prevCard.focus();
                        break;
                    case 'Home':
                        e.preventDefault();
                        cards[0].focus();
                        break;
                    case 'End':
                        e.preventDefault();
                        cards[cards.length - 1].focus();
                        break;
                }
            });
        });
    }

    static setupFocusManagement() {
        // Focus trap for modals
        document.addEventListener('keydown', function(e) {
            const modal = document.querySelector('.moneyrite-modal-container[style*="flex"]');
            if (!modal) return;
            
            if (e.key === 'Tab') {
                const focusableElements = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                
                const firstFocusable = focusableElements[0];
                const lastFocusable = focusableElements[focusableElements.length - 1];
                
                if (e.shiftKey) {
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
        });
    }

    static setupScreenReaderSupport() {
        // Announce modal state changes
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.id = 'moneyrite-announcer';
        document.body.appendChild(announcer);
        
        // Announce when modals open/close
        const originalOpenModal = window.MoneyRiteTools?.modalManager?.openModal;
        if (originalOpenModal) {
            window.MoneyRiteTools.modalManager.openModal = function(title, content, toolName) {
                const result = originalOpenModal.call(this, title, content, toolName);
                announcer.textContent = `${title} dialog opened`;
                return result;
            };
        }
        
        const originalCloseModal = window.MoneyRiteTools?.modalManager?.closeModal;
        if (originalCloseModal) {
            window.MoneyRiteTools.modalManager.closeModal = function() {
                const result = originalCloseModal.call(this);
                announcer.textContent = 'Dialog closed';
                return result;
            };
        }
    }

    static setupViewportHandling() {
        // Handle viewport changes (orientation, resize)
        let resizeTimeout;
        
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                MobileAccessibilityManager.adjustModalForViewport();
            }, 250);
        });
        
        window.addEventListener('orientationchange', function() {
            setTimeout(() => {
                MobileAccessibilityManager.adjustModalForViewport();
            }, 100);
        });
    }

    static adjustModalForViewport() {
        const modal = document.querySelector('.moneyrite-modal-container[style*="flex"]');
        if (!modal) return;
        
        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) return;
        
        // Adjust modal height for mobile keyboards
        if (window.innerWidth <= 768) {
            const viewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
            modalContent.style.maxHeight = `${viewportHeight - 40}px`;
        }
    }

    static preventBackgroundScroll(prevent = true) {
        if (prevent) {
            // Store current scroll position
            const scrollY = window.scrollY;
            document.body.style.position = 'fixed';
            document.body.style.top = `-${scrollY}px`;
            document.body.style.width = '100%';
            document.body.classList.add('modal-open');
        } else {
            // Restore scroll position
            const scrollY = document.body.style.top;
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
            document.body.classList.remove('modal-open');
            
            if (scrollY) {
                window.scrollTo(0, parseInt(scrollY || '0') * -1);
            }
        }
    }

    static addLoadingState(element, toolName) {
        if (!element) return;
        
        element.classList.add('loading');
        element.setAttribute('aria-busy', 'true');
        element.setAttribute('aria-label', `Loading ${toolName}...`);
        
        // Add loading announcement for screen readers
        const announcer = document.getElementById('moneyrite-announcer');
        if (announcer) {
            announcer.textContent = `Loading ${toolName}...`;
        }
    }

    static removeLoadingState(element, originalLabel) {
        if (!element) return;
        
        element.classList.remove('loading');
        element.setAttribute('aria-busy', 'false');
        if (originalLabel) {
            element.setAttribute('aria-label', originalLabel);
        }
    }

    static addErrorState(element, error) {
        if (!element) return;
        
        element.classList.add('error');
        element.setAttribute('aria-invalid', 'true');
        element.setAttribute('aria-describedby', 'error-message');
        
        // Create error message for screen readers
        let errorMsg = document.getElementById('error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('div');
            errorMsg.id = 'error-message';
            errorMsg.className = 'sr-only';
            document.body.appendChild(errorMsg);
        }
        errorMsg.textContent = `Error: ${error.message}`;
    }

    static addSuccessState(element, message) {
        if (!element) return;
        
        element.classList.add('success');
        
        // Announce success
        const announcer = document.getElementById('moneyrite-announcer');
        if (announcer) {
            announcer.textContent = message || 'Operation completed successfully';
        }
    }
}

// Initialize mobile and accessibility features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        MobileAccessibilityManager.init();
    }, 500);
});

// Export for global access
window.MobileAccessibilityManager = MobileAccessibilityManager;//
 Responsive Modal Handler
class ResponsiveModalHandler {
    static init() {
        this.setupResponsiveBreakpoints();
        this.setupDynamicSizing();
        this.setupOrientationHandling();
        console.log('📱 Responsive Modal Handler initialized');
    }

    static setupResponsiveBreakpoints() {
        // Define breakpoints
        this.breakpoints = {
            mobile: 768,
            tablet: 1024,
            desktop: 1200
        };
        
        // Current device type
        this.currentDevice = this.getDeviceType();
        
        // Listen for resize events
        window.addEventListener('resize', debounce(() => {
            const newDevice = this.getDeviceType();
            if (newDevice !== this.currentDevice) {
                this.currentDevice = newDevice;
                this.handleDeviceChange();
            }
            this.adjustModalSize();
        }, 250));
    }

    static getDeviceType() {
        const width = window.innerWidth;
        if (width < this.breakpoints.mobile) return 'mobile';
        if (width < this.breakpoints.tablet) return 'tablet';
        return 'desktop';
    }

    static handleDeviceChange() {
        const modal = document.querySelector('.moneyrite-modal-container[style*="flex"]');
        if (!modal) return;
        
        console.log(`📱 Device changed to: ${this.currentDevice}`);
        this.adjustModalForDevice(modal);
    }

    static adjustModalForDevice(modal) {
        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) return;
        
        // Remove existing device classes
        modalContent.classList.remove('modal-mobile', 'modal-tablet', 'modal-desktop');
        
        // Add current device class
        modalContent.classList.add(`modal-${this.currentDevice}`);
        
        // Apply device-specific adjustments
        switch (this.currentDevice) {
            case 'mobile':
                this.applyMobileLayout(modalContent);
                break;
            case 'tablet':
                this.applyTabletLayout(modalContent);
                break;
            case 'desktop':
                this.applyDesktopLayout(modalContent);
                break;
        }
    }

    static applyMobileLayout(modalContent) {
        modalContent.style.width = '100%';
        modalContent.style.height = 'auto';
        modalContent.style.maxHeight = 'calc(100vh - 2rem)';
        modalContent.style.margin = '1rem';
        modalContent.style.borderRadius = '1rem 1rem 0 0';
        
        // Adjust form elements for mobile
        const inputs = modalContent.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.style.fontSize = '16px'; // Prevent zoom on iOS
            input.style.minHeight = '44px'; // Touch-friendly
        });
    }

    static applyTabletLayout(modalContent) {
        modalContent.style.width = '90%';
        modalContent.style.maxWidth = '600px';
        modalContent.style.height = 'auto';
        modalContent.style.maxHeight = 'calc(100vh - 4rem)';
        modalContent.style.margin = '2rem auto';
        modalContent.style.borderRadius = '1rem';
    }

    static applyDesktopLayout(modalContent) {
        modalContent.style.width = 'auto';
        modalContent.style.maxWidth = '800px';
        modalContent.style.height = 'auto';
        modalContent.style.maxHeight = 'calc(100vh - 6rem)';
        modalContent.style.margin = '3rem auto';
        modalContent.style.borderRadius = '1.5rem';
    }

    static setupDynamicSizing() {
        // Adjust modal size based on content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    const modal = document.querySelector('.moneyrite-modal-container[style*="flex"]');
                    if (modal) {
                        this.adjustModalSize();
                    }
                }
            });
        });

        // Observe modal content changes
        const modalContainer = document.getElementById('moneyrite-modal-container');
        if (modalContainer) {
            observer.observe(modalContainer, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }
    }

    static adjustModalSize() {
        const modal = document.querySelector('.moneyrite-modal-container[style*="flex"]');
        if (!modal) return;
        
        const modalContent = modal.querySelector('.modal-content');
        const modalBody = modal.querySelector('.modal-body');
        
        if (!modalContent || !modalBody) return;
        
        // Calculate available space
        const viewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Adjust for mobile keyboard
        if (this.currentDevice === 'mobile' && window.visualViewport) {
            const keyboardHeight = window.innerHeight - window.visualViewport.height;
            if (keyboardHeight > 150) { // Keyboard is likely open
                modalContent.style.maxHeight = `${viewportHeight - 20}px`;
                modalBody.style.maxHeight = `${viewportHeight - 120}px`;
            }
        }
        
        // Ensure modal doesn't exceed viewport
        const modalRect = modalContent.getBoundingClientRect();
        if (modalRect.height > viewportHeight * 0.9) {
            modalContent.style.height = `${viewportHeight * 0.9}px`;
            modalBody.style.overflowY = 'auto';
        }
        
        if (modalRect.width > viewportWidth * 0.95) {
            modalContent.style.width = `${viewportWidth * 0.95}px`;
        }
    }

    static setupOrientationHandling() {
        // Handle orientation changes
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                console.log('📱 Orientation changed');
                this.handleOrientationChange();
            }, 100);
        });
        
        // Also listen for resize events that might indicate orientation change
        let lastOrientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
        
        window.addEventListener('resize', debounce(() => {
            const currentOrientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
            if (currentOrientation !== lastOrientation) {
                lastOrientation = currentOrientation;
                this.handleOrientationChange();
            }
        }, 300));
    }

    static handleOrientationChange() {
        const modal = document.querySelector('.moneyrite-modal-container[style*="flex"]');
        if (!modal) return;
        
        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) return;
        
        // Reset styles to allow recalculation
        modalContent.style.height = 'auto';
        modalContent.style.maxHeight = '';
        
        // Reapply device-specific layout
        setTimeout(() => {
            this.adjustModalForDevice(modal);
            this.adjustModalSize();
        }, 50);
    }

    static getOptimalModalSize(contentHeight, contentWidth) {
        const viewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        let optimalHeight, optimalWidth;
        
        switch (this.currentDevice) {
            case 'mobile':
                optimalHeight = Math.min(contentHeight, viewportHeight * 0.9);
                optimalWidth = Math.min(contentWidth, viewportWidth * 0.95);
                break;
            case 'tablet':
                optimalHeight = Math.min(contentHeight, viewportHeight * 0.85);
                optimalWidth = Math.min(contentWidth, Math.min(600, viewportWidth * 0.9));
                break;
            case 'desktop':
                optimalHeight = Math.min(contentHeight, viewportHeight * 0.8);
                optimalWidth = Math.min(contentWidth, Math.min(800, viewportWidth * 0.8));
                break;
        }
        
        return { height: optimalHeight, width: optimalWidth };
    }
}

// Initialize responsive modal handling
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        ResponsiveModalHandler.init();
    }, 600);
});

// Export for global access
window.ResponsiveModalHandler = ResponsiveModalHandler;