/**
 * MoneyRite Accessibility and Mobile Enhancements
 * Provides keyboard navigation, touch support, and accessibility features
 */

// Keyboard navigation handler for MoneyRite cards
function handleCardKeydown(event, toolName, handlerFunction) {
    // Handle Enter and Space keys
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        event.stopPropagation();
        
        // Use the same safe wrapper as click events
        safeCardClick(toolName, handlerFunction)(event);
    }
    
    // Handle arrow key navigation
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
        event.preventDefault();
        focusNextCard(event.target);
    } else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
        event.preventDefault();
        focusPreviousCard(event.target);
    }
}

// Focus management for card navigation
function focusNextCard(currentCard) {
    const cards = document.querySelectorAll('[role="button"][tabindex="0"]');
    const currentIndex = Array.from(cards).indexOf(currentCard);
    const nextIndex = (currentIndex + 1) % cards.length;
    cards[nextIndex].focus();
}

function focusPreviousCard(currentCard) {
    const cards = document.querySelectorAll('[role="button"][tabindex="0"]');
    const currentIndex = Array.from(cards).indexOf(currentCard);
    const prevIndex = currentIndex === 0 ? cards.length - 1 : currentIndex - 1;
    cards[prevIndex].focus();
}

// Touch event enhancements for mobile
class MobileTouchHandler {
    constructor() {
        this.touchStartTime = 0;
        this.touchStartPos = { x: 0, y: 0 };
        this.isScrolling = false;
        this.initializeTouchHandlers();
    }

    initializeTouchHandlers() {
        // Add touch event listeners to all MoneyRite cards
        const cards = document.querySelectorAll('[onclick*="safeCardClick"]');
        
        cards.forEach(card => {
            // Add touch feedback
            card.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
            card.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
            card.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false });
            card.addEventListener('touchcancel', this.handleTouchCancel.bind(this), { passive: true });
            
            // Add visual feedback class
            card.classList.add('touch-enabled');
        });
    }

    handleTouchStart(event) {
        this.touchStartTime = Date.now();
        this.touchStartPos = {
            x: event.touches[0].clientX,
            y: event.touches[0].clientY
        };
        this.isScrolling = false;
        
        // Add pressed state
        event.currentTarget.classList.add('touch-pressed');
        
        // Provide haptic feedback if available
        if (navigator.vibrate) {
            navigator.vibrate(10);
        }
    }

    handleTouchMove(event) {
        if (!this.touchStartTime) return;
        
        const touch = event.touches[0];
        const deltaX = Math.abs(touch.clientX - this.touchStartPos.x);
        const deltaY = Math.abs(touch.clientY - this.touchStartPos.y);
        
        // Detect if user is scrolling
        if (deltaY > deltaX && deltaY > 10) {
            this.isScrolling = true;
            event.currentTarget.classList.remove('touch-pressed');
        }
        
        // If moved too far, cancel the touch
        if (deltaX > 20 || deltaY > 20) {
            event.currentTarget.classList.remove('touch-pressed');
        }
    }

    handleTouchEnd(event) {
        const touchDuration = Date.now() - this.touchStartTime;
        const card = event.currentTarget;
        
        // Remove pressed state
        card.classList.remove('touch-pressed');
        
        // Only trigger click if it was a quick tap and not scrolling
        if (!this.isScrolling && touchDuration < 500) {
            // Prevent the subsequent click event
            event.preventDefault();
            
            // Trigger the card click
            const onclickAttr = card.getAttribute('onclick');
            if (onclickAttr) {
                try {
                    // Create a synthetic event
                    const syntheticEvent = new Event('click', { bubbles: true, cancelable: true });
                    syntheticEvent.isSynthetic = true;
                    
                    // Execute the onclick handler
                    eval(onclickAttr.replace('(event)', '(syntheticEvent)'));
                } catch (error) {
                    console.error('Touch handler error:', error);
                }
            }
        }
        
        this.touchStartTime = 0;
        this.isScrolling = false;
    }

    handleTouchCancel(event) {
        event.currentTarget.classList.remove('touch-pressed');
        this.touchStartTime = 0;
        this.isScrolling = false;
    }
}

// Modal accessibility enhancements
class ModalAccessibilityManager {
    constructor() {
        this.previousFocus = null;
        this.trapFocus = this.trapFocus.bind(this);
    }

    enhanceModal(modalContainer) {
        if (!modalContainer) return;

        // Store the previously focused element
        this.previousFocus = document.activeElement;

        // Set up focus trap
        modalContainer.addEventListener('keydown', this.trapFocus);

        // Focus the first focusable element
        setTimeout(() => {
            const firstFocusable = this.getFirstFocusableElement(modalContainer);
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }, 100);

        // Prevent background scrolling on mobile
        if (this.isMobile()) {
            document.body.style.position = 'fixed';
            document.body.style.top = `-${window.scrollY}px`;
            document.body.style.width = '100%';
        }

        // Add ARIA attributes
        modalContainer.setAttribute('aria-modal', 'true');
        modalContainer.setAttribute('role', 'dialog');
        
        const title = modalContainer.querySelector('.modal-title');
        if (title) {
            title.id = 'modal-title-' + Date.now();
            modalContainer.setAttribute('aria-labelledby', title.id);
        }
    }

