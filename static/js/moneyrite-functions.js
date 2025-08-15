// MoneyRite Tools Functions
function openSalaryCalculator() {
    const content = `
        <form class="tool-form" id="salary-calculator-form">
            <div class="form-group">
                <label class="form-label">Pay Amount (ZAR)</label>
                <input type="number" class="form-input" id="pay-amount" placeholder="Enter amount" step="0.01" min="0.01" required>
            </div>
            
            <div class="form-group">
                <label class="form-label">Pay Period</label>
                <select class="form-select" id="pay-period" required>
                    <option value="monthly">Monthly</option>
                    <option value="annually">Annually</option>
                    <option value="weekly">Weekly</option>
                    <option value="daily">Daily</option>
                    <option value="hourly">Hourly</option>
                </select>
            </div>
            
            <div class="form-group" id="hours-group" style="display: none;">
                <label class="form-label">Hours Per Week</label>
                <input type="number" class="form-input" id="hours-per-week" placeholder="40" step="0.01" min="0.01" max="168">
            </div>
            
            <div class="form-checkbox-group">
                <input type="checkbox" class="form-checkbox" id="include-medical">
                <label class="checkbox-label" for="include-medical">Include Medical Aid Tax Credit</label>
            </div>
            
            <div class="form-group" id="medical-members-group" style="display: none;">
                <label class="form-label">Number of Medical Aid Members</label>
                <input type="number" class="form-input" id="medical-members" placeholder="1" min="1" value="1">
            </div>
            
            <div class="form-group">
                <label class="form-label">Pension Contribution (%)</label>
                <input type="number" class="form-input" id="pension-percentage" placeholder="0.00" step="0.01" min="0" max="27.5" value="0">
            </div>
            
            <div class="action-buttons">
                <button type="submit" class="btn-primary">Calculate Salary</button>
                <button type="button" class="btn-secondary" onclick="clearSalaryData()">Clear Data</button>
            </div>
        </form>
        
        <div id="salary-results" class="results-container" style="display: none;">
            <h3 class="results-title">Your Salary Breakdown</h3>
            <div class="results-grid" id="salary-results-grid"></div>
        </div>
    `;
    
    window.MoneyRiteTools.modalManager.openModal('Salary Calculator', content, 'salary');
    
    // Add event listeners
    document.getElementById('pay-period').addEventListener('change', function() {
        const hoursGroup = document.getElementById('hours-group');
        hoursGroup.style.display = this.value === 'hourly' ? 'block' : 'none';
    });
    
    document.getElementById('include-medical').addEventListener('change', function() {
        const membersGroup = document.getElementById('medical-members-group');
        membersGroup.style.display = this.checked ? 'block' : 'none';
    });
    
    document.getElementById('salary-calculator-form').addEventListener('submit', function(e) {
        e.preventDefault();
        calculateSalary();
    });
    
    // Load saved data
    loadSalaryData();
}

function calculateSalary() {
    const payAmount = parseFloat(document.getElementById('pay-amount').value);
    const payPeriod = document.getElementById('pay-period').value;
    const hoursPerWeek = parseFloat(document.getElementById('hours-per-week').value) || 40;
    const includeMedical = document.getElementById('include-medical').checked;
    const medicalMembers = parseInt(document.getElementById('medical-members').value) || 1;
    const pensionPercentage = parseFloat(document.getElementById('pension-percentage').value) || 0;
    
    if (!payAmount || payAmount <= 0) {
        alert('Please enter a valid pay amount');
        return;
    }
    
    // Convert to monthly
    const grossMonthly = window.MoneyRiteTools.PayRateConverter.toMonthly(payAmount, payPeriod, hoursPerWeek);
    
    // Calculate net salary
    const results = window.MoneyRiteTools.taxCalculator.calculateNetSalary(grossMonthly, {
        includeMedical,
        medicalMembers,
        pensionPercentage
    });
    
    // Display results
    displaySalaryResults(results, payAmount, payPeriod, hoursPerWeek);
    
    // Save data
    const data = {
        payAmount, payPeriod, hoursPerWeek, includeMedical, medicalMembers, pensionPercentage, results
    };
    window.MoneyRiteTools.dataManager.save('salary', data);
}

