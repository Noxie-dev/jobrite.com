#!/usr/bin/env python3
"""
MoneyRite Test Runner

Comprehensive test runner for MoneyRite reliability and accuracy testing.
Runs golden vectors, property-based tests, and snapshot tests.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.settings')

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Command: {cmd}")
    print(f"Duration: {end_time - start_time:.2f}s")
    
    if result.returncode == 0:
        print("✅ PASSED")
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
    else:
        print("❌ FAILED")
        if result.stderr:
            print("\nError:")
            print(result.stderr)
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
    
    return result.returncode == 0

def main():
    """Run comprehensive test suite"""
    print("🚀 MoneyRite Reliability Test Suite")
    print("Testing calculation accuracy, properties, and UI consistency")
    
    # Check if required packages are installed
    try:
        import pytest
        import hypothesis
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install test dependencies:")
        print("pip install -r requirements.txt")
        return 1
    
    # Test categories to run
    test_categories = [
        {
            'name': 'Golden Test Vectors (SARS Accuracy)',
            'command': 'python -m pytest moneyrite/tests/test_golden_vectors.py -v --tb=short',
            'critical': True
        },
        {
            'name': 'Property-Based Tests (Invariants)',
            'command': 'python -m pytest moneyrite/tests/test_property_based.py -v --tb=short',
            'critical': True
        },
        {
            'name': 'Snapshot Tests (UI Consistency)',
            'command': 'python -m pytest moneyrite/tests/test_snapshots.py -v --tb=short',
            'critical': False
        },
        {
            'name': 'Legacy Calculation Tests',
            'command': 'python moneyrite/test_calculations.py',
            'critical': True
        },
        {
            'name': 'Coverage Report',
            'command': 'python -m pytest moneyrite/tests/ --cov=moneyrite --cov-report=term-missing --cov-report=html',
            'critical': False
        }
    ]
    
    results = []
    critical_failures = 0
    
    for category in test_categories:
        success = run_command(category['command'], category['name'])
        results.append({
            'name': category['name'],
            'success': success,
            'critical': category['critical']
        })
        
        if not success and category['critical']:
            critical_failures += 1
    
    # Summary report
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY REPORT")
    print(f"{'='*60}")
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        critical = " (CRITICAL)" if result['critical'] else ""
        print(f"{status} {result['name']}{critical}")
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"Passed: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"Critical Failures: {critical_failures}")
    
    if critical_failures > 0:
        print("\n🚨 CRITICAL TEST FAILURES DETECTED!")
        print("These failures indicate potential calculation accuracy issues.")
        print("DO NOT DEPLOY until all critical tests pass.")
        return 1
    elif any(not r['success'] for r in results):
        print("\n⚠️  Some non-critical tests failed.")
        print("Review failures and consider fixing before deployment.")
        return 0
    else:
        print("\n🎉 ALL TESTS PASSED!")
        print("MoneyRite calculations are accurate and reliable.")
        return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
