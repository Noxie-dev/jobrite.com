#!/usr/bin/env python3
"""
MoneyRite Safe Deployment Script

Implements safe deployment practices with feature flags, health checks,
and instant rollback capabilities.
"""

import os
import sys
import time
import json
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jobrite_project.settings')

class DeploymentManager:
    """Manages safe deployments with rollback capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.deployment_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log deployment message"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
    
    def run_command(self, command: str, description: str) -> bool:
        """Run command and log results"""
        self.log(f"Running: {description}")
        self.log(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.log(f"✅ {description} completed successfully")
                if result.stdout:
                    self.log(f"Output: {result.stdout.strip()}")
                return True
            else:
                self.log(f"❌ {description} failed", "ERROR")
                if result.stderr:
                    self.log(f"Error: {result.stderr.strip()}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log(f"❌ {description} timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ {description} failed with exception: {e}", "ERROR")
            return False
    
    def health_check(self, endpoint: str = "/health") -> Dict[str, Any]:
        """Perform health check"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
                return health_data
            else:
                self.log(f"❌ Health check failed: HTTP {response.status_code}", "ERROR")
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.log(f"❌ Health check failed: {e}", "ERROR")
            return {"status": "error", "error": str(e)}
    
    def slo_check(self) -> Dict[str, Any]:
        """Check SLO status"""
        try:
            response = requests.get(f"{self.base_url}/health/slo", timeout=10)
            
            if response.status_code == 200:
                slo_data = response.json()
                overall_status = slo_data.get('overall_status', 'UNKNOWN')
                
                if overall_status == 'OK':
                    self.log("✅ All SLOs are healthy")
                elif overall_status == 'WARNING':
                    self.log("⚠️  Some SLOs are in warning state", "WARNING")
                else:
                    self.log("❌ Critical SLO violations detected", "ERROR")
                
                return slo_data
            else:
                self.log(f"❌ SLO check failed: HTTP {response.status_code}", "ERROR")
                return {"overall_status": "ERROR"}
                
        except Exception as e:
            self.log(f"❌ SLO check failed: {e}", "ERROR")
            return {"overall_status": "ERROR", "error": str(e)}
    
    def run_tests(self) -> bool:
        """Run comprehensive test suite"""
        self.log("🧪 Running comprehensive test suite...")
        
        test_commands = [
            ("python run_tests.py", "Golden test vectors and property-based tests"),
            ("python manage.py test moneyrite", "Django unit tests"),
            ("python -m pytest moneyrite/tests/ -x", "Pytest suite")
        ]
        
        for command, description in test_commands:
            if not self.run_command(command, description):
                return False
        
        return True
    
    def deploy_with_feature_flags(self, features_to_enable: List[str] = None) -> bool:
        """Deploy with feature flag protection"""
        features_to_enable = features_to_enable or []
        
        self.log("🚀 Starting safe deployment with feature flags...")
        
        # Step 1: Run tests
        if not self.run_tests():
            self.log("❌ Tests failed - aborting deployment", "ERROR")
            return False
        
        # Step 2: Database migrations
        if not self.run_command("python manage.py migrate", "Database migrations"):
            self.log("❌ Database migration failed - aborting deployment", "ERROR")
            return False
        
        # Step 3: Collect static files
        if not self.run_command("python manage.py collectstatic --noinput", "Collect static files"):
            self.log("⚠️  Static file collection failed - continuing", "WARNING")
        
        # Step 4: Initialize rate engine
        if not self.run_command("python manage.py update_tax_rates --init", "Initialize tax rates"):
            self.log("⚠️  Tax rate initialization failed - using fallback", "WARNING")
        
        # Step 5: Restart application (simulated)
        self.log("🔄 Restarting application...")
        time.sleep(2)  # Simulate restart time
        
        # Step 6: Health checks
        health_status = self.health_check()
        if health_status.get('status') != 'healthy':
            self.log("❌ Health check failed after deployment", "ERROR")
            return False
        
        # Step 7: Enable features gradually
        for feature in features_to_enable:
            self.log(f"🚩 Enabling feature flag: {feature}")
            if not self.run_command(
                f"python manage.py manage_feature_flags --enable {feature}",
                f"Enable feature {feature}"
            ):
                self.log(f"⚠️  Failed to enable feature {feature}", "WARNING")
        
        # Step 8: Final SLO check
        slo_status = self.slo_check()
        if slo_status.get('overall_status') == 'CRITICAL':
            self.log("❌ Critical SLO violations - consider rollback", "ERROR")
            return False
        
        self.log("✅ Deployment completed successfully!")
        return True
    
    def canary_deployment(self, feature_name: str, canary_percentage: float = 5.0) -> bool:
        """Perform canary deployment"""
        self.log(f"🐤 Starting canary deployment for {feature_name} at {canary_percentage}%")
        
        # Enable canary
        if not self.run_command(
            f"python manage.py manage_feature_flags --enable {feature_name}",
            f"Enable canary for {feature_name}"
        ):
            return False
        
        # Monitor canary for 5 minutes
        self.log("📊 Monitoring canary deployment...")
        monitoring_duration = 300  # 5 minutes
        check_interval = 30  # 30 seconds
        
        for i in range(0, monitoring_duration, check_interval):
            time.sleep(check_interval)
            
            # Check canary health
            if not self.run_command(
                f"python manage.py manage_feature_flags --canary-status {feature_name}",
                f"Check canary status ({i + check_interval}s)"
            ):
                self.log("❌ Canary monitoring failed", "ERROR")
                return False
            
            # Check overall system health
            health_status = self.health_check()
            if health_status.get('status') != 'healthy':
                self.log("❌ System health degraded during canary", "ERROR")
                return False
        
        # Promote canary if successful
        self.log("🚀 Promoting canary to full rollout")
        return self.run_command(
            f"python manage.py manage_feature_flags --promote-canary {feature_name}",
            f"Promote canary {feature_name}"
        )
    
    def rollback(self, reason: str = "Manual rollback") -> bool:
        """Perform emergency rollback"""
        self.log(f"🔄 Starting emergency rollback: {reason}", "WARNING")
        
        # Disable all non-critical features
        critical_features = ["observability_tracing", "circuit_breakers"]
        
        rollback_commands = [
            ("python manage.py manage_feature_flags --emergency-disable new_tax_engine", "Disable new tax engine"),
            ("python manage.py manage_feature_flags --emergency-disable enhanced_error_handling", "Disable enhanced error handling"),
            ("python manage.py manage_feature_flags --emergency-disable shadow_calculation_comparison", "Disable shadow mode"),
        ]
        
        success = True
        for command, description in rollback_commands:
            if not self.run_command(command, description):
                success = False
        
        # Health check after rollback
        health_status = self.health_check()
        if health_status.get('status') == 'healthy':
            self.log("✅ Rollback completed - system is healthy")
        else:
            self.log("❌ System still unhealthy after rollback", "ERROR")
            success = False
        
        return success
    
    def save_deployment_log(self, filename: str = None):
        """Save deployment log to file"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"deployment_log_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write('\n'.join(self.deployment_log))
            self.log(f"📝 Deployment log saved to {filename}")
        except Exception as e:
            self.log(f"❌ Failed to save deployment log: {e}", "ERROR")


def main():
    """Main deployment script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MoneyRite Safe Deployment')
    parser.add_argument('--deploy', action='store_true', help='Perform full deployment')
    parser.add_argument('--canary', type=str, help='Perform canary deployment for feature')
    parser.add_argument('--rollback', action='store_true', help='Perform emergency rollback')
    parser.add_argument('--health-check', action='store_true', help='Perform health check only')
    parser.add_argument('--test-only', action='store_true', help='Run tests only')
    parser.add_argument('--base-url', default='http://localhost:8000', help='Base URL for health checks')
    
    args = parser.parse_args()
    
    deployer = DeploymentManager(args.base_url)
    
    try:
        if args.health_check:
            health_status = deployer.health_check()
            slo_status = deployer.slo_check()
            print(f"Health: {health_status.get('status')}")
            print(f"SLOs: {slo_status.get('overall_status')}")
            
        elif args.test_only:
            success = deployer.run_tests()
            sys.exit(0 if success else 1)
            
        elif args.deploy:
            features_to_enable = [
                "enhanced_error_handling",
                "observability_tracing",
                "circuit_breakers"
            ]
            success = deployer.deploy_with_feature_flags(features_to_enable)
            sys.exit(0 if success else 1)
            
        elif args.canary:
            success = deployer.canary_deployment(args.canary)
            sys.exit(0 if success else 1)
            
        elif args.rollback:
            success = deployer.rollback("Manual rollback requested")
            sys.exit(0 if success else 1)
            
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        deployer.log("❌ Deployment interrupted by user", "ERROR")
        sys.exit(1)
    except Exception as e:
        deployer.log(f"❌ Deployment failed with exception: {e}", "ERROR")
        sys.exit(1)
    finally:
        deployer.save_deployment_log()


if __name__ == '__main__':
    main()
