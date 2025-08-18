/**
 * MoneyRite Testing and Debugging Utilities
 * Provides comprehensive testing, debugging, and performance monitoring
 */

// Testing and Debugging Manager
class MoneyRiteTestingManager {
    constructor() {
        this.testResults = [];
        this.performanceMetrics = {};
        this.debugMode = this.isDebugMode();
        this.init();
    }

    init() {
        if (this.debugMode) {
            console.log('🔧 MoneyRite Testing & Debug Manager initialized');
            this.setupDebugConsole();
            this.setupPerformanceMonitoring();
            this.setupErrorTracking();
        }
    }

    isDebugMode() {
        return localStorage.getItem('moneyrite_debug') === 'true' || 
               window.location.search.includes('debug=true') ||
               window.location.hostname === 'localhost';
    }

    // Comprehensive system test
    async runSystemTests() {
        console.group('🧪 MoneyRite System Tests');
        
        const tests = [
            this.testDOMReady,
            this.testScriptsLoaded,
            this.testModalSystem,
            this.testErrorHandling,
            this.testAccessibility,
            this.testMobileFeatures,
            this.testPerformance
        ];

        this.testResults = [];
        
        for (const test of tests) {
            try {
                const result = await test.call(this);
                this.testResults.push(result);
                
                if (result.passed) {
                    console.log(`✅ ${result.name}: PASSED`);
                } else {
                    console.error(`❌ ${result.name}: FAILED - ${result.error}`);
                }
            } catch (error) {
                console.error(`💥 Test execution error: ${error.message}`);
                this.testResults.push({
                    name: test.name,
                    passed: false,
                    error: error.message,
                    timestamp: Date.now()
                });
            }
        }
        
        console.groupEnd();
        this.generateTestReport();
        return this.testResults;
    }

