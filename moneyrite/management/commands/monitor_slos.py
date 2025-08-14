"""
SLO Monitoring Command for MoneyRite

Monitors Service Level Objectives and triggers alerts when thresholds are breached.
"""

import time
import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from moneyrite.observability import slo_monitor, observability


class Command(BaseCommand):
    help = 'Monitor SLOs and trigger alerts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Check current SLO status',
        )
        parser.add_argument(
            '--alert',
            action='store_true',
            help='Check for alert conditions',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate SLO report',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format',
        )

    def handle(self, *args, **options):
        if options['check']:
            self.check_slos(options['json'])
        elif options['alert']:
            self.check_alerts(options['json'])
        elif options['report']:
            self.generate_report(options['json'])
        else:
            self.stdout.write(self.style.ERROR('Please specify an action. Use --help for options.'))

    def check_slos(self, json_output=False):
        """Check current SLO status"""
        try:
            status = slo_monitor.check_slos()
            
            if json_output:
                self.stdout.write(json.dumps(status, indent=2))
                return
            
            self.stdout.write('📊 Current SLO Status')
            self.stdout.write('=' * 50)
            
            for slo_name, slo_data in status.items():
                current = slo_data['current']
                target = slo_data['target']
                error_budget = slo_data['error_budget_remaining']
                slo_status = slo_data['status']
                
                # Format based on SLO type
                if slo_name == 'latency_p95':
                    current_str = f"{current * 1000:.1f}ms"
                    target_str = f"{target * 1000:.1f}ms"
                else:
                    current_str = f"{current * 100:.2f}%"
                    target_str = f"{target * 100:.2f}%"
                
                # Status styling
                if slo_status == 'OK':
                    status_style = self.style.SUCCESS
                elif slo_status == 'WARNING':
                    status_style = self.style.WARNING
                else:
                    status_style = self.style.ERROR
                
                self.stdout.write(f"\n{slo_name.upper()}:")
                self.stdout.write(f"  Current: {current_str}")
                self.stdout.write(f"  Target:  {target_str}")
                self.stdout.write(f"  Error Budget: {error_budget * 100:.1f}%")
                self.stdout.write(f"  Status: {status_style(slo_status)}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to check SLOs: {e}'))

    def check_alerts(self, json_output=False):
        """Check for alert conditions"""
        try:
            status = slo_monitor.check_slos()
            alerts = []
            
            for slo_name, slo_data in status.items():
                if slo_monitor.should_alert(slo_name):
                    alert = {
                        'slo': slo_name,
                        'status': slo_data['status'],
                        'current': slo_data['current'],
                        'target': slo_data['target'],
                        'error_budget_remaining': slo_data['error_budget_remaining'],
                        'timestamp': timezone.now().isoformat()
                    }
                    alerts.append(alert)
            
            if json_output:
                self.stdout.write(json.dumps({
                    'alerts': alerts,
                    'alert_count': len(alerts)
                }, indent=2))
                return
            
            if alerts:
                self.stdout.write(self.style.ERROR(f'🚨 {len(alerts)} SLO ALERTS'))
                self.stdout.write('=' * 50)
                
                for alert in alerts:
                    slo_name = alert['slo']
                    status = alert['status']
                    
                    self.stdout.write(f"\nALERT: {slo_name.upper()} - {status}")
                    
                    if slo_name == 'latency_p95':
                        self.stdout.write(f"  Current latency: {alert['current'] * 1000:.1f}ms")
                        self.stdout.write(f"  Target: {alert['target'] * 1000:.1f}ms")
                    else:
                        self.stdout.write(f"  Current: {alert['current'] * 100:.2f}%")
                        self.stdout.write(f"  Target: {alert['target'] * 100:.2f}%")
                    
                    self.stdout.write(f"  Error budget: {alert['error_budget_remaining'] * 100:.1f}%")
                    
                    # Suggested actions
                    self.stdout.write("  Suggested actions:")
                    if slo_name == 'availability':
                        self.stdout.write("    - Check for service outages")
                        self.stdout.write("    - Review error logs")
                        self.stdout.write("    - Consider scaling resources")
                    elif slo_name == 'latency_p95':
                        self.stdout.write("    - Check database performance")
                        self.stdout.write("    - Review calculation complexity")
                        self.stdout.write("    - Consider caching improvements")
                    elif slo_name == 'accuracy':
                        self.stdout.write("    - Review recent rate updates")
                        self.stdout.write("    - Check calculation logic")
                        self.stdout.write("    - Run golden test vectors")
            else:
                self.stdout.write(self.style.SUCCESS('✅ No SLO alerts'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to check alerts: {e}'))

    def generate_report(self, json_output=False):
        """Generate comprehensive SLO report"""
        try:
            status = slo_monitor.check_slos()
            
            # Calculate overall health score
            health_scores = []
            for slo_data in status.values():
                if slo_data['status'] == 'OK':
                    health_scores.append(1.0)
                elif slo_data['status'] == 'WARNING':
                    health_scores.append(0.7)
                else:
                    health_scores.append(0.3)
            
            overall_health = sum(health_scores) / len(health_scores) if health_scores else 0
            
            report = {
                'timestamp': timezone.now().isoformat(),
                'overall_health_score': overall_health,
                'slo_status': status,
                'recommendations': self._generate_recommendations(status)
            }
            
            if json_output:
                self.stdout.write(json.dumps(report, indent=2))
                return
            
            self.stdout.write('📈 MoneyRite SLO Report')
            self.stdout.write('=' * 50)
            self.stdout.write(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.stdout.write(f"Overall Health Score: {overall_health * 100:.1f}%")
            
            # Health status
            if overall_health >= 0.9:
                health_status = self.style.SUCCESS("EXCELLENT")
            elif overall_health >= 0.7:
                health_status = self.style.WARNING("GOOD")
            elif overall_health >= 0.5:
                health_status = self.style.WARNING("FAIR")
            else:
                health_status = self.style.ERROR("POOR")
            
            self.stdout.write(f"System Health: {health_status}")
            
            # Detailed SLO status
            self.stdout.write('\n📊 Detailed SLO Status:')
            for slo_name, slo_data in status.items():
                self.stdout.write(f"\n{slo_name.upper()}:")
                self.stdout.write(f"  Status: {slo_data['status']}")
                self.stdout.write(f"  Error Budget: {slo_data['error_budget_remaining'] * 100:.1f}%")
            
            # Recommendations
            recommendations = report['recommendations']
            if recommendations:
                self.stdout.write('\n💡 Recommendations:')
                for i, rec in enumerate(recommendations, 1):
                    self.stdout.write(f"  {i}. {rec}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to generate report: {e}'))

    def _generate_recommendations(self, status):
        """Generate recommendations based on SLO status"""
        recommendations = []
        
        for slo_name, slo_data in status.items():
            if slo_data['status'] in ['WARNING', 'CRITICAL']:
                if slo_name == 'availability':
                    recommendations.append(
                        "Improve availability by implementing circuit breakers and better error handling"
                    )
                elif slo_name == 'latency_p95':
                    recommendations.append(
                        "Optimize calculation performance and consider implementing caching"
                    )
                elif slo_name == 'accuracy':
                    recommendations.append(
                        "Review calculation logic and run comprehensive test suite"
                    )
            
            if slo_data['error_budget_remaining'] < 0.2:  # Less than 20% error budget
                recommendations.append(
                    f"Error budget for {slo_name} is low - consider slowing down releases"
                )
        
        if not recommendations:
            recommendations.append("All SLOs are healthy - continue current practices")
        
        return recommendations
