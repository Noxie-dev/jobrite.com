/**
 * MoneyRite Financial Tools - Client-Side Implementation
 * Free financial calculators for JobRite landing page
 */

// Local Storage Manager
class FinancialDataManager {
    constructor() {
        this.storagePrefix = 'jobrite_moneyrite_';
    }

    save(toolName, data) {
        try {
            const key = this.storagePrefix + toolName;
            localStorage.setItem(key, JSON.stringify({
                data: data,
                timestamp: Date.now()
            }));
            return true;
        } catch (error) {
            console.warn('Failed to save data to localStorage:', error);
            return false;
        }
    }

    load(toolName) {
        try {
            const key = this.storagePrefix + toolName;
            const stored = localStorage.getItem(key);
            if (stored) {
                return JSON.parse(stored);
            }
            return null;
        } catch (error) {
            console.warn('Failed to load data from localStorage:', error);
            return null;
        }
    }

    clear(toolName) {
        try {
            const key = this.storagePrefix + toolName;
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.warn('Failed to clear data from localStorage:', error);
            return false;
        }
    }

    clearAll() {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(this.storagePrefix)) {
                    localStorage.removeItem(key);
                }
            });
            return true;
        } catch (error) {
            console.warn('Failed to clear all data from localStorage:', error);
            return false;
        }
    }
}

// South African Tax Calculator
class SARSTaxCalculator {
    constructor() {
        // 2024 Tax Year brackets
        this.taxBrackets = [
            { min: 0, max: 237100, rate: 0.18, base: 0 },
            { min: 237100, max: 370500, rate: 0.26, base: 42678 },
            { min: 370500, max: 512800, rate: 0.31, base: 77362 },
            { min: 512800, max: 673000, rate: 0.36, base: 121475 },
            { min: 673000, max: 857900, rate: 0.39, base: 179147 },
            { min: 857900, max: 1817000, rate: 0.41, base: 251258 },
            { min: 1817000, max: Infinity, rate: 0.45, base: 644489 }
        ];

        // Medical aid tax credits (2024)
        this.medicalCredits = {
            main: 347,      // Main member
            dependent: 234  // Each dependent
        };

        // UIF rate
        this.uifRate = 0.01; // 1%
        this.uifMax = 177.12; // Monthly maximum
    }

    calculateIncomeTax(annualIncome) {
        for (let bracket of this.taxBrackets) {
            if (annualIncome > bracket.min && annualIncome <= bracket.max) {
                return bracket.base + (annualIncome - bracket.min) * bracket.rate;
            }
        }
        return 0;
    }

    calculateUIF(monthlyIncome) {
        const uifAmount = monthlyIncome * this.uifRate;
        return Math.min(uifAmount, this.uifMax);
    }

    calculateMedicalCredit(members) {
        if (members <= 0) return 0;
        return this.medicalCredits.main + (Math.max(0, members - 1) * this.medicalCredits.dependent);
    }

    calculateNetSalary(grossMonthly, options = {}) {
        const {
            includeMedical = false,
            medicalMembers = 1,
            pensionPercentage = 0
        } = options;

        const grossAnnual = grossMonthly * 12;
        
        // Calculate pension contribution
        const pensionMonthly = grossMonthly * (pensionPercentage / 100);
        const pensionAnnual = pensionMonthly * 12;
        
        // Taxable income after pension
        const taxableAnnual = grossAnnual - pensionAnnual;
        
        // Calculate annual tax
        const annualTax = this.calculateIncomeTax(taxableAnnual);
        const monthlyTax = annualTax / 12;
        
        // Calculate UIF
        const uifMonthly = this.calculateUIF(grossMonthly);
        
        // Calculate medical aid tax credit
        const medicalCreditMonthly = includeMedical ? this.calculateMedicalCredit(medicalMembers) : 0;
        
        // Calculate net salary
        const netMonthly = grossMonthly - monthlyTax - uifMonthly - pensionMonthly + medicalCreditMonthly;
        
        return {
            grossMonthly: Math.round(grossMonthly * 100) / 100,
            grossAnnual: Math.round(grossAnnual * 100) / 100,
            taxableAnnual: Math.round(taxableAnnual * 100) / 100,
            incomeTaxMonthly: Math.round(monthlyTax * 100) / 100,
            incomeTaxAnnual: Math.round(annualTax * 100) / 100,
            uifMonthly: Math.round(uifMonthly * 100) / 100,
            pensionMonthly: Math.round(pensionMonthly * 100) / 100,
            pensionAnnual: Math.round(pensionAnnual * 100) / 100,
            medicalCreditMonthly: Math.round(medicalCreditMonthly * 100) / 100,
            netMonthly: Math.round(netMonthly * 100) / 100,
            netAnnual: Math.round(netMonthly * 12 * 100) / 100
        };
    }
}