    // Individual test methods
    async testDOMReady() {
        const startTime = performance.now();
        
        try {
            const isReady = document.readyState === 'complete' || document.readyState === 'interactive';
            const hasBody = document.body !== null;
            const hasMoneyRiteCards = document.querySelectorAll('[onclick*="safeCardClick"]').length > 0;
            
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'DOM Ready Test',
                passed: isReady && hasBody && hasMoneyRiteCards,
                details: {
                    domReady: isReady,
                    hasBody,
                    moneyRiteCards: hasMoneyRiteCards,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'DOM Ready Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    async testScriptsLoaded() {
        const startTime = performance.now();
        
        try {
            const requiredObjects = [
                'MoneyRiteTools',
                'MoneyRiteErrorHandler',
                'DOMValidator',
                'MobileAccessibilityManager'
            ];
            
            const loadedObjects = {};
            const missingObjects = [];
            
            requiredObjects.forEach(obj => {
                if (window[obj]) {
                    loadedObjects[obj] = true;
                } else {
                    loadedObjects[obj] = false;
                    missingObjects.push(obj);
                }
            });
            
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'Scripts Loaded Test',
                passed: missingObjects.length === 0,
                details: {
                    loadedObjects,
                    missingObjects,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                error: missingObjects.length > 0 ? `Missing: ${missingObjects.join(', ')}` : null,
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'Scripts Loaded Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    async testModalSystem() {
        const startTime = performance.now();
        
        try {
            const hasModalManager = window.MoneyRiteTools && window.MoneyRiteTools.modalManager;
            const hasModalContainer = document.getElementById('moneyrite-modal-container') !== null;
            
            let modalStructureValid = false;
            if (hasModalContainer) {
                const container = document.getElementById('moneyrite-modal-container');
                const requiredElements = ['.modal-backdrop', '.modal-content', '.modal-header', '.modal-body'];
                modalStructureValid = requiredElements.every(selector => container.querySelector(selector));
            }
            
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'Modal System Test',
                passed: hasModalManager && hasModalContainer && modalStructureValid,
                details: {
                    hasModalManager,
                    hasModalContainer,
                    modalStructureValid,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'Modal System Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    async testErrorHandling() {
        const startTime = performance.now();
        
        try {
            // Test error handler functionality
            const hasErrorHandler = typeof window.MoneyRiteErrorHandler !== 'undefined';
            
            let errorLoggingWorks = false;
            if (hasErrorHandler) {
                try {
                    const testError = new Error('Test error');
                    window.MoneyRiteErrorHandler.logError('Test Context', testError);
                    errorLoggingWorks = true;
                } catch (e) {
                    errorLoggingWorks = false;
                }
            }
            
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'Error Handling Test',
                passed: hasErrorHandler && errorLoggingWorks,
                details: {
                    hasErrorHandler,
                    errorLoggingWorks,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'Error Handling Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    async testAccessibility() {
        const startTime = performance.now();
        
        try {
            const cards = document.querySelectorAll('[onclick*="safeCardClick"]');
            let accessibilityScore = 0;
            let totalChecks = 0;
            
            cards.forEach(card => {
                // Check for tabindex
                if (card.hasAttribute('tabindex')) accessibilityScore++;
                totalChecks++;
                
                // Check for ARIA role
                if (card.hasAttribute('role')) accessibilityScore++;
                totalChecks++;
                
                // Check for ARIA label
                if (card.hasAttribute('aria-label')) accessibilityScore++;
                totalChecks++;
            });
            
            const accessibilityPercentage = totalChecks > 0 ? (accessibilityScore / totalChecks) * 100 : 0;
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'Accessibility Test',
                passed: accessibilityPercentage >= 80,
                details: {
                    accessibilityScore: `${accessibilityScore}/${totalChecks}`,
                    accessibilityPercentage: `${accessibilityPercentage.toFixed(1)}%`,
                    cardsFound: cards.length,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'Accessibility Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    async testMobileFeatures() {
        const startTime = performance.now();
        
        try {
            const hasMobileManager = typeof window.MobileAccessibilityManager !== 'undefined';
            const hasTouchClass = document.body.classList.contains('touch-device') || 
                                 document.body.classList.contains('non-touch-device');
            
            // Test viewport meta tag
            const hasViewportMeta = document.querySelector('meta[name="viewport"]') !== null;
            
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'Mobile Features Test',
                passed: hasMobileManager && hasTouchClass && hasViewportMeta,
                details: {
                    hasMobileManager,
                    hasTouchClass,
                    hasViewportMeta,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'Mobile Features Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    async testPerformance() {
        const startTime = performance.now();
        
        try {
            // Test script loading performance
            const navigationTiming = performance.getEntriesByType('navigation')[0];
            const domContentLoaded = navigationTiming.domContentLoadedEventEnd - navigationTiming.navigationStart;
            const pageLoad = navigationTiming.loadEventEnd - navigationTiming.navigationStart;
            
            // Test modal opening performance (simulate)
            const modalOpenStart = performance.now();
            const hasModalManager = window.MoneyRiteTools && window.MoneyRiteTools.modalManager;
            const modalOpenTime = performance.now() - modalOpenStart;
            
            const executionTime = performance.now() - startTime;
            
            return {
                name: 'Performance Test',
                passed: domContentLoaded < 3000 && pageLoad < 5000 && modalOpenTime < 100,
                details: {
                    domContentLoaded: `${domContentLoaded.toFixed(2)}ms`,
                    pageLoad: `${pageLoad.toFixed(2)}ms`,
                    modalOpenTime: `${modalOpenTime.toFixed(2)}ms`,
                    executionTime: `${executionTime.toFixed(2)}ms`
                },
                timestamp: Date.now()
            };
        } catch (error) {
            return {
                name: 'Performance Test',
                passed: false,
                error: error.message,
                timestamp: Date.now()
            };
        }
    }

    // Rapid clicking test
    async testRapidClicking() {
        console.log('🔄 Testing rapid clicking behavior...');
        
        const cards = document.querySelectorAll('[onclick*="safeCardClick"]');
        if (cards.length === 0) {
            console.warn('No MoneyRite cards found for rapid clicking test');
            return;
        }
        
        const testCard = cards[0];
        const clickCount = 10;
        const clickInterval = 50; // 50ms between clicks
        
        let successfulClicks = 0;
        let errors = 0;
        
        for (let i = 0; i < clickCount; i++) {
            try {
                testCard.click();
                successfulClicks++;
                
                // Close modal if it opened
                setTimeout(() => {
                    if (window.MoneyRiteTools && window.MoneyRiteTools.modalManager) {
                        window.MoneyRiteTools.modalManager.closeModal();
                    }
                }, 10);
                
                await new Promise(resolve => setTimeout(resolve, clickInterval));
            } catch (error) {
                errors++;
                console.error(`Click ${i + 1} failed:`, error);
            }
        }
        
        console.log(`Rapid clicking test completed: ${successfulClicks}/${clickCount} successful, ${errors} errors`);
        return { successfulClicks, errors, total: clickCount };
    }

    // Performance monitoring
    setupPerformanceMonitoring() {
        // Monitor modal opening times
        const originalOpenModal = window.MoneyRiteTools?.modalManager?.openModal;
        
        if (originalOpenModal) {
            window.MoneyRiteTools.modalManager.openModal = function(title, content, toolName) {
                const startTime = performance.now();
                const result = originalOpenModal.call(this, title, content, toolName);
                const endTime = performance.now();
                
                const executionTime = endTime - startTime;
                console.log(`⏱️ Modal "${toolName}" opened in ${executionTime.toFixed(2)}ms`);
                
                if (executionTime > 500) {
                    console.warn(`⚠️ Performance warning: Modal took ${executionTime.toFixed(2)}ms (target: <500ms)`);
                }
                
                return result;
            };
        }
    }

    // Error tracking
    setupErrorTracking() {
        const originalLogError = window.MoneyRiteErrorHandler?.logError;
        
        if (originalLogError) {
            window.MoneyRiteErrorHandler.logError = function(context, error, additionalInfo = {}) {
                const result = originalLogError.call(this, context, error, additionalInfo);
                
                // Track error frequency
                const errorKey = `${context}:${error.name}`;
                const errorCount = parseInt(sessionStorage.getItem(`error_count_${errorKey}`) || '0') + 1;
                sessionStorage.setItem(`error_count_${errorKey}`, errorCount.toString());
                
                if (errorCount > 3) {
                    console.warn(`🚨 Frequent error detected: ${errorKey} (${errorCount} times)`);
                }
                
                return result;
            };
        }
    }

    // Debug console
    setupDebugConsole() {
        // Add debug commands to window
        window.MoneyRiteDebug = {
            runTests: () => this.runSystemTests(),
            testRapidClicking: () => this.testRapidClicking(),
            showErrors: () => {
                const errors = JSON.parse(localStorage.getItem('moneyrite_errors') || '[]');
                console.table(errors);
            },
            clearErrors: () => {
                localStorage.removeItem('moneyrite_errors');
                console.log('Error log cleared');
            },
            enableDebug: () => {
                localStorage.setItem('moneyrite_debug', 'true');
                console.log('Debug mode enabled');
            },
            disableDebug: () => {
                localStorage.removeItem('moneyrite_debug');
                console.log('Debug mode disabled');
            },
            getPerformanceMetrics: () => {
                return this.performanceMetrics;
            }
        };
        
        console.log('🔧 Debug console available at window.MoneyRiteDebug');
        console.log('Available commands: runTests(), testRapidClicking(), showErrors(), clearErrors(), enableDebug(), disableDebug()');
    }

    // Generate test report
    generateTestReport() {
        const passedTests = this.testResults.filter(test => test.passed).length;
        const totalTests = this.testResults.length;
        const successRate = totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
        
        console.group('📊 Test Report');
        console.log(`Overall Success Rate: ${successRate.toFixed(1)}% (${passedTests}/${totalTests})`);
        
        const failedTests = this.testResults.filter(test => !test.passed);
        if (failedTests.length > 0) {
            console.group('❌ Failed Tests');
            failedTests.forEach(test => {
                console.error(`${test.name}: ${test.error}`);
            });
            console.groupEnd();
        }
        
        console.groupEnd();
        
        // Store report in sessionStorage
        sessionStorage.setItem('moneyrite_test_report', JSON.stringify({
            timestamp: Date.now(),
            successRate,
            passedTests,
            totalTests,
            results: this.testResults
        }));
    }
}

// Initialize testing manager
let testingManager;

document.addEventListener('DOMContentLoaded', () => {
    testingManager = new MoneyRiteTestingManager();
    
    // Auto-run tests in debug mode
    if (testingManager.debugMode) {
        setTimeout(() => {
            testingManager.runSystemTests();
        }, 2000);
    }
});

// Export for global access
window.MoneyRiteTestingManager = MoneyRiteTestingManager;