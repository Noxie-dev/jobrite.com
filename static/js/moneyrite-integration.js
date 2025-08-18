/**
 * MoneyRite Integration and Final Setup
 * Ensures all components are properly integrated and working together
 */

// Integration manager to coordinate all MoneyRite components
class MoneyRiteIntegrationManager {
    constructor() {
        this.components = {
            errorHandler: false,
            modalManager: false,
            accessibility: false,
            testing: false
        };
        this.isInitialized = false;
        this.initializationErrors = [];
    }

    async initialize() {
        console.group('🚀 MoneyRite Integration Manager');
        console.log('Initializing MoneyRite system...');

        try {
            // Wait for DOM to be ready
            await this.waitForDOM();
            
            // Initialize components in order
            await this.initializeErrorHandler();
            await this.initializeModalManager();
            await this.initializeAccessibility();
            await this.initializeTesting();
            
            // Validate complete setup
            await this.validateIntegration();
            
            // Run initial tests
            await this.runInitialTests();
            
            this.isInitialized = true;
            console.log('✅ MoneyRite system initialized successfully');
            
        } catch (error) {
            this.initializationErrors.push(error);
            console.error('❌ MoneyRite initialization failed:', error);
        }
        
        console.groupEnd();
        return this.isInitialized;
    }

    async waitForDOM() {
        if (document.readyState === 'complete') return;
        
        return new Promise(resolve => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    async initializeErrorHandler() {
        try {
            if (!window.MoneyRiteErrorHandler) {
                throw new Error('MoneyRiteErrorHandler not loaded');
            }
            
            // Test error handler
            const testError = new Error('Integration test');
            window.MoneyRiteErrorHandler.logError('Integration Test', testError, { test: true });
            
            this.components.errorHandler = true;
            console.log('✅ Error Handler initialized');
            
        } catch (error) {
            console.error('❌ Error Handler initialization failed:', error);
            throw error;
        }
    }

    async initializeModalManager() {
        try {
            if (!window.MoneyRiteTools?.modalManager) {
                throw new Error('Modal Manager not available');
            }
            
            // Validate modal container
            const container = document.getElementById('moneyrite-modal-container');
            if (!container) {
                throw new Error('Modal container not found');
            }
            
            this.components.modalManager = true;
            console.log('✅ Modal Manager initialized');
            
        } catch (error) {
            console.error('❌ Modal Manager initialization failed:', error);
            throw error;
        }
    }

    async initializeAccessibility() {
        try {
            if (!window.MobileTouchHandler || !window.ModalAccessibilityManager) {
                throw new Error('Accessibility components not loaded');
            }
            
            // Validate accessibility features are applied
            const cards = document.querySelectorAll('[role="button"][tabindex="0"]');
            if (cards.length === 0) {
                console.warn('⚠️ No accessible cards found');
            }
            
            this.components.accessibility = true;
            console.log('✅ Accessibility features initialized');
            
        } catch (error) {
            console.error('❌ Accessibility initialization failed:', error);
            throw error;
        }
    }

    async initializeTesting() {
        try {
            if (!window.MoneyRiteTestSuite || !window.MoneyRiteDebugger) {
                throw new Error('Testing components not loaded');
            }
            
            this.components.testing = true;
            console.log('✅ Testing framework initialized');
            
        } catch (error) {
            console.error('❌ Testing initialization failed:', error);
            throw error;
        }
    }

    async validateIntegration() {
        const validation = {
            dom: DOMValidator.validateMoneyRiteSetup(),
            functions: this.validateFunctions(),
            performance: await this.validatePerformance()
        };

        if (!validation.dom.isValid) {
            throw new Error(`DOM validation failed: ${validation.dom.errors.join(', ')}`);
        }

        if (validation.functions.missing.length > 0) {
            throw new Error(`Missing functions: ${validation.functions.missing.join(', ')}`);
        }

        console.log('✅ Integration validation passed');
        return validation;
    }

    validateFunctions() {
        const requiredFunctions = [
            'openSalaryCalculator',
            'openBudgetPlanner', 
            'openDebtTracker',
            'openCreditMonitor'
        ];

        const missing = requiredFunctions.filter(func => !window[func]);
        const available = requiredFunctions.filter(func => window[func]);

        return { missing, available };
    }

    async validatePerformance() {
        // Quick performance check
        const startTime = performance.now();
        
        try {
            // Test modal opening speed
            await window.openSalaryCalculator();
            const openTime = performance.now() - startTime;
            
            // Close modal
            window.MoneyRiteTools.modalManager.closeModal();
            
            return {
                modalOpenTime: openTime.toFixed(2),
                meetsRequirement: openTime < 500
            };
            
        } catch (error) {
            return {
                error: error.message,
                meetsRequirement: false
            };
        }
    }

    async runInitialTests() {
        if (!this.components.testing) return;

        try {
            const testSuite = window.initializeMoneyRiteTests();
            await testSuite.runAllTests();
            
            console.log('✅ Initial tests completed');
            
        } catch (error) {
            console.warn('⚠️ Initial tests failed:', error);
        }
    }

    getStatus() {
        return {
            initialized: this.isInitialized,
            components: this.components,
            errors: this.initializationErrors
        };
    }
}

// Global integration manager instance
let integrationManager;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    // Small delay to ensure all scripts are loaded
    setTimeout(async () => {
        integrationManager = new MoneyRiteIntegrationManager();
        await integrationManager.initialize();
        
        // Make available globally for debugging
        window.MoneyRiteIntegration = integrationManager;
        
        // Log final status
        const status = integrationManager.getStatus();
        if (status.initialized) {
            console.log('🎉 MoneyRite system is ready!');
            
            // Show success message in development
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.log('💡 Try clicking on the MoneyRite cards to test the functionality');
                console.log('💡 Use MoneyRiteDebugger commands for testing and debugging');
            }
        } else {
            console.error('💥 MoneyRite system failed to initialize:', status.errors);
        }
    }, 500);
});

// Export for global access
window.MoneyRiteIntegrationManager = MoneyRiteIntegrationManager;