function displaySalaryResults(results, originalAmount, originalPeriod, hoursPerWeek) {
    const resultsContainer = document.getElementById('salary-results');
    const resultsGrid = document.getElementById('salary-results-grid');
    
    resultsGrid.innerHTML = `
        <div class="result-item">
            <div class="result-label">Gross Monthly</div>
            <div class="result-value">R${results.grossMonthly.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Income Tax</div>
            <div class="result-value">R${results.incomeTaxMonthly.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">UIF</div>
            <div class="result-value">R${results.uifMonthly.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Pension</div>
            <div class="result-value">R${results.pensionMonthly.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Medical Credit</div>
            <div class="result-value positive">R${results.medicalCreditMonthly.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Net Monthly</div>
            <div class="result-value positive">R${results.netMonthly.toLocaleString()}</div>
        </div>
    `;
    
    resultsContainer.style.display = 'block';
}

function loadSalaryData() {
    const saved = window.MoneyRiteTools.dataManager.load('salary');
    if (saved && saved.data) {
        const data = saved.data;
        document.getElementById('pay-amount').value = data.payAmount || '';
        document.getElementById('pay-period').value = data.payPeriod || 'monthly';
        document.getElementById('hours-per-week').value = data.hoursPerWeek || 40;
        document.getElementById('include-medical').checked = data.includeMedical || false;
        document.getElementById('medical-members').value = data.medicalMembers || 1;
        document.getElementById('pension-percentage').value = data.pensionPercentage || 0;
        
        // Trigger change events
        document.getElementById('pay-period').dispatchEvent(new Event('change'));
        document.getElementById('include-medical').dispatchEvent(new Event('change'));
        
        if (data.results) {
            displaySalaryResults(data.results, data.payAmount, data.payPeriod, data.hoursPerWeek);
        }
    }
}

function clearSalaryData() {
    if (confirm('Are you sure you want to clear all salary data?')) {
        window.MoneyRiteTools.dataManager.clear('salary');
        document.getElementById('salary-calculator-form').reset();
        document.getElementById('salary-results').style.display = 'none';
        document.getElementById('hours-group').style.display = 'none';
        document.getElementById('medical-members-group').style.display = 'none';
    }
}

function openBudgetPlanner() {
    const content = `
        <form class="tool-form" id="budget-planner-form">
            <div class="form-group">
                <label class="form-label">Monthly Income (ZAR)</label>
                <input type="number" class="form-input" id="monthly-income" placeholder="Enter monthly income" step="0.01" min="0" required>
            </div>
            
            <h4 style="margin: 2rem 0 1rem; color: var(--text-primary); font-weight: 600;">Monthly Expenses</h4>
            
            <div class="form-group">
                <label class="form-label">Housing (Rent/Bond)</label>
                <input type="number" class="form-input expense-input" id="housing" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Groceries & Household</label>
                <input type="number" class="form-input expense-input" id="groceries" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Utilities (Water/Electricity)</label>
                <input type="number" class="form-input expense-input" id="utilities" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Transport (Fuel/Taxi)</label>
                <input type="number" class="form-input expense-input" id="transport" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Education (School Fees)</label>
                <input type="number" class="form-input expense-input" id="education" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Healthcare/Medical</label>
                <input type="number" class="form-input expense-input" id="healthcare" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Insurance</label>
                <input type="number" class="form-input expense-input" id="insurance" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Loan Repayments</label>
                <input type="number" class="form-input expense-input" id="loans" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Family Support (Black Tax)</label>
                <input type="number" class="form-input expense-input" id="family" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Entertainment & Lifestyle</label>
                <input type="number" class="form-input expense-input" id="entertainment" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Savings & Investments</label>
                <input type="number" class="form-input expense-input" id="savings" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Other Expenses</label>
                <input type="number" class="form-input expense-input" id="other" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="action-buttons">
                <button type="button" class="btn-primary" onclick="calculateBudget()">Calculate Budget</button>
                <button type="button" class="btn-secondary" onclick="clearBudgetData()">Clear Data</button>
            </div>
        </form>
        
        <div id="budget-results" class="results-container" style="display: none;">
            <h3 class="results-title">Your Budget Summary</h3>
            <div class="results-grid" id="budget-results-grid"></div>
        </div>
    `;
    
    window.MoneyRiteTools.modalManager.openModal('Budget Planner', content, 'budget');
    
    // Add real-time calculation
    setTimeout(() => {
        const expenseInputs = document.querySelectorAll('.expense-input');
        expenseInputs.forEach(input => {
            input.addEventListener('input', calculateBudget);
        });
        
        document.getElementById('monthly-income').addEventListener('input', calculateBudget);
    }, 100);
    
    // Load saved data
    loadBudgetData();
}

