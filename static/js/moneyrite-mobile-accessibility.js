/**
 * MoneyRite Mobile and Accessibility Enhancements
 * Provides touch event handling, keyboard navigation, and accessibility features
 */

// Mobile and Touch Event Handler
class MobileAccessibilityManager {
    constructor() {
        this.touchStartTime = 0;
        this.touchStartPos = { x: 0, y: 0 };
        this.isTouch = false;
        this.focusedElement = null;
        this.init();
    }

    init() {
        this.detectTouchDevice();
        this.setupTouchEvents();
        this.setupKeyboardNavigation();
        this.setupAccessibilityFeatures();
        this.setupMobileModalHandling();
        console.log('🔧 Mobile & Accessibility Manager initialized');
    }

    detectTouchDevice() {
        this.isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        
        if (this.isTouch) {
            document.body.classList.add('touch-device');
            console.log('📱 Touch device detected');
        } else {
            document.body.classList.add('non-touch-device');
        }
    }

    setupTouchEvents() {
        // Add touch event handling for MoneyRite cards
        document.addEventListener('DOMContentLoaded', () => {
            const cards = document.querySelectorAll('[onclick*="safeCardClick"]');
            
            cards.forEach(card => {
                this.enhanceCardForTouch(card);
            });
        });
    }

    enhanceCardForTouch(card) {
        // Add touch feedback
        card.addEventListener('touchstart', (e) => {
            this.touchStartTime = Date.now();
            this.touchStartPos = {
                x: e.touches[0].clientX,
                y: e.touches[0].clientY
            };
            
            // Visual feedback
            card.style.transform = 'scale(0.98) translateY(-2px)';
            card.style.transition = 'transform 0.1s ease';
        }, { passive: true });

        card.addEventListener('touchend', (e) => {
            const touchEndTime = Date.now();
            const touchDuration = touchEndTime - this.touchStartTime;
            
            // Reset visual feedback
            setTimeout(() => {
                card.style.transform = '';
                card.style.transition = 'transform 0.3s ease';
            }, 100);
            
            // Prevent accidental taps (too short or too long)
            if (touchDuration < 50 || touchDuration > 2000) {
                e.preventDefault();
                return;
            }
            
            // Check if touch moved too much (might be scroll)
            if (e.changedTouches && e.changedTouches[0]) {
                const touchEndPos = {
                    x: e.changedTouches[0].clientX,
                    y: e.changedTouches[0].clientY
                };
                
                const distance = Math.sqrt(
                    Math.pow(touchEndPos.x - this.touchStartPos.x, 2) +
                    Math.pow(touchEndPos.y - this.touchStartPos.y, 2)
                );
                
                if (distance > 10) {
                    e.preventDefault();
                    return;
                }
            }
        }, { passive: false });

        card.addEventListener('touchcancel', () => {
            // Reset visual feedback on cancel
            card.style.transform = '';
            card.style.transition = 'transform 0.3s ease';
        });
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Handle Enter key on focused MoneyRite cards
            if (e.key === 'Enter' || e.key === ' ') {
                const focusedElement = document.activeElement;
                
                if (focusedElement && focusedElement.hasAttribute('onclick')) {
                    const onclickAttr = focusedElement.getAttribute('onclick');
                    
                    if (onclickAttr.includes('safeCardClick')) {
                        e.preventDefault();
                        
                        // Add visual feedback for keyboard activation
                        focusedElement.style.transform = 'scale(0.98)';
                        
                        setTimeout(() => {
                            focusedElement.style.transform = '';
                            // Execute the onclick handler
                            try {
                                eval(onclickAttr);
                            } catch (error) {
                                console.error('Keyboard activation error:', error);
                            }
                        }, 100);
                    }
                }
            }
            
            // Handle Escape key to close modals
            if (e.key === 'Escape') {
                if (window.MoneyRiteTools && window.MoneyRiteTools.modalManager) {
                    if (window.MoneyRiteTools.modalManager.modalState && 
                        window.MoneyRiteTools.modalManager.modalState.isOpen) {
                        window.MoneyRiteTools.modalManager.closeModal();
                    }
                }
            }
        });
    }

    setupAccessibilityFeatures() {
        // Add ARIA labels and roles to MoneyRite cards
        document.addEventListener('DOMContentLoaded', () => {
            const cards = document.querySelectorAll('[onclick*="safeCardClick"]');
            
            cards.forEach((card, index) => {
                // Make cards focusable
                if (!card.hasAttribute('tabindex')) {
                    card.setAttribute('tabindex', '0');
                }
                
                // Add ARIA role
                card.setAttribute('role', 'button');
                
                // Add ARIA label based on card content
                const title = card.querySelector('h3');
                if (title) {
                    card.setAttribute('aria-label', `Open ${title.textContent} financial tool`);
                }
                
                // Add keyboard focus styles
                card.addEventListener('focus', () => {
                    card.style.outline = '2px solid #3b82f6';
                    card.style.outlineOffset = '2px';
                });
                
                card.addEventListener('blur', () => {
                    card.style.outline = '';
                    card.style.outlineOffset = '';
                });
            });
        });
    }

    setupMobileModalHandling() {
        // Prevent background scrolling on mobile when modal is open
        const originalOpenModal = window.MoneyRiteTools?.modalManager?.openModal;
        
        if (originalOpenModal) {
            window.MoneyRiteTools.modalManager.openModal = function(title, content, toolName) {
                const result = originalOpenModal.call(this, title, content, toolName);
                
                // Mobile-specific modal handling
                if (window.innerWidth <= 768) {
                    document.body.style.position = 'fixed';
                    document.body.style.top = `-${window.scrollY}px`;
                    document.body.style.width = '100%';
                }
                
                return result;
            };
        }
        
        const originalCloseModal = window.MoneyRiteTools?.modalManager?.closeModal;
        
        if (originalCloseModal) {
            window.MoneyRiteTools.modalManager.closeModal = function() {
                const scrollY = document.body.style.top;
                
                const result = originalCloseModal.call(this);
                
                // Restore scroll position on mobile
                if (window.innerWidth <= 768) {
                    document.body.style.position = '';
                    document.body.style.top = '';
                    document.body.style.width = '';
                    
                    if (scrollY) {
                        window.scrollTo(0, parseInt(scrollY || '0') * -1);
                    }
                }
                
                return result;
            };
        }
    }

    // Focus management for modals
    manageFocusInModal(modalContainer) {
        const focusableElements = modalContainer.querySelectorAll(
            'input, button, select, textarea, [tabindex]:not([tabindex="-1"]), [href]'
        );
        
        if (focusableElements.length === 0) return;
        
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
        
        // Focus first element
        setTimeout(() => {
            firstFocusable.focus();
        }, 100);
        
        // Trap focus within modal
        modalContainer.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    // Shift + Tab
                    if (document.activeElement === firstFocusable) {
                        e.preventDefault();
                        lastFocusable.focus();
                    }
                } else {
                    // Tab
                    if (document.activeElement === lastFocusable) {
                        e.preventDefault();
                        firstFocusable.focus();
                    }
                }
            }
        });
    }

    // Add screen reader announcements
    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.style.position = 'absolute';
        announcement.style.left = '-10000px';
        announcement.style.width = '1px';
        announcement.style.height = '1px';
        announcement.style.overflow = 'hidden';
        
        document.body.appendChild(announcement);
        announcement.textContent = message;
        
        // Remove after announcement
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    // Handle viewport changes (orientation, resize)
    handleViewportChanges() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.adjustModalForViewport();
            }, 250);
        });
        
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.adjustModalForViewport();
            }, 500);
        });
    }

    adjustModalForViewport() {
        const modal = document.getElementById('moneyrite-modal-container');
        if (!modal || modal.style.display === 'none') return;
        
        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) return;
        
        // Adjust modal size for mobile
        if (window.innerWidth <= 768) {
            modalContent.style.maxHeight = '90vh';
            modalContent.style.margin = '1rem';
            modalContent.style.width = 'calc(100% - 2rem)';
        } else {
            modalContent.style.maxHeight = '';
            modalContent.style.margin = '';
            modalContent.style.width = '';
        }
    }

    // Add haptic feedback for supported devices
    addHapticFeedback(type = 'light') {
        if (navigator.vibrate) {
            const patterns = {
                light: [10],
                medium: [20],
                heavy: [30]
            };
            
            navigator.vibrate(patterns[type] || patterns.light);
        }
    }
}

