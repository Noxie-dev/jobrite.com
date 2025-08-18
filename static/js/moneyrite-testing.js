/**
 * MoneyRite Testing and Debugging Utilities
 * Comprehensive testing framework for MoneyRite functionality
 */

class MoneyRiteTestSuite {
    constructor() {
        this.tests = [];
        this.results = [];
        this.isRunning = false;
    }

    // Add a test to the suite
    addTest(name, testFunction, timeout = 5000) {
        this.tests.push({
            name,
            testFunction,
            timeout,
            status: 'pending'
        });
    }

    // Run all tests
    async runAllTests() {
        if (this.isRunning) {
            console.warn('Tests are already running');
            return;
        }

        this.isRunning = true;
        this.results = [];
        
        console.group('🧪 MoneyRite Test Suite');
        console.log(`Running ${this.tests.length} tests...`);

        for (const test of this.tests) {
            await this.runSingleTest(test);
        }

        this.generateTestReport();
        this.isRunning = false;
        console.groupEnd();
    }

    async runSingleTest(test) {
        const startTime = performance.now();
        
        try {
            console.log(`🔍 Running: ${test.name}`);
            
            // Run test with timeout
            const result = await Promise.race([
                test.testFunction(),
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Test timeout')), test.timeout)
                )
            ]);

            const duration = performance.now() - startTime;
            test.status = 'passed';
            
            this.results.push({
                name: test.name,
                status: 'passed',
                duration: duration.toFixed(2),
                result
            });
            
            console.log(`✅ ${test.name} - PASSED (${duration.toFixed(2)}ms)`);
            
        } catch (error) {
            const duration = performance.now() - startTime;
            test.status = 'failed';
            
            this.results.push({
                name: test.name,
                status: 'failed',
                duration: duration.toFixed(2),
                error: error.message
            });
            
            console.error(`❌ ${test.name} - FAILED (${duration.toFixed(2)}ms):`, error);
        }
    }
}  
  generateTestReport() {
        const passed = this.results.filter(r => r.status === 'passed').length;
        const failed = this.results.filter(r => r.status === 'failed').length;
        const totalTime = this.results.reduce((sum, r) => sum + parseFloat(r.duration), 0);

        console.log('\n📊 Test Results Summary:');
        console.log(`✅ Passed: ${passed}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`⏱️ Total Time: ${totalTime.toFixed(2)}ms`);
        
        if (failed > 0) {
            console.log('\n❌ Failed Tests:');
            this.results.filter(r => r.status === 'failed').forEach(result => {
                console.log(`  • ${result.name}: ${result.error}`);
            });
        }
    }
}

// Performance testing utilities
class PerformanceTester {
    static async testModalOpeningSpeed(toolName, handlerFunction) {
        const iterations = 5;
        const times = [];
        
        for (let i = 0; i < iterations; i++) {
            const startTime = performance.now();
            
            try {
                await handlerFunction();
                const endTime = performance.now();
                times.push(endTime - startTime);
                
                // Close modal for next iteration
                if (window.MoneyRiteTools?.modalManager) {
                    window.MoneyRiteTools.modalManager.closeModal();
                }
                
                // Wait a bit between iterations
                await new Promise(resolve => setTimeout(resolve, 100));
                
            } catch (error) {
                console.error(`Performance test failed for ${toolName}:`, error);
                return null;
            }
        }
        
        const avgTime = times.reduce((sum, time) => sum + time, 0) / times.length;
        const minTime = Math.min(...times);
        const maxTime = Math.max(...times);
        
        return {
            toolName,
            averageTime: avgTime.toFixed(2),
            minTime: minTime.toFixed(2),
            maxTime: maxTime.toFixed(2),
            iterations,
            meetsRequirement: avgTime < 500
        };
    }

    static async testRapidClicking(toolName, handlerFunction, clickCount = 10) {
        const results = [];
        const startTime = performance.now();
        
        for (let i = 0; i < clickCount; i++) {
            try {
                const clickStart = performance.now();
                await handlerFunction();
                const clickEnd = performance.now();
                
                results.push({
                    clickNumber: i + 1,
                    duration: clickEnd - clickStart,
                    success: true
                });
                
                // Close modal quickly
                if (window.MoneyRiteTools?.modalManager) {
                    window.MoneyRiteTools.modalManager.closeModal();
                }
                
            } catch (error) {
                results.push({
                    clickNumber: i + 1,
                    duration: 0,
                    success: false,
                    error: error.message
                });
            }
        }
        
        const totalTime = performance.now() - startTime;
        const successCount = results.filter(r => r.success).length;
        
        return {
            toolName,
            totalClicks: clickCount,
            successfulClicks: successCount,
            failedClicks: clickCount - successCount,
            totalTime: totalTime.toFixed(2),
            averageClickTime: (totalTime / clickCount).toFixed(2),
            results
        };
    }
}

// Initialize comprehensive test suite
function initializeMoneyRiteTests() {
    const testSuite = new MoneyRiteTestSuite();
    
    // Test 1: DOM Validation
    testSuite.addTest('DOM Elements Validation', async () => {
        const validation = DOMValidator.validateMoneyRiteSetup();
        if (!validation.isValid) {
            throw new Error(`DOM validation failed: ${validation.errors.join(', ')}`);
        }
        return validation;
    });
    
    // Test 2: Script Dependencies
    testSuite.addTest('Script Dependencies', async () => {
        const requiredGlobals = ['MoneyRiteTools', 'MoneyRiteErrorHandler', 'safeCardClick', 'DOMValidator'];
        const missing = requiredGlobals.filter(global => !window[global]);
        if (missing.length > 0) {
            throw new Error(`Missing dependencies: ${missing.join(', ')}`);
        }
        return { loaded: requiredGlobals };
    });
    
    // Test 3: Modal Manager Initialization
    testSuite.addTest('Modal Manager Initialization', async () => {
        if (!window.MoneyRiteTools?.modalManager) {
            throw new Error('Modal manager not initialized');
        }
        
        const modalContainer = document.getElementById('moneyrite-modal-container');
        if (!modalContainer) {
            throw new Error('Modal container not found');
        }
        
        return { modalManager: 'initialized', container: 'found' };
    });
    
    // Test 4: Error Handler Functionality
    testSuite.addTest('Error Handler Functionality', async () => {
        const testError = new Error('Test error');
        const logEntry = MoneyRiteErrorHandler.logError('Test Context', testError, { test: true });
        
        if (!logEntry || !logEntry.timestamp) {
            throw new Error('Error handler not working properly');
        }
        
        return logEntry;
    });
    
    return testSuite;
}

// Debug utilities
const MoneyRiteDebugger = {
    logSystemState() {
        console.group('🔧 MoneyRite System State');
        
        console.log('DOM Ready:', DOMValidator.isReady());
        console.log('MoneyRiteTools:', !!window.MoneyRiteTools);
        console.log('Modal Manager:', !!window.MoneyRiteTools?.modalManager);
        console.log('Error Handler:', !!window.MoneyRiteErrorHandler);
        console.log('Accessibility:', !!window.MobileTouchHandler);
        
        const modalContainer = document.getElementById('moneyrite-modal-container');
        console.log('Modal Container:', !!modalContainer);
        
        if (modalContainer) {
            console.log('Modal Display:', modalContainer.style.display);
            console.log('Modal Visible:', modalContainer.offsetWidth > 0);
        }
        
        console.groupEnd();
    },
    
    testAllCards() {
        console.group('🎯 Testing All MoneyRite Cards');
        
        const cards = [
            { name: 'Salary Calculator', func: 'openSalaryCalculator' },
            { name: 'Budget Planner', func: 'openBudgetPlanner' },
            { name: 'Debt Tracker', func: 'openDebtTracker' },
            { name: 'Credit Education', func: 'openCreditMonitor' }
        ];
        
        cards.forEach(card => {
            try {
                if (window[card.func]) {
                    console.log(`✅ ${card.name}: Function available`);
                } else {
                    console.error(`❌ ${card.name}: Function missing`);
                }
            } catch (error) {
                console.error(`❌ ${card.name}: Error -`, error);
            }
        });
        
        console.groupEnd();
    },
    
    async runPerformanceTests() {
        console.group('⚡ Performance Tests');
        
        const tools = [
            { name: 'Salary Calculator', func: window.openSalaryCalculator },
            { name: 'Budget Planner', func: window.openBudgetPlanner },
            { name: 'Debt Tracker', func: window.openDebtTracker },
            { name: 'Credit Education', func: window.openCreditMonitor }
        ];
        
        for (const tool of tools) {
            if (tool.func) {
                const result = await PerformanceTester.testModalOpeningSpeed(tool.name, tool.func);
                if (result) {
                    console.log(`${result.meetsRequirement ? '✅' : '⚠️'} ${tool.name}:`, 
                               `Avg: ${result.averageTime}ms`, 
                               `(Min: ${result.minTime}ms, Max: ${result.maxTime}ms)`);
                }
            }
        }
        
        console.groupEnd();
    }
};

// Export for global access
window.MoneyRiteTestSuite = MoneyRiteTestSuite;
window.PerformanceTester = PerformanceTester;
window.MoneyRiteDebugger = MoneyRiteDebugger;
window.initializeMoneyRiteTests = initializeMoneyRiteTests;

// Auto-initialize debugging in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔧 MoneyRite Debug Mode Enabled');
    
    // Add debug commands to console
    console.log('Available debug commands:');
    console.log('- MoneyRiteDebugger.logSystemState()');
    console.log('- MoneyRiteDebugger.testAllCards()');
    console.log('- MoneyRiteDebugger.runPerformanceTests()');
    console.log('- initializeMoneyRiteTests().runAllTests()');
}