function calculateBudget() {
    const monthlyIncome = parseFloat(document.getElementById('monthly-income').value) || 0;
    
    const expenses = {
        housing: parseFloat(document.getElementById('housing').value) || 0,
        groceries: parseFloat(document.getElementById('groceries').value) || 0,
        utilities: parseFloat(document.getElementById('utilities').value) || 0,
        transport: parseFloat(document.getElementById('transport').value) || 0,
        education: parseFloat(document.getElementById('education').value) || 0,
        healthcare: parseFloat(document.getElementById('healthcare').value) || 0,
        insurance: parseFloat(document.getElementById('insurance').value) || 0,
        loans: parseFloat(document.getElementById('loans').value) || 0,
        family: parseFloat(document.getElementById('family').value) || 0,
        entertainment: parseFloat(document.getElementById('entertainment').value) || 0,
        savings: parseFloat(document.getElementById('savings').value) || 0,
        other: parseFloat(document.getElementById('other').value) || 0
    };
    
    const totalExpenses = Object.values(expenses).reduce((sum, val) => sum + val, 0);
    const remainingBalance = monthlyIncome - totalExpenses;
    
    // Display results
    displayBudgetResults(monthlyIncome, totalExpenses, remainingBalance);
    
    // Save data
    const data = { monthlyIncome, expenses, totalExpenses, remainingBalance };
    window.MoneyRiteTools.dataManager.save('budget', data);
}

function displayBudgetResults(income, expenses, balance) {
    const resultsContainer = document.getElementById('budget-results');
    const resultsGrid = document.getElementById('budget-results-grid');
    
    const balanceClass = balance >= 0 ? 'positive' : 'negative';
    const healthStatus = balance >= 0 ? 'Healthy Budget' : 'Overspending';
    
    resultsGrid.innerHTML = `
        <div class="result-item">
            <div class="result-label">Monthly Income</div>
            <div class="result-value">R${income.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Total Expenses</div>
            <div class="result-value">R${expenses.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Remaining Balance</div>
            <div class="result-value ${balanceClass}">R${balance.toLocaleString()}</div>
        </div>
        <div class="result-item">
            <div class="result-label">Budget Health</div>
            <div class="result-value ${balanceClass}">${healthStatus}</div>
        </div>
    `;
    
    resultsContainer.style.display = 'block';
}

function loadBudgetData() {
    const saved = window.MoneyRiteTools.dataManager.load('budget');
    if (saved && saved.data) {
        const data = saved.data;
        document.getElementById('monthly-income').value = data.monthlyIncome || '';
        
        if (data.expenses) {
            Object.keys(data.expenses).forEach(key => {
                const element = document.getElementById(key);
                if (element) {
                    element.value = data.expenses[key] || '';
                }
            });
        }
        
        if (data.monthlyIncome || Object.values(data.expenses || {}).some(val => val > 0)) {
            calculateBudget();
        }
    }
}

function clearBudgetData() {
    if (confirm('Are you sure you want to clear all budget data?')) {
        window.MoneyRiteTools.dataManager.clear('budget');
        document.getElementById('budget-planner-form').reset();
        document.getElementById('budget-results').style.display = 'none';
    }
}