// Initialize mobile and accessibility features
let mobileAccessibilityManager;

document.addEventListener('DOMContentLoaded', () => {
    mobileAccessibilityManager = new MobileAccessibilityManager();
});

// Export for global access
window.MobileAccessibilityManager = MobileAccessibilityManager;
//
 Responsive Modal Handler
class ResponsiveModalHandler {
    constructor() {
        this.currentBreakpoint = this.getBreakpoint();
        this.init();
    }

    init() {
        this.setupViewportHandling();
        this.setupResponsiveModalBehavior();
        this.setupSwipeGestures();
        console.log('📱 Responsive Modal Handler initialized');
    }

    getBreakpoint() {
        const width = window.innerWidth;
        if (width <= 768) return 'mobile';
        if (width <= 1024) return 'tablet';
        return 'desktop';
    }

    setupViewportHandling() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const newBreakpoint = this.getBreakpoint();
                
                if (newBreakpoint !== this.currentBreakpoint) {
                    this.currentBreakpoint = newBreakpoint;
                    this.adjustModalForBreakpoint();
                }
            }, 250);
        });

        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.adjustModalForBreakpoint();
            }, 500);
        });
    }

    setupResponsiveModalBehavior() {
        // Override modal opening behavior for different screen sizes
        const originalOpenModal = window.MoneyRiteTools?.modalManager?.openModal;
        
        if (originalOpenModal) {
            window.MoneyRiteTools.modalManager.openModal = (title, content, toolName) => {
                const result = originalOpenModal.call(window.MoneyRiteTools.modalManager, title, content, toolName);
                
                setTimeout(() => {
                    this.adjustModalForBreakpoint();
                    this.setupModalInteractions();
                }, 100);
                
                return result;
            };
        }
    }

    adjustModalForBreakpoint() {
        const modal = document.getElementById('moneyrite-modal-container');
        if (!modal || modal.style.display === 'none') return;

        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) return;

        // Remove existing responsive classes
        modalContent.classList.remove('mobile-modal', 'tablet-modal', 'desktop-modal');
        
        // Add appropriate class based on breakpoint
        modalContent.classList.add(`${this.currentBreakpoint}-modal`);

        switch (this.currentBreakpoint) {
            case 'mobile':
                this.setupMobileModal(modalContent);
                break;
            case 'tablet':
                this.setupTabletModal(modalContent);
                break;
            case 'desktop':
                this.setupDesktopModal(modalContent);
                break;
        }
    }

    setupMobileModal(modalContent) {
        // Mobile-specific modal setup
        modalContent.style.width = '100%';
        modalContent.style.maxWidth = 'none';
        modalContent.style.margin = '0';
        modalContent.style.borderRadius = '1rem 1rem 0 0';
        modalContent.style.maxHeight = 'calc(100vh - 2rem)';
        
        // Add swipe-to-close functionality
        this.enableSwipeToClose(modalContent);
        
        // Adjust form elements for touch
        const inputs = modalContent.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.style.fontSize = '16px'; // Prevent zoom on iOS
            input.style.minHeight = '44px';
        });
        
        // Adjust buttons for touch
        const buttons = modalContent.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.minHeight = '44px';
            button.style.padding = '0.75rem 1.5rem';
        });
    }

    setupTabletModal(modalContent) {
        // Tablet-specific modal setup
        modalContent.style.width = '90%';
        modalContent.style.maxWidth = '600px';
        modalContent.style.margin = '2rem auto';
        modalContent.style.borderRadius = '1rem';
        modalContent.style.maxHeight = 'calc(100vh - 4rem)';
    }

    setupDesktopModal(modalContent) {
        // Desktop-specific modal setup
        modalContent.style.width = 'auto';
        modalContent.style.maxWidth = '800px';
        modalContent.style.margin = '2rem auto';
        modalContent.style.borderRadius = '1rem';
        modalContent.style.maxHeight = 'calc(100vh - 4rem)';
    }

    setupModalInteractions() {
        const modal = document.getElementById('moneyrite-modal-container');
        if (!modal) return;

        // Setup keyboard navigation
        this.setupModalKeyboardNavigation(modal);
        
        // Setup focus management
        this.setupModalFocusManagement(modal);
        
        // Setup scroll behavior
        this.setupModalScrollBehavior(modal);
    }

    setupModalKeyboardNavigation(modal) {
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                window.MoneyRiteTools.modalManager.closeModal();
            }
            
            // Tab navigation within modal
            if (e.key === 'Tab') {
                this.handleTabNavigation(e, modal);
            }
        });
    }

    handleTabNavigation(e, modal) {
        const focusableElements = modal.querySelectorAll(
            'input:not([disabled]), button:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
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

    setupModalFocusManagement(modal) {
        const focusableElements = modal.querySelectorAll(
            'input, button, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            setTimeout(() => {
                focusableElements[0].focus();
            }, 100);
        }
    }

    setupModalScrollBehavior(modal) {
        const modalBody = modal.querySelector('.modal-body');
        if (!modalBody) return;

        // Enable smooth scrolling
        modalBody.style.scrollBehavior = 'smooth';
        
        // Add scroll indicators for mobile
        if (this.currentBreakpoint === 'mobile') {
            this.addScrollIndicators(modalBody);
        }
    }

    addScrollIndicators(scrollContainer) {
        const indicator = document.createElement('div');
        indicator.className = 'scroll-indicator';
        indicator.style.cssText = `
            position: absolute;
            right: 0.5rem;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 50px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 2px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        scrollContainer.style.position = 'relative';
        scrollContainer.appendChild(indicator);
        
        scrollContainer.addEventListener('scroll', () => {
            indicator.style.opacity = '1';
            clearTimeout(indicator.hideTimeout);
            indicator.hideTimeout = setTimeout(() => {
                indicator.style.opacity = '0';
            }, 1000);
        });
    }

    setupSwipeGestures() {
        if (this.currentBreakpoint !== 'mobile') return;
        
        let startY = 0;
        let currentY = 0;
        let isDragging = false;
        
        document.addEventListener('touchstart', (e) => {
            const modal = document.getElementById('moneyrite-modal-container');
            if (!modal || modal.style.display === 'none') return;
            
            startY = e.touches[0].clientY;
            isDragging = true;
        }, { passive: true });
        
        document.addEventListener('touchmove', (e) => {
            if (!isDragging) return;
            
            currentY = e.touches[0].clientY;
            const deltaY = currentY - startY;
            
            // Only allow downward swipe to close
            if (deltaY > 0) {
                const modal = document.getElementById('moneyrite-modal-container');
                const modalContent = modal?.querySelector('.modal-content');
                
                if (modalContent) {
                    const opacity = Math.max(0.5, 1 - (deltaY / 300));
                    const translateY = Math.min(deltaY * 0.5, 100);
                    
                    modalContent.style.transform = `translateY(${translateY}px)`;
                    modal.style.backgroundColor = `rgba(0, 0, 0, ${opacity * 0.8})`;
                }
            }
        }, { passive: true });
        
        document.addEventListener('touchend', () => {
            if (!isDragging) return;
            
            const deltaY = currentY - startY;
            const modal = document.getElementById('moneyrite-modal-container');
            const modalContent = modal?.querySelector('.modal-content');
            
            if (deltaY > 100) {
                // Close modal if swiped down enough
                window.MoneyRiteTools.modalManager.closeModal();
            } else if (modalContent) {
                // Reset position
                modalContent.style.transform = '';
                modal.style.backgroundColor = '';
            }
            
            isDragging = false;
            startY = 0;
            currentY = 0;
        }, { passive: true });
    }

    enableSwipeToClose(modalContent) {
        // Add visual indicator for swipe-to-close
        const swipeIndicator = document.createElement('div');
        swipeIndicator.style.cssText = `
            width: 40px;
            height: 4px;
            background: #d1d5db;
            border-radius: 2px;
            margin: 0.5rem auto;
            cursor: grab;
        `;
        
        const modalHeader = modalContent.querySelector('.modal-header');
        if (modalHeader) {
            modalHeader.insertBefore(swipeIndicator, modalHeader.firstChild);
        }
    }
}

// Initialize responsive modal handler
let responsiveModalHandler;

document.addEventListener('DOMContentLoaded', () => {
    // Wait for MoneyRiteTools to be available
    const initResponsiveHandler = () => {
        if (window.MoneyRiteTools && window.MoneyRiteTools.modalManager) {
            responsiveModalHandler = new ResponsiveModalHandler();
        } else {
            setTimeout(initResponsiveHandler, 100);
        }
    };
    
    initResponsiveHandler();
});

// Export for global access
window.ResponsiveModalHandler = ResponsiveModalHandler;