    restoreModal() {
        // Remove focus trap
        const modalContainer = document.getElementById('moneyrite-modal-container');
        if (modalContainer) {
            modalContainer.removeEventListener('keydown', this.trapFocus);
        }

        // Restore focus
        if (this.previousFocus) {
            this.previousFocus.focus();
            this.previousFocus = null;
        }

        // Restore scrolling on mobile
        if (this.isMobile()) {
            const scrollY = document.body.style.top;
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
            window.scrollTo(0, parseInt(scrollY || '0') * -1);
        }
    }

    trapFocus(event) {
        if (event.key !== 'Tab') return;

        const modalContainer = document.getElementById('moneyrite-modal-container');
        const focusableElements = this.getFocusableElements(modalContainer);
        
        if (focusableElements.length === 0) return;

        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstFocusable) {
                event.preventDefault();
                lastFocusable.focus();
            }
        } else {
            // Tab
            if (document.activeElement === lastFocusable) {
                event.preventDefault();
                firstFocusable.focus();
            }
        }
    }

    getFocusableElements(container) {
        const focusableSelectors = [
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            'a[href]',
            '[tabindex]:not([tabindex="-1"])'
        ];

        return Array.from(container.querySelectorAll(focusableSelectors.join(', ')))
            .filter(el => {
                return el.offsetWidth > 0 && el.offsetHeight > 0 && 
                       getComputedStyle(el).visibility !== 'hidden';
            });
    }

    getFirstFocusableElement(container) {
        const focusableElements = this.getFocusableElements(container);
        return focusableElements[0] || null;
    }

    isMobile() {
        return window.innerWidth <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
}

// Responsive design enhancements
class ResponsiveManager {
    constructor() {
        this.currentBreakpoint = this.getCurrentBreakpoint();
        this.initializeResponsiveHandlers();
    }

    getCurrentBreakpoint() {
        const width = window.innerWidth;
        if (width < 640) return 'mobile';
        if (width < 768) return 'tablet';
        if (width < 1024) return 'desktop-small';
        return 'desktop';
    }

    initializeResponsiveHandlers() {
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const newBreakpoint = this.getCurrentBreakpoint();
                
                if (newBreakpoint !== this.currentBreakpoint) {
                    this.handleBreakpointChange(this.currentBreakpoint, newBreakpoint);
                    this.currentBreakpoint = newBreakpoint;
                }
                
                this.adjustModalForViewport();
            }, 250);
        });

        // Handle orientation change on mobile
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.adjustModalForViewport();
            }, 100);
        });
    }

    handleBreakpointChange(oldBreakpoint, newBreakpoint) {
        console.log(`Breakpoint changed: ${oldBreakpoint} → ${newBreakpoint}`);
        
        // Adjust modal if it's open
        const modal = document.getElementById('moneyrite-modal-container');
        if (modal && modal.style.display === 'flex') {
            this.adjustModalForViewport();
        }
    }

    adjustModalForViewport() {
        const modal = document.getElementById('moneyrite-modal-container');
        if (!modal || modal.style.display !== 'flex') return;

        const modalContent = modal.querySelector('.modal-content');
        if (!modalContent) return;

        const breakpoint = this.getCurrentBreakpoint();
        
        // Adjust modal size based on viewport
        if (breakpoint === 'mobile') {
            modalContent.style.maxWidth = '95vw';
            modalContent.style.maxHeight = '90vh';
            modalContent.style.margin = '1rem';
        } else if (breakpoint === 'tablet') {
            modalContent.style.maxWidth = '85vw';
            modalContent.style.maxHeight = '85vh';
            modalContent.style.margin = '2rem';
        } else {
            modalContent.style.maxWidth = '800px';
            modalContent.style.maxHeight = '90vh';
            modalContent.style.margin = 'auto';
        }
    }
}

// Initialize accessibility and mobile enhancements
let mobileTouchHandler;
let modalAccessibilityManager;
let responsiveManager;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Initializing MoneyRite accessibility and mobile enhancements...');
    
    try {
        // Initialize touch handling for mobile
        mobileTouchHandler = new MobileTouchHandler();
        
        // Initialize modal accessibility
        modalAccessibilityManager = new ModalAccessibilityManager();
        
        // Initialize responsive management
        responsiveManager = new ResponsiveManager();
        
        // Enhance existing modal manager
        if (window.MoneyRiteTools && window.MoneyRiteTools.modalManager) {
            const originalOpenModal = window.MoneyRiteTools.modalManager.openModal;
            const originalCloseModal = window.MoneyRiteTools.modalManager.closeModal;
            
            window.MoneyRiteTools.modalManager.openModal = function(title, content, toolName) {
                const result = originalOpenModal.call(this, title, content, toolName);
                
                // Enhance with accessibility
                const modalContainer = document.getElementById('moneyrite-modal-container');
                if (modalContainer) {
                    modalAccessibilityManager.enhanceModal(modalContainer);
                    responsiveManager.adjustModalForViewport();
                }
                
                return result;
            };
            
            window.MoneyRiteTools.modalManager.closeModal = function() {
                modalAccessibilityManager.restoreModal();
                return originalCloseModal.call(this);
            };
        }
        
        console.log('✅ MoneyRite accessibility and mobile enhancements initialized');
        
    } catch (error) {
        console.error('❌ Failed to initialize accessibility enhancements:', error);
    }
});

// Export for global access
window.handleCardKeydown = handleCardKeydown;
window.MobileTouchHandler = MobileTouchHandler;
window.ModalAccessibilityManager = ModalAccessibilityManager;
window.ResponsiveManager = ResponsiveManager;