function openDebtTracker() {
    const content = `
        <div class="tool-form">
            <h4 style="margin: 0 0 1rem; color: var(--text-primary); font-weight: 600;">Add Debt Account</h4>
            
            <div class="form-group">
                <label class="form-label">Debt Name</label>
                <input type="text" class="form-input" id="debt-name" placeholder="e.g., Car Loan - Toyota">
            </div>
            
            <div class="form-group">
                <label class="form-label">Current Balance (ZAR)</label>
                <input type="number" class="form-input" id="debt-balance" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="form-group">
                <label class="form-label">Annual Interest Rate (%)</label>
                <input type="number" class="form-input" id="debt-rate" placeholder="12.50" step="0.01" min="0" max="50">
            </div>
            
            <div class="form-group">
                <label class="form-label">Monthly Payment (ZAR)</label>
                <input type="number" class="form-input" id="debt-payment" placeholder="0.00" step="0.01" min="0">
            </div>
            
            <div class="action-buttons">
                <button type="button" class="btn-primary" onclick="addDebt()">Add Debt</button>
                <button type="button" class="btn-secondary" onclick="clearDebtData()">Clear All</button>
            </div>
        </div>
        
        <div id="debt-list" class="results-container">
            <h3 class="results-title">Your Debts</h3>
            <div id="debt-items"></div>
        </div>
    `;
    
    window.MoneyRiteTools.modalManager.openModal('Debt Tracker', content, 'debt');
    loadDebtData();
}

function addDebt() {
    const name = document.getElementById('debt-name').value.trim();
    const balance = parseFloat(document.getElementById('debt-balance').value);
    const rate = parseFloat(document.getElementById('debt-rate').value);
    const payment = parseFloat(document.getElementById('debt-payment').value);
    
    if (!name || !balance || !rate || !payment) {
        alert('Please fill in all fields');
        return;
    }
    
    const debt = {
        id: Date.now().toString(),
        name,
        balance,
        rate,
        payment,
        createdAt: new Date().toISOString()
    };
    
    // Get existing debts
    const saved = window.MoneyRiteTools.dataManager.load('debts');
    const debts = (saved && saved.data) ? saved.data : [];
    
    debts.push(debt);
    window.MoneyRiteTools.dataManager.save('debts', debts);
    
    // Clear form
    document.getElementById('debt-name').value = '';
    document.getElementById('debt-balance').value = '';
    document.getElementById('debt-rate').value = '';
    document.getElementById('debt-payment').value = '';
    
    displayDebts();
}

