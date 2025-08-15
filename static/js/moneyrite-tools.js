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
        this.createModalContainer();
    }

    createModalContainer() {
        if (document.getElementById('moneyrite-modal-container')) return;
        
        const container = document.createElement('div');
        container.id = 'moneyrite-modal-container';
        container.className = 'moneyrite-modal-container';
        container.innerHTML = `
            <div class="modal-backdrop" onclick="modalManager.closeModal()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="modal-title"></h3>
                    <button class="modal-close" onclick="modalManager.closeModal()">&times;</button>
                </div>
                <div class="modal-body"></div>
            </div>
        `;
        document.body.appendChild(container);
    }

    openModal(title, content, toolName) {
        const container = document.getElementById('moneyrite-modal-container');
        const titleEl = container.querySelector('.modal-title');
        const bodyEl = container.querySelector('.modal-body');
        
        titleEl.textContent = title;
        bodyEl.innerHTML = content;
        
        container.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        this.activeModal = toolName;
        
        // Add privacy notice
        this.addPrivacyNotice(bodyEl);
    }

    closeModal() {
        const container = document.getElementById('moneyrite-modal-container');
        container.style.display = 'none';
        document.body.style.overflow = 'auto';
        this.activeModal = null;
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