// Pay Rate Converter
class PayRateConverter {
    static toMonthly(amount, period, hoursPerWeek = 40) {
        const conversions = {
            'hourly': amount * hoursPerWeek * 4.33,
            'daily': amount * 5 * 4.33,
            'weekly': amount * 4.33,
            'monthly': amount,
            'annually': amount / 12
        };
        return conversions[period] || amount;
    }

    static fromMonthly(monthlyAmount, targetPeriod, hoursPerWeek = 40) {
        const conversions = {
            'hourly': monthlyAmount / (hoursPerWeek * 4.33),
            'daily': monthlyAmount / (5 * 4.33),
            'weekly': monthlyAmount / 4.33,
            'monthly': monthlyAmount,
            'annually': monthlyAmount * 12
        };
        return Math.round((conversions[targetPeriod] || monthlyAmount) * 100) / 100;
    }
}

// Debt Calculator
class DebtCalculator {
    static calculatePayoffTime(balance, interestRate, monthlyPayment) {
        if (monthlyPayment <= 0 || balance <= 0) return null;
        
        const monthlyRate = interestRate / 12 / 100;
        const monthlyInterest = balance * monthlyRate;
        
        if (monthlyPayment <= monthlyInterest) {
            return null; // Payment doesn't cover interest
        }
        
        let currentBalance = balance;
        let months = 0;
        
        while (currentBalance > 0 && months < 600) { // Cap at 50 years
            const interestPayment = currentBalance * monthlyRate;
            const principalPayment = monthlyPayment - interestPayment;
            currentBalance -= principalPayment;
            months++;
        }
        
        return currentBalance <= 0 ? months : null;
    }

    static calculateTotalInterest(balance, interestRate, monthlyPayment) {
        const payoffMonths = this.calculatePayoffTime(balance, interestRate, monthlyPayment);
        if (!payoffMonths) return null;
        
        const totalPayments = monthlyPayment * payoffMonths;
        return Math.round((totalPayments - balance) * 100) / 100;
    }

    static calculateMonthlyBreakdown(balance, interestRate, monthlyPayment) {
        const monthlyRate = interestRate / 12 / 100;
        const interestPortion = balance * monthlyRate;
        const principalPortion = Math.max(0, monthlyPayment - interestPortion);
        
        return {
            interestPortion: Math.round(interestPortion * 100) / 100,
            principalPortion: Math.round(principalPortion * 100) / 100,
            newBalance: Math.round((balance - principalPortion) * 100) / 100
        };
    }
}

// Modal Manager
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.modalState = {
            isOpen: false,
            currentTool: null,
            container: null,
            hasError: false,
            fallbackMode: false
        };
        this.initializeModal();
    }

    initializeModal() {
        try {
            this.createModalContainer();
            this.validateInitialization();
            console.log('✅ ModalManager initialized successfully');
        } catch (error) {
            if (window.MoneyRiteErrorHandler) {
                window.MoneyRiteErrorHandler.logError('ModalManager Initialization', error);
            } else {
                console.error('ModalManager initialization failed:', error);
            }
            throw error;
        }
    }

    validateInitialization() {
        const container = document.getElementById('moneyrite-modal-container');
        if (!container) {
            throw new Error('Modal container creation failed');
        }

        const requiredElements = ['.modal-backdrop', '.modal-content', '.modal-title', '.modal-close', '.modal-body'];
        const missing = requiredElements.filter(selector => !container.querySelector(selector));
        
        if (missing.length > 0) {
            throw new Error(`Modal structure incomplete. Missing elements: ${missing.join(', ')}`);
        }

        this.modalState.container = container;
        return true;
    }

    createModalContainer() {
        if (document.getElementById('moneyrite-modal-container')) {
            console.log('Modal container already exists');
            return;
        }
        
        try {
            const container = document.createElement('div');
            container.id = 'moneyrite-modal-container';
            container.className = 'moneyrite-modal-container';
            container.innerHTML = `
                <div class="modal-backdrop" onclick="modalManager.closeModal()"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 class="modal-title"></h3>
                        <button class="modal-close" onclick="modalManager.closeModal()" aria-label="Close modal">&times;</button>
                    </div>
                    <div class="modal-body"></div>
                </div>
            `;
            
            // Add keyboard event listener for ESC key
            container.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.closeModal();
                }
            });

            document.body.appendChild(container);
            console.log('Modal container created successfully');
        } catch (error) {
            throw new Error(`Failed to create modal container: ${error.message}`);
        }
    }

    openModal(title, content, toolName) {
        const startTime = performance.now();
        
        try {
            // Validate inputs
            if (!title || !content || !toolName) {
                throw new Error('Missing required parameters: title, content, or toolName');
            }

            // Ensure modal is properly initialized
            if (!this.modalState.container) {
                this.validateInitialization();
            }

            const container = this.modalState.container;
            const titleEl = container.querySelector('.modal-title');
            const bodyEl = container.querySelector('.modal-body');
            
            if (!titleEl || !bodyEl) {
                throw new Error('Modal elements not found');
            }

            // Clear previous content
            bodyEl.innerHTML = '';
            
            // Set new content
            titleEl.textContent = title;
            bodyEl.innerHTML = content;
            
            // Update modal state
            this.modalState.isOpen = true;
            this.modalState.currentTool = toolName;
            this.modalState.hasError = false;
            this.modalState.fallbackMode = false;
            this.activeModal = toolName;
            
            // Show modal with animation
            container.style.display = 'flex';
            container.setAttribute('aria-hidden', 'false');
            
            // Prevent background scrolling (mobile-friendly)
            if (window.MobileAccessibilityManager) {
                window.MobileAccessibilityManager.preventBackgroundScroll(true);
            } else {
                document.body.style.overflow = 'hidden';
            }
            
            // Focus management for accessibility
            setTimeout(() => {
                const firstFocusable = container.querySelector('input, button, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (firstFocusable) {
                    firstFocusable.focus();
                }
            }, 100);
            
            // Add privacy notice (only for non-error modals)
            if (!toolName.includes('error')) {
                this.addPrivacyNotice(bodyEl);
            }

            const executionTime = performance.now() - startTime;
            console.log(`✅ Modal opened: ${toolName} (${executionTime.toFixed(2)}ms)`);
            
            return true;
        } catch (error) {
            const executionTime = performance.now() - startTime;
            
            if (window.MoneyRiteErrorHandler) {
                window.MoneyRiteErrorHandler.logError('Modal Open Error', error, {
                    toolName,
                    title,
                    executionTime: executionTime.toFixed(2)
                });
            }

            // Try fallback modal
            return this.handleModalError(error, toolName);
        }
    }

    closeModal() {
        try {
            const container = this.modalState.container || document.getElementById('moneyrite-modal-container');
            
            if (container) {
                container.style.display = 'none';
                container.setAttribute('aria-hidden', 'true');
            }
            
            // Restore background scrolling (mobile-friendly)
            if (window.MobileAccessibilityManager) {
                window.MobileAccessibilityManager.preventBackgroundScroll(false);
            } else {
                document.body.style.overflow = 'auto';
            }
            
            // Reset modal state
            this.modalState.isOpen = false;
            this.modalState.currentTool = null;
            this.modalState.hasError = false;
            this.modalState.fallbackMode = false;
            this.activeModal = null;
            
            console.log('Modal closed successfully');
            return true;
        } catch (error) {
            if (window.MoneyRiteErrorHandler) {
                window.MoneyRiteErrorHandler.logError('Modal Close Error', error);
            }
            
            // Force close as fallback
            try {
                const container = document.getElementById('moneyrite-modal-container');
                if (container) {
                    container.style.display = 'none';
                }
                document.body.style.overflow = 'auto';
            } catch (fallbackError) {
                console.error('Critical modal close error:', fallbackError);
            }
            
            return false;
        }
    }

    handleModalError(error, toolName) {
        try {
            this.modalState.hasError = true;
            this.modalState.fallbackMode = true;
            
            const fallbackContent = this.createFallbackContent(toolName, error);
            
            // Try to show fallback modal
            const container = this.modalState.container || document.getElementById('moneyrite-modal-container');
            if (container) {
                const titleEl = container.querySelector('.modal-title');
                const bodyEl = container.querySelector('.modal-body');
                
                if (titleEl && bodyEl) {
                    titleEl.textContent = `${toolName} - Error`;
                    bodyEl.innerHTML = fallbackContent;
                    
                    container.style.display = 'flex';
                    document.body.style.overflow = 'hidden';
                    
                    this.modalState.isOpen = true;
                    this.modalState.currentTool = `${toolName}-error`;
                    
                    return true;
                }
            }
            
            // If modal system completely fails, show alert
            alert(`Sorry, the ${toolName} is temporarily unavailable. Please refresh the page and try again.`);
            return false;
            
        } catch (fallbackError) {
            console.error('Critical modal error handling failure:', fallbackError);
            alert(`Sorry, there was an error opening the ${toolName}. Please refresh the page.`);
            return false;
        }
    }

    createFallbackContent(toolName, error) {
        return `
            <div class="fallback-modal" style="text-align: center; padding: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚠️</div>
                <h3 style="color: #dc2626; margin-bottom: 1rem;">Financial Tool Temporarily Unavailable</h3>
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    We're experiencing technical difficulties with the ${toolName}.
                </p>
                <p style="color: #6b7280; margin-bottom: 2rem;">
                    Please try refreshing the page or contact support if the issue persists.
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button onclick="location.reload()" 
                            style="background: #3b82f6; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.5rem; cursor: pointer; min-width: 120px;">
                        Refresh Page
                    </button>
                    <button onclick="modalManager.closeModal()" 
                            style="background: #6b7280; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.5rem; cursor: pointer; min-width: 120px;">
                        Close
                    </button>
                </div>
                <details style="margin-top: 2rem; text-align: left; max-width: 500px; margin-left: auto; margin-right: auto;">
                    <summary style="cursor: pointer; color: #6b7280; padding: 0.5rem;">Technical Details (for developers)</summary>
                    <pre style="background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; margin-top: 0.5rem; font-size: 0.8rem; overflow: auto; white-space: pre-wrap;">
Error: ${error.message}
Context: ${toolName}
Time: ${new Date().toLocaleString()}
User Agent: ${navigator.userAgent}
                    </pre>
                </details>
            </div>
        `;
    }

    addPrivacyNotice(container) {
        const notice = document.createElement('div');
        notice.className = 'privacy-notice';
        notice.innerHTML = `
            <div class="privacy-notice-content">
                <svg class="privacy-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16V13C8,12.4 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
                </svg>
                <div class="privacy-text">
                    <strong>Your Privacy is Protected</strong>
                    <p>All calculations are performed locally in your browser. No financial data is sent to our servers.</p>
                </div>
            </div>
        `;
        container.appendChild(notice);
    }
}

// Initialize global instances
const dataManager = new FinancialDataManager();
const taxCalculator = new SARSTaxCalculator();
const modalManager = new ModalManager();

// Export for global access
window.MoneyRiteTools = {
    dataManager,
    taxCalculator,
    modalManager,
    PayRateConverter,
    DebtCalculator
};