function displayDebts() {
    const saved = window.MoneyRiteTools.dataManager.load('debts');
    const debts = (saved && saved.data) ? saved.data : [];
    const container = document.getElementById('debt-items');
    
    if (debts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No debts added yet.</p>';
        return;
    }
    
    container.innerHTML = debts.map(debt => {
        const payoffMonths = window.MoneyRiteTools.DebtCalculator.calculatePayoffTime(debt.balance, debt.rate, debt.payment);
        const totalInterest = window.MoneyRiteTools.DebtCalculator.calculateTotalInterest(debt.balance, debt.rate, debt.payment);
        const breakdown = window.MoneyRiteTools.DebtCalculator.calculateMonthlyBreakdown(debt.balance, debt.rate, debt.payment);
        
        return `
            <div class="debt-item" style="background: white; border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid #e5e7eb;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: var(--text-primary); font-weight: 600;">${debt.name}</h4>
                    <button onclick="removeDebt('${debt.id}')" style="background: none; border: none; color: var(--error-color); cursor: pointer; font-size: 1.2rem;">&times;</button>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Balance</div>
                        <div style="font-weight: 600; color: var(--text-primary);">R${debt.balance.toLocaleString()}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Interest Rate</div>
                        <div style="font-weight: 600; color: var(--text-primary);">${debt.rate}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Monthly Payment</div>
                        <div style="font-weight: 600; color: var(--text-primary);">R${debt.payment.toLocaleString()}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Payoff Time</div>
                        <div style="font-weight: 600; color: var(--text-primary);">${payoffMonths ? Math.ceil(payoffMonths / 12) + ' years' : 'Never'}</div>
                    </div>
                </div>
                
                ${breakdown ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #f1f5f9;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 1rem; font-size: 0.9rem;">
                        <div>Interest: <strong>R${breakdown.interestPortion.toLocaleString()}</strong></div>
                        <div>Principal: <strong>R${breakdown.principalPortion.toLocaleString()}</strong></div>
                        ${totalInterest ? `<div>Total Interest: <strong>R${totalInterest.toLocaleString()}</strong></div>` : ''}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function removeDebt(debtId) {
    if (confirm('Are you sure you want to remove this debt?')) {
        const saved = window.MoneyRiteTools.dataManager.load('debts');
        const debts = (saved && saved.data) ? saved.data : [];
        const filteredDebts = debts.filter(debt => debt.id !== debtId);
        
        window.MoneyRiteTools.dataManager.save('debts', filteredDebts);
        displayDebts();
    }
}

function loadDebtData() {
    displayDebts();
}

function clearDebtData() {
    if (confirm('Are you sure you want to clear all debt data?')) {
        window.MoneyRiteTools.dataManager.clear('debts');
        displayDebts();
    }
}

function openCreditMonitor() {
    const content = `
        <div class="tool-form">
            <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); border-radius: 1rem; padding: 2rem; margin-bottom: 2rem; border: 1px solid #bae6fd;">
                <h4 style="margin: 0 0 1rem; color: #0369a1; font-weight: 600;">🎓 Credit Education Center</h4>
                <p style="margin: 0; color: #0c4a6e; line-height: 1.6;">Learn about credit scores, understand what affects your creditworthiness, and get actionable tips to improve your financial health.</p>
            </div>
            
            <div style="display: grid; gap: 1.5rem;">
                <div class="credit-section" style="background: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #e5e7eb;">
                    <h5 style="margin: 0 0 1rem; color: var(--text-primary); font-weight: 600;">💡 Credit Score Factors</h5>
                    <ul style="margin: 0; padding-left: 1.5rem; color: var(--text-secondary); line-height: 1.6;">
                        <li><strong>Payment History (35%)</strong> - Always pay on time</li>
                        <li><strong>Credit Utilization (30%)</strong> - Keep balances low</li>
                        <li><strong>Length of Credit History (15%)</strong> - Keep old accounts open</li>
                        <li><strong>Credit Mix (10%)</strong> - Have different types of credit</li>
                        <li><strong>New Credit (10%)</strong> - Don't apply for too much credit at once</li>
                    </ul>
                </div>
                
                <div class="credit-section" style="background: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #e5e7eb;">
                    <h5 style="margin: 0 0 1rem; color: var(--text-primary); font-weight: 600;">📊 Debt-to-Income Calculator</h5>
                    <div style="display: grid; gap: 1rem;">
                        <div class="form-group">
                            <label class="form-label">Monthly Income (ZAR)</label>
                            <input type="number" class="form-input" id="credit-income" placeholder="0.00" step="0.01" min="0">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Total Monthly Debt Payments (ZAR)</label>
                            <input type="number" class="form-input" id="credit-debt" placeholder="0.00" step="0.01" min="0">
                        </div>
                        <button type="button" class="btn-primary" onclick="calculateDebtToIncome()">Calculate Ratio</button>
                    </div>
                    <div id="dti-result" style="margin-top: 1rem; display: none;"></div>
                </div>
                
                <div class="credit-section" style="background: white; border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #e5e7eb;">
                    <h5 style="margin: 0 0 1rem; color: var(--text-primary); font-weight: 600;">💳 Credit Utilization Calculator</h5>
                    <div style="display: grid; gap: 1rem;">
                        <div class="form-group">
                            <label class="form-label">Total Credit Limit (ZAR)</label>
                            <input type="number" class="form-input" id="credit-limit" placeholder="0.00" step="0.01" min="0">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Current Balance (ZAR)</label>
                            <input type="number" class="form-input" id="credit-balance" placeholder="0.00" step="0.01" min="0">
                        </div>
                        <button type="button" class="btn-primary" onclick="calculateCreditUtilization()">Calculate Utilization</button>
                    </div>
                    <div id="utilization-result" style="margin-top: 1rem; display: none;"></div>
                </div>
                
                <div class="credit-section" style="background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-radius: 0.75rem; padding: 1.5rem; border: 1px solid #bbf7d0;">
                    <h5 style="margin: 0 0 1rem; color: #15803d; font-weight: 600;">✅ Credit Improvement Tips</h5>
                    <ul style="margin: 0; padding-left: 1.5rem; color: #166534; line-height: 1.6;">
                        <li>Pay all bills on time, every time</li>
                        <li>Keep credit card balances below 30% of limits</li>
                        <li>Don't close old credit card accounts</li>
                        <li>Check your credit report regularly for errors</li>
                        <li>Pay down existing debt before taking on new debt</li>
                        <li>Consider becoming an authorized user on someone else's account</li>
                    </ul>
                </div>
            </div>
            
            <div class="action-buttons">
                <button type="button" class="btn-secondary" onclick="clearCreditData()">Clear Data</button>
            </div>
        </div>
    `;
    
    window.MoneyRiteTools.modalManager.openModal('Credit Education', content, 'credit');
    loadCreditData();
}

function calculateDebtToIncome() {
    const income = parseFloat(document.getElementById('credit-income').value);
    const debt = parseFloat(document.getElementById('credit-debt').value);
    
    if (!income || income <= 0) {
        alert('Please enter a valid monthly income');
        return;
    }
    
    const ratio = debt / income * 100;
    const resultDiv = document.getElementById('dti-result');
    
    let status, color, advice;
    if (ratio <= 20) {
        status = 'Excellent';
        color = 'var(--success-color)';
        advice = 'Your debt-to-income ratio is excellent! You have good financial flexibility.';
    } else if (ratio <= 36) {
        status = 'Good';
        color = 'var(--success-color)';
        advice = 'Your debt-to-income ratio is manageable. Consider paying down debt to improve further.';
    } else if (ratio <= 50) {
        status = 'Fair';
        color = 'var(--warning-color)';
        advice = 'Your debt-to-income ratio is high. Focus on paying down debt and avoid taking on new debt.';
    } else {
        status = 'Poor';
        color = 'var(--error-color)';
        advice = 'Your debt-to-income ratio is very high. Consider debt consolidation or speaking with a financial advisor.';
    }
    
    resultDiv.innerHTML = `
        <div style="background: #f9fafb; border-radius: 0.5rem; padding: 1rem; border: 1px solid #e5e7eb;">
            <div style="font-size: 1.25rem; font-weight: 600; color: ${color}; margin-bottom: 0.5rem;">
                ${ratio.toFixed(1)}% - ${status}
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">${advice}</p>
        </div>
    `;
    resultDiv.style.display = 'block';
    
    // Save data
    const data = { income, debt, ratio };
    window.MoneyRiteTools.dataManager.save('credit', data);
}

function calculateCreditUtilization() {
    const limit = parseFloat(document.getElementById('credit-limit').value);
    const balance = parseFloat(document.getElementById('credit-balance').value);
    
    if (!limit || limit <= 0) {
        alert('Please enter a valid credit limit');
        return;
    }
    
    const utilization = balance / limit * 100;
    const resultDiv = document.getElementById('utilization-result');
    
    let status, color, advice;
    if (utilization <= 10) {
        status = 'Excellent';
        color = 'var(--success-color)';
        advice = 'Excellent! Keep your utilization this low for the best credit score impact.';
    } else if (utilization <= 30) {
        status = 'Good';
        color = 'var(--success-color)';
        advice = 'Good utilization rate. Try to keep it below 30% for optimal credit health.';
    } else if (utilization <= 50) {
        status = 'Fair';
        color = 'var(--warning-color)';
        advice = 'Consider paying down your balance to improve your credit utilization ratio.';
    } else {
        status = 'Poor';
        color = 'var(--error-color)';
        advice = 'High utilization can hurt your credit score. Focus on paying down this balance.';
    }
    
    resultDiv.innerHTML = `
        <div style="background: #f9fafb; border-radius: 0.5rem; padding: 1rem; border: 1px solid #e5e7eb;">
            <div style="font-size: 1.25rem; font-weight: 600; color: ${color}; margin-bottom: 0.5rem;">
                ${utilization.toFixed(1)}% - ${status}
            </div>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">${advice}</p>
        </div>
    `;
    resultDiv.style.display = 'block';
}

function loadCreditData() {
    const saved = window.MoneyRiteTools.dataManager.load('credit');
    if (saved && saved.data) {
        const data = saved.data;
        if (data.income) document.getElementById('credit-income').value = data.income;
        if (data.debt) document.getElementById('credit-debt').value = data.debt;
    }
}

function clearCreditData() {
    if (confirm('Are you sure you want to clear all credit data?')) {
        window.MoneyRiteTools.dataManager.clear('credit');
        document.getElementById('credit-income').value = '';
        document.getElementById('credit-debt').value = '';
        document.getElementById('credit-limit').value = '';
        document.getElementById('credit-balance').value = '';
        document.getElementById('dti-result').style.display = 'none';
        document.getElementById('utilization-result').style.display = 'none